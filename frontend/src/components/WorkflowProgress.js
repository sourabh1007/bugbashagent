import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useWorkflow } from '../context/WorkflowContext';

const ProgressCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
  borderRadius: '16px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  margin: theme.spacing(2, 0),
}));

const ProgressContainer = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
  borderRadius: '12px',
  padding: theme.spacing(2),
  margin: theme.spacing(2, 0),
  border: '1px solid #e2e8f0',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
}));

const StyledLinearProgress = styled(LinearProgress)(({ theme }) => ({
  height: 12,
  borderRadius: 6,
  backgroundColor: '#e5e7eb',
  '& .MuiLinearProgress-bar': {
    background: 'linear-gradient(90deg, #667eea, #764ba2)',
    borderRadius: 6,
    position: 'relative',
    overflow: 'hidden',
    '&::after': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: '-100%',
      width: '100%',
      height: '100%',
      background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
      animation: 'shimmer 2s infinite',
    },
  },
  '@keyframes shimmer': {
    '0%': { transform: 'translateX(-100%)' },
    '100%': { transform: 'translateX(100%)' },
  },
}));

const MetricCard = styled(Box)(({ theme }) => ({
  background: '#ffffff',
  padding: theme.spacing(2),
  borderRadius: '12px',
  textAlign: 'center',
  border: '1px solid #e2e8f0',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-1px)',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  },
}));

const MetricValue = styled(Typography)(({ theme }) => ({
  fontSize: '2rem',
  fontWeight: 700,
  color: '#1e293b',
  margin: theme.spacing(0.5, 0),
}));

const MetricLabel = styled(Typography)(({ theme }) => ({
  fontSize: '0.875rem',
  color: '#64748b',
  fontWeight: 500,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
}));

