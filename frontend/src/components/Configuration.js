import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Grid,
    Switch,
    FormControlLabel,
    Alert,
    Snackbar,
    Divider,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Chip,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    Tooltip
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    Save as SaveIcon,
    Refresh as RefreshIcon,
    BugReport as TestIcon,
    Visibility as VisibilityIcon,
    VisibilityOff as VisibilityOffIcon,
    Settings as SettingsIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import axios from 'axios';

const Configuration = () => {
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const [showPassword, setShowPassword] = useState({});
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
    const [testDialog, setTestDialog] = useState({ open: false, result: null });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        loadConfiguration();
    }, []);

    const loadConfiguration = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/config');
            if (response.data.success) {
                setConfig(response.data.config);
            } else {
                showSnackbar('Failed to load configuration', 'error');
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
            showSnackbar('Failed to load configuration', 'error');
        } finally {
            setLoading(false);
        }
    };

    const saveConfiguration = async () => {
        try {
            setSaving(true);
            setErrors({});
            
            const response = await axios.post('/api/config', { config });
            if (response.data.success) {
                showSnackbar('Configuration saved successfully', 'success');
                // Reload to get the masked values
                setTimeout(() => loadConfiguration(), 1000);
            } else {
                showSnackbar(response.data.error || 'Failed to save configuration', 'error');
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            showSnackbar('Failed to save configuration', 'error');
        } finally {
            setSaving(false);
        }
    };

    const testConfiguration = async () => {
        try {
            setTesting(true);
            const response = await axios.post('/api/config/test');
            if (response.data.success) {
                setTestDialog({ open: true, result: response.data.test_result });
            } else {
                showSnackbar('Configuration test failed', 'error');
            }
        } catch (error) {
            console.error('Error testing configuration:', error);
            showSnackbar('Failed to test configuration', 'error');
        } finally {
            setTesting(false);
        }
    };

    const showSnackbar = (message, severity = 'info') => {
        setSnackbar({ open: true, message, severity });
    };

    const handleConfigChange = (section, field, value) => {
        setConfig(prev => ({
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value
            }
        }));
    };

    const togglePasswordVisibility = (field) => {
        setShowPassword(prev => ({
            ...prev,
            [field]: !prev[field]
        }));
    };

    const validateRequired = (value, fieldName) => {
        if (!value || value.trim() === '') {
            setErrors(prev => ({
                ...prev,
                [fieldName]: 'This field is required'
            }));
            return false;
        }
        setErrors(prev => {
            const newErrors = { ...prev };
            delete newErrors[fieldName];
            return newErrors;
        });
        return true;
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    if (!config) {
        return (
            <Alert severity="error">
                Failed to load configuration. Please try refreshing the page.
            </Alert>
        );
    }

    return (
        <Box sx={{ maxWidth: 1200, margin: '0 auto', padding: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <SettingsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Typography variant="h4" component="h1" fontWeight="bold">
                        Model Configuration
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                        variant="outlined"
                        startIcon={<RefreshIcon />}
                        onClick={loadConfiguration}
                        disabled={loading}
                    >
                        Refresh
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={testing ? <CircularProgress size={16} /> : <TestIcon />}
                        onClick={testConfiguration}
                        disabled={testing}
                        color="info"
                    >
                        Test Configuration
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
                        onClick={saveConfiguration}
                        disabled={saving}
                    >
                        Save Changes
                    </Button>
                </Box>
            </Box>

            {/* Configuration Sections */}
            <Grid container spacing={3}>
                {/* Azure OpenAI Configuration */}
                <Grid item xs={12}>
                    <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="h6" fontWeight="bold">
                                    Azure OpenAI Configuration
                                </Typography>
                                <Chip label="Required" color="error" size="small" />
                            </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Key"
                                        type={showPassword.azure_api_key ? 'text' : 'password'}
                                        value={config.azure_openai.api_key}
                                        onChange={(e) => handleConfigChange('azure_openai', 'api_key', e.target.value)}
                                        error={!!errors.azure_api_key}
                                        helperText={errors.azure_api_key}
                                        InputProps={{
                                            endAdornment: (
                                                <IconButton
                                                    onClick={() => togglePasswordVisibility('azure_api_key')}
                                                    edge="end"
                                                >
                                                    {showPassword.azure_api_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                </IconButton>
                                            ),
                                        }}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Endpoint URL"
                                        value={config.azure_openai.endpoint}
                                        onChange={(e) => handleConfigChange('azure_openai', 'endpoint', e.target.value)}
                                        placeholder="https://your-resource.openai.azure.com/"
                                        error={!!errors.azure_endpoint}
                                        helperText={errors.azure_endpoint}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Deployment Name"
                                        value={config.azure_openai.deployment_name}
                                        onChange={(e) => handleConfigChange('azure_openai', 'deployment_name', e.target.value)}
                                        error={!!errors.azure_deployment}
                                        helperText={errors.azure_deployment}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Version"
                                        value={config.azure_openai.api_version}
                                        onChange={(e) => handleConfigChange('azure_openai', 'api_version', e.target.value)}
                                    />
                                </Grid>
                            </Grid>
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* Global Model Configuration */}
                <Grid item xs={12}>
                    <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="h6" fontWeight="bold">
                                Global Model Settings
                            </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Model Name"
                                        value={config.global_model.model_name}
                                        onChange={(e) => handleConfigChange('global_model', 'model_name', e.target.value)}
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Temperature"
                                        type="number"
                                        inputProps={{ min: 0, max: 2, step: 0.1 }}
                                        value={config.global_model.temperature}
                                        onChange={(e) => handleConfigChange('global_model', 'temperature', parseFloat(e.target.value))}
                                        helperText="Controls randomness (0.0 - 2.0)"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Max Tokens"
                                        type="number"
                                        inputProps={{ min: 1, max: 32000 }}
                                        value={config.global_model.max_tokens}
                                        onChange={(e) => handleConfigChange('global_model', 'max_tokens', parseInt(e.target.value))}
                                        helperText="Maximum response length"
                                    />
                                </Grid>
                            </Grid>
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* LangSmith Configuration */}
                <Grid item xs={12}>
                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="h6" fontWeight="bold">
                                    LangSmith Monitoring
                                </Typography>
                                <Chip label="Optional" color="primary" size="small" />
                            </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={config.langsmith.tracing_enabled}
                                                onChange={(e) => handleConfigChange('langsmith', 'tracing_enabled', e.target.checked)}
                                            />
                                        }
                                        label="Enable LangSmith Tracing"
                                    />
                                </Grid>
                                {config.langsmith.tracing_enabled && (
                                    <>
                                        <Grid item xs={12} md={6}>
                                            <TextField
                                                fullWidth
                                                label="LangSmith API Key"
                                                type={showPassword.langsmith_api_key ? 'text' : 'password'}
                                                value={config.langsmith.api_key}
                                                onChange={(e) => handleConfigChange('langsmith', 'api_key', e.target.value)}
                                                InputProps={{
                                                    endAdornment: (
                                                        <IconButton
                                                            onClick={() => togglePasswordVisibility('langsmith_api_key')}
                                                            edge="end"
                                                        >
                                                            {showPassword.langsmith_api_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                        </IconButton>
                                                    ),
                                                }}
                                            />
                                        </Grid>
                                        <Grid item xs={12} md={6}>
                                            <TextField
                                                fullWidth
                                                label="Project Name"
                                                value={config.langsmith.project}
                                                onChange={(e) => handleConfigChange('langsmith', 'project', e.target.value)}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <TextField
                                                fullWidth
                                                label="LangSmith Endpoint"
                                                value={config.langsmith.endpoint}
                                                onChange={(e) => handleConfigChange('langsmith', 'endpoint', e.target.value)}
                                            />
                                        </Grid>
                                    </>
                                )}
                            </Grid>
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* Document Analyzer Agent Configuration */}
                <Grid item xs={12}>
                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="h6" fontWeight="bold">
                                    Document Analyzer Agent Overrides
                                </Typography>
                                <Chip label="Optional" color="secondary" size="small" />
                            </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Alert severity="info" sx={{ mb: 3 }}>
                                Configure agent-specific settings to override global values. Leave empty to use global configuration.
                            </Alert>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Key (Override)"
                                        type={showPassword.doc_analyzer_api_key ? 'text' : 'password'}
                                        value={config.document_analyzer.api_key}
                                        onChange={(e) => handleConfigChange('document_analyzer', 'api_key', e.target.value)}
                                        placeholder="Leave empty to use global API key"
                                        InputProps={{
                                            endAdornment: (
                                                <IconButton
                                                    onClick={() => togglePasswordVisibility('doc_analyzer_api_key')}
                                                    edge="end"
                                                >
                                                    {showPassword.doc_analyzer_api_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                </IconButton>
                                            ),
                                        }}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Endpoint (Override)"
                                        value={config.document_analyzer.endpoint}
                                        onChange={(e) => handleConfigChange('document_analyzer', 'endpoint', e.target.value)}
                                        placeholder="Leave empty to use global endpoint"
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Deployment Name (Override)"
                                        value={config.document_analyzer.deployment_name}
                                        onChange={(e) => handleConfigChange('document_analyzer', 'deployment_name', e.target.value)}
                                        placeholder="Leave empty to use global deployment"
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Version (Override)"
                                        value={config.document_analyzer.api_version}
                                        onChange={(e) => handleConfigChange('document_analyzer', 'api_version', e.target.value)}
                                        placeholder="Leave empty to use global API version"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Model Name (Override)"
                                        value={config.document_analyzer.model_name}
                                        onChange={(e) => handleConfigChange('document_analyzer', 'model_name', e.target.value)}
                                        placeholder="Leave empty to use global model"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Temperature (Override)"
                                        type="number"
                                        inputProps={{ min: 0, max: 2, step: 0.1 }}
                                        value={config.document_analyzer.temperature || ''}
                                        onChange={(e) => handleConfigChange('document_analyzer', 'temperature', e.target.value ? parseFloat(e.target.value) : null)}
                                        placeholder="0.4 (recommended for analysis)"
                                        helperText="Lower values for more focused analysis"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Max Tokens (Override)"
                                        type="number"
                                        inputProps={{ min: 1, max: 32000 }}
                                        value={config.document_analyzer.max_tokens || ''}
                                        onChange={(e) => handleConfigChange('document_analyzer', 'max_tokens', e.target.value ? parseInt(e.target.value) : null)}
                                        placeholder="6000 (recommended for analysis)"
                                        helperText="Sufficient for analysis tasks"
                                    />
                                </Grid>
                            </Grid>
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* Code Generator Agent Configuration */}
                <Grid item xs={12}>
                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="h6" fontWeight="bold">
                                    Code Generator Agent Overrides
                                </Typography>
                                <Chip label="Optional" color="secondary" size="small" />
                            </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Alert severity="info" sx={{ mb: 3 }}>
                                Configure agent-specific settings to override global values. Leave empty to use global configuration.
                            </Alert>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Key (Override)"
                                        type={showPassword.code_generator_api_key ? 'text' : 'password'}
                                        value={config.code_generator.api_key}
                                        onChange={(e) => handleConfigChange('code_generator', 'api_key', e.target.value)}
                                        placeholder="Leave empty to use global API key"
                                        InputProps={{
                                            endAdornment: (
                                                <IconButton
                                                    onClick={() => togglePasswordVisibility('code_generator_api_key')}
                                                    edge="end"
                                                >
                                                    {showPassword.code_generator_api_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                </IconButton>
                                            ),
                                        }}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Endpoint (Override)"
                                        value={config.code_generator.endpoint}
                                        onChange={(e) => handleConfigChange('code_generator', 'endpoint', e.target.value)}
                                        placeholder="Leave empty to use global endpoint"
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Deployment Name (Override)"
                                        value={config.code_generator.deployment_name}
                                        onChange={(e) => handleConfigChange('code_generator', 'deployment_name', e.target.value)}
                                        placeholder="Leave empty to use global deployment"
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Version (Override)"
                                        value={config.code_generator.api_version}
                                        onChange={(e) => handleConfigChange('code_generator', 'api_version', e.target.value)}
                                        placeholder="Leave empty to use global API version"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Model Name (Override)"
                                        value={config.code_generator.model_name}
                                        onChange={(e) => handleConfigChange('code_generator', 'model_name', e.target.value)}
                                        placeholder="Leave empty to use global model"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Temperature (Override)"
                                        type="number"
                                        inputProps={{ min: 0, max: 2, step: 0.1 }}
                                        value={config.code_generator.temperature || ''}
                                        onChange={(e) => handleConfigChange('code_generator', 'temperature', e.target.value ? parseFloat(e.target.value) : null)}
                                        placeholder="0.5 (recommended for code)"
                                        helperText="Balanced creativity for code generation"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Max Tokens (Override)"
                                        type="number"
                                        inputProps={{ min: 1, max: 32000 }}
                                        value={config.code_generator.max_tokens || ''}
                                        onChange={(e) => handleConfigChange('code_generator', 'max_tokens', e.target.value ? parseInt(e.target.value) : null)}
                                        placeholder="9000 (recommended for code)"
                                        helperText="Higher limit for complex code generation"
                                    />
                                </Grid>
                            </Grid>
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* Test Runner Agent Configuration */}
                <Grid item xs={12}>
                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="h6" fontWeight="bold">
                                    Test Runner Agent Overrides
                                </Typography>
                                <Chip label="Optional" color="secondary" size="small" />
                            </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Alert severity="info" sx={{ mb: 3 }}>
                                Configure agent-specific settings to override global values. Leave empty to use global configuration.
                            </Alert>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Key (Override)"
                                        type={showPassword.test_runner_api_key ? 'text' : 'password'}
                                        value={config.test_runner.api_key}
                                        onChange={(e) => handleConfigChange('test_runner', 'api_key', e.target.value)}
                                        placeholder="Leave empty to use global API key"
                                        InputProps={{
                                            endAdornment: (
                                                <IconButton
                                                    onClick={() => togglePasswordVisibility('test_runner_api_key')}
                                                    edge="end"
                                                >
                                                    {showPassword.test_runner_api_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                </IconButton>
                                            ),
                                        }}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Endpoint (Override)"
                                        value={config.test_runner.endpoint}
                                        onChange={(e) => handleConfigChange('test_runner', 'endpoint', e.target.value)}
                                        placeholder="Leave empty to use global endpoint"
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Deployment Name (Override)"
                                        value={config.test_runner.deployment_name}
                                        onChange={(e) => handleConfigChange('test_runner', 'deployment_name', e.target.value)}
                                        placeholder="Leave empty to use global deployment"
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="API Version (Override)"
                                        value={config.test_runner.api_version}
                                        onChange={(e) => handleConfigChange('test_runner', 'api_version', e.target.value)}
                                        placeholder="Leave empty to use global API version"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Model Name (Override)"
                                        value={config.test_runner.model_name}
                                        onChange={(e) => handleConfigChange('test_runner', 'model_name', e.target.value)}
                                        placeholder="Leave empty to use global model"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Temperature (Override)"
                                        type="number"
                                        inputProps={{ min: 0, max: 2, step: 0.1 }}
                                        value={config.test_runner.temperature || ''}
                                        onChange={(e) => handleConfigChange('test_runner', 'temperature', e.target.value ? parseFloat(e.target.value) : null)}
                                        placeholder="0.3 (recommended for testing)"
                                        helperText="Lower temperature for more deterministic testing"
                                    />
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        label="Max Tokens (Override)"
                                        type="number"
                                        inputProps={{ min: 1, max: 32000 }}
                                        value={config.test_runner.max_tokens || ''}
                                        onChange={(e) => handleConfigChange('test_runner', 'max_tokens', e.target.value ? parseInt(e.target.value) : null)}
                                        placeholder="8000 (recommended for testing)"
                                        helperText="Adequate for test analysis and reporting"
                                    />
                                </Grid>
                            </Grid>
                        </AccordionDetails>
                    </Accordion>
                </Grid>
            </Grid>

            {/* Test Results Dialog */}
            <Dialog open={testDialog.open} onClose={() => setTestDialog({ open: false, result: null })} maxWidth="md" fullWidth>
                <DialogTitle>Configuration Test Results</DialogTitle>
                <DialogContent>
                    {testDialog.result && (
                        <Box sx={{ mt: 2 }}>
                            <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                        {testDialog.result.azure_openai ? (
                                            <CheckCircleIcon color="success" />
                                        ) : (
                                            <ErrorIcon color="error" />
                                        )}
                                        <Typography variant="h6">
                                            Azure OpenAI: {testDialog.result.azure_openai ? 'Connected' : 'Failed'}
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                        {testDialog.result.langsmith === null ? (
                                            <WarningIcon color="warning" />
                                        ) : testDialog.result.langsmith ? (
                                            <CheckCircleIcon color="success" />
                                        ) : (
                                            <ErrorIcon color="error" />
                                        )}
                                        <Typography variant="h6">
                                            LangSmith: {testDialog.result.langsmith === null ? 'Disabled' : testDialog.result.langsmith ? 'Connected' : 'Failed'}
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                            {testDialog.result.errors && testDialog.result.errors.length > 0 && (
                                <Box sx={{ mt: 3 }}>
                                    <Typography variant="h6" color="error" gutterBottom>
                                        Errors:
                                    </Typography>
                                    {testDialog.result.errors.map((error, index) => (
                                        <Alert key={index} severity="error" sx={{ mb: 1 }}>
                                            {error}
                                        </Alert>
                                    ))}
                                </Box>
                            )}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setTestDialog({ open: false, result: null })}>
                        Close
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar for notifications */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
            >
                <Alert severity={snackbar.severity} onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default Configuration;
