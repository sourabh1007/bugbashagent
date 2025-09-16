import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Header from './components/Header';
import InputSection from './components/InputSection';
import WorkflowProgress from './components/WorkflowProgress';
import AgentPipeline from './components/AgentPipeline';
import RealTimeLogs from './components/RealTimeLogs';
import TestRunnerResults from './components/TestRunnerResults';
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
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <WorkflowProvider>
        <div className="App">
          <Header />
          <Container maxWidth="xl" sx={{ py: 4 }}>
            <InputSection />
            <WorkflowProgress />
            <AgentPipeline />
            <RealTimeLogs />
            <TestRunnerResults />
          </Container>
        </div>
      </WorkflowProvider>
    </ThemeProvider>
  );
}

export default App;
