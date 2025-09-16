import React, { createContext, useContext, useReducer, useEffect } from 'react';
import io from 'socket.io-client';

const WorkflowContext = createContext();

// Initial state
const initialState = {
  workflowStatus: 'idle', // idle, running, completed, failed
  currentAgent: null,
  currentStep: 0,
  totalSteps: 3,
  agents: [
    {
      name: 'Document Analyzer',
      icon: '📊',
      description: 'Setup Guide Analysis & Test Scenario Extraction',
      status: 'pending',
      progress: 0,
      message: 'Waiting to start...',
      startTime: null,
      endTime: null,
      output: null
    },
    {
      name: 'Code Generator',
      icon: '⚙️',
      description: 'Automated Test Script Generation & Compilation',
      status: 'pending',
      progress: 0,
      message: 'Waiting to start...',
      startTime: null,
      endTime: null,
      output: null
    },
    {
      name: 'Test Runner',
      icon: '🔍',
      description: 'Bug Bash Execution & Comprehensive Reporting',
      status: 'pending',
      progress: 0,
      message: 'Waiting to start...',
      startTime: null,
      endTime: null,
      output: null
    }
  ],
  logs: [],
  testRunnerOutput: null,
  inputData: '',
  socket: null,
  isConnected: false
};

// Action types
const actionTypes = {
  SET_INPUT_DATA: 'SET_INPUT_DATA',
  START_WORKFLOW: 'START_WORKFLOW',
  UPDATE_WORKFLOW_STATUS: 'UPDATE_WORKFLOW_STATUS',
  UPDATE_AGENT_STATUS: 'UPDATE_AGENT_STATUS',
  UPDATE_AGENT_PROGRESS: 'UPDATE_AGENT_PROGRESS',
  ADD_LOG: 'ADD_LOG',
  SET_TEST_RUNNER_OUTPUT: 'SET_TEST_RUNNER_OUTPUT',
  SET_SOCKET: 'SET_SOCKET',
  SET_CONNECTION_STATUS: 'SET_CONNECTION_STATUS',
  RESET_WORKFLOW: 'RESET_WORKFLOW'
};

// Reducer function
function workflowReducer(state, action) {
  switch (action.type) {
    case actionTypes.SET_INPUT_DATA:
      return {
        ...state,
        inputData: action.payload
      };

    case actionTypes.START_WORKFLOW:
      return {
        ...state,
        workflowStatus: 'running',
        currentStep: 1,
        agents: state.agents.map((agent, index) => ({
          ...agent,
          status: index === 0 ? 'starting' : 'pending',
          startTime: index === 0 ? new Date() : null
        }))
      };

    case actionTypes.UPDATE_WORKFLOW_STATUS:
      return {
        ...state,
        workflowStatus: action.payload.status,
        currentAgent: action.payload.currentAgent,
        currentStep: action.payload.currentStep || state.currentStep
      };

    case actionTypes.UPDATE_AGENT_STATUS:
      const { agentName, status, message, progress } = action.payload;
      return {
        ...state,
        agents: state.agents.map(agent => {
          if (agent.name === agentName) {
            const updatedAgent = {
              ...agent,
              status,
              message: message || agent.message,
              progress: progress !== undefined ? progress : agent.progress
            };

            // Set timestamps
            if (status === 'running' && !agent.startTime) {
              updatedAgent.startTime = new Date();
            } else if ((status === 'success' || status === 'error') && !agent.endTime) {
              updatedAgent.endTime = new Date();
            }

            return updatedAgent;
          }
          return agent;
        })
      };

    case actionTypes.UPDATE_AGENT_PROGRESS:
      return {
        ...state,
        agents: state.agents.map(agent => 
          agent.name === action.payload.agentName
            ? { ...agent, progress: action.payload.progress, message: action.payload.message || agent.message }
            : agent
        )
      };

    case actionTypes.ADD_LOG:
      return {
        ...state,
        logs: [
          ...state.logs,
          {
            id: Date.now() + Math.random(),
            timestamp: new Date(),
            ...action.payload
          }
        ].slice(-100) // Keep only last 100 logs
      };

    case actionTypes.SET_TEST_RUNNER_OUTPUT:
      return {
        ...state,
        testRunnerOutput: action.payload,
        agents: state.agents.map(agent => 
          agent.name === 'Test Runner'
            ? { ...agent, output: action.payload }
            : agent
        )
      };

    case actionTypes.SET_SOCKET:
      return {
        ...state,
        socket: action.payload
      };

    case actionTypes.SET_CONNECTION_STATUS:
      return {
        ...state,
        isConnected: action.payload
      };

    case actionTypes.RESET_WORKFLOW:
      return {
        ...initialState,
        socket: state.socket,
        isConnected: state.isConnected
      };

    default:
      return state;
  }
}

