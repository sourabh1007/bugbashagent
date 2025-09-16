import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Grid
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useWorkflow } from '../context/WorkflowContext';

const PipelineCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
  borderRadius: '16px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  margin: theme.spacing(2, 0),
}));

const AgentCard = styled(Card)(({ theme, status }) => ({
  background: '#ffffff',
  borderRadius: '16px',
  padding: theme.spacing(3),
  border: '1px solid #e2e8f0',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  transition: 'all 0.3s ease',
  position: 'relative',
  overflow: 'hidden',
  minHeight: '280px', // Fixed minimum height for consistent sizing
  height: '100%', // Ensure all cards take full grid height
  display: 'flex',
  flexDirection: 'column',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1)',
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    left: 0,
    top: 0,
    height: '100%',
    width: '4px',
    background: getStatusColor(status),
    transition: 'all 0.3s ease',
  },
}));

const AgentProgress = styled(LinearProgress)(({ theme }) => ({
  height: 8,
  borderRadius: 4,
  backgroundColor: '#e5e7eb',
  '& .MuiLinearProgress-bar': {
    borderRadius: 4,
    transition: 'width 0.3s ease',
  },
}));

function getStatusColor(status) {
  switch (status) {
    case 'success':
      return 'linear-gradient(135deg, #16a34a, #15803d)';
    case 'error':
      return 'linear-gradient(135deg, #dc2626, #b91c1c)';
    case 'running':
      return 'linear-gradient(135deg, #ca8a04, #a16207)';
    case 'starting':
      return 'linear-gradient(135deg, #2563eb, #1d4ed8)';
    default:
      return 'linear-gradient(135deg, #64748b, #475569)';
  }
}

function getStatusEmoji(status) {
  switch (status) {
    case 'success':
      return '✅';
    case 'error':
      return '❌';
    case 'running':
      return '🔄';
    case 'starting':
      return '🚀';
    default:
      return '⏳';
  }
}

function getStatusChipColor(status) {
  switch (status) {
    case 'success':
      return 'success';
    case 'error':
      return 'error';
    case 'running':
    case 'starting':
      return 'warning';
    default:
      return 'default';
  }
}

function formatDuration(startTime, endTime) {
  if (!startTime) return 'Not started';
  
  const end = endTime || new Date();
  const duration = Math.floor((end.getTime() - startTime.getTime()) / 1000);
  
  if (duration < 60) {
    return `${duration}s`;
  } else {
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}m ${seconds}s`;
  }
}

function AgentPipeline() {
  const { state } = useWorkflow();

  if (state.workflowStatus === 'idle') {
    return null; // Don't show pipeline until workflow starts
  }

  return (
    <PipelineCard className="animate-fade-in">
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 600, color: '#1e293b', mb: 3, textAlign: 'center' }}>
          🔄 AI Workflow Pipeline
        </Typography>

        <Grid container spacing={3} sx={{ alignItems: 'stretch' }}>
          {state.agents.map((agent, index) => (
            <Grid item xs={12} md={4} key={agent.name} sx={{ display: 'flex' }}>
              <AgentCard status={agent.status} sx={{ width: '100%' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          fontWeight: 600, 
                          color: '#1e293b', 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: 1,
                          mb: 1 
                        }}
                      >
                        <span style={{ fontSize: '1.5rem' }}>{agent.icon}</span>
                        Step {index + 1}: {agent.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#64748b', mb: 2, minHeight: '40px' }}>
                        {agent.description}
                      </Typography>
                    </Box>
                    <Chip
                      label={`${getStatusEmoji(agent.status)} ${agent.status.toUpperCase()}`}
                      color={getStatusChipColor(agent.status)}
                      size="small"
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>

                  {/* Progress Bar */}
                  <Box sx={{ mb: 2, minHeight: '48px' }}>
                    {(agent.status === 'running' || agent.status === 'starting' || agent.status === 'success') ? (
                      <>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                          <Typography variant="body2" sx={{ fontWeight: 500, color: '#64748b' }}>
                            Progress
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: '#667eea' }}>
                            {agent.progress.toFixed(1)}%
                          </Typography>
                        </Box>
                        <AgentProgress
                          variant="determinate"
                          value={agent.progress}
                          sx={{
                            '& .MuiLinearProgress-bar': {
                              background: getStatusColor(agent.status),
                            },
                          }}
                        />
                      </>
                    ) : (
                      <>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                          <Typography variant="body2" sx={{ fontWeight: 500, color: '#94a3b8' }}>
                            Progress
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: '#94a3b8' }}>
                            {agent.status === 'pending' ? '0.0%' : agent.status === 'error' ? 'Failed' : '0.0%'}
                          </Typography>
                        </Box>
                        <AgentProgress
                          variant="determinate"
                          value={0}
                          sx={{
                            '& .MuiLinearProgress-bar': {
                              background: getStatusColor(agent.status),
                            },
                          }}
                        />
                      </>
                    )}
                  </Box>

                  {/* Agent Status Message */}
                  <Box sx={{ mb: 2, flex: 1, minHeight: '40px' }}>
                    {agent.message ? (
                      <Typography variant="body2" sx={{ color: '#475569', fontStyle: 'italic' }}>
                        {agent.message}
                      </Typography>
                    ) : (
                      <Typography variant="body2" sx={{ color: '#94a3b8', fontStyle: 'italic', opacity: 0.7 }}>
                        {agent.status === 'pending' ? 'Waiting to start...' : 
                         agent.status === 'success' ? 'Execution completed successfully' :
                         agent.status === 'error' ? 'Execution failed' : 'Processing...'}
                      </Typography>
                    )}
                  </Box>

                  {/* Spacer to push timing info to bottom */}
                  <Box sx={{ flex: 1 }} />

                  {/* Timing Information */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, color: '#64748b', fontSize: '0.875rem', mt: 'auto' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <span>⏱️</span>
                      <span>{formatDuration(agent.startTime, agent.endTime)}</span>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <span>📊</span>
                      <span>Status: {agent.status}</span>
                    </Box>
                  </Box>
                </Box>

                {/* Running Animation */}
                {agent.status === 'running' && (
                  <Box 
                    sx={{ 
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 2,
                      background: 'linear-gradient(90deg, transparent, #667eea, transparent)',
                      animation: 'slide 2s infinite',
                      '@keyframes slide': {
                        '0%': { transform: 'translateX(-100%)' },
                        '100%': { transform: 'translateX(100%)' },
                      },
                    }} 
                  />
                )}
              </AgentCard>

              {/* Arrow between agents */}
              {index < state.agents.length - 1 && (
                <Box sx={{ textAlign: 'center', my: 2, display: { xs: 'block', md: 'none' } }}>
                  <Typography sx={{ fontSize: '2rem', color: '#64748b' }}>↓</Typography>
                </Box>
              )}
            </Grid>
          ))}
        </Grid>

        {/* Desktop Arrow Indicators */}
        <Box sx={{ 
          display: { xs: 'none', md: 'flex' }, 
          justifyContent: 'center', 
          alignItems: 'center', 
          mt: 2,
          gap: 4 
        }}>
          {state.agents.map((_, index) => (
            index < state.agents.length - 1 && (
              <Typography key={index} sx={{ fontSize: '2rem', color: '#64748b' }}>
                →
              </Typography>
            )
          ))}
        </Box>
      </CardContent>
    </PipelineCard>
  );
}

export default AgentPipeline;
