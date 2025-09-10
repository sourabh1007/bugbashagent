# 🤖 Bug Bash Agent - AI-Powered Multi-Language Code Generation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-Enabled-orange.svg)](https://azure.microsoft.com/services/cognitive-services/openai-service/)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-purple.svg)](https://smith.langchain.com)

## 📋 Project Introduction

Bug Bash Agent is an intelligent **multi-agent AI system** that automates the complete software development lifecycle from requirements analysis to code generation, compilation, and testing. Built with LangChain and Azure OpenAI, it supports **7 programming languages** and delivers production-ready code with comprehensive error handling and compilation feedback.

### 🎯 Core Capabilities

- **🔄 3-Agent Workflow**: Document Analyzer → Code Generator → Test Runner (orchestrated by `workflow.py`)
- **🌍 Multi-Language Support**: TypeScript, JavaScript, Python, C#, Java, Go, Rust  
- **🔧 Smart Compilation Loop**: Iterative build attempts, categorized error analysis, selective regeneration
- **🧪 Automated Testing**: Test discovery + execution + LLM-driven analysis with dual reports (`test_report.md`, `test_report_ui.md`)
- **🧠 LLM Quality Insights**: Structured scoring + root cause detection (environment vs logic)
- **📊 Monitoring & Tracing**: LangSmith integration (optional) for chain/token diagnostics
- **🎨 Project Scaffolding**: Language-aware generators with best practices baked in
- **♻️ Resilient Recovery**: Non-blocking agent failures, graceful degradation & validation issue tracking
- **🧾 UI-Friendly Reporting**: Streamlit app renders consolidated workflow + test summaries

## 🏗️ System Architecture (Updated)

```
                        ┌─── INPUT ────┐
                        │ Requirements │
                        │ Documents    │
                        │ Specifications│
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │ 📄 Document  │ 
                        │   Analyzer   │ ──── Language Detection
                        │              │ ──── Scenario Extraction  
                        │              │ ──── Setup Analysis
                        └──────┬───────┘
                               │ JSON Output
                        ┌──────▼───────┐
                        │ 🔨 Code      │
                        │  Generator   │ ──── Multi-Language Support
                        │              │ ──── Compilation Feedback Loop
                        │              │ ──── Selective Regeneration
                        └──────┬───────┘
                               │ Generated Code
                        ┌──────▼───────┐
                        │ 🧪 Test      │
                        │   Runner     │ ──── Test Discovery & Execution
                        │              │ ──── LLM Failure Clustering
                        │              │ ──── Dual Report Generation (Raw/UI)
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │   OUTPUT     │
                        │ Complete     │
                        │ Project      │
                        └──────────────┘
```

### 🔧 Agent Responsibilities

| Agent | Core Function | Key Outputs | Technologies |
|-------|---------------|-------------|--------------|
| **📄 Document Analyzer** | Parse requirements, extract scenarios, detect language | Structured JSON, scenarios list, setup instructions | LangChain, Azure OpenAI, PromptyLoader |
| **🔨 Code Generator** | Generate code, compile, fix errors, create projects | Source code, build files, compilation reports | Language-specific compilers, project generators, selective regeneration |
| **🧪 Test Runner** | Discover & run tests, analyze failures, generate dual reports | Raw + UI reports, quality score (0-100), root cause detection | NUnit / pytest / Jest / cargo / go test, LLM analysis |

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Azure OpenAI subscription** with API access
- **Node.js 16+** (for TypeScript/JavaScript projects)
- **Language-specific toolchains** (optional, for compilation)

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/sourabh1007/bugbashagent.git
   cd bugbashagent
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   
   Copy the template and configure:
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your_gpt4_deployment_name
   
   # Model Configuration  
   MODEL_NAME=gpt-4
   TEMPERATURE=0.3
   
   # LangSmith Tracing (Optional)
   LANGCHAIN_API_KEY=your_langsmith_api_key
   LANGCHAIN_PROJECT=BugBashAgent
   LANGCHAIN_TRACING_V2=true
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## 💻 Usage

