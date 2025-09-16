import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import { Tabs, Tab, Box, Paper } from '@mui/material';
import { Settings as SettingsIcon, PlayArrow as PlayArrowIcon, Schedule as ScheduleIcon } from '@mui/icons-material';
import Header from './components/Header';
import InputSection from './components/InputSection';
import WorkflowProgress from './components/WorkflowProgress';
import AgentPipeline from './components/AgentPipeline';
import RealTimeLogs from './components/RealTimeLogs';
import TestRunnerResults from './components/TestRunnerResults';
import Configuration from './components/Configuration';
import HistoricalRuns from './components/HistoricalRuns';
import { WorkflowProvider } from './context/WorkflowContext';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
    background: {
      default: '#f8fafc',
    },
  },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '16px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          fontSize: '16px',
        },
      },
    },
  },
});

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <WorkflowProvider>
        <div className="App">
          <Header />
          <Container maxWidth="xl" sx={{ py: 4 }}>
            {/* Navigation Tabs */}
            <Paper sx={{ mb: 3 }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                aria-label="main navigation tabs"
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab
                  icon={<PlayArrowIcon />}
                  iconPosition="start"
                  label="Workflow"
                  id="simple-tab-0"
                  aria-controls="simple-tabpanel-0"
                />
                <Tab
                  icon={<ScheduleIcon />}
                  iconPosition="start"
                  label="Historical Runs"
                  id="simple-tab-1"
                  aria-controls="simple-tabpanel-1"
                />
                <Tab
                  icon={<SettingsIcon />}
                  iconPosition="start"
                  label="Configuration"
                  id="simple-tab-2"
                  aria-controls="simple-tabpanel-2"
                />
              </Tabs>
            </Paper>

            {/* Workflow Tab */}
            <TabPanel value={tabValue} index={0}>
              <InputSection />
              <WorkflowProgress />
              <AgentPipeline />
              <RealTimeLogs />
              <TestRunnerResults />
            </TabPanel>

            {/* Historical Runs Tab */}
            <TabPanel value={tabValue} index={1}>
              <HistoricalRuns />
            </TabPanel>

            {/* Configuration Tab */}
            <TabPanel value={tabValue} index={2}>
              <Configuration />
            </TabPanel>
          </Container>
        </div>
      </WorkflowProvider>
    </ThemeProvider>
  );
}

export default App;
