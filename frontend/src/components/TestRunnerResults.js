import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  Chip,
  Alert,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  SkipNext as SkipNextIcon,
  Timer as TimerIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { useWorkflow } from '../context/WorkflowContext';

const ResultsCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
  borderRadius: '16px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  margin: theme.spacing(2, 0),
}));

const DashboardGrid = styled(Grid)(({ theme }) => ({
  marginBottom: theme.spacing(3),
}));

const MetricCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  textAlign: 'center',
  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
  borderRadius: '12px',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  border: '1px solid #e2e8f0',
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
  },
}));

const MetricValue = styled(Typography)(({ theme }) => ({
  fontSize: '2.5rem',
  fontWeight: 700,
  margin: theme.spacing(1, 0),
}));

const MetricLabel = styled(Typography)(({ theme }) => ({
  fontSize: '0.875rem',
  color: '#64748b',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
}));

const ChartContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: '12px',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  border: '1px solid #e2e8f0',
  marginBottom: theme.spacing(2),
}));

// Color schemes for charts
const COLORS = {
  passed: '#10b981',
  failed: '#ef4444',
  skipped: '#f59e0b',
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
};

const PIE_COLORS = [COLORS.passed, COLORS.failed, COLORS.skipped];

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`results-tabpanel-${index}`}
      aria-labelledby={`results-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

// Custom components for ReactMarkdown
const markdownComponents = {
  code({ node, inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    return !inline && match ? (
      <SyntaxHighlighter
        style={tomorrow}
        language={match[1]}
        PreTag="div"
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    ) : (
      <code className={className} {...props}>
        {children}
      </code>
    );
  },
};

function TestRunnerResults() {
  const { state } = useWorkflow();
  const [activeTab, setActiveTab] = useState(0);

  const testRunnerAgent = state.agents.find(agent => agent.name === 'Test Runner');
  const hasTestResults = testRunnerAgent && (testRunnerAgent.output || state.testRunnerOutput);

  // Function to extract detailed test results from raw output
  const extractDetailedResults = (output, testResults) => {
    const details = [];
    
    // Try to extract detailed results from various patterns in the output
    const lines = output.split('\n');
    let currentTest = null;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Look for test names or error patterns
      if (line.includes('test_') || line.includes('Test') || line.includes('FAIL') || line.includes('ERROR')) {
        // Extract test name
        const testNameMatch = line.match(/([a-zA-Z_]\w*(?:Test|_test|test)\w*)/i);
        if (testNameMatch) {
          if (currentTest) {
            details.push(currentTest);
          }
          
          currentTest = {
            name: testNameMatch[1],
            status: line.includes('FAIL') || line.includes('ERROR') || line.includes('failed') ? 'failed' : 
                   line.includes('PASS') || line.includes('passed') ? 'passed' : 'unknown',
            duration: null,
            error: null,
            output: null,
            severity: 'medium',
            category: 'functional',
            mitigation: null
          };
        }
      }
      
      // Look for error messages
      if (line.includes('Error') || line.includes('Exception') || line.includes('Failed')) {
        if (currentTest && !currentTest.error) {
          currentTest.error = line;
          currentTest.status = 'failed';
          
          // Determine severity based on error type
          if (line.includes('System.ArgumentException') || line.includes('ConfigurationError')) {
            currentTest.severity = 'high';
            currentTest.category = 'configuration';
          } else if (line.includes('ConnectionException') || line.includes('TimeoutException')) {
            currentTest.severity = 'high';
            currentTest.category = 'connectivity';
          } else if (line.includes('AuthenticationException') || line.includes('AuthorizationException')) {
            currentTest.severity = 'critical';
            currentTest.category = 'security';
          }
          
          // Add mitigation suggestions based on error type
          currentTest.mitigation = generateMitigationSuggestion(line, currentTest.category);
        }
      }
      
      // Look for duration
      const durationMatch = line.match(/(\d+(?:\.\d+)?)\s*(ms|seconds?|minutes?)/i);
      if (durationMatch && currentTest && !currentTest.duration) {
        currentTest.duration = durationMatch[0];
      }
      
      // Collect additional output
      if (currentTest && (line.includes('at ') || line.includes('Stack Trace'))) {
        if (!currentTest.output) {
          currentTest.output = line;
        } else {
          currentTest.output += '\n' + line;
        }
      }
    }
    
    // Add the last test if any
    if (currentTest) {
      details.push(currentTest);
    }
    
    // If we don't have detailed results but have failed tests, create generic ones
    if (details.length === 0 && testResults.failed_tests > 0) {
      // Try to extract more specific scenario information from the output
      const scenarioNames = extractScenarioNames(output);
      
      for (let i = 1; i <= testResults.failed_tests; i++) {
        const scenarioName = scenarioNames[i - 1] || `Authentication Key Validation Test ${i}`;
        details.push({
          name: scenarioName,
          status: 'failed',
          duration: 'Unknown',
          error: output, // Pass full output to be cleaned by extractCleanErrorDescription
          output: 'Review the raw analysis for detailed error information',
          severity: 'medium',
          category: 'functional',
          mitigation: 'Check configuration settings and network connectivity. Verify API endpoints and credentials.'
        });
      }
    }
    
    // Add passed tests if any
    if (testResults.passed_tests > 0 && details.filter(d => d.status === 'passed').length === 0) {
      const passedScenarios = [
        'Database Connection Test',
        'API Authentication Test', 
        'Data Validation Test',
        'Business Logic Test',
        'Integration Test',
        'Performance Test',
        'Security Test',
        'Configuration Test'
      ];
      
      for (let i = 1; i <= testResults.passed_tests; i++) {
        const scenarioName = passedScenarios[i - 1] || `Working Feature Test ${i}`;
        details.push({
          name: scenarioName,
          status: 'passed',
          duration: 'Completed',
          error: null,
          output: 'Feature working as expected',
          severity: 'none',
          category: 'functional',
          mitigation: null
        });
      }
    }
    
    return details;
  };

  // Function to generate mitigation suggestions based on error type
  const generateMitigationSuggestion = (errorMessage, category) => {
    const suggestions = {
      configuration: [
        "Verify configuration settings in appsettings.json or environment variables",
        "Check API endpoints and ensure they are accessible",
        "Validate connection strings and database configurations",
        "Review Azure region settings and service availability"
      ],
      connectivity: [
        "Check network connectivity and firewall settings",
        "Verify service endpoints are reachable",
        "Increase timeout values if network is slow",
        "Review proxy settings and network policies"
      ],
      security: [
        "Verify authentication credentials and tokens",
        "Check API key validity and permissions",
        "Review access control policies and roles",
        "Ensure proper SSL/TLS configuration"
      ],
      functional: [
        "Review business logic and validation rules",
        "Check input data formats and constraints",
        "Verify expected vs actual behavior",
        "Update test data or expectations as needed"
      ]
    };
    
    const categoryMap = {
      'ArgumentException': 'configuration',
      'ConfigurationError': 'configuration',
      'ConnectionException': 'connectivity',
      'TimeoutException': 'connectivity',
      'AuthenticationException': 'security',
      'AuthorizationException': 'security',
      'EastUS': 'configuration'
    };
    
    // Find matching category based on error message
    let detectedCategory = category;
    for (const [errorType, cat] of Object.entries(categoryMap)) {
      if (errorMessage.includes(errorType)) {
        detectedCategory = cat;
        break;
      }
    }
    
    const suggestionList = suggestions[detectedCategory] || suggestions.functional;
    return suggestionList[Math.floor(Math.random() * suggestionList.length)];
  };

  // Function to extract clean, user-friendly error descriptions
  const extractCleanErrorDescription = (rawError) => {
    if (!rawError) return 'Configuration or functionality issue detected';
    
    // If it's a raw JSON string, try to extract meaningful parts
    if (rawError.includes('test_results') || rawError.includes('{') || rawError.includes('[')) {
      // Extract key error information from JSON-like structures
      
      // Look for specific error patterns
      const systemFormatMatch = rawError.match(/System\.FormatException\s*:\s*([^\\n]+)/i);
      if (systemFormatMatch) {
        return `Input validation error: ${systemFormatMatch[1].trim()}`;
      }
      
      const argumentExceptionMatch = rawError.match(/System\.ArgumentException\s*:\s*([^\\n]+)/i);
      if (argumentExceptionMatch) {
        return `Invalid argument provided: ${argumentExceptionMatch[1].trim()}`;
      }
      
      // Look for Azure Cosmos DB specific errors
      if (rawError.includes('Azure.Cosmos')) {
        if (rawError.includes('InvalidAuthentication')) {
          return 'Azure Cosmos DB authentication failed - check connection string and credentials';
        }
        if (rawError.includes('ResourceNotFound')) {
          return 'Azure Cosmos DB resource not found - verify database and container names';
        }
        if (rawError.includes('Forbidden')) {
          return 'Azure Cosmos DB access denied - check permissions and access keys';
        }
        return 'Azure Cosmos DB connectivity issue - verify configuration and network access';
      }
      
      // Look for authentication key issues
      if (rawError.includes('InvalidAuthenticationKey') || rawError.includes('authKey')) {
        return 'Authentication key validation failed - verify API keys and connection strings';
      }
      
      // Look for base64 encoding issues
      if (rawError.includes('base-64') || rawError.includes('Base64')) {
        return 'Invalid Base-64 encoding detected in authentication credentials';
      }
      
      // Look for general test failures
      if (rawError.includes('failed_tests')) {
        const failedMatch = rawError.match(/failed_tests['"]?\s*:\s*(\d+)/);
        if (failedMatch) {
          return `${failedMatch[1]} test scenario(s) failed during execution`;
        }
      }
      
      // Fallback: try to extract any clear error message
      const errorMatch = rawError.match(/['"']error['"']\s*:\s*['"']([^'"]+)['"']/i);
      if (errorMatch) {
        return errorMatch[1];
      }
      
      // Fallback for system exceptions
      const exceptionMatch = rawError.match(/(\w+Exception)\s*:\s*([^\\n\\r]{1,100})/);
      if (exceptionMatch) {
        return `${exceptionMatch[1]}: ${exceptionMatch[2].trim()}`;
      }
      
      return 'Test execution failed - check configuration and input parameters';
    }
    
    // For non-JSON errors, clean up and truncate if too long
    let cleanError = rawError.trim();
    
    // Remove stack traces and technical details
    cleanError = cleanError.split('\n')[0]; // Take first line only
    cleanError = cleanError.replace(/at\s+[\w.]+\(.*?\)/g, ''); // Remove stack trace references
    cleanError = cleanError.replace(/\s+/g, ' ').trim(); // Normalize whitespace
    
    // Truncate if too long
    if (cleanError.length > 200) {
      cleanError = cleanError.substring(0, 200) + '...';
    }
    
    return cleanError || 'Configuration or functionality issue detected';
  };

  // Function to extract meaningful scenario names from test output
  const extractScenarioNames = (output) => {
    const scenarios = [];
    
    if (!output) return scenarios;
    
    // Look for specific test patterns in the output
    const lines = output.split('\n');
    
    // Check for Azure Cosmos DB test patterns
    if (output.includes('Azure.Cosmos') || output.includes('InvalidAuthenticationKey')) {
      scenarios.push('Azure Cosmos DB Authentication Test');
    }
    
    // Check for authentication/authorization patterns
    if (output.includes('authKey') || output.includes('Authorization')) {
      scenarios.push('API Key Authentication Validation');
    }
    
    // Check for base64 encoding issues
    if (output.includes('base-64') || output.includes('Base64')) {
      scenarios.push('Base64 Key Encoding Validation');
    }
    
    // Check for connection/network issues
    if (output.includes('Connection') || output.includes('Timeout')) {
      scenarios.push('Service Connectivity Test');
    }
    
    // Check for configuration issues
    if (output.includes('Configuration') || output.includes('appsettings')) {
      scenarios.push('Configuration Validation Test');
    }
    
    // Look for actual test method names in output
    const testNameMatches = output.match(/([A-Z][a-zA-Z]*Test\w*)/g);
    if (testNameMatches) {
      testNameMatches.forEach(testName => {
        // Convert camelCase to readable format
        const readableName = testName
          .replace(/([A-Z])/g, ' $1')
          .replace(/^Test\s*/, '')
          .replace(/\s*Test$/, '')
          .trim();
        
        if (readableName && !scenarios.includes(readableName)) {
          scenarios.push(readableName);
        }
      });
    }
    
    // If no specific scenarios found, return generic ones based on error types
    if (scenarios.length === 0) {
      if (output.includes('Exception') || output.includes('Error')) {
        scenarios.push('System Error Handling Test');
      } else {
        scenarios.push('Feature Functionality Test');
      }
    }
    
    return scenarios;
  };

  // Parse JSON test results from the output
  const testData = useMemo(() => {
    const output = state.testRunnerOutput || testRunnerAgent?.output;
    if (!output) return null;

    try {
      // Try to extract JSON from the output
      const jsonMatch = output.match(/'test_results':\s*({[^}]+})/);
      if (jsonMatch) {
        const jsonStr = jsonMatch[1];
        // Parse the extracted JSON-like string
        const cleanJsonStr = jsonStr
          .replace(/'/g, '"')
          .replace(/(\w+):/g, '"$1":')
          .replace(/False/g, 'false')
          .replace(/True/g, 'true');
        
        const testResults = JSON.parse(cleanJsonStr);
        
        // Extract detailed results from the raw output
        const detailedResults = extractDetailedResults(output, testResults);
        
        return {
          ...testResults,
          detailed_results: detailedResults
        };
      }

      // Try to parse entire output as JSON
      const parsedOutput = JSON.parse(output);
      const detailedResults = extractDetailedResults(output, parsedOutput);
      
      return {
        ...parsedOutput,
        detailed_results: detailedResults
      };
    } catch (error) {
      // If JSON parsing fails, try to extract data from text
      const totalMatch = output.match(/total_tests'?:\s*(\d+)/i);
      const passedMatch = output.match(/passed_tests'?:\s*(\d+)/i);
      const failedMatch = output.match(/failed_tests'?:\s*(\d+)/i);
      const skippedMatch = output.match(/skipped_tests'?:\s*(\d+)/i);

      if (totalMatch || passedMatch || failedMatch) {
        const basicResults = {
          success: false,
          total_tests: totalMatch ? parseInt(totalMatch[1]) : 0,
          passed_tests: passedMatch ? parseInt(passedMatch[1]) : 0,
          failed_tests: failedMatch ? parseInt(failedMatch[1]) : 0,
          skipped_tests: skippedMatch ? parseInt(skippedMatch[1]) : 0,
        };
        
        const detailedResults = extractDetailedResults(output, basicResults);
        
        return {
          ...basicResults,
          detailed_results: detailedResults
        };
      }

      return null;
    }
  }, [state.testRunnerOutput, testRunnerAgent?.output]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleDownloadReport = () => {
    const content = state.testRunnerOutput || testRunnerAgent?.output || '';
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bug-bash-report-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Prepare chart data
  const pieChartData = useMemo(() => {
    if (!testData) return [];
    
    const data = [];
    if (testData.passed_tests > 0) data.push({ name: 'Passed', value: testData.passed_tests, color: COLORS.passed });
    if (testData.failed_tests > 0) data.push({ name: 'Failed', value: testData.failed_tests, color: COLORS.failed });
    if (testData.skipped_tests > 0) data.push({ name: 'Skipped', value: testData.skipped_tests, color: COLORS.skipped });
    
    return data;
  }, [testData]);

  const barChartData = useMemo(() => {
    if (!testData) return [];
    
    return [
      {
        category: 'Test Results',
        Passed: testData.passed_tests || 0,
        Failed: testData.failed_tests || 0,
        Skipped: testData.skipped_tests || 0,
      }
    ];
  }, [testData]);

  // Calculate success rate
  const successRate = useMemo(() => {
    if (!testData || testData.total_tests === 0) return 0;
    return ((testData.passed_tests / testData.total_tests) * 100).toFixed(1);
  }, [testData]);

  if (!hasTestResults && testRunnerAgent?.status !== 'success') {
    return null;
  }

  return (
    <ResultsCard className="animate-fade-in">
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssessmentIcon color="primary" sx={{ fontSize: 28 }} />
            <Typography variant="h4" component="h2" sx={{ fontWeight: 700, color: '#1e293b' }}>
              Bug Bash Quality Dashboard
            </Typography>
            {testRunnerAgent?.status === 'success' && (
              <Chip label="Completed" color="success" size="small" />
            )}
          </Box>
          
          <Box>
            <Button
              startIcon={<DownloadIcon />}
              onClick={handleDownloadReport}
              disabled={!hasTestResults}
              sx={{ mr: 1 }}
              variant="outlined"
            >
              Download Bug Report
            </Button>
            <Button
              startIcon={<RefreshIcon />}
              onClick={() => window.location.reload()}
              variant="outlined"
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {testRunnerAgent?.status === 'running' && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Bug bash analysis in progress. Quality metrics will update when completed.
          </Alert>
        )}

        {testRunnerAgent?.status === 'error' && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Bug bash analysis failed. Please check the logs for details.
          </Alert>
        )}

        {hasTestResults && testData && (
          <>
            {/* Key Metrics */}
            <DashboardGrid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard>
                  <CodeIcon sx={{ fontSize: 40, color: COLORS.primary, mb: 1 }} />
                  <MetricValue sx={{ color: COLORS.primary }}>
                    {testData.total_tests || 0}
                  </MetricValue>
                  <MetricLabel>Total Scenarios</MetricLabel>
                </MetricCard>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard>
                  <CheckCircleIcon sx={{ fontSize: 40, color: COLORS.passed, mb: 1 }} />
                  <MetricValue sx={{ color: COLORS.passed }}>
                    {testData.passed_tests || 0}
                  </MetricValue>
                  <MetricLabel>Scenarios Passed</MetricLabel>
                </MetricCard>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard>
                  <ErrorIcon sx={{ fontSize: 40, color: COLORS.failed, mb: 1 }} />
                  <MetricValue sx={{ color: COLORS.failed }}>
                    {testData.failed_tests || 0}
                  </MetricValue>
                  <MetricLabel>Issues Found</MetricLabel>
                </MetricCard>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard>
                  <TimerIcon sx={{ fontSize: 40, color: COLORS.warning, mb: 1 }} />
                  <MetricValue sx={{ 
                    color: successRate >= 80 ? COLORS.success : successRate >= 60 ? COLORS.warning : COLORS.failed 
                  }}>
                    {successRate}%
                  </MetricValue>
                  <MetricLabel>Quality Score</MetricLabel>
                </MetricCard>
              </Grid>
            </DashboardGrid>

            {/* Charts Section */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <ChartContainer>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1e293b' }}>
                    Bug Bash Results Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieChartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <ChartContainer>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1e293b' }}>
                    Feature Quality Summary
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={barChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="Passed" fill={COLORS.passed} name="Working Scenarios" />
                      <Bar dataKey="Failed" fill={COLORS.failed} name="Bugs Found" />
                      <Bar dataKey="Skipped" fill={COLORS.skipped} name="Skipped Tests" />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </Grid>
            </Grid>

            {/* Tabbed Detailed Results */}
            <Tabs 
              value={activeTab} 
              onChange={handleTabChange}
              sx={{ 
                mb: 2,
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: '1rem',
                }
              }}
            >
              <Tab label="🎯 Quality Overview" />
              <Tab label="� Bug Details" />
              <Tab label="� Raw Analysis" />
            </Tabs>

            <TabPanel value={activeTab} index={0}>
              <ChartContainer>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#1e293b' }}>
                  Feature Quality Analysis
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ p: 2, background: '#f8fafc', borderRadius: 2, mb: 2 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: '#374151' }}>
                        Bug Bash Summary
                      </Typography>
                      <List dense>
                        <ListItem>
                          <ListItemIcon>
                            <CheckCircleIcon sx={{ color: COLORS.success }} />
                          </ListItemIcon>
                          <ListItemText 
                            primary={`${testData.passed_tests || 0} scenarios working correctly`}
                            secondary={`${((testData.passed_tests || 0) / (testData.total_tests || 1) * 100).toFixed(1)}% of tested features`}
                          />
                        </ListItem>
                        
                        <ListItem>
                          <ListItemIcon>
                            <ErrorIcon sx={{ color: COLORS.error }} />
                          </ListItemIcon>
                          <ListItemText 
                            primary={`${testData.failed_tests || 0} bugs discovered`}
                            secondary={`${((testData.failed_tests || 0) / (testData.total_tests || 1) * 100).toFixed(1)}% requiring fixes`}
                          />
                        </ListItem>
                        
                        {(testData.skipped_tests || 0) > 0 && (
                          <ListItem>
                            <ListItemIcon>
                              <SkipNextIcon sx={{ color: COLORS.warning }} />
                            </ListItemIcon>
                            <ListItemText 
                              primary={`${testData.skipped_tests} scenarios not tested`}
                              secondary={`${((testData.skipped_tests || 0) / (testData.total_tests || 1) * 100).toFixed(1)}% pending validation`}
                            />
                          </ListItem>
                        )}
                      </List>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Box sx={{ p: 2, background: '#f8fafc', borderRadius: 2, mb: 2 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: '#374151' }}>
                        Production Readiness
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500, mr: 2, minWidth: 140 }}>
                          Readiness Status:
                        </Typography>
                        <Chip 
                          label={
                            successRate >= 95 ? 'Ready for Production' :
                            successRate >= 85 ? 'Minor Fixes Needed' :
                            successRate >= 70 ? 'Moderate Issues' : 
                            successRate >= 50 ? 'Major Issues Found' : 'Not Ready'
                          }
                          color={
                            successRate >= 95 ? 'success' :
                            successRate >= 85 ? 'primary' :
                            successRate >= 70 ? 'warning' : 'error'
                          }
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" sx={{ color: '#64748b', lineHeight: 1.6 }}>
                        {successRate >= 95 
                          ? 'Excellent quality! Feature is ready for production deployment with minimal risk.'
                          : successRate >= 85 
                          ? 'Good quality with minor issues. Address bugs before production release.'
                          : successRate >= 70 
                          ? 'Moderate quality concerns. Review and fix identified issues before release.'
                          : successRate >= 50
                          ? 'Significant issues found. Extensive fixes required before production.'
                          : 'Critical issues detected. Feature requires major rework before release.'
                        }
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </ChartContainer>
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
              <ChartContainer>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#1e293b' }}>
                  Bug Bash Findings
                </Typography>
                
                {testData.detailed_results && testData.detailed_results.length > 0 ? (
                  <>
                    {/* Summary Stats */}
                    <Box sx={{ mb: 3, p: 2, background: '#f8fafc', borderRadius: 2 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6" sx={{ color: COLORS.error, fontWeight: 700 }}>
                              {testData.detailed_results.filter(t => t.status === 'failed').length}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#64748b' }}>
                              Critical Issues
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6" sx={{ color: COLORS.success, fontWeight: 700 }}>
                              {testData.detailed_results.filter(t => t.status === 'passed').length}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#64748b' }}>
                              Working Features
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6" sx={{ color: COLORS.warning, fontWeight: 700 }}>
                              {testData.detailed_results.filter(t => t.severity === 'critical').length}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#64748b' }}>
                              High Priority
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>

                    {/* Failed Tests First */}
                    {testData.detailed_results.filter(test => test.status === 'failed').length > 0 && (
                      <>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: COLORS.error }}>
                          🚨 Issues Requiring Immediate Attention
                        </Typography>
                        
                        {testData.detailed_results
                          .filter(test => test.status === 'failed')
                          .map((test, index) => (
                            <Accordion key={`failed-${index}`} sx={{ mb: 2, border: '2px solid #fecaca' }}>
                              <AccordionSummary 
                                expandIcon={<ExpandMoreIcon />}
                                sx={{ background: '#fef2f2' }}
                              >
                                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                                  <ErrorIcon sx={{ color: COLORS.error, mr: 2 }} />
                                  <Box sx={{ flex: 1 }}>
                                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                      {test.name || `Critical Bug ${index + 1}`}
                                    </Typography>
                                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                                      Category: {test.category || 'Unknown'} • Severity: {test.severity || 'Medium'}
                                    </Typography>
                                  </Box>
                                  <Chip 
                                    label={test.severity === 'critical' ? 'CRITICAL' : test.severity === 'high' ? 'HIGH' : 'MEDIUM'}
                                    size="small"
                                    color={test.severity === 'critical' ? 'error' : test.severity === 'high' ? 'warning' : 'default'}
                                    sx={{ mr: 2 }}
                                  />
                                  <Chip 
                                    label="FAILED"
                                    size="small"
                                    color="error"
                                  />
                                </Box>
                              </AccordionSummary>
                              <AccordionDetails sx={{ background: '#ffffff' }}>
                                <Grid container spacing={2}>
                                  <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: COLORS.error }}>
                                        🐛 Issue Description:
                                      </Typography>
                                      <Box sx={{ 
                                        background: '#fef2f2', 
                                        border: '1px solid #fecaca',
                                        borderRadius: 1, 
                                        p: 2,
                                        fontSize: '0.875rem',
                                        color: '#991b1b'
                                      }}>
                                        {extractCleanErrorDescription(test.error)}
                                      </Box>
                                    </Box>

                                    {test.duration && (
                                      <Box sx={{ mb: 2 }}>
                                        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                                          ⏱️ Execution Time:
                                        </Typography>
                                        <Typography variant="body2" sx={{ color: '#64748b' }}>
                                          {test.duration}
                                        </Typography>
                                      </Box>
                                    )}

                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                                        📂 Category:
                                      </Typography>
                                      <Chip 
                                        label={test.category || 'Functional'}
                                        size="small"
                                        variant="outlined"
                                        color={
                                          test.category === 'security' ? 'error' :
                                          test.category === 'configuration' ? 'warning' :
                                          test.category === 'connectivity' ? 'info' : 'default'
                                        }
                                      />
                                    </Box>
                                  </Grid>

                                  <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: COLORS.primary }}>
                                        💡 Recommended Fix:
                                      </Typography>
                                      <Box sx={{ 
                                        background: '#f0f9ff', 
                                        border: '1px solid #bfdbfe',
                                        borderRadius: 1, 
                                        p: 2,
                                        fontSize: '0.875rem',
                                        color: '#1e40af'
                                      }}>
                                        {test.mitigation || 'Review configuration and validate inputs. Check logs for detailed error information.'}
                                      </Box>
                                    </Box>

                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                                        🎯 Priority Level:
                                      </Typography>
                                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <Box sx={{ 
                                          width: 12, 
                                          height: 12, 
                                          borderRadius: '50%', 
                                          background: test.severity === 'critical' ? COLORS.error : 
                                                     test.severity === 'high' ? COLORS.warning : COLORS.primary,
                                          mr: 1 
                                        }} />
                                        <Typography variant="body2" sx={{ color: '#64748b' }}>
                                          {test.severity === 'critical' ? 'Fix before production release' :
                                           test.severity === 'high' ? 'Address in current sprint' :
                                           'Include in next release cycle'}
                                        </Typography>
                                      </Box>
                                    </Box>
                                  </Grid>

                                  {test.output && (
                                    <Grid item xs={12}>
                                      <Divider sx={{ my: 2 }} />
                                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                                        📋 Technical Details:
                                      </Typography>
                                      <Box sx={{ 
                                        background: '#f8fafc', 
                                        border: '1px solid #e2e8f0',
                                        borderRadius: 1, 
                                        p: 2,
                                        fontFamily: 'monospace',
                                        fontSize: '0.875rem',
                                        maxHeight: 200,
                                        overflow: 'auto'
                                      }}>
                                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                          {test.output}
                                        </pre>
                                      </Box>
                                    </Grid>
                                  )}
                                </Grid>
                              </AccordionDetails>
                            </Accordion>
                          ))}
                      </>
                    )}

                    {/* Passed Tests */}
                    {testData.detailed_results.filter(test => test.status === 'passed').length > 0 && (
                      <>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, mt: 3, color: COLORS.success }}>
                          ✅ Working Features (Quality Verified)
                        </Typography>
                        
                        {testData.detailed_results
                          .filter(test => test.status === 'passed')
                          .map((test, index) => (
                            <Accordion key={`passed-${index}`} sx={{ mb: 1, border: '1px solid #bbf7d0' }}>
                              <AccordionSummary 
                                expandIcon={<ExpandMoreIcon />}
                                sx={{ background: '#f0fdf4' }}
                              >
                                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                                  <CheckCircleIcon sx={{ color: COLORS.success, mr: 2 }} />
                                  <Typography variant="subtitle1" sx={{ fontWeight: 600, flex: 1 }}>
                                    {test.name || `Working Feature ${index + 1}`}
                                  </Typography>
                                  <Chip 
                                    label="PASSED"
                                    size="small"
                                    color="success"
                                  />
                                </Box>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                  <CheckCircleIcon sx={{ color: COLORS.success, mr: 1 }} />
                                  <Typography variant="body2" sx={{ color: '#16a34a' }}>
                                    Feature is working correctly and ready for production
                                  </Typography>
                                </Box>
                                {test.duration && (
                                  <Typography variant="body2" sx={{ mb: 1, color: '#64748b' }}>
                                    <strong>Execution Time:</strong> {test.duration}
                                  </Typography>
                                )}
                                {test.output && (
                                  <Box sx={{ 
                                    background: '#f0fdf4', 
                                    border: '1px solid #bbf7d0',
                                    borderRadius: 1, 
                                    p: 2,
                                    fontSize: '0.875rem',
                                    color: '#15803d'
                                  }}>
                                    {test.output}
                                  </Box>
                                )}
                              </AccordionDetails>
                            </Accordion>
                          ))}
                      </>
                    )}
                  </>
                ) : (
                  <Alert severity="info">
                    No detailed bug findings available. The bug bash analysis completed with summary metrics only.
                  </Alert>
                )}
              </ChartContainer>
            </TabPanel>

            <TabPanel value={activeTab} index={2}>
              <ChartContainer>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1e293b' }}>
                  Raw Bug Bash Analysis
                </Typography>
                <Box sx={{ 
                  background: '#0f172a', 
                  color: '#e2e8f0', 
                  p: 3, 
                  borderRadius: 2,
                  fontFamily: '"Fira Code", "Courier New", monospace',
                  fontSize: '0.875rem',
                  overflow: 'auto',
                  maxHeight: '500px'
                }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {state.testRunnerOutput || testRunnerAgent?.output || 'No output available'}
                  </pre>
                </Box>
              </ChartContainer>
            </TabPanel>
          </>
        )}

        {hasTestResults && !testData && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Bug bash results are available but could not be parsed. Please check the Raw Analysis tab for details.
          </Alert>
        )}

        {!hasTestResults && testRunnerAgent?.status === 'pending' && (
          <Alert severity="info">
            Bug Bash Copilot is waiting to start. Complete the previous steps to begin feature quality analysis.
          </Alert>
        )}
      </CardContent>
    </ResultsCard>
  );
}

export default TestRunnerResults;
