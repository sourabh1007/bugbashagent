import React, { useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  LinearProgress
} from '@mui/material';
import {
  Clear as ClearIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useWorkflow } from '../context/WorkflowContext';

const LogsCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
  borderRadius: '16px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  margin: theme.spacing(2, 0),
}));

const LogsContainer = styled(Box)(({ theme }) => ({
  background: '#0f172a',
  borderRadius: '12px',
  padding: theme.spacing(2),
  color: '#e2e8f0',
  fontFamily: '"Fira Code", "Courier New", monospace',
  maxHeight: '400px',
  overflowY: 'auto',
  position: 'relative',
  '&::-webkit-scrollbar': {
    width: '8px',
  },
  '&::-webkit-scrollbar-track': {
    background: '#1e293b',
    borderRadius: '4px',
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#475569',
    borderRadius: '4px',
  },
  '&::-webkit-scrollbar-thumb:hover': {
    background: '#64748b',
  },
}));

const LogEntry = styled(Box)(({ theme, level }) => ({
  marginBottom: theme.spacing(1),
  padding: theme.spacing(0.5, 1),
  borderRadius: '4px',
  fontSize: '0.875rem',
  lineHeight: 1.4,
  borderLeft: `3px solid ${getLogColor(level)}`,
  background: `${getLogColor(level)}10`,
}));

const LogTimestamp = styled('span')(({ theme }) => ({
  color: '#94a3b8',
  fontSize: '0.75rem',
  marginRight: theme.spacing(1),
}));

const LogAgent = styled('span')(({ theme, level }) => ({
  color: getLogColor(level),
  fontWeight: 600,
  marginRight: theme.spacing(1),
  fontSize: '0.75rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
}));

const LogMessage = styled('span')(({ theme, level }) => ({
  color: level === 'error' ? '#f87171' : '#e2e8f0',
}));

const ProgressContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  marginTop: theme.spacing(0.5),
}));

const ProgressText = styled(Typography)(({ theme }) => ({
  fontSize: '0.75rem',
  color: '#94a3b8',
  minWidth: '40px',
}));

function getLogColor(level) {
  switch (level) {
    case 'error':
      return '#f87171';
    case 'warning':
      return '#fbbf24';
    case 'success':
      return '#34d399';
    case 'info':
    default:
      return '#60a5fa';
  }
}

function formatTimestamp(timestamp) {
  // Convert to Date object if it's a string
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
  
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3
  });
}

function extractProgressFromMessage(message) {
  // Extract percentage from messages like "Progress: 50%" or "Processing... 75% complete"
  const percentMatch = message.match(/(\d+)%/);
  if (percentMatch) {
    return parseInt(percentMatch[1], 10);
  }
  
  // Extract progress from messages like "Step 3 of 5"
  const stepMatch = message.match(/step\s+(\d+)\s+of\s+(\d+)/i);
  if (stepMatch) {
    const current = parseInt(stepMatch[1], 10);
    const total = parseInt(stepMatch[2], 10);
    return Math.round((current / total) * 100);
  }
  
  // Extract progress from messages like "Processing scenario 2/4"
  const fractionMatch = message.match(/(\d+)\/(\d+)/);
  if (fractionMatch) {
    const current = parseInt(fractionMatch[1], 10);
    const total = parseInt(fractionMatch[2], 10);
    return Math.round((current / total) * 100);
  }
  
  return null;
}

function isProgressMessage(message) {
  const progressKeywords = [
    'progress', 'processing', 'executing', 'running', 'analyzing',
    'generating', 'compiling', 'testing', 'complete', 'finished'
  ];
  return progressKeywords.some(keyword => 
    message.toLowerCase().includes(keyword)
  ) || extractProgressFromMessage(message) !== null;
}

function RealTimeLogs() {
  const { state, actions } = useWorkflow();
  const logsEndRef = useRef(null);
  const logsContainerRef = useRef(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [state.logs]);

  const handleClearLogs = () => {
    // This would need to be implemented in the context
    // For now, we'll just add a log about clearing
    actions.addLog('info', 'System', 'Logs cleared by user');
  };

  const handleDownloadLogs = () => {
    const logsText = state.logs
      .map(log => `[${formatTimestamp(log.timestamp)}] [${log.agent}] [${log.level.toUpperCase()}] ${log.message}`)
      .join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bugbash-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (state.logs.length === 0) {
    return null; // Don't show logs until there are some
  }

  return (
    <LogsCard className="animate-fade-in">
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h5" component="h2" sx={{ fontWeight: 600, color: '#1e293b' }}>
              📊 Real-Time Logs
            </Typography>
            <Chip 
              label={`${state.logs.length} entries`} 
              size="small" 
              color="primary" 
            />
            {state.isConnected && (
              <Box className="live-indicator">
                <Box className="live-dot" />
                <Typography variant="caption" sx={{ color: '#16a34a', fontWeight: 600 }}>
                  LIVE
                </Typography>
              </Box>
            )}
          </Box>
          
          <Box>
            <IconButton 
              onClick={handleDownloadLogs} 
              size="small" 
              title="Download Logs"
              sx={{ mr: 1 }}
            >
              <DownloadIcon />
            </IconButton>
            <IconButton 
              onClick={handleClearLogs} 
              size="small" 
              title="Clear Logs"
            >
              <ClearIcon />
            </IconButton>
          </Box>
        </Box>

        <LogsContainer ref={logsContainerRef}>
          {state.logs.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4, color: '#64748b' }}>
              <Typography variant="body2">
                No logs yet. Start a workflow to see real-time updates.
              </Typography>
            </Box>
          ) : (
            <>
              {state.logs.map((log) => {
                const progress = extractProgressFromMessage(log.message);
                const isProgress = isProgressMessage(log.message);
                
                return (
                  <LogEntry key={log.id} level={log.level}>
                    <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                        <LogTimestamp>
                          {formatTimestamp(log.timestamp)}
                        </LogTimestamp>
                        <LogAgent level={log.level}>
                          [{log.agent}]
                        </LogAgent>
                        <LogMessage level={log.level}>
                          {log.message}
                        </LogMessage>
                      </Box>
                      
                      {isProgress && progress !== null && (
                        <ProgressContainer>
                          <LinearProgress
                            variant="determinate"
                            value={progress}
                            sx={{
                              flex: 1,
                              height: 4,
                              borderRadius: 2,
                              backgroundColor: '#334155',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: getLogColor(log.level),
                              },
                            }}
                          />
                          <ProgressText variant="caption">
                            {progress}%
                          </ProgressText>
                        </ProgressContainer>
                      )}
                      
                      {isProgress && progress === null && (
                        <ProgressContainer>
                          <LinearProgress
                            sx={{
                              flex: 1,
                              height: 4,
                              borderRadius: 2,
                              backgroundColor: '#334155',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: getLogColor(log.level),
                              },
                            }}
                          />
                          <ProgressText variant="caption">
                            ...
                          </ProgressText>
                        </ProgressContainer>
                      )}
                    </Box>
                  </LogEntry>
                );
              })}
              <div ref={logsEndRef} />
            </>
          )}
        </LogsContainer>

        <Typography variant="caption" sx={{ color: '#64748b', mt: 1, display: 'block' }}>
          Logs are updated in real-time. Maximum 100 entries are kept in memory.
        </Typography>
      </CardContent>
    </LogsCard>
  );
}

export default RealTimeLogs;
