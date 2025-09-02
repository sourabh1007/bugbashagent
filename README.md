# 🤖 Bug Bash Agent - Advanced AI Code Generation System

[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-LangChain-green.svg)](https://langchain.com)
[![AI](https://img.shields.io/badge/AI-Azure%20OpenAI-orange.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

The **Bug Bash Agent** is an advanced AI-powered code generation system that transforms business requirements into comprehensive, production-ready test code across multiple programming languages. It uses a sophisticated multi-agent workflow with intelligent compilation feedback, selective scenario regeneration, and comprehensive error handling.

### 🎯 Key Features

- ✅ **Multi-Language Support**: C#, Python, JavaScript, Java, Go, Rust
- ✅ **Intelligent Scenario Generation**: 15-25+ comprehensive test scenarios per project
- ✅ **Selective Retry System**: Only regenerates failed scenarios, preserving working code
- ✅ **Advanced Error Handling**: Language-specific compilation error parsing and fixing
- ✅ **Comprehensive Reporting**: Detailed analysis of all attempts, errors, and fixes
- ✅ **Prompt Logging**: Complete audit trail of all LLM interactions
- ✅ **External Prompt Management**: Prompty file system with YAML metadata
- ✅ **Organized Tool Architecture**: Categorized tool structure for maintainability
- ✅ **SDK-Specific Optimization**: Tailored for major SDKs and frameworks

## 🏗️ System Architecture

### 🔄 Multi-Agent Workflow

The system uses a sophisticated 2-agent workflow:

1. **📊 Document Analyzer Agent** → 2. **🛠️ Code Generator Agent**

With intelligent feedback loops for compilation error handling and selective scenario regeneration.

### 🔧 Recent Refactoring (v2.0)

The project has undergone major architectural improvements:

#### External Prompt Management
- **Prompty Files**: All LLM prompts moved to `.prompty` files with YAML metadata
- **Dynamic Variables**: Template variables replaced at runtime using PromptyLoader
- **Version Control**: Prompts now versioned and maintainable separately from code

#### Organized Tool Architecture
- **tools/compilation/**: Compilation and error checking utilities
- **tools/file_management/**: File creation and management tools  
- **tools/parsing/**: Code parsing and analysis tools
- **tools/project_generators/**: Language-specific project generators
- **tools/prompt_loader/**: Prompty file loading and processing utilities

#### Enhanced Error Handling
- **Selective Retry**: Only failed scenarios are regenerated, preserving working code
- **Error Context**: Compilation errors passed to LLM with specific fix suggestions
- **Comprehensive Reporting**: Detailed analysis of all attempts, errors, and fixes

### 🧠 Agent Responsibilities

1. **📊 Document Analyzer Agent**
   - Analyzes business requirements and documentation
   - Extracts structured information and scenarios
   - Generates 15-25+ comprehensive test scenarios
   - Prevents duplicate scenarios with advanced detection

2. **🛠️ Code Generator Agent**
   - Generates compilation-error-free code for each scenario
   - Implements selective retry system for failed scenarios
   - Provides detailed error context to LLM for targeted fixes
   - Creates comprehensive reports with attempt-by-attempt analysis

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Azure OpenAI account with API access
- Git (for cloning the repository)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/sourabh1007/bugbashagent.git
cd bugbashagent

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configuration

Edit the `.env` file with your Azure OpenAI credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Model Configuration (Optional)
MODEL_NAME=gpt-4-turbo  # Recommended for best results
TEMPERATURE=0.7
```

### 4. Run the Application

```bash
# Interactive mode
python main.py

# File input mode
python run_with_file.py
```

## 🎛️ Usage Examples

### Interactive Mode

```bash
python main.py
```

Choose from:
1. **Direct Text Input**: Paste requirements directly
2. **File Input**: Provide local file path
3. **URL Input**: Analyze documentation from web URLs

### File Input Mode

```bash
python run_with_file.py path/to/your/requirements.txt
```

### Sample Input Formats

The system accepts various input formats:
- **API Documentation**: REST API specs, SDK documentation
- **Requirements Documents**: Business requirements, user stories
- **Technical Specifications**: Architecture docs, integration guides
- **GitHub README files**: Project documentation from repositories

## 📁 Project Structure

```
bugbashagent/
├── 📁 agents/                          # Core agent implementations
│   ├── 📄 document_analyzer.py         # Document analysis & scenario generation
│   ├── 📄 code_generator.py            # Advanced code generation with error handling
│   └── 📄 base_agent.py               # Base agent class with prompt logging
├── 📁 config_package/                  # Configuration management
│   ├── 📄 __init__.py                 # Main configuration settings
│   └── 📄 package_versions.py         # SDK version management
├── 📁 factories/                       # Prompt generation factories
│   └── 📄 prompt_factory.py           # Language-specific prompt strategies
├── 📁 patterns/                        # Language configuration patterns
│   ├── 📄 language_config.py          # Language-specific configurations
│   └── 📁 languages/                  # Individual language configs
├── 📁 strategies/                      # Advanced prompt strategies
│   ├── 📄 prompt_strategies.py        # Core prompt generation strategies
│   └── 📁 languages/                  # Language-specific strategies
├── 📁 tools/                          # Code generation utilities
│   └── 📁 code_generator/             # Advanced code generation tools
├── 📁 workflow_outputs/               # Generated outputs (timestamped folders)
├── 📄 main.py                         # Main application entry point
├── 📄 run_with_file.py               # File-based input runner
├── 📄 workflow.py                     # Multi-agent workflow orchestration
├── 📄 requirements.txt                # Python dependencies
└── 📄 README.md                       # This file
```

## 🔧 Advanced Features

### 🎯 Selective Scenario Regeneration

The system intelligently identifies failed scenarios and only regenerates those, preserving working code:

```python
# Automatically identifies scenarios with compilation errors
failed_scenarios = self._identify_scenarios_with_compilation_errors(
    compilation_result, scenarios
)

# Only regenerates failed scenarios with error context
enhanced_scenarios = self._regenerate_only_failed_scenarios(
    failed_scenarios, compilation_result, language, product_name, version, setup_info, analysis_data
)
```

### 📊 Comprehensive Error Analysis

Language-specific error parsing with targeted fix suggestions:

- **C# Errors**: NuGet packages, namespace issues, async/await patterns
- **Python Errors**: Import issues, syntax errors, type hints
- **JavaScript Errors**: Module resolution, async/promise patterns
- **Java Errors**: Package imports, annotation issues, generics

### 📝 Complete Prompt Logging

Every LLM interaction is logged with full context:

```
workflow_outputs/
└── workflow_output_YYYYMMDD_HHMMSS/
    ├── prompts/
    │   ├── TIMESTAMP_document_analyzer_document_analysis.txt
    │   ├── TIMESTAMP_code_generator_scenario_generation_scenario_1.txt
    │   └── TIMESTAMP_code_generator_error_fix_regeneration_scenario_X.txt
    └── [other outputs]
```

### 📈 Detailed Reporting

Multiple levels of reporting for complete transparency:

1. **Executive Summary**: High-level success metrics and statistics
2. **Attempt-by-Attempt Analysis**: Detailed breakdown of each compilation attempt
3. **Error Progress Tracking**: How errors were addressed between attempts
4. **Final Recommendations**: Actionable next steps and improvements

## 🛠️ Supported Languages & Frameworks

### Programming Languages
- **C#**: .NET Core, .NET Framework, Azure SDKs
- **Python**: pytest, asyncio, popular libraries
- **JavaScript/TypeScript**: Jest, Node.js, React
- **Java**: JUnit 5, Spring Framework, Maven/Gradle
- **Go**: Built-in testing, popular frameworks
- **Rust**: Built-in test framework, Cargo

### Popular SDKs & Libraries
- **Azure SDKs**: Cosmos DB, Storage, Service Bus
- **AWS SDKs**: S3, DynamoDB, Lambda
- **Google Cloud**: Firestore, Cloud Storage
- **Database Libraries**: Entity Framework, SQLAlchemy
- **API Frameworks**: Express.js, FastAPI, Spring Boot

## 📊 Output Structure

### Workflow Outputs

Each run creates a timestamped folder with complete outputs:

```
workflow_output_YYYYMMDD_HHMMSS/
├── 📄 00_workflow_summary.txt           # Complete workflow summary
├── 📄 step_01_document_analyzer.txt     # Document analysis results
├── 📄 step_02_code_generator.txt        # Code generation results
├── 📄 COMPREHENSIVE_CODE_GENERATION_REPORT.md  # Detailed analysis report
├── 📁 prompts/                          # All LLM prompts with context
│   ├── 📄 TIMESTAMP_document_analyzer_document_analysis.txt
│   ├── 📄 TIMESTAMP_code_generator_scenario_generation_scenario_1.txt
│   └── 📄 [additional prompt files]
└── 📁 [project_name]/                   # Generated code project
    ├── 📄 [TestClass1].cs              # Individual test files
    ├── 📄 [TestClass2].cs
    ├── 📄 [Project].csproj             # Project file
    └── 📄 CONSOLIDATED_IMPLEMENTATION.md
```

### Code Generation Features

- **Compilation-Error-Free**: Prioritizes working code over feature completeness
- **Comprehensive Test Coverage**: Multiple test methods per scenario
- **Proper Error Handling**: Language-appropriate exception handling
- **Resource Management**: Proper cleanup using language idioms
- **Documentation**: Clear comments explaining test logic

## ⚙️ Configuration Options

### Model Selection

Choose the appropriate model for your needs:

```env
# For basic scenarios (4K tokens)
MODEL_NAME=gpt-35-turbo

# For complex scenarios (8K tokens) 
MODEL_NAME=gpt-4

# For comprehensive scenarios (128K tokens) - Recommended
MODEL_NAME=gpt-4-turbo
MODEL_NAME=gpt-4o
```

### Language-Specific Settings

Configure language-specific behavior in `config_package/package_versions.py`.

## 🔍 Troubleshooting

### Common Issues

1. **Token Limit Exceeded**
   ```
   Solution: Upgrade to GPT-4-turbo or GPT-4o for higher token limits
   ```

2. **Compilation Errors Persist**
   ```
   Solution: Check the comprehensive report for specific error patterns
   Review the prompt logs to ensure error context is being passed correctly
   ```

3. **No Code Generated**
   ```
   Solution: Verify Azure OpenAI configuration in .env file
   Check network connectivity and API key permissions
   ```

### Debug Mode

Enable detailed logging by setting environment variables:

```env
DEBUG=true
VERBOSE_LOGGING=true
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Add comprehensive docstrings to all functions and classes
- Write unit tests for new features
- Update documentation for any API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Open an issue on GitHub for bug reports or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support

## 🙏 Acknowledgments

- **LangChain**: For the powerful agent framework
- **Azure OpenAI**: For providing advanced language models
- **Open Source Community**: For inspiration and best practices

---

**Built with ❤️ using LangChain and Azure OpenAI**