### Interactive Mode

```bash
python main.py
```

Choose from 3 input options:

1. **📝 Direct Text Input**: Enter requirements directly
2. **📄 File Upload**: Upload requirements document (.txt, .pdf, .docx)  
3. **🌐 URL Input**: Provide URL to online requirements

### Example Workflow

```bash
🤖 LangChain Multi-Agent Code Development Workflow
==================================================

Choose input method:
1. Enter text directly
2. Provide local file path  
3. Provide URL (if supported)

Enter your choice (1/2/3): 1

📝 Enter your requirements:
Create a TypeScript REST API for user management with CRUD operations, 
authentication, and database integration using MongoDB.

🔄 Processing with 3-agent workflow...
✅ Document analysis complete
✅ Code generation with compilation feedback complete  
✅ Test execution and reporting complete

📁 Output saved to: workflow_outputs/user_management_api_20250906_143022/
```

## 🌍 Supported Languages

### Fully Supported Languages

| Language | Version | Build Tool | Test Framework | Compilation | Project Generation |
|----------|---------|------------|----------------|-------------|-------------------|
| **TypeScript** | 5.0+ | npm/yarn | Jest + ts-jest | `npx tsc` | ✅ Complete |
| **JavaScript** | ES2020+ | npm/yarn | Jest | Node.js | ✅ Complete |
| **Python** | 3.8+ | pip | pytest | py_compile | ✅ Complete |
| **C#** | .NET 6+ | dotnet | xUnit/NUnit | `dotnet build` | ✅ Complete |
| **Java** | 11+ | Maven/Gradle | JUnit 5 | `mvn compile` | ✅ Complete |
| **Go** | 1.19+ | go mod | go test | `go build` | ✅ Complete |
| **Rust** | 1.70+ | Cargo | cargo test | `cargo build` | ✅ Complete |

### Language-Specific Features

#### TypeScript
- **Advanced Features**: Full type safety, interfaces, generics, decorators
- **Frameworks**: Node.js, Express, NestJS patterns
- **Testing**: Jest with TypeScript integration, comprehensive type testing
- **Build**: Strict TypeScript compiler with real-time error analysis

#### Python  
- **Modern Python**: Type hints, async/await, dataclasses, context managers
- **Frameworks**: FastAPI, Flask, Django patterns with dependency injection
- **Testing**: pytest with fixtures, parametrized tests, coverage analysis
- **Packaging**: requirements.txt, setup.py, modern project structure

#### C#
- **Enterprise Ready**: .NET 6+, dependency injection, Entity Framework
- **Patterns**: Clean Architecture, SOLID principles, async/await
- **Testing**: xUnit, NUnit, MSTest with mocking and integration tests
- **Build**: Full MSBuild integration with NuGet package management

#### Java
- **Enterprise Java**: Spring Boot, Spring Data, JPA/Hibernate patterns
- **Modern Features**: Java 11+ features, streams, lambda expressions
- **Testing**: JUnit 5, Mockito, TestContainers for integration testing
- **Build**: Maven with multi-module support and dependency management

#### Go
- **Idiomatic Go**: Goroutines, channels, interfaces, error handling
- **Frameworks**: Gin, Echo, standard library patterns
- **Testing**: Native testing with benchmarks, examples, race detection
- **Build**: Go modules with vendoring and cross-compilation

#### Rust
- **Systems Programming**: Ownership, borrowing, zero-cost abstractions
- **Async**: Tokio, async/await, concurrent programming patterns
- **Testing**: Cargo test with unit, integration, and doc tests
- **Build**: Cargo with workspace management and feature flags

## 📁 Project Structure (High-Level)

