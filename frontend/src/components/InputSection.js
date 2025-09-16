import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Tab,
  Tabs,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Description as DocumentIcon,
  Upload as UploadIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useWorkflow } from '../context/WorkflowContext';

const InputCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
  borderRadius: '16px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  margin: theme.spacing(2, 0),
}));

const TabContainer = styled(Box)(({ theme }) => ({
  background: '#f8fafc',
  borderRadius: '12px',
  padding: theme.spacing(0.5),
  marginBottom: theme.spacing(2),
}));

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`input-tabpanel-${index}`}
      aria-labelledby={`input-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

function InputSection() {
  const { state, actions } = useWorkflow();
  const [inputMethod, setInputMethod] = useState(0);
  const [textInput, setTextInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleInputMethodChange = (event, newValue) => {
    setInputMethod(newValue);
  };

  const handleStartWorkflow = () => {
    let inputData = '';
    
    if (inputMethod === 0 && textInput.trim()) {
      inputData = textInput.trim();
    } else if (inputMethod === 1 && uploadedFile) {
      // In a real implementation, you'd process the file
      inputData = `File uploaded: ${uploadedFile.name}`;
    }

    if (!inputData) {
      actions.addLog('error', 'Input', 'Please provide input data before starting the workflow');
      return;
    }

    actions.setInputData(inputData);
    actions.startWorkflow(inputData);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
      // In a real implementation, you'd read and process the file content
      actions.addLog('info', 'Input', `File selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`);
    }
  };

  const handleReset = () => {
    actions.resetWorkflow();
    setTextInput('');
    setUploadedFile(null);
  };

  const isWorkflowRunning = state.workflowStatus === 'running';
  const canStart = !isWorkflowRunning && ((inputMethod === 0 && textInput.trim()) || (inputMethod === 1 && uploadedFile));

  return (
    <InputCard className="animate-fade-in">
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <DocumentIcon color="primary" />
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600, color: '#1e293b' }}>
            Bug Bash Setup & Documentation Input
          </Typography>
          {state.isConnected && (
            <Chip 
              label="Connected" 
              color="success" 
              size="small" 
              sx={{ ml: 'auto' }}
            />
          )}
          {!state.isConnected && (
            <Chip 
              label="Disconnected" 
              color="error" 
              size="small" 
              sx={{ ml: 'auto' }}
            />
          )}
        </Box>

        <Typography variant="body1" sx={{ color: '#64748b', mb: 3, lineHeight: 1.6 }}>
          Provide your product documentation, setup guides, or feature descriptions. The AI will analyze them to generate comprehensive test scenarios and execute automated bug bash sessions.
        </Typography>

        <TabContainer>
          <Tabs 
            value={inputMethod} 
            onChange={handleInputMethodChange}
            sx={{
              '& .MuiTab-root': {
                borderRadius: '8px',
                fontWeight: 500,
                textTransform: 'none',
                minHeight: '48px'
              }
            }}
          >
            <Tab icon={<DocumentIcon />} label="Direct Text Input" />
            <Tab icon={<UploadIcon />} label="Upload Documentation" />
            <Tab icon={<HistoryIcon />} label="Load Previous Session" />
          </Tabs>
        </TabContainer>

        <TabPanel value={inputMethod} index={0}>
          <TextField
            fullWidth
            multiline
            rows={8}
            variant="outlined"
            placeholder="Paste your product documentation, setup guide, or feature description here...

Example: 'We have a new checkout flow feature that allows users to save payment methods, apply discount codes, and choose shipping options. The feature needs comprehensive testing across different user scenarios including guest checkout, registered users, and edge cases like expired cards or invalid codes.'"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            disabled={isWorkflowRunning}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                background: '#ffffff'
              }
            }}
          />
        </TabPanel>

        <TabPanel value={inputMethod} index={1}>
          <Box sx={{ textAlign: 'center', p: 3, border: '2px dashed #cbd5e1', borderRadius: '12px' }}>
            <input
              accept=".txt,.md,.pdf,.docx"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              onChange={handleFileUpload}
              disabled={isWorkflowRunning}
            />
            <label htmlFor="file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadIcon />}
                disabled={isWorkflowRunning}
                sx={{ mb: 2 }}
              >
                Choose File
              </Button>
            </label>
            
            {uploadedFile && (
              <Alert severity="success" sx={{ mt: 2 }}>
                File selected: {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
              </Alert>
            )}
            
            <Typography variant="body2" sx={{ color: '#64748b', mt: 1 }}>
              Supported formats: TXT, MD, PDF, DOCX
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={inputMethod} index={2}>
          <Alert severity="info">
            Previous session loading functionality will be implemented based on your workflow outputs directory structure.
          </Alert>
        </TabPanel>

        <Box sx={{ display: 'flex', gap: 2, mt: 3, justifyContent: 'center' }}>
          {!isWorkflowRunning ? (
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayIcon />}
              onClick={handleStartWorkflow}
              disabled={!canStart || !state.isConnected}
              sx={{
                px: 4,
                py: 1.5,
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a67d8, #6b46c1)',
                },
                borderRadius: '12px',
                fontWeight: 600
              }}
            >
              Start Bug Bash Workflow
            </Button>
          ) : (
            <Button
              variant="outlined"
              size="large"
              startIcon={<CircularProgress size={20} />}
              disabled
              sx={{ px: 4, py: 1.5, borderRadius: '12px' }}
            >
              Workflow Running...
            </Button>
          )}
          
          <Button
            variant="outlined"
            size="large"
            startIcon={<RefreshIcon />}
            onClick={handleReset}
            disabled={isWorkflowRunning}
            sx={{ px: 4, py: 1.5, borderRadius: '12px' }}
          >
            Reset
          </Button>
        </Box>

        {state.workflowStatus === 'completed' && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Workflow completed successfully! Check the results below.
          </Alert>
        )}

        {state.workflowStatus === 'failed' && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Workflow failed. Please check the logs for details.
          </Alert>
        )}
      </CardContent>
    </InputCard>
  );
}

export default InputSection;
