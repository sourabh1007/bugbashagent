import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Collapse,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Visibility as VisibilityIcon,
  PlayArrow as PlayArrowIcon,
  Build as BuildIcon,
  BugReport as BugReportIcon,
  Assessment as AssessmentIcon,
  Description as DescriptionIcon,
  Code as CodeIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';

// Helper function to format duration
const formatDuration = (timeStr) => {
  if (!timeStr) {
    return 'N/A';
  }
  
  // If it's already in a readable format, return as is
  if (timeStr.includes('m') || timeStr.includes('s')) {
    return timeStr;
  }
  
  // Try to parse as seconds
  const seconds = parseFloat(timeStr);
  if (isNaN(seconds)) {
    return timeStr;
  }
  
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  }
};

const HistoricalRuns = () => {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedRun, setExpandedRun] = useState(null);
  const [selectedRun, setSelectedRun] = useState(null);
  const [runDetails, setRunDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [detailsTab, setDetailsTab] = useState(0);

  useEffect(() => {
    fetchHistoricalRuns();
  }, []);

  const fetchHistoricalRuns = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/historical-runs');
      const data = await response.json();
      
      if (data.success) {
        setRuns(data.runs);
        setError(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError(`Failed to fetch historical runs: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchRunDetails = async (runId) => {
    try {
      setDetailsLoading(true);
      const response = await fetch(`http://localhost:5000/api/historical-runs/${runId}/details`);
      const data = await response.json();
      
      if (data.success) {
        setRunDetails(data.details);
        setDetailsDialogOpen(true);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError(`Failed to fetch run details: ${err.message}`);
    } finally {
      setDetailsLoading(false);
    }
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      success: { color: 'success', label: 'Success' },
      partial: { color: 'warning', label: 'Partial' },
      failed: { color: 'error', label: 'Failed' },
      compiled: { color: 'info', label: 'Compiled' },
      error: { color: 'error', label: 'Error' },
      unknown: { color: 'default', label: 'Unknown' }
    };
    
    const config = statusConfig[status] || statusConfig.unknown;
    return <Chip size="small" color={config.color} label={config.label} />;
  };

  const getCompilationStatusChip = (status) => {
    const statusConfig = {
      success: { color: 'success', label: 'Success', icon: <BuildIcon fontSize="small" /> },
      failed: { color: 'error', label: 'Failed', icon: <BugReportIcon fontSize="small" /> },
      error: { color: 'error', label: 'Error', icon: <BugReportIcon fontSize="small" /> },
      unknown: { color: 'default', label: 'Unknown', icon: <BuildIcon fontSize="small" /> }
    };
    
    const config = statusConfig[status] || statusConfig.unknown;
    return <Chip size="small" color={config.color} label={config.label} icon={config.icon} />;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) {
      return 'N/A';
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const filteredRuns = runs.filter(run =>
    run.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    run.language.toLowerCase().includes(searchTerm.toLowerCase()) ||
    run.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleExpandClick = (runId) => {
    setExpandedRun(expandedRun === runId ? null : runId);
  };

  const handleViewDetails = (run) => {
    setSelectedRun(run);
    fetchRunDetails(run.id);
  };

  const renderDetailsDialog = () => {
    if (!runDetails) {
      return null;
    }

    const tabNames = ['Overview', 'Compilation', 'Test Results', 'Scenarios', 'Reports'];

    return (
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Run Details: {selectedRun?.project_name}
          <Typography variant="body2" color="text.secondary">
            {selectedRun && formatDate(selectedRun.execution_date)}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={detailsTab} onChange={(e, newValue) => setDetailsTab(newValue)}>
              {tabNames.map((name, index) => (
                <Tab key={index} label={name} />
              ))}
            </Tabs>
          </Box>

          {/* Overview Tab */}
          {detailsTab === 0 && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Execution Summary
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Project:</strong> {selectedRun?.project_name}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Language:</strong> {selectedRun?.language}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Status:</strong> {selectedRun && getStatusChip(selectedRun.status)}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Duration:</strong> {selectedRun && formatDuration(selectedRun.duration)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Generated Content
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Scenarios Generated:</strong> {selectedRun?.scenarios_generated || 0}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Test Files:</strong> {selectedRun?.test_files_count || 0}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Output Files:</strong> {runDetails.output_files?.length || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Compilation Tab */}
          {detailsTab === 1 && (
            <Box>
              {runDetails.compilation_results ? (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Compilation Results
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Status:</strong> {getCompilationStatusChip(runDetails.compilation_results.success ? 'success' : 'failed')}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Return Code:</strong> {runDetails.compilation_results.returncode || 'N/A'}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Command:</strong> <code>{runDetails.compilation_results.command || 'N/A'}</code>
                    </Typography>
                    {runDetails.compilation_results.stdout && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2">Output:</Typography>
                        <Paper sx={{ p: 2, backgroundColor: '#f5f5f5', overflow: 'auto', maxHeight: 400 }}>
                          <pre style={{ margin: 0, fontSize: '0.8rem' }}>
                            {runDetails.compilation_results.stdout}
                          </pre>
                        </Paper>
                      </Box>
                    )}
                    {runDetails.compilation_results.stderr && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2">Errors:</Typography>
                        <Paper sx={{ p: 2, backgroundColor: '#ffebee', overflow: 'auto', maxHeight: 300 }}>
                          <pre style={{ margin: 0, fontSize: '0.8rem', color: '#c62828' }}>
                            {runDetails.compilation_results.stderr}
                          </pre>
                        </Paper>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ) : (
                <Alert severity="info">No compilation results available</Alert>
              )}
            </Box>
          )}

          {/* Test Results Tab */}
          {detailsTab === 2 && (
            <Box>
              {runDetails.test_results ? (
                <Box>
                  {/* Test Summary Cards */}
                  <Card sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Test Execution Summary
                      </Typography>
                      <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={6} md={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#e3f2fd' }}>
                            <Typography variant="h4" color="primary">
                              {runDetails.test_results.test_results?.total_tests || 0}
                            </Typography>
                            <Typography variant="body2">Total Tests</Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#e8f5e8' }}>
                            <Typography variant="h4" color="success.main">
                              {runDetails.test_results.test_results?.passed_tests || 0}
                            </Typography>
                            <Typography variant="body2">Passed</Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#ffebee' }}>
                            <Typography variant="h4" color="error.main">
                              {runDetails.test_results.test_results?.failed_tests || 0}
                            </Typography>
                            <Typography variant="body2">Failed</Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#fff3e0' }}>
                            <Typography variant="h4" color="warning.main">
                              {runDetails.test_results.test_results?.skipped_tests || 0}
                            </Typography>
                            <Typography variant="body2">Skipped</Typography>
                          </Paper>
                        </Grid>
                      </Grid>
                      
                      {runDetails.test_results.test_results?.success_rate !== undefined && (
                        <Typography variant="body2" paragraph>
                          <strong>Success Rate:</strong> {runDetails.test_results.test_results.success_rate.toFixed(1)}%
                        </Typography>
                      )}
                      
                      {runDetails.test_results.test_results?.execution_time && (
                        <Typography variant="body2" paragraph>
                          <strong>Execution Time:</strong> {formatDuration(runDetails.test_results.test_results.execution_time)}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>

                  {/* Detailed Test Results */}
                  {runDetails.test_results.test_results?.output && (
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Detailed Test Results & Scenario Analysis
                        </Typography>
                        
                        {(() => {
                          const { test_results: testResults } = runDetails.test_results;
                          const { output } = testResults || {};
                          const failedTests = [];
                          const passedTests = [];
                          
                          // Parse failed tests from output
                          const failedMatches = output.match(/Failed\s+([^\[]+)\s+\[[\d\s]+s\]/g);
                          if (failedMatches) {
                            failedMatches.forEach(match => {
                              const testName = match.replace(/Failed\s+/, '').replace(/\s+\[[\d\s]+s\]/, '').trim();
                              
                              // Extract error message
                              const testIndex = output.indexOf(match);
                              const nextTestIndex = output.indexOf('Failed ', testIndex + 1);
                              const endIndex = nextTestIndex > -1 ? nextTestIndex : output.length;
                              const testSection = output.substring(testIndex, endIndex);
                              
                              // Find error message
                              const errorMatch = testSection.match(/Error Message:\s*\n([\s\S]*?)(?=\n\s*Stack Trace:|$)/);
                              const errorMessage = errorMatch ? errorMatch[1].trim() : 'No error message available';
                              
                              // Determine scenario and resolution
                              let scenario = 'Unknown Scenario';
                              let resolution = 'Resolution not determined';
                              
                              if (testName.includes('PartitionKey')) {
                                scenario = 'Partition Key Validation Scenario';
                                resolution = 'Add proper partition key validation before document insertion. Ensure CosmosException is thrown for missing partition keys.';
                              } else if (testName.includes('ConsistencyLevel')) {
                                scenario = 'Consistency Level Configuration Scenario';
                                resolution = 'Ensure consistency level in request does not exceed service configuration. Use Session or lower consistency levels.';
                              } else if (testName.includes('Query') || testName.includes('Pagination')) {
                                scenario = 'Query and Pagination Scenario';
                                resolution = 'Fix SQL query syntax errors. Validate query structure and ensure proper continuation token handling.';
                              }
                              
                              failedTests.push({
                                name: testName,
                                scenario,
                                errorMessage,
                                resolution
                              });
                            });
                          }
                          
                          // Extract passed test count info
                          const totalTests = testResults?.total_tests || 0;
                          const failedCount = testResults?.failed_tests || 0;
                          const passedCount = testResults?.passed_tests || 0;
                          
                          return (
                            <Box>
                              {/* Failed Tests Section */}
                              {failedTests.length > 0 && (
                                <Box sx={{ mb: 3 }}>
                                  <Typography variant="h6" color="error.main" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                    <BugReportIcon sx={{ mr: 1 }} />
                                    Failed Tests & Scenarios ({failedTests.length})
                                  </Typography>
                                  
                                  {failedTests.map((test, index) => (
                                    <Card key={index} sx={{ mb: 2, borderLeft: '4px solid #f44336' }}>
                                      <CardContent>
                                        <Typography variant="subtitle1" fontWeight="bold" color="error.main">
                                          {test.name}
                                        </Typography>
                                        
                                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 2 }}>
                                          <strong>Scenario:</strong> {test.scenario}
                                        </Typography>
                                        
                                        <Box sx={{ backgroundColor: '#ffebee', p: 2, borderRadius: 1, mb: 2 }}>
                                          <Typography variant="subtitle2" color="error.main" gutterBottom>
                                            Error Details:
                                          </Typography>
                                          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                            {test.errorMessage}
                                          </Typography>
                                        </Box>
                                        
                                        <Box sx={{ backgroundColor: '#e3f2fd', p: 2, borderRadius: 1 }}>
                                          <Typography variant="subtitle2" color="primary" gutterBottom>
                                            Recommended Resolution:
                                          </Typography>
                                          <Typography variant="body2">
                                            {test.resolution}
                                          </Typography>
                                        </Box>
                                      </CardContent>
                                    </Card>
                                  ))}
                                </Box>
                              )}
                              
                              {/* Passed Tests Section */}
                              {passedCount > 0 && (
                                <Box sx={{ mb: 3 }}>
                                  <Typography variant="h6" color="success.main" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                    <AssessmentIcon sx={{ mr: 1 }} />
                                    Successful Test Scenarios ({passedCount})
                                  </Typography>
                                  
                                  <Card sx={{ borderLeft: '4px solid #4caf50' }}>
                                    <CardContent>
                                      <Typography variant="body1" paragraph>
                                        <strong>{passedCount} test scenarios passed successfully</strong>, indicating that the following functionality is working correctly:
                                      </Typography>
                                      
                                      <Box sx={{ backgroundColor: '#e8f5e8', p: 2, borderRadius: 1 }}>
                                        <Typography variant="subtitle2" color="success.main" gutterBottom>
                                          Validated Scenarios Include:
                                        </Typography>
                                        <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                          <li>Basic document insertion and CRUD operations</li>
                                          <li>Container creation and configuration</li>
                                          <li>Authentication and connection handling</li>
                                          <li>Query execution for valid scenarios</li>
                                          <li>Integration with Azure services</li>
                                          <li>Proper exception handling for known error cases</li>
                                        </ul>
                                      </Box>
                                    </CardContent>
                                  </Card>
                                </Box>
                              )}
                              
                              {/* Full Test Output */}
                              <Box sx={{ mt: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                  Complete Test Output Log
                                </Typography>
                                <Paper sx={{ p: 2, backgroundColor: '#f5f5f5', overflow: 'auto', maxHeight: 400 }}>
                                  <pre style={{ margin: 0, fontSize: '0.8rem', whiteSpace: 'pre-wrap' }}>
                                    {output}
                                  </pre>
                                </Paper>
                              </Box>
                            </Box>
                          );
                        })()}
                      </CardContent>
                    </Card>
                  )}
                </Box>
              ) : (
                <Alert severity="info">No test results available</Alert>
              )}
            </Box>
          )}

          {/* Scenarios Tab */}
          {detailsTab === 3 && (
            <Box>
              {runDetails.scenario_summary ? (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Scenario Generation Summary
                    </Typography>
                    <Paper sx={{ p: 2, backgroundColor: '#f5f5f5', overflow: 'auto', maxHeight: 500 }}>
                      <pre style={{ margin: 0, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>
                        {runDetails.scenario_summary}
                      </pre>
                    </Paper>
                  </CardContent>
                </Card>
              ) : (
                <Alert severity="info">No scenario summary available</Alert>
              )}
            </Box>
          )}

          {/* Reports Tab */}
          {detailsTab === 4 && (
            <Box>
              {runDetails.comprehensive_report ? (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Comprehensive Generation Report
                    </Typography>
                    <Paper sx={{ p: 2, backgroundColor: '#f5f5f5', overflow: 'auto', maxHeight: 500 }}>
                      <pre style={{ margin: 0, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>
                        {runDetails.comprehensive_report}
                      </pre>
                    </Paper>
                  </CardContent>
                </Card>
              ) : (
                <Alert severity="info">No comprehensive report available</Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading historical runs...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <ScheduleIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
        Historical Workflow Runs
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        View and analyze past workflow executions, including compilation results, test outcomes, and generated artifacts.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Search and Filters */}
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by project name, language, or status..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {/* Results Summary */}
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Showing {filteredRuns.length} of {runs.length} workflow runs
      </Typography>

      {/* Runs Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell></TableCell>
              <TableCell><strong>Project Name</strong></TableCell>
              <TableCell><strong>Language</strong></TableCell>
              <TableCell><strong>Execution Date</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Compilation</strong></TableCell>
              <TableCell><strong>Tests</strong></TableCell>
              <TableCell><strong>Duration</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRuns.map((run) => (
              <React.Fragment key={run.id}>
                <TableRow hover>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleExpandClick(run.id)}
                    >
                      {expandedRun === run.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {run.project_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip size="small" label={run.language} variant="outlined" />
                  </TableCell>
                  <TableCell>{formatDate(run.execution_date)}</TableCell>
                  <TableCell>{getStatusChip(run.status)}</TableCell>
                  <TableCell>{getCompilationStatusChip(run.compilation_status)}</TableCell>
                  <TableCell>
                    {run.test_results.total_tests > 0 ? (
                      <Tooltip title={`${run.test_results.passed_tests}/${run.test_results.total_tests} passed`}>
                        <Chip
                          size="small"
                          label={`${run.test_results.passed_tests}/${run.test_results.total_tests}`}
                          color={run.test_results.passed_tests === run.test_results.total_tests ? 'success' : 'warning'}
                        />
                      </Tooltip>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No tests
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{formatDuration(run.duration)}</TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={() => handleViewDetails(run)}
                        disabled={detailsLoading}
                      >
                        {detailsLoading && selectedRun?.id === run.id ? (
                          <CircularProgress size={20} />
                        ) : (
                          <VisibilityIcon />
                        )}
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
                
                {/* Expanded Row */}
                <TableRow>
                  <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
                    <Collapse in={expandedRun === run.id} timeout="auto" unmountOnExit>
                      <Box sx={{ margin: 1 }}>
                        <Typography variant="h6" gutterBottom component="div">
                          Run Details
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={4}>
                            <Typography variant="body2">
                              <strong>Scenarios Generated:</strong> {run.scenarios_generated}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <Typography variant="body2">
                              <strong>Test Files:</strong> {run.test_files_count}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <Typography variant="body2">
                              <strong>Success Rate:</strong> {run.test_results.total_tests > 0 
                                ? `${((run.test_results.passed_tests / run.test_results.total_tests) * 100).toFixed(1)}%`
                                : 'N/A'
                              }
                            </Typography>
                          </Grid>
                        </Grid>
                      </Box>
                    </Collapse>
                  </TableCell>
                </TableRow>
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredRuns.length === 0 && !loading && (
        <Box textAlign="center" sx={{ mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No workflow runs found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchTerm 
              ? "Try adjusting your search criteria"
              : "Execute some workflows to see results here"
            }
          </Typography>
        </Box>
      )}

      {/* Details Dialog */}
      {renderDetailsDialog()}
    </Box>
  );
};

export default HistoricalRuns;