```
bugbashagent/
├── agents/                    # Core AI agents
│   ├── base_agent.py         # Base agent interface
│   ├── document_analyzer.py  # Requirements analysis agent
│   ├── code_generator.py     # Code generation agent
│   └── test_runner.py        # Test execution agent
├── integrations/             # External service integrations
│   ├── azure_openai/        # Azure OpenAI client setup
│   ├── langsmith/           # LangSmith tracing integration
│   └── file_processing/     # Document processing utilities
├── patterns/                # Language configuration patterns
│   └── languages/          # Language-specific configurations
├── tools/                   # Utility tools and generators
│   ├── compilation/        # Code compilation and error analysis
│   ├── project_generators/ # Language-specific project scaffolding
│   ├── parsing/           # Content and structure parsing
│   └── file_management/   # File creation and management
├── prompts/               # AI prompt templates (loaded via Prompty loader)
│   ├── code_generator/   # Code generation prompts
│   ├── document_analyzer/# Analysis prompts  
│   └── test_runner/     # Testing prompts
├── strategies/           # Prompt generation strategies
│   └── languages/       # Language-specific prompt strategies
├── config_package/      # Configuration and version management
├── factories/          # Factory patterns for prompt generation
├── workflow_outputs/   # Generated project outputs & test artifacts
├── streamlit_app.py    # Rich UI for running & inspecting workflows
├── ui_preview.py       # Static styling preview (design reference)
├── main.py            # CLI application entry point
├── workflow.py        # Multi-agent workflow orchestrator
├── UI_ENHANCEMENT_SUMMARY.md  # UI improvement documentation
└── requirements.txt   # Python dependencies
```

## 🔄 Workflow Process (Execution Model)

### 1. Document Analysis Phase
- **Input Processing**: Supports text, file uploads (.txt, .pdf, .docx), and URLs
- **Content Extraction**: Advanced parsing of requirements and specifications
- **Language Detection**: Automatic identification of target programming language
- **Scenario Generation**: Creation of comprehensive test scenarios with categorization
- **Setup Analysis**: Extraction of dependencies, build requirements, and configuration

### 2. Code Generation Phase
- **Project Scaffolding**: Complete project structure with language-specific conventions
- **Smart Code Generation**: Production-ready code with best practices and patterns
- **Compilation Feedback Loop**: Real-time compilation with error detection and auto-fixing
- **Selective Regeneration**: Only regenerates code sections with compilation errors
- **Multi-Attempt Strategy**: Up to 3 compilation attempts with progressive error fixing

### 3. Test Execution & Analysis Phase
- **Discovery**: Pattern-based file + framework inference
- **Execution**: Language dispatcher (e.g., `dotnet test`, `pytest`, `go test`)
- **Resilience**: Always returns structured summary even on failures
- **LLM Analysis**: Generates comprehensive + UI-focused reports
- **Root Cause Heuristics**: Detects common infra issues (e.g., connection refused)
- **Artifacts**: `test_results.json`, `test_report.md`, `test_report_ui.md`

## 📊 Output Structure & Generated Reports

Each workflow run creates a timestamped project directory:

```
workflow_outputs/project_name_YYYYMMDD_HHMMSS/
├── step_01_document_analyzer.txt     # Analysis results and scenarios
├── step_02_code_generator.txt        # Generation details and compilation reports
├── step_03_test_runner.txt           # Test execution results and coverage
└── generated_code/                   # Complete project structure
    ├── src/                          # Source code files
    │   ├── main.ts                   # Main application entry point
    │   ├── models/                   # Data models and types
    │   ├── services/                 # Business logic services
    │   └── utils/                    # Utility functions
    ├── tests/                        # Test files
    │   ├── unit/                     # Unit tests
    │   ├── integration/              # Integration tests
    │   └── fixtures/                 # Test data and fixtures
    ├── package.json                  # Dependencies (Node.js)
    ├── tsconfig.json                 # TypeScript configuration
    ├── jest.config.js                # Test configuration
    ├── .gitignore                    # Git ignore rules
    └── README.md                     # Project documentation
```

## 🛠️ Advanced Features