function WorkflowProgress() {
  const { state } = useWorkflow();

  // Calculate overall progress
  const completedAgents = state.agents.filter(agent => agent.status === 'success').length;
  const runningAgents = state.agents.filter(agent => agent.status === 'running').length;
  const failedAgents = state.agents.filter(agent => agent.status === 'error').length;
  
  // Calculate overall progress as a percentage
  let overallProgress = (completedAgents / state.totalSteps) * 100;
  
  // Add partial progress for running agents
  if (runningAgents > 0) {
    const runningAgent = state.agents.find(agent => agent.status === 'running');
    if (runningAgent && runningAgent.progress > 0) {
      // Add the running agent's progress as a fraction of one agent's worth
      overallProgress += (runningAgent.progress / 100) * (100 / state.totalSteps);
    }
  }
  
  // Ensure progress doesn't exceed 100%
  overallProgress = Math.min(overallProgress, 100);

  // Debug logging
  console.log('Progress Debug:', {
    completedAgents,
    runningAgents,
    totalSteps: state.totalSteps,
    calculatedProgress: overallProgress,
    agentStatuses: state.agents.map(a => ({ name: a.name, status: a.status, progress: a.progress }))
  });

  // Calculate execution time
  const startedAgents = state.agents.filter(agent => agent.startTime);
  let executionTime = 0;
  if (startedAgents.length > 0) {
    const getTime = (dateValue) => {
      if (!dateValue) {
        return Date.now();
      }
      if (dateValue instanceof Date) {
        return dateValue.getTime();
      }
      if (typeof dateValue === 'string') {
        return new Date(dateValue).getTime();
      }
      return Date.now();
    };
    
    const firstStartTime = Math.min(...startedAgents.map(agent => getTime(agent.startTime)));
    const now = new Date().getTime();
    const lastEndTime = Math.max(
      ...state.agents
        .filter(agent => agent.endTime)
        .map(agent => getTime(agent.endTime)),
      now
    );
    executionTime = Math.floor((lastEndTime - firstStartTime) / 1000);
  }

  const getStatusText = () => {
    if (state.workflowStatus === 'completed') {
      return 'Completed';
    }
    if (state.workflowStatus === 'failed') {
      return 'Failed';
    }
    if (failedAgents > 0) {
      return `${failedAgents} Failed`;
    }
    if (runningAgents > 0) {
      return 'Running';
    }
    return 'Ready';
  };

  const getStatusColor = () => {
    if (state.workflowStatus === 'completed') {
      return '#16a34a';
    }
    if (state.workflowStatus === 'failed' || failedAgents > 0) {
      return '#dc2626';
    }
    if (runningAgents > 0) {
      return '#ca8a04';
    }
    return '#64748b';
  };

  // Always show progress if there's any activity or completion
  if (state.workflowStatus === 'idle' && completedAgents === 0 && runningAgents === 0 && failedAgents === 0) {
    return null; // Don't show progress until workflow starts
  }

  return (
    <ProgressCard className="animate-fade-in">
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 600, color: '#1e293b', mb: 2 }}>
          🚀 Workflow Execution Progress
        </Typography>

        <ProgressContainer>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1e293b' }}>
              Overall Progress
            </Typography>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#667eea' }}>
              {overallProgress.toFixed(1)}%
            </Typography>
          </Box>
          
          <Box sx={{ 
            width: '100%', 
            height: '12px', 
            backgroundColor: '#e5e7eb', 
            borderRadius: '6px', 
            overflow: 'hidden',
            position: 'relative',
            mb: 1
          }}>
            <Box sx={{
              height: '100%',
              width: `${overallProgress}%`,
              background: 'linear-gradient(90deg, #667eea, #764ba2)',
              borderRadius: '6px',
              transition: 'width 0.5s ease',
              position: 'relative',
              overflow: 'hidden',
              '&::after': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
                animation: overallProgress > 0 && overallProgress < 100 ? 'shimmer 2s infinite' : 'none',
              },
              '@keyframes shimmer': {
                '0%': { transform: 'translateX(-100%)' },
                '100%': { transform: 'translateX(100%)' },
              },
            }} />
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              {completedAgents}/{state.totalSteps} Agents Complete
            </Typography>
            <Chip 
              label={state.currentAgent || 'Workflow'}
              size="small"
              sx={{ fontWeight: 500 }}
            />
          </Box>
        </ProgressContainer>

        {/* Live Performance Metrics */}
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 2, mt: 3 }}>
          📊 Live Performance Metrics
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
          <MetricCard>
            <MetricLabel>Overall Progress</MetricLabel>
            <MetricValue>{overallProgress.toFixed(0)}%</MetricValue>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              {completedAgents}/{state.totalSteps} Agents Complete
            </Typography>
          </MetricCard>

          <MetricCard>
            <MetricLabel>Execution Time</MetricLabel>
            <MetricValue>{executionTime}s</MetricValue>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Real-time Duration
            </Typography>
          </MetricCard>

          <MetricCard>
            <MetricLabel>System Status</MetricLabel>
            <MetricValue sx={{ color: getStatusColor() }}>
              {getStatusText()}
            </MetricValue>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Agent Health
            </Typography>
          </MetricCard>

          <MetricCard>
            <MetricLabel>Active Logs</MetricLabel>
            <MetricValue>{state.logs.length}</MetricValue>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Real-time Events
            </Typography>
          </MetricCard>
        </Box>

        {/* Workflow Status Message */}
        {state.workflowStatus === 'completed' && (
          <Box sx={{ 
            mt: 2, 
            p: 2, 
            background: 'linear-gradient(135deg, #dcfce7, #bbf7d0)',
            border: '1px solid #16a34a',
            borderRadius: 2,
            color: '#166534'
          }}>
            ✅ Workflow Completed Successfully
          </Box>
        )}

        {state.workflowStatus === 'failed' && (
          <Box sx={{ 
            mt: 2, 
            p: 2, 
            background: 'linear-gradient(135deg, #fef2f2, #fecaca)',
            border: '1px solid #dc2626',
            borderRadius: 2,
            color: '#991b1b'
          }}>
            ❌ Workflow Failed
          </Box>
        )}

        {state.workflowStatus === 'running' && (
          <Box sx={{ 
            mt: 2, 
            p: 2, 
            background: 'linear-gradient(135deg, #fef3c7, #fde68a)',
            border: '1px solid #ca8a04',
            borderRadius: 2,
            color: '#92400e'
          }}>
            🔄 Running: {state.currentAgent || 'Processing...'}
          </Box>
        )}
      </CardContent>
    </ProgressCard>
  );
}

export default WorkflowProgress;
