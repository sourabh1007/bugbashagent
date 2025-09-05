# 🤖 Bug Bash Agent - Advanced AI Code Generation System

[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-LangChain-green.svg)](https://langchain.com)
[![AI](https://img.shields.io/badge/AI-Azure%20OpenAI-orange.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

The **Bug Bash Agent** is an advanced AI-powered code generation system that transforms business requirements into comprehensive, production-ready test code across multiple programming languages. It uses a sophisticated **3-agent workflow** with intelligent compilation feedback, selective scenario regeneration, comprehensive test execution, and detailed analysis reporting.

### 🎯 Key Features

- ✅ **Multi-Language Support**: C#, Python, JavaScript, TypeScript, Java, Go, Rust (complete end-to-end)
- ✅ **Intelligent Scenario Generation**: 15-25+ comprehensive test scenarios per project
- ✅ **Selective Retry System**: Only regenerates failed scenarios, preserving working code
- ✅ **Advanced Error Handling**: Language-specific compilation error parsing and fixing
- ✅ **Comprehensive Test Runner**: Automated test execution with AI-powered analysis
- ✅ **Detailed Reporting**: Multi-level analysis of generation, compilation, and test results
- ✅ **Prompt Logging**: Complete audit trail of all LLM interactions
- ✅ **External Prompt Management**: Prompty file system with YAML metadata
- ✅ **Organized Tool Architecture**: Categorized tool structure for maintainability
- ✅ **SDK-Specific Optimization**: Tailored for major SDKs and frameworks
- ✅ **LangSmith Integration**: Advanced monitoring, tracing, and observability

## 🏗️ System Architecture

### 🔄 Multi-Agent Workflow

**Complete 3-Agent Pipeline:**

1. **📊 Document Analyzer Agent** → 2. **🛠️ Code Generator Agent** → 3. **🧪 Test Runner Agent**

Each agent specializes in a specific aspect of the development lifecycle:

#### 📊 Document Analyzer Agent
- Extracts and structures business requirements into test scenarios
- Removes duplicates and categorizes scenarios by complexity
- Provides structured input for code generation

#### 🛠️ Code Generator Agent  
- Generates complete, compilable code projects
- Performs selective regeneration for failed scenarios
- Handles compilation feedback and error correction
- Creates comprehensive project structures with proper dependencies

#### 🧪 Test Runner Agent
- Executes tests on generated code across all supported languages
- Performs AI-powered analysis of test results and failures
- Generates detailed reports with insights and recommendations
- Provides quality scoring and improvement suggestions

### 🔧 Architecture Features

#### External Prompt Management

- **Prompty Files**: All prompts are `.prompty` files with YAML metadata
- **Unified Language Guidance**: `language_guidelines` replaces separate best-practices + compilation checklist prompts (each best-practice file embeds a concise checklist)
- **Dynamic Variables**: Runtime substitution via `PromptyLoader`
- **Version Control**: Prompts versioned separately from code

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

1. **📊 Document Analyzer** – Extracts, deduplicates, and structures scenarios from business requirements
2. **🛠️ Code Generator** – Generates code with selective regeneration for failed scenarios and compilation validation
3. **🧪 Test Runner** – Executes tests, analyzes results with AI, and produces comprehensive quality reports

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
cp .env.template .env
```

### 3. Configuration

Edit the `.env` file with your Azure OpenAI credentials:

```env
# Azure OpenAI Configuration (Required)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here

# LangSmith Configuration (Optional - for monitoring)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=BugBashAgent
```

### 4. LangSmith Integration (Optional)

For advanced monitoring, tracing, and observability, integrate with LangSmith:

1. **Sign up** at [LangSmith](https://smith.langchain.com/)
2. **Create an API key** in your LangSmith dashboard
3. **Set environment variables** in your `.env` file:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=BugBashAgent
```

4. **Monitor your runs** at the [LangSmith Dashboard](https://smith.langchain.com/projects)

**LangSmith Features:**

- 📊 Real-time workflow monitoring
- 🔍 Detailed agent execution traces
- 📈 Performance metrics and analytics  
- 🐛 Error tracking and debugging
- 💾 Complete prompt and response logging
- 📋 Workflow success/failure analytics

**LangSmith Setup:**

1. Sign up at [LangSmith](https://smith.langchain.com/)
2. Create an API key in your dashboard
3. Run the setup script: `python setup_langsmith.py`
4. Add your API key to the `.env` file
5. View traces at [LangSmith Dashboard](https://smith.langchain.com/projects)

### 4. Run the Application

```bash
python main.py
```

## 🎛️ Usage Examples

Choose from:

1. **Direct Text Input**: Paste requirements directly
2. **File Input**: Provide local file path  
3. **URL Input**: Analyze documentation from web URLs

### Sample Input Formats

The system accepts various input formats:

- **API Documentation**: REST API specs, SDK documentation
- **Requirements Documents**: Business requirements, user stories
- **Technical Specifications**: Architecture docs, integration guides
- **GitHub README files**: Project documentation from repositories

## 📁 Project Structure (Simplified)

```text
bugbashagent/
├── agents/                # document_analyzer, code_generator, base_agent
├── config_package/        # global config & package versions
├── factories/             # prompt strategy factory
├── integrations/          # azure_openai, langsmith, web, file_processing
├── patterns/              # language configs
├── prompts/               # scenario, error-fix, language & product guidance prompty files
├── strategies/            # advanced prompt strategies
├── tools/                 # parsing, compilation, project generation, best practices manager
├── workflow_outputs/      # run artifacts
├── workflow.py            # workflow orchestration
├── main.py                # CLI entrypoint
├── requirements.txt
└── README.md
```text

Removed legacy: standalone compilation checklist prompty files, temp/backup LangSmith integration modules, secondary integrations README.

### 🔧 Unified Language Guidelines

Use `language_guidelines` for each scenario or regeneration request. It merges best practices + a concise compilation checklist per language to reduce duplication and token usage.

## 🔧 Advanced Features (Selected)

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

```text
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

## 🔍 Troubleshooting & Recent Maintenance

Recent cleanup (2025-09-04):

- Unified language guidance (`language_guidelines`)
- Removed deprecated compilation checklist prompts
- Deleted backup/temporary LangSmith integration modules
- Consolidated markdown into this single README
- Clarified active 2-agent workflow

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

## 🚀 Built with ❤️ using LangChain and Azure OpenAI

_README updated post-cleanup (2025-09-04)_