### Compilation Feedback Loop
- **Real-time Error Detection**: Immediate compilation after code generation
- **Intelligent Error Analysis**: Categorization of syntax, type, and logic errors
- **Selective Regeneration**: Only regenerates failing code sections
- **Progressive Fixing**: Multiple attempts with increasingly specific error context

### Multi-Language Project Generation
- **Language-Specific Scaffolding**: Proper project structure for each language
- **Dependency Management**: Automatic package and dependency configuration
- **Build System Integration**: Native build tool configuration (npm, pip, dotnet, etc.)
- **Testing Framework Setup**: Complete testing environment configuration

### Advanced Monitoring
- **LangSmith Integration**: Complete workflow tracing and performance monitoring
- **Detailed Logging**: Comprehensive logs for debugging and optimization
- **Error Tracking**: Full error context preservation and analysis
- **Performance Metrics**: Response times, token usage, and success rates

## 🔍 Troubleshooting & Quality Signals

### Common Issues

1. **Azure OpenAI Connection**
   ```bash
   # Check your .env configuration
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   ```

2. **Compilation Errors**
   ```bash
   # Check language-specific tools installation
   npm --version    # For TypeScript/JavaScript
   python --version # For Python
   dotnet --version # For C#
   ```

3. **Permission Issues**
   ```bash
   # Ensure write permissions for workflow_outputs/
   chmod 755 workflow_outputs/
   ```

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export LANGCHAIN_VERBOSE=true
python main.py
```

## 🧹 Repository Maintenance & Cleanup

Recent cleanup completed:
- **Removed 6 empty placeholder files**: `demo_ui.py`, `demo_test_reports.py`, `launch_ui.py`, `launch_ui.bat`, `UI_README.md`, `verify_scenario_logic.py`
- **Cleaned unused imports**: Removed `LanguageBestPracticesManager` and `LanguageConfig` from test_runner, `trace_agent_execution` from base_agent
- **Eliminated unused variables**: Removed `workflow_history` from AgentWorkflow class
- **Enhanced UI test report generator**: Quality score normalization (0-100), root cause detection, improved messaging
- **Streamlined architecture documentation**: Updated README to reflect current execution model and file structure
- **Project size optimization**: Reduced from 99 to 93 files (excluding .venv/.git)

### Static Analysis Tools

For ongoing maintenance, use:
```bash
pip install vulture
vulture . --min-confidence 70  # Detect unused code
```

## 🤝 Contributing

1. **Fork the Repository**
   ```bash
   git fork https://github.com/sourabh1007/bugbashagent.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-language-support
   ```

3. **Make Changes and Test**
   ```bash
   # Add new language support
   # Update documentation
   # Run comprehensive tests
   ```

4. **Submit Pull Request**
   - Detailed description of changes
   - Test results and validation
   - Updated documentation

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode with tracing
export LANGCHAIN_TRACING_V2=true
python main.py
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Resources

- **📋 Issues**: [GitHub Issues](https://github.com/sourabh1007/bugbashagent/issues)
- **📖 Documentation**: This README and inline code documentation
- **🔍 Monitoring**: [LangSmith Dashboard](https://smith.langchain.com) for workflow tracing
- **💬 Discussions**: [GitHub Discussions](https://github.com/sourabh1007/bugbashagent/discussions)

---

**🚀 Built with ❤️ using LangChain, Azure OpenAI, and modern AI engineering practices**

*Transform requirements into production-ready code across 7 programming languages with intelligent compilation feedback, resilient execution, and LLM-enhanced quality insights.*
| **📄 Document Analyzer** | Analyze requirements and extract structured information | JSON with scenarios, language detection, setup instructions |
| **🔨 Code Generator** | Generate complete projects with compilation validation | Source code, build files, project structure, compilation reports |
| **🧪 Test Runner** | Execute tests and generate comprehensive reports | Test results, coverage analysis, execution summaries |

## 🚀 Setup

### Prerequisites

- **Python 3.8+**
- **Azure OpenAI** subscription and API key
- **Node.js** (for TypeScript/JavaScript projects)
- **Language-specific tools** (optional, based on target languages)

### 1. Clone Repository

```bash
git clone https://github.com/sourabh1007/bugbashagent.git
cd bugbashagent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file from template:

```bash
cp .env.template .env
```

Configure your `.env` file:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# Model Configuration
MODEL_NAME=gpt-4
TEMPERATURE=0.3

# LangSmith Tracing (Optional)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=BugBashAgent
LANGCHAIN_TRACING_V2=true
```

### 4. Verify Setup

```bash
python main.py
```

## 💻 Important Commands

### Basic Usage

```bash
# Start the interactive workflow
python main.py

# Run with direct text input (Option 1)
# Enter requirements directly in the prompt

# Run with file input (Option 2) 
# Provide path to requirements document (.txt, .pdf, .docx)

# Run with URL input (Option 3)
# Provide URL to online requirements document
```

### Advanced Operations

```bash
# View workflow outputs
ls workflow_outputs/

# Check latest run results
cd workflow_outputs/workflow_output_YYYYMMDD_HHMMSS/

# Validate specific language support
python -c "from patterns.language_config import LanguageConfigManager; print(LanguageConfigManager().get_supported_languages())"

# Run manual compilation test
cd workflow_outputs/latest_project/ && npm install && npm test
```

### Development Commands

```bash
# Install development dependencies for specific languages

# TypeScript/JavaScript
npm install -g typescript ts-node

# Java
# Install Maven or Gradle

# C# 
# Install .NET SDK

# Go
# Install Go toolchain

