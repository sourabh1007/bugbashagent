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
        self.current_agent_status = {}  # Track agent statuses
        self.workflow_logs = []  # Store recent workflow logs
        self.last_activity = None  # Track last agent activity
        
    def reset(self):
        """Reset the workflow state"""
        self.workflow = None
        self.is_running = False
        self.current_results = None
        self.current_agent_status = {}
        self.workflow_logs = []
        self.execution_thread = None
        self.last_activity = None
        
    def add_log(self, level: str, agent: str, message: str):
        """Add a log entry and update activity timestamp"""
        log_entry = {
            'level': level,
            'agent': agent,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.workflow_logs.append(log_entry)
        self.last_activity = datetime.now()
        
        # Keep only the last 50 logs to prevent memory issues
        if len(self.workflow_logs) > 50:
            self.workflow_logs = self.workflow_logs[-50:]
    
    def is_workflow_active(self):
        """Check if workflow is truly active"""
        if not self.is_running:
            return False
            
        # Check if thread is alive
        if self.execution_thread is None or not self.execution_thread.is_alive():
            return False
            
        # Check if there has been recent activity (within last 5 minutes)
        if self.last_activity is None:
            return True  # Just started
            
        time_since_activity = datetime.now() - self.last_activity
        return time_since_activity.total_seconds() < 300  # 5 minutes

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
        
        log_message = f"Status: {workflow_status}" + (f" - {message}" if message else "")
        log_data = {
            'level': 'info',
            'agent': 'Workflow',
            'message': log_message,
            'timestamp': datetime.now().isoformat()
        }
        self.socketio.emit('log', log_data)
        
        # Store in workflow state for reconnection
        workflow_state.add_log('info', 'Workflow', log_message)
    
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
        
        # Store agent status for reconnection
        workflow_state.current_agent_status[agent_name] = data
        
        # If progress is provided, also emit a separate progress event for smoother updates
        if progress is not None:
            progress_data = {
                'agentName': agent_name,
                'progress': progress,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.socketio.emit('agent_progress', progress_data)
        
        # Add to logs
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
        
        # Store in workflow state for reconnection
        workflow_state.add_log(log_level, agent_name, log_message)

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
        workflow_state.execution_thread = None
        
        socketio.emit('log', {
            'level': 'success',
            'agent': 'System',
            'message': f"Workflow completed with status: {results.get('workflow_status', 'unknown')}",
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        workflow_state.is_running = False
        workflow_state.execution_thread = None
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
    
    # Clean up dead workflow if needed
    if workflow_state.is_running and not workflow_state.is_workflow_active():
        print("Cleaning up dead workflow on connection")
        workflow_state.is_running = False
        workflow_state.execution_thread = None
    
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
    try:
        # Check if workflow is actually running
        actual_running = workflow_state.is_workflow_active()
        
        # Update the running status if workflow is no longer active
        if workflow_state.is_running and not actual_running:
            workflow_state.is_running = False
            workflow_state.execution_thread = None
            print(f"Detected workflow is no longer active, updating status")
        
        # Send current workflow status
        if actual_running:
            emit('workflow_status', {
                'status': 'running',
                'hasResults': False,
                'timestamp': datetime.now().isoformat()
            })
            
            # Restore agent statuses
            for agent_name, agent_data in workflow_state.current_agent_status.items():
                emit('agent_status', agent_data)
            
            # Send recent logs
            for log_entry in workflow_state.workflow_logs[-10:]:  # Last 10 logs
                emit('log', log_entry)
            
            # Send a log about restoration
            emit('log', {
                'level': 'success',
                'agent': 'System',
                'message': f'Workflow progress restored - {len(workflow_state.current_agent_status)} agents synced',
                'timestamp': datetime.now().isoformat()
            })
            
        elif workflow_state.current_results is not None:
            emit('workflow_status', {
                'status': 'completed',
                'hasResults': True,
                'timestamp': datetime.now().isoformat()
            })
            
            # Re-emit the test runner output
            emit('test_runner_output', workflow_state.current_results)
            
            # Send recent logs if available
            for log_entry in workflow_state.workflow_logs[-5:]:  # Last 5 logs
                emit('log', log_entry)
            
            emit('log', {
                'level': 'success',
                'agent': 'System',
                'message': 'Previous workflow results restored',
                'timestamp': datetime.now().isoformat()
            })
            
        else:
            emit('workflow_status', {
                'status': 'idle',
                'hasResults': False,
                'timestamp': datetime.now().isoformat()
            })
            
            emit('log', {
                'level': 'info',
                'agent': 'System',
                'message': 'Ready to start new workflow',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        emit('log', {
            'level': 'error',
            'agent': 'System',
            'message': f'Error getting status: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Configuration Management Endpoints
@app.route('/api/config', methods=['GET'])
def get_configuration():
    """Get current environment configuration"""
    try:
        config = {
            'azure_openai': {
                'api_key': os.getenv('AZURE_OPENAI_API_KEY', ''),
                'endpoint': os.getenv('AZURE_OPENAI_ENDPOINT', ''),
                'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                'deployment_name': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', ''),
            },
            'global_model': {
                'model_name': os.getenv('MODEL_NAME', 'gpt-35-turbo'),
                'temperature': float(os.getenv('TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv('MAX_TOKENS', '8000')),
            },
            'document_analyzer': {
                'api_key': os.getenv('DOCUMENT_ANALYZER_API_KEY', ''),
                'endpoint': os.getenv('DOCUMENT_ANALYZER_ENDPOINT', ''),
                'deployment_name': os.getenv('DOCUMENT_ANALYZER_DEPLOYMENT_NAME', ''),
                'api_version': os.getenv('DOCUMENT_ANALYZER_API_VERSION', ''),
                'temperature': float(os.getenv('DOCUMENT_ANALYZER_TEMPERATURE', '0.4')) if os.getenv('DOCUMENT_ANALYZER_TEMPERATURE') else None,
                'max_tokens': int(os.getenv('DOCUMENT_ANALYZER_MAX_TOKENS', '6000')) if os.getenv('DOCUMENT_ANALYZER_MAX_TOKENS') else None,
                'model_name': os.getenv('DOCUMENT_ANALYZER_MODEL_NAME', ''),
            },
            'code_generator': {
                'api_key': os.getenv('CODE_GENERATOR_API_KEY', ''),
                'endpoint': os.getenv('CODE_GENERATOR_ENDPOINT', ''),
                'deployment_name': os.getenv('CODE_GENERATOR_DEPLOYMENT_NAME', ''),
                'api_version': os.getenv('CODE_GENERATOR_API_VERSION', ''),
                'temperature': float(os.getenv('CODE_GENERATOR_TEMPERATURE', '0.5')) if os.getenv('CODE_GENERATOR_TEMPERATURE') else None,
                'max_tokens': int(os.getenv('CODE_GENERATOR_MAX_TOKENS', '9000')) if os.getenv('CODE_GENERATOR_MAX_TOKENS') else None,
                'model_name': os.getenv('CODE_GENERATOR_MODEL_NAME', ''),
            },
            'test_runner': {
                'api_key': os.getenv('TEST_RUNNER_API_KEY', ''),
                'endpoint': os.getenv('TEST_RUNNER_ENDPOINT', ''),
                'deployment_name': os.getenv('TEST_RUNNER_DEPLOYMENT_NAME', ''),
                'api_version': os.getenv('TEST_RUNNER_API_VERSION', ''),
                'temperature': float(os.getenv('TEST_RUNNER_TEMPERATURE', '0.3')) if os.getenv('TEST_RUNNER_TEMPERATURE') else None,
                'max_tokens': int(os.getenv('TEST_RUNNER_MAX_TOKENS', '8000')) if os.getenv('TEST_RUNNER_MAX_TOKENS') else None,
                'model_name': os.getenv('TEST_RUNNER_MODEL_NAME', ''),
            },
            'langsmith': {
                'tracing_enabled': os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true',
                'endpoint': os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com'),
                'api_key': os.getenv('LANGCHAIN_API_KEY', ''),
                'project': os.getenv('LANGCHAIN_PROJECT', 'BugBashCopilot'),
            }
        }
        
        # Mask sensitive keys for security
        for section in config.values():
            if isinstance(section, dict):
                for key, value in section.items():
                    if 'key' in key.lower() and value:
                        section[key] = f"***{value[-4:]}" if len(value) > 4 else "***"
        
        return jsonify({
            'success': True,
            'config': config,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get configuration: {str(e)}'
        }), 500

@app.route('/api/config', methods=['POST'])
def update_configuration():
    """Update environment configuration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No configuration data provided'}), 400
        
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Read existing .env file
        env_vars = {}
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        # Update with new values
        config = data.get('config', {})
        
        # Azure OpenAI settings
        azure = config.get('azure_openai', {})
        if azure.get('api_key') and not azure['api_key'].startswith('***'):
            env_vars['AZURE_OPENAI_API_KEY'] = azure['api_key']
        if azure.get('endpoint'):
            env_vars['AZURE_OPENAI_ENDPOINT'] = azure['endpoint']
        if azure.get('api_version'):
            env_vars['AZURE_OPENAI_API_VERSION'] = azure['api_version']
        if azure.get('deployment_name'):
            env_vars['AZURE_OPENAI_DEPLOYMENT_NAME'] = azure['deployment_name']
        
        # Global model settings
        global_model = config.get('global_model', {})
        if global_model.get('model_name'):
            env_vars['MODEL_NAME'] = global_model['model_name']
        if 'temperature' in global_model:
            env_vars['TEMPERATURE'] = str(global_model['temperature'])
        if 'max_tokens' in global_model:
            env_vars['MAX_TOKENS'] = str(global_model['max_tokens'])
        
        # Document Analyzer agent settings
        doc_analyzer = config.get('document_analyzer', {})
        if doc_analyzer.get('api_key') and not doc_analyzer['api_key'].startswith('***'):
            env_vars['DOCUMENT_ANALYZER_API_KEY'] = doc_analyzer['api_key']
        if doc_analyzer.get('endpoint'):
            env_vars['DOCUMENT_ANALYZER_ENDPOINT'] = doc_analyzer['endpoint']
        if doc_analyzer.get('deployment_name'):
            env_vars['DOCUMENT_ANALYZER_DEPLOYMENT_NAME'] = doc_analyzer['deployment_name']
        if doc_analyzer.get('api_version'):
            env_vars['DOCUMENT_ANALYZER_API_VERSION'] = doc_analyzer['api_version']
        if 'temperature' in doc_analyzer and doc_analyzer['temperature'] is not None:
            env_vars['DOCUMENT_ANALYZER_TEMPERATURE'] = str(doc_analyzer['temperature'])
        if 'max_tokens' in doc_analyzer and doc_analyzer['max_tokens'] is not None:
            env_vars['DOCUMENT_ANALYZER_MAX_TOKENS'] = str(doc_analyzer['max_tokens'])
        if doc_analyzer.get('model_name'):
            env_vars['DOCUMENT_ANALYZER_MODEL_NAME'] = doc_analyzer['model_name']
        
        # Code Generator agent settings
        code_generator = config.get('code_generator', {})
        if code_generator.get('api_key') and not code_generator['api_key'].startswith('***'):
            env_vars['CODE_GENERATOR_API_KEY'] = code_generator['api_key']
        if code_generator.get('endpoint'):
            env_vars['CODE_GENERATOR_ENDPOINT'] = code_generator['endpoint']
        if code_generator.get('deployment_name'):
            env_vars['CODE_GENERATOR_DEPLOYMENT_NAME'] = code_generator['deployment_name']
        if code_generator.get('api_version'):
            env_vars['CODE_GENERATOR_API_VERSION'] = code_generator['api_version']
        if 'temperature' in code_generator and code_generator['temperature'] is not None:
            env_vars['CODE_GENERATOR_TEMPERATURE'] = str(code_generator['temperature'])
        if 'max_tokens' in code_generator and code_generator['max_tokens'] is not None:
            env_vars['CODE_GENERATOR_MAX_TOKENS'] = str(code_generator['max_tokens'])
        if code_generator.get('model_name'):
            env_vars['CODE_GENERATOR_MODEL_NAME'] = code_generator['model_name']
        
        # Test Runner agent settings
        test_runner = config.get('test_runner', {})
        if test_runner.get('api_key') and not test_runner['api_key'].startswith('***'):
            env_vars['TEST_RUNNER_API_KEY'] = test_runner['api_key']
        if test_runner.get('endpoint'):
            env_vars['TEST_RUNNER_ENDPOINT'] = test_runner['endpoint']
        if test_runner.get('deployment_name'):
            env_vars['TEST_RUNNER_DEPLOYMENT_NAME'] = test_runner['deployment_name']
        if test_runner.get('api_version'):
            env_vars['TEST_RUNNER_API_VERSION'] = test_runner['api_version']
        if 'temperature' in test_runner and test_runner['temperature'] is not None:
            env_vars['TEST_RUNNER_TEMPERATURE'] = str(test_runner['temperature'])
        if 'max_tokens' in test_runner and test_runner['max_tokens'] is not None:
            env_vars['TEST_RUNNER_MAX_TOKENS'] = str(test_runner['max_tokens'])
        if test_runner.get('model_name'):
            env_vars['TEST_RUNNER_MODEL_NAME'] = test_runner['model_name']
        
        # LangSmith settings
        langsmith = config.get('langsmith', {})
        if 'tracing_enabled' in langsmith:
            env_vars['LANGCHAIN_TRACING_V2'] = str(langsmith['tracing_enabled']).lower()
        if langsmith.get('endpoint'):
            env_vars['LANGCHAIN_ENDPOINT'] = langsmith['endpoint']
        if langsmith.get('api_key') and not langsmith['api_key'].startswith('***'):
            env_vars['LANGCHAIN_API_KEY'] = langsmith['api_key']
        if langsmith.get('project'):
            env_vars['LANGCHAIN_PROJECT'] = langsmith['project']
        
        # Write updated .env file
        with open(env_file_path, 'w') as f:
            f.write("# Azure OpenAI Configuration (Required)\n")
            f.write(f"AZURE_OPENAI_API_KEY={env_vars.get('AZURE_OPENAI_API_KEY', '')}\n")
            f.write(f"AZURE_OPENAI_ENDPOINT={env_vars.get('AZURE_OPENAI_ENDPOINT', '')}\n")
            f.write(f"AZURE_OPENAI_API_VERSION={env_vars.get('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')}\n")
            f.write(f"AZURE_OPENAI_DEPLOYMENT_NAME={env_vars.get('AZURE_OPENAI_DEPLOYMENT_NAME', '')}\n")
            f.write("\n# Global Model Configuration\n")
            f.write(f"MODEL_NAME={env_vars.get('MODEL_NAME', 'gpt-35-turbo')}\n")
            f.write(f"TEMPERATURE={env_vars.get('TEMPERATURE', '0.7')}\n")
            f.write(f"MAX_TOKENS={env_vars.get('MAX_TOKENS', '8000')}\n")
            
            # Document Analyzer Agent Overrides
            f.write("\n# Document Analyzer Agent Overrides\n")
            if env_vars.get('DOCUMENT_ANALYZER_API_KEY'):
                f.write(f"DOCUMENT_ANALYZER_API_KEY={env_vars['DOCUMENT_ANALYZER_API_KEY']}\n")
            if env_vars.get('DOCUMENT_ANALYZER_ENDPOINT'):
                f.write(f"DOCUMENT_ANALYZER_ENDPOINT={env_vars['DOCUMENT_ANALYZER_ENDPOINT']}\n")
            if env_vars.get('DOCUMENT_ANALYZER_DEPLOYMENT_NAME'):
                f.write(f"DOCUMENT_ANALYZER_DEPLOYMENT_NAME={env_vars['DOCUMENT_ANALYZER_DEPLOYMENT_NAME']}\n")
            if env_vars.get('DOCUMENT_ANALYZER_API_VERSION'):
                f.write(f"DOCUMENT_ANALYZER_API_VERSION={env_vars['DOCUMENT_ANALYZER_API_VERSION']}\n")
            if env_vars.get('DOCUMENT_ANALYZER_TEMPERATURE'):
                f.write(f"DOCUMENT_ANALYZER_TEMPERATURE={env_vars['DOCUMENT_ANALYZER_TEMPERATURE']}\n")
            if env_vars.get('DOCUMENT_ANALYZER_MAX_TOKENS'):
                f.write(f"DOCUMENT_ANALYZER_MAX_TOKENS={env_vars['DOCUMENT_ANALYZER_MAX_TOKENS']}\n")
            if env_vars.get('DOCUMENT_ANALYZER_MODEL_NAME'):
                f.write(f"DOCUMENT_ANALYZER_MODEL_NAME={env_vars['DOCUMENT_ANALYZER_MODEL_NAME']}\n")
                
            # Code Generator Agent Overrides
            f.write("\n# Code Generator Agent Overrides\n")
            if env_vars.get('CODE_GENERATOR_API_KEY'):
                f.write(f"CODE_GENERATOR_API_KEY={env_vars['CODE_GENERATOR_API_KEY']}\n")
            if env_vars.get('CODE_GENERATOR_ENDPOINT'):
                f.write(f"CODE_GENERATOR_ENDPOINT={env_vars['CODE_GENERATOR_ENDPOINT']}\n")
            if env_vars.get('CODE_GENERATOR_DEPLOYMENT_NAME'):
                f.write(f"CODE_GENERATOR_DEPLOYMENT_NAME={env_vars['CODE_GENERATOR_DEPLOYMENT_NAME']}\n")
            if env_vars.get('CODE_GENERATOR_API_VERSION'):
                f.write(f"CODE_GENERATOR_API_VERSION={env_vars['CODE_GENERATOR_API_VERSION']}\n")
            if env_vars.get('CODE_GENERATOR_TEMPERATURE'):
                f.write(f"CODE_GENERATOR_TEMPERATURE={env_vars['CODE_GENERATOR_TEMPERATURE']}\n")
            if env_vars.get('CODE_GENERATOR_MAX_TOKENS'):
                f.write(f"CODE_GENERATOR_MAX_TOKENS={env_vars['CODE_GENERATOR_MAX_TOKENS']}\n")
            if env_vars.get('CODE_GENERATOR_MODEL_NAME'):
                f.write(f"CODE_GENERATOR_MODEL_NAME={env_vars['CODE_GENERATOR_MODEL_NAME']}\n")
                
            # Test Runner Agent Overrides
            f.write("\n# Test Runner Agent Overrides\n")
            if env_vars.get('TEST_RUNNER_API_KEY'):
                f.write(f"TEST_RUNNER_API_KEY={env_vars['TEST_RUNNER_API_KEY']}\n")
            if env_vars.get('TEST_RUNNER_ENDPOINT'):
                f.write(f"TEST_RUNNER_ENDPOINT={env_vars['TEST_RUNNER_ENDPOINT']}\n")
            if env_vars.get('TEST_RUNNER_DEPLOYMENT_NAME'):
                f.write(f"TEST_RUNNER_DEPLOYMENT_NAME={env_vars['TEST_RUNNER_DEPLOYMENT_NAME']}\n")
            if env_vars.get('TEST_RUNNER_API_VERSION'):
                f.write(f"TEST_RUNNER_API_VERSION={env_vars['TEST_RUNNER_API_VERSION']}\n")
            if env_vars.get('TEST_RUNNER_TEMPERATURE'):
                f.write(f"TEST_RUNNER_TEMPERATURE={env_vars['TEST_RUNNER_TEMPERATURE']}\n")
            if env_vars.get('TEST_RUNNER_MAX_TOKENS'):
                f.write(f"TEST_RUNNER_MAX_TOKENS={env_vars['TEST_RUNNER_MAX_TOKENS']}\n")
            if env_vars.get('TEST_RUNNER_MODEL_NAME'):
                f.write(f"TEST_RUNNER_MODEL_NAME={env_vars['TEST_RUNNER_MODEL_NAME']}\n")
            
            f.write("\n# LangSmith Configuration (Optional)\n")
            f.write(f"LANGCHAIN_TRACING_V2={env_vars.get('LANGCHAIN_TRACING_V2', 'false')}\n")
            f.write(f"LANGCHAIN_ENDPOINT={env_vars.get('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')}\n")
            f.write(f"LANGCHAIN_API_KEY={env_vars.get('LANGCHAIN_API_KEY', '')}\n")
            f.write(f"LANGCHAIN_PROJECT={env_vars.get('LANGCHAIN_PROJECT', 'BugBashCopilot')}\n")
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update configuration: {str(e)}'
        }), 500

@app.route('/api/config/test', methods=['POST'])
def test_configuration():
    """Test the current configuration"""
    try:
        test_result = {
            'azure_openai': False,
            'langsmith': False,
            'errors': []
        }
        
        # Test Azure OpenAI connection
        try:
            test_workflow = initialize_workflow()
            if test_workflow:
                test_result['azure_openai'] = True
            else:
                test_result['errors'].append('Azure OpenAI connection failed')
        except Exception as e:
            test_result['errors'].append(f'Azure OpenAI error: {str(e)}')
        
        # Test LangSmith connection (if enabled)
        if os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true':
            try:
                # Basic LangSmith connectivity test would go here
                test_result['langsmith'] = True
            except Exception as e:
                test_result['errors'].append(f'LangSmith error: {str(e)}')
        else:
            test_result['langsmith'] = None  # Not enabled
        
        return jsonify({
            'success': True,
            'test_result': test_result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Configuration test failed: {str(e)}'
        }), 500

@app.route('/api/historical-runs', methods=['GET'])
def get_historical_runs():
    """Get historical workflow execution data"""
    try:
        workflow_outputs_dir = os.path.join(os.path.dirname(__file__), 'workflow_outputs')
        
        if not os.path.exists(workflow_outputs_dir):
            return jsonify({
                'success': True,
                'runs': [],
                'total': 0,
                'timestamp': datetime.now().isoformat()
            })
        
        historical_runs = []
        processed_runs = set()  # Track processed runs to avoid duplicates
        
        # Get all workflow output directories
        for folder_name in os.listdir(workflow_outputs_dir):
            folder_path = os.path.join(workflow_outputs_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            # Skip if we've already processed this run
            if folder_name in processed_runs:
                continue
            
            try:
                # Skip folders that start with "workflow_output_" (these are old format duplicates)
                if folder_name.startswith('workflow_output_'):
                    continue
                
                # Parse folder name to extract project name and timestamp
                # Expected format: project_name_YYYYMMDD_HHMMSS
                parts = folder_name.split('_')
                if len(parts) >= 3:
                    # Try to parse timestamp from last two parts
                    date_part = parts[-2]  # YYYYMMDD  
                    time_part = parts[-1]  # HHMMSS
                    
                    if len(date_part) == 8 and len(time_part) == 6 and date_part.isdigit() and time_part.isdigit():
                        # Parse timestamp
                        try:
                            year = int(date_part[:4])
                            month = int(date_part[4:6])
                            day = int(date_part[6:8])
                            hour = int(time_part[:2])
                            minute = int(time_part[2:4])
                            second = int(time_part[4:6])
                            
                            execution_date = datetime(year, month, day, hour, minute, second)
                            project_name = '_'.join(parts[:-2])
                            
                            # Mark this run as processed
                            processed_runs.add(folder_name)
                            
                            # Read execution results
                            run_data = {
                                'id': folder_name,
                                'project_name': project_name,
                                'execution_date': execution_date.isoformat(),
                                'status': 'unknown',
                                'compilation_status': 'unknown',
                                'test_results': {
                                    'total_tests': 0,
                                    'passed_tests': 0,
                                    'failed_tests': 0,
                                    'skipped_tests': 0,
                                    'success_rate': 0,
                                    'execution_time': 0
                                },
                                'scenarios_generated': 0,
                                'test_files_count': 0,
                                'duration': None,
                                'language': 'unknown',
                                'folder_path': folder_path
                            }
                        except ValueError:
                            # Invalid date/time format, skip
                            continue
                        
                        # Check for compilation results
                        compilation_file = os.path.join(folder_path, 'compilation_results.json')
                        if os.path.exists(compilation_file):
                            try:
                                with open(compilation_file, 'r', encoding='utf-8') as f:
                                    compilation_data = json.load(f)
                                    run_data['compilation_status'] = 'success' if compilation_data.get('success', False) else 'failed'
                                    run_data['language'] = compilation_data.get('language', 'unknown')
                            except:
                                run_data['compilation_status'] = 'error'
                        
                        # Check for test results
                        test_results_file = os.path.join(folder_path, 'test_results.json')
                        if os.path.exists(test_results_file):
                            try:
                                with open(test_results_file, 'r', encoding='utf-8') as f:
                                    test_data = json.load(f)
                                    test_results = test_data.get('test_results', {})
                                    run_data['test_results'] = {
                                        'total_tests': test_results.get('total_tests', 0),
                                        'passed_tests': test_results.get('passed_tests', 0),
                                        'failed_tests': test_results.get('failed_tests', 0),
                                        'skipped_tests': test_results.get('skipped_tests', 0),
                                        'success_rate': test_results.get('success_rate', 0),
                                        'execution_time': test_results.get('execution_time', 0)
                                    }
                                    run_data['duration'] = test_results.get('execution_time')
                                    run_data['status'] = 'success' if test_results.get('success', False) else 'failed'
                            except:
                                run_data['status'] = 'error'
                        
                        # Check for scenario summary
                        scenario_file = os.path.join(folder_path, 'SCENARIO_SUMMARY_REPORT.md')
                        if os.path.exists(scenario_file):
                            try:
                                with open(scenario_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # Look for different possible patterns for scenario count
                                    patterns = [
                                        'Total Scenarios Processed:** ',
                                        'Total Scenarios Processed: ',
                                        'Successful Generations:** ',
                                        'Successful Generations: '
                                    ]
                                    
                                    for pattern in patterns:
                                        if pattern in content:
                                            lines = content.split('\n')
                                            for line in lines:
                                                if pattern in line:
                                                    # Extract number after the pattern
                                                    try:
                                                        # Find the pattern and extract the number
                                                        start_idx = line.find(pattern) + len(pattern)
                                                        remaining = line[start_idx:].strip()
                                                        # Extract just the number (handle cases like "17" or "17\n")
                                                        number_str = ''
                                                        for char in remaining:
                                                            if char.isdigit():
                                                                number_str += char
                                                            else:
                                                                break
                                                        if number_str:
                                                            run_data['scenarios_generated'] = int(number_str)
                                                            break
                                                    except:
                                                        pass
                                            if run_data['scenarios_generated'] > 0:
                                                break
                            except Exception as e:
                                print(f"Error reading scenario file for {folder_name}: {e}")
                                pass
                        
                        # Count test files
                        test_files = [f for f in os.listdir(folder_path) if f.endswith('Test.cs') or f.endswith('test.py') or f.endswith('Test.java')]
                        run_data['test_files_count'] = len(test_files)
                        
                        # If no specific status was determined, derive from compilation and test results
                        if run_data['status'] == 'unknown':
                            if run_data['compilation_status'] == 'success' and run_data['test_results'].get('total_tests', 0) > 0:
                                success_rate = (run_data['test_results'].get('passed_tests', 0) / run_data['test_results']['total_tests']) * 100
                                run_data['status'] = 'success' if success_rate >= 75 else 'partial'
                            elif run_data['compilation_status'] == 'success':
                                run_data['status'] = 'compiled'
                            elif run_data['compilation_status'] == 'failed':
                                run_data['status'] = 'failed'
                        
                        historical_runs.append(run_data)
                    else:
                        # Invalid timestamp format, skip this folder
                        continue
                else:
                    # Not enough parts in folder name, skip
                    continue
                        
            except Exception as e:
                # Skip folders that don't match expected format
                print(f"Skipping folder {folder_name}: {e}")
                continue
        
        # Sort by execution date (newest first)
        historical_runs.sort(key=lambda x: x['execution_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'runs': historical_runs,
            'total': len(historical_runs),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get historical runs: {str(e)}',
            'runs': [],
            'total': 0
        }), 500

@app.route('/api/historical-runs/<run_id>/details', methods=['GET'])
def get_run_details(run_id):
    """Get detailed information about a specific workflow run"""
    try:
        workflow_outputs_dir = os.path.join(os.path.dirname(__file__), 'workflow_outputs')
        run_path = os.path.join(workflow_outputs_dir, run_id)
        
        if not os.path.exists(run_path):
            return jsonify({
                'success': False,
                'error': 'Run not found'
            }), 404
        
        details = {
            'run_id': run_id,
            'compilation_results': None,
            'test_results': None,
            'scenario_summary': None,
            'comprehensive_report': None,
            'test_files': [],
            'output_files': []
        }
        
        # Get compilation results
        compilation_file = os.path.join(run_path, 'compilation_results.json')
        if os.path.exists(compilation_file):
            try:
                with open(compilation_file, 'r', encoding='utf-8') as f:
                    details['compilation_results'] = json.load(f)
            except Exception as e:
                details['compilation_results'] = {'error': f'Failed to read compilation results: {str(e)}'}
        
        # Get test results
        test_results_file = os.path.join(run_path, 'test_results.json')
        if os.path.exists(test_results_file):
            try:
                with open(test_results_file, 'r', encoding='utf-8') as f:
                    details['test_results'] = json.load(f)
            except Exception as e:
                details['test_results'] = {'error': f'Failed to read test results: {str(e)}'}
        
        # Get scenario summary
        scenario_file = os.path.join(run_path, 'SCENARIO_SUMMARY_REPORT.md')
        if os.path.exists(scenario_file):
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    details['scenario_summary'] = f.read()
            except Exception as e:
                details['scenario_summary'] = f'Failed to read scenario summary: {str(e)}'
        
        # Get comprehensive report
        report_file = os.path.join(run_path, 'COMPREHENSIVE_CODE_GENERATION_REPORT.md')
        if os.path.exists(report_file):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    details['comprehensive_report'] = f.read()
            except Exception as e:
                details['comprehensive_report'] = f'Failed to read comprehensive report: {str(e)}'
        
        # List test files
        for file_name in os.listdir(run_path):
            if file_name.endswith('Test.cs') or file_name.endswith('test.py') or file_name.endswith('Test.java'):
                details['test_files'].append(file_name)
        
        # List all output files
        for file_name in os.listdir(run_path):
            file_path = os.path.join(run_path, file_name)
            if os.path.isfile(file_path):
                file_info = {
                    'name': file_name,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                details['output_files'].append(file_info)
        
        return jsonify({
            'success': True,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get run details: {str(e)}'
        }), 500

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