// Context provider component
export function WorkflowProvider({ children }) {
  const [state, dispatch] = useReducer(workflowReducer, initialState);

  // Initialize socket connection
  useEffect(() => {
    // Clear any old localStorage data on first load
    try {
      localStorage.removeItem('bugbash_workflow_state');
      localStorage.removeItem('bugbash_workflow_session');
    } catch (error) {
      console.warn('Could not clear localStorage:', error);
    }
    
    const socket = io('http://localhost:5000', {
      transports: ['websocket', 'polling']
    });

    socket.on('connect', () => {
      console.log('Connected to server');
      dispatch({ type: actionTypes.SET_CONNECTION_STATUS, payload: true });
      
      // Request current workflow status on connection/reconnection
      socket.emit('get_status');
      
      dispatch({ 
        type: actionTypes.ADD_LOG, 
        payload: { 
          level: 'info', 
          agent: 'System', 
          message: 'Connected to Bug Bash Copilot server - syncing status...' 
        } 
      });
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
      dispatch({ type: actionTypes.SET_CONNECTION_STATUS, payload: false });
      dispatch({ 
        type: actionTypes.ADD_LOG, 
        payload: { 
          level: 'warning', 
          agent: 'System', 
          message: 'Disconnected from server' 
        } 
      });
    });

    // Listen for workflow status updates
    socket.on('workflow_status', (data) => {
      dispatch({
        type: actionTypes.UPDATE_WORKFLOW_STATUS,
        payload: data
      });
      dispatch({
        type: actionTypes.ADD_LOG,
        payload: {
          level: 'info',
          agent: 'Workflow',
          message: `Status: ${data.status}`
        }
      });
    });

    // Listen for agent status updates
    socket.on('agent_status', (data) => {
      dispatch({
        type: actionTypes.UPDATE_AGENT_STATUS,
        payload: data
      });
      dispatch({
        type: actionTypes.ADD_LOG,
        payload: {
          level: data.status === 'error' ? 'error' : 'info',
          agent: data.agentName,
          message: data.message || `Status: ${data.status}`
        }
      });
    });

    // Listen for agent progress updates
    socket.on('agent_progress', (data) => {
      dispatch({
        type: actionTypes.UPDATE_AGENT_PROGRESS,
        payload: data
      });
      if (data.message) {
        dispatch({
          type: actionTypes.ADD_LOG,
          payload: {
            level: 'info',
            agent: data.agentName,
            message: `${data.message} (${data.progress.toFixed(1)}%)`
          }
        });
      }
    });

    // Listen for test runner output
    socket.on('test_runner_output', (data) => {
      dispatch({
        type: actionTypes.SET_TEST_RUNNER_OUTPUT,
        payload: data
      });
      dispatch({
        type: actionTypes.ADD_LOG,
        payload: {
          level: 'success',
          agent: 'Test Runner',
          message: 'Test execution completed - results available'
        }
      });
    });

    // Listen for general log messages
    socket.on('log', (data) => {
      dispatch({
        type: actionTypes.ADD_LOG,
        payload: data
      });
    });

    dispatch({ type: actionTypes.SET_SOCKET, payload: socket });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Actions
  const actions = {
    setInputData: (data) => {
      dispatch({ type: actionTypes.SET_INPUT_DATA, payload: data });
    },

    startWorkflow: async (inputData) => {
      if (!state.socket || !state.isConnected) {
        dispatch({
          type: actionTypes.ADD_LOG,
          payload: {
            level: 'error',
            agent: 'System',
            message: 'Not connected to server. Please refresh the page.'
          }
        });
        return;
      }

      dispatch({ type: actionTypes.START_WORKFLOW });
      
      // Emit start workflow event
      state.socket.emit('start_workflow', { inputData });
      
      dispatch({
        type: actionTypes.ADD_LOG,
        payload: {
          level: 'info',
          agent: 'Workflow',
          message: 'Starting Bug Bash Copilot workflow...'
        }
      });
    },

    resetWorkflow: () => {
      dispatch({ type: actionTypes.RESET_WORKFLOW });
      dispatch({
        type: actionTypes.ADD_LOG,
        payload: {
          level: 'info',
          agent: 'System',
          message: 'Workflow reset'
        }
      });
    },

    addLog: (level, agent, message) => {
      dispatch({
        type: actionTypes.ADD_LOG,
        payload: { level, agent, message }
      });
    }
  };

  return (
    <WorkflowContext.Provider value={{ state, actions }}>
      {children}
    </WorkflowContext.Provider>
  );
}

// Hook to use workflow context
export function useWorkflow() {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within a WorkflowProvider');
  }
  return context;
}