# Rust
# Install Rust toolchain via rustup
```

## 🌍 Languages Supported

### Fully Supported Languages

| Language | Version | Framework | Build Tool | Test Framework | Compilation | Status |
|----------|---------|-----------|------------|----------------|-------------|---------|
| **TypeScript** | 5.0+ | Node.js | npm/yarn | Jest | `npx tsc` | ✅ Active |
| **JavaScript** | ES2020+ | Node.js | npm/yarn | Jest | Node.js | ✅ Active |
| **Python** | 3.8+ | - | pip | pytest | py_compile | ✅ Active |
| **C#** | .NET 6+ | .NET | dotnet | xUnit/NUnit | dotnet build | ✅ Active |
| **Java** | 11+ | Spring/Maven | Maven/Gradle | JUnit | javac/mvn | ✅ Active |
| **Go** | 1.19+ | - | go mod | go test | go build | ✅ Active |
| **Rust** | 1.70+ | - | Cargo | cargo test | cargo build | ✅ Active |

### Language-Specific Features

#### TypeScript
- **Features**: Full type safety, interfaces, generics, decorators
- **Frameworks**: Node.js, Express, NestJS
- **Testing**: Jest with ts-jest, comprehensive type testing
- **Compilation**: Strict TypeScript compiler with `--noEmit` for validation

#### JavaScript
- **Features**: ES6+, async/await, modules, modern syntax
- **Frameworks**: Node.js, Express, React patterns
- **Testing**: Jest, comprehensive async testing
- **Compilation**: Node.js syntax validation

#### Python
- **Features**: Type hints, async/await, dataclasses, modern Python
- **Frameworks**: FastAPI, Flask, Django patterns
- **Testing**: pytest, unittest, coverage analysis
- **Compilation**: Python syntax validation and import checking

#### C#
- **Features**: .NET 6+, async/await, LINQ, dependency injection
- **Frameworks**: ASP.NET Core, Entity Framework
- **Testing**: xUnit, NUnit, MSTest
- **Compilation**: Full dotnet build with project references

#### Java
- **Features**: Java 11+, Spring patterns, streams, lambdas
- **Frameworks**: Spring Boot, Spring Data, JPA
- **Testing**: JUnit 5, Mockito, integration testing
- **Compilation**: Maven/Gradle build with dependency management

#### Go
- **Features**: Goroutines, channels, interfaces, modern Go idioms
- **Frameworks**: Gin, Echo, standard library patterns
- **Testing**: Native go test, benchmarks, examples
- **Compilation**: Go build with module support

#### Rust
- **Features**: Ownership, borrowing, traits, async/await
- **Frameworks**: Tokio, Serde, Clap patterns
- **Testing**: Cargo test, unit and integration tests
- **Compilation**: Cargo build with full dependency resolution

## 📁 Project Structure

```
bugbashagent/
├── agents/                     # Core AI agents
│   ├── document_analyzer.py    # Requirements analysis agent
│   ├── code_generator.py       # Code generation agent
│   └── test_runner.py          # Test execution agent
├── integrations/               # External service integrations
│   ├── azure_openai/          # Azure OpenAI client
│   ├── langsmith/             # LangSmith tracing
│   └── file_processing/       # Document processing
├── patterns/                   # Language configurations
│   └── languages/             # Language-specific configs
├── tools/                      # Utility tools
│   ├── compilation/           # Code compilation tools
│   ├── project_generators/    # Project scaffolding
│   └── parsing/              # Content parsing tools
├── prompts/                   # AI prompt templates
│   ├── code_generator/        # Code generation prompts
│   ├── document_analyzer/     # Analysis prompts
│   └── test_runner/          # Testing prompts
├── strategies/               # Prompt strategies
│   └── languages/           # Language-specific strategies
├── workflow_outputs/        # Generated project outputs
├── main.py                 # Application entry point
├── workflow.py            # Multi-agent workflow orchestrator
└── requirements.txt       # Python dependencies
```

## 🔄 Workflow Process

### Step 1: Document Analysis
1. **Input Processing**: Accepts text, file paths, or URLs
2. **Content Extraction**: Parses requirements and specifications
3. **Language Detection**: Automatically identifies target programming language
4. **Scenario Generation**: Creates comprehensive test scenarios
5. **Setup Analysis**: Extracts dependencies and configuration requirements

### Step 2: Code Generation
1. **Project Scaffolding**: Creates complete project structure
2. **Code Implementation**: Generates production-ready source code
3. **Build Configuration**: Sets up build files and dependencies
4. **Compilation Validation**: Real-time syntax checking and error analysis
5. **Best Practices**: Applies language-specific coding standards

### Step 3: Test Execution
1. **Test Discovery**: Identifies and categorizes generated tests
2. **Environment Setup**: Configures test execution environment
3. **Test Execution**: Runs comprehensive test suites
4. **Results Analysis**: Analyzes test outcomes and coverage
5. **Report Generation**: Creates detailed execution reports

## 📊 Output Structure

Each workflow run creates a timestamped output directory:

```
workflow_outputs/workflow_output_YYYYMMDD_HHMMSS/
├── step_01_document_analyzer.txt    # Analysis results
├── step_02_code_generator.txt       # Generation details  
├── step_03_test_runner.txt          # Test execution results
└── generated_code/                  # Complete project
    ├── src/                        # Source files
    ├── tests/                      # Test files
    ├── package.json               # Dependencies (Node.js)
    ├── tsconfig.json              # TypeScript config
    ├── requirements.txt           # Python dependencies
    └── README.md                  # Project documentation
```

## 🔍 Monitoring & Tracing

### LangSmith Integration
- **Workflow Tracing**: Complete agent execution tracking
- **Performance Monitoring**: Response times and token usage
- **Error Analysis**: Detailed failure investigation
- **Dashboard Access**: Real-time workflow visualization

### Local Monitoring
- **File Outputs**: Detailed logs for each agent step
- **Compilation Reports**: Real-time build status and errors
- **Test Results**: Comprehensive execution summaries
- **Debug Information**: Full context preservation for troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-language-support`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/sourabh1007/bugbashagent/issues)
- **Documentation**: This README and inline code comments
- **Tracing**: LangSmith dashboard for workflow monitoring
- **Community**: Contributing guidelines for collaboration

---

**Built with ❤️ using LangChain, Azure OpenAI, and modern AI engineering practices.**