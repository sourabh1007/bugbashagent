#!/usr/bin/env python3
"""
Bug Bash Copilot Flask Backend with WebSocket Support

This Flask application provides a REST API and WebSocket interface for the React frontend
to communicate with the Bug Bash Copilot workflow system.

Features:
- WebSocket real-time communication for workflow status updates
- REST API endpoints for workflow management
- Real-time progress tracking and logging
- Integration with existing workflow system
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS

# Add the parent directory to Python path to import workflow modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the existing workflow components
try:
    from workflow import AgentWorkflow
    from integrations import (
        get_azure_openai_client,
        get_agent_azure_openai_client,
        check_azure_config,
        configure_llm_tracing
    )
    from config_package import TEMPERATURE
    print("✅ Successfully imported workflow components")
except ImportError as e:
    print(f"❌ Error importing workflow components: {e}")
    print("Make sure you're running this from the Bug Bash Copilot directory")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Enable CORS for React frontend
CORS(app, origins=["http://localhost:3000"])

# Initialize SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins="http://localhost:3000",
    logger=True,
    engineio_logger=True
)

# Global state management
class WorkflowState:
    def __init__(self):
        self.workflow: Optional[AgentWorkflow] = None
        self.is_running = False
        self.current_results: Optional[Dict[str, Any]] = None
        self.execution_thread: Optional[threading.Thread] = None
        self.connected_clients = set()
        
    def reset(self):
        """Reset the workflow state"""
        self.workflow = None
        self.is_running = False
        self.current_results = None
        self.execution_thread = None

# Global workflow state
workflow_state = WorkflowState()

class SocketIOCallbackHandler:
    """Handles callbacks from the workflow and forwards them via SocketIO"""
    
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
    
    def workflow_status_callback(self, workflow_status: str, message: str = "", 
                                current_agent: str = None, current_step: int = None, 
                                total_steps: int = None):
        """Handle workflow status updates"""
        data = {
            'status': workflow_status,
            'message': message,
            'currentAgent': current_agent,
            'currentStep': current_step,
            'totalSteps': total_steps,
            'timestamp': datetime.now().isoformat()
        }
        self.socketio.emit('workflow_status', data)
        self.socketio.emit('log', {
            'level': 'info',
            'agent': 'Workflow',
            'message': f"Status: {workflow_status}" + (f" - {message}" if message else ""),
            'timestamp': datetime.now().isoformat()
        })
    
    def agent_status_callback(self, agent_name: str, status: str, message: str = "", progress: float = None):
        """Handle agent status updates"""
        data = {
            'agentName': agent_name,
            'status': status,
            'message': message,
            'progress': progress,
            'timestamp': datetime.now().isoformat()
        }
        self.socketio.emit('agent_status', data)
        
        # If progress is provided, also emit a separate progress event for smoother updates
        if progress is not None:
            progress_data = {
                'agentName': agent_name,
                'progress': progress,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.socketio.emit('agent_progress', progress_data)
        
        # Also emit as a log entry
        log_level = 'error' if status == 'error' else 'info'
        log_message = message if message else f"Status: {status}"
        if progress is not None:
            log_message += f" ({progress:.1f}%)"
            
        self.socketio.emit('log', {
            'level': log_level,
            'agent': agent_name,
            'message': log_message,
            'timestamp': datetime.now().isoformat()
        })

# Initialize callback handler
callback_handler = SocketIOCallbackHandler(socketio)

def initialize_workflow():
    """Initialize the workflow with LLM clients and callbacks"""
    try:
        # Check Azure configuration
        check_azure_config()
        
        # Initialize LLMs
        document_llm = get_agent_azure_openai_client("document_analyzer", temperature=TEMPERATURE)
        code_llm = get_agent_azure_openai_client("code_generator", temperature=TEMPERATURE)
        
        # Configure tracing
        llm = configure_llm_tracing(document_llm)
        
        # Create workflow
        workflow = AgentWorkflow(llm, code_llm=code_llm)
        
        # Set up callbacks for real-time updates
        workflow.set_status_callback(callback_handler.workflow_status_callback)
        workflow.set_agent_status_callback(callback_handler.agent_status_callback)
        
        return workflow
        
    except Exception as e:
        print(f"❌ Error initializing workflow: {e}")
        return None

def run_workflow_async(workflow: AgentWorkflow, input_data: str):
    """Run workflow in a separate thread"""
    try:
        workflow_state.is_running = True
        
        # Emit start event
        socketio.emit('log', {
            'level': 'info',
            'agent': 'System',
            'message': 'Starting Bug Bash Copilot workflow...',
            'timestamp': datetime.now().isoformat()
        })
        
        # Execute workflow
        results = workflow.execute_workflow(input_data)
        workflow_state.current_results = results
        
        # Check if Test Runner completed and has output
        if results.get('workflow_status') == 'completed':
            test_runner_output = None
            for agent_output in results.get('agent_outputs', []):
                if agent_output.get('agent') == 'Test Runner' and agent_output.get('status') == 'success':
                    # Extract the test runner output
                    output_data = agent_output.get('output', {})
                    if isinstance(output_data, dict) and 'output' in output_data:
                        test_runner_output = output_data['output']
                    else:
                        test_runner_output = str(output_data)
                    break
            
            if test_runner_output:
                socketio.emit('test_runner_output', test_runner_output)
        
        workflow_state.is_running = False
        
        socketio.emit('log', {
            'level': 'success',
            'agent': 'System',
            'message': f"Workflow completed with status: {results.get('workflow_status', 'unknown')}",
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        workflow_state.is_running = False
        workflow_state.current_results = {
            "workflow_status": "error",
            "error": str(e),
            "agent_outputs": []
        }
        
        socketio.emit('log', {
            'level': 'error',
            'agent': 'System',
            'message': f"Workflow error: {str(e)}",
            'timestamp': datetime.now().isoformat()
        })

# REST API Endpoints

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'connected_clients': len(workflow_state.connected_clients)
    })

@app.route('/api/workflow/status', methods=['GET'])
def get_workflow_status():
    """Get current workflow status"""
    return jsonify({
        'isRunning': workflow_state.is_running,
        'results': workflow_state.current_results,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/workflow/start', methods=['POST'])
def start_workflow():
    """Start the workflow"""
    try:
        data = request.get_json()
        input_data = data.get('inputData', '')
        
        if not input_data:
            return jsonify({'error': 'No input data provided'}), 400
        
        if workflow_state.is_running:
            return jsonify({'error': 'Workflow is already running'}), 409
        
        # Initialize workflow
        workflow = initialize_workflow()
        if not workflow:
            return jsonify({'error': 'Failed to initialize workflow'}), 500
        
        workflow_state.workflow = workflow
        
        # Start workflow in background thread
        thread = threading.Thread(
            target=run_workflow_async, 
            args=(workflow, input_data)
        )
        thread.daemon = True
        thread.start()
        workflow_state.execution_thread = thread
        
        return jsonify({
            'message': 'Workflow started successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/reset', methods=['POST'])
def reset_workflow():
    """Reset the workflow"""
    try:
        if workflow_state.is_running:
            return jsonify({'error': 'Cannot reset while workflow is running'}), 409
        
        workflow_state.reset()
        
        return jsonify({
            'message': 'Workflow reset successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    workflow_state.connected_clients.add(request.sid)
    
    # Send connection confirmation
    emit('log', {
        'level': 'info',
        'agent': 'System',
        'message': 'Connected to Bug Bash Copilot server',
        'timestamp': datetime.now().isoformat()
    })
    
    # Send current workflow status if available
    if workflow_state.current_results:
        emit('workflow_status', {
            'status': workflow_state.current_results.get('workflow_status', 'unknown'),
            'message': 'Reconnected to existing session',
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    workflow_state.connected_clients.discard(request.sid)

@socketio.on('start_workflow')
def handle_start_workflow(data):
    """Handle workflow start request via WebSocket"""
    try:
        input_data = data.get('inputData', '')
        
        if not input_data:
            emit('log', {
                'level': 'error',
                'agent': 'System',
                'message': 'No input data provided',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        if workflow_state.is_running:
            emit('log', {
                'level': 'warning',
                'agent': 'System',
                'message': 'Workflow is already running',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # Initialize workflow
        workflow = initialize_workflow()
        if not workflow:
            emit('log', {
                'level': 'error',
                'agent': 'System',
                'message': 'Failed to initialize workflow',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        workflow_state.workflow = workflow
        
        # Start workflow in background thread
        thread = threading.Thread(
            target=run_workflow_async, 
            args=(workflow, input_data)
        )
        thread.daemon = True
        thread.start()
        workflow_state.execution_thread = thread
        
        emit('log', {
            'level': 'info',
            'agent': 'System',
            'message': 'Workflow initialization completed',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        emit('log', {
            'level': 'error',
            'agent': 'System',
            'message': f'Error starting workflow: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('get_status')
def handle_get_status():
    """Handle status request"""
    emit('workflow_status', {
        'status': 'running' if workflow_state.is_running else 'idle',
        'hasResults': workflow_state.current_results is not None,
        'timestamp': datetime.now().isoformat()
    })

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Bug Bash Copilot Backend Server...")
    print("Frontend should connect to: http://localhost:5000")
    print("WebSocket endpoint: ws://localhost:5000/socket.io/")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Test workflow initialization on startup
        test_workflow = initialize_workflow()
        if test_workflow:
            print("✅ Workflow initialization test successful")
        else:
            print("⚠️ Workflow initialization test failed - check your configuration")
    except Exception as e:
        print(f"⚠️ Warning: Workflow initialization test failed: {e}")
    
    # Start the server
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        allow_unsafe_werkzeug=True
    )
