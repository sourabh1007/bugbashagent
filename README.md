# 🤖 Bug Bash Agent - AI-Powered Multi-Agent Code Generation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-GPT--4-orange.svg)](https://azure.microsoft.com/services/cognitive-services/openai-service/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io)

> **Built with Vibe Coding** - An intuitive, AI-first development approach that transforms requirements into production-ready code through intelligent multi-agent orchestration.

## 🚀 About the Project

Bug Bash Agent is a **cutting-edge multi-agent AI system** engineered for full-stack software development lifecycle automation. Born from vibe coding principles, it seamlessly transforms natural language specifications into production-ready applications across **7 programming languages** with intelligent compilation feedback loops and comprehensive testing automation.

### ⚡ Core Features

- **🔄 3-Agent Pipeline Architecture**: Document Analyzer → Code Generator → Test Runner
- **🌍 Multi-Language Code Generation**: TypeScript, JavaScript, Python, C#, Java, Go, Rust
- **🔧 Intelligent Compilation Loop**: Real-time error detection, categorization, and selective regeneration
- **🧪 Automated Test Discovery & Execution**: Framework-agnostic testing with LLM-powered failure analysis
- **📊 Dual Reporting System**: Technical reports + UI-optimized summaries with quality scoring
- **🎨 Smart Project Scaffolding**: Language-aware project generation with best practices
- **🔍 Advanced Monitoring**: LangSmith integration for workflow tracing and performance analytics
- **⚡ Streamlit Web Interface**: Professional UI for interactive workflow management
- **♻️ Resilient Architecture**: Graceful degradation, error recovery, and non-blocking failures

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────────────────────────────────────────┐
│   USER INPUT    │    │                 MULTI-AGENT PIPELINE                 │
│                 │    │                                                      │
│ • Requirements  │    │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐ │
│ • Documents     │────┼─►│ 📄 Document │──►│ 🔨 Code     │──►│ 🧪 Test     │ │
│ • Specifications│    │  │   Analyzer  │   │  Generator  │   │   Runner    │ │
└─────────────────┘    │  │             │   │             │   │             │ │
                       │  │ • Language  │   │ • Multi-    │   │ • Discovery │ │
┌─────────────────┐    │  │   Detection │   │   Language  │   │ • Execution │ │
│    STREAMLIT    │    │  │ • Scenario  │   │   Support   │   │ • Analysis  │ │
│       UI        │◄───┼──│   Extract   │   │ • Compile   │   │ • Reporting │ │
│                 │    │  │ • Setup     │   │   Feedback  │   │ • Quality   │ │
│ • Live Monitor  │    │  │   Analysis  │   │ • Auto-Fix  │   │   Scoring   │ │
│ • Config Panel  │    │  └─────────────┘   └─────────────┘   └─────────────┘ │
│ • Results View  │    │                                                      │
└─────────────────┘    └──────────────────────────────────────────────────────┘
                                                │
                       ┌─────────────────────────▼──────────────────────────────┐
                       │                  OUTPUT ARTIFACTS                      │
                       │                                                        │
                       │ • Complete Project Structure  • Test Reports          │
                       │ • Source Code & Build Files   • Quality Analytics     │
                       │ • Documentation & README      • Execution Logs        │
                       └────────────────────────────────────────────────────────┘
```

### 🔧 Agent Responsibilities

| Agent | Primary Function | Key Outputs | Technologies |
|-------|------------------|-------------|--------------|
| **📄 Document Analyzer** | Requirements parsing, language detection, scenario extraction | Structured JSON, test scenarios, setup instructions | LangChain, Azure OpenAI GPT-4, PromptyLoader |
| **🔨 Code Generator** | Multi-language code generation, compilation validation, project scaffolding | Source code, build configurations, compilation reports | Language compilers, project generators, error analysis |
| **🧪 Test Runner** | Test discovery, execution, failure analysis, quality reporting | Test results, coverage reports, quality scores (0-100) | Framework dispatchers, LLM analysis, dual reporting |

## 📁 Project Structure & Responsibilities

```
bugbashagent/
├── 🎯 main.py                      # CLI entry point for interactive workflows
├── 🌐 streamlit_app.py            # Professional web UI with real-time monitoring
├── ⚙️ workflow.py                 # Multi-agent orchestration engine
├── 
├── 🤖 agents/                     # Core AI agents with specialized roles
│   ├── base_agent.py              # Abstract base class with callback support
│   ├── document_analyzer.py       # Requirements analysis & language detection
│   ├── code_generator.py          # Multi-language code generation & compilation
│   └── test_runner.py             # Test execution & intelligent failure analysis
├── 
├── 🔌 integrations/               # External service integrations
│   ├── azure_openai/              # Azure OpenAI client with retry logic
│   ├── langsmith/                 # LangSmith tracing & monitoring
│   ├── file_processing/           # Document parsing (PDF, DOCX, TXT)
│   └── web/                       # Web content extraction utilities
├── 
├── 🧬 patterns/                   # Language configuration & patterns
│   ├── language_config.py         # Central language configuration manager
│   └── languages/                 # Language-specific configurations
│       ├── python_config.py       # Python patterns & best practices
│       ├── typescript_config.py   # TypeScript/Node.js configurations
│       ├── csharp_config.py       # .NET & C# patterns
│       ├── java_config.py         # Java & Spring Boot configurations
│       ├── go_config.py           # Go patterns & conventions
│       └── rust_config.py         # Rust & Cargo configurations
├── 
├── 🛠️ tools/                      # Utility tools & generators
│   ├── compilation/               # Code compilation & error analysis
│   ├── project_generators/        # Language-specific project scaffolding
│   ├── parsing/                   # Content & structure parsing utilities
│   ├── file_management/           # File operations & directory management
│   └── language_best_practices_manager.py # Best practices enforcement
├── 
├── 📝 prompts/                    # AI prompt templates (Prompty format)
│   ├── code_generator/            # Code generation prompt templates
│   │   ├── scenario_generation.prompty    # Scenario-based code generation
│   │   ├── error_fix_regeneration.prompty # Compilation error fixing
│   │   └── language_best_practices/       # Language-specific prompts
│   ├── document_analyzer/         # Requirements analysis prompts
│   │   └── scenario_extraction.prompty    # Scenario extraction templates
│   └── test_runner/               # Test execution & analysis prompts
│       └── test_analysis.prompty          # Test failure analysis
├── 
├── 🎨 strategies/                 # Prompt generation strategies
│   ├── prompt_strategies.py       # Strategy pattern implementations
│   └── languages/                 # Language-specific prompt strategies
├── 
├── 🏭 factories/                  # Factory patterns for prompt generation
│   └── prompt_factory.py          # Centralized prompt generation
├── 
├── ⚙️ config_package/             # Configuration & version management
│   ├── __init__.py                # Environment variable management
│   └── package_versions.py        # Language & framework version definitions
├── 
└── 📊 workflow_outputs/           # Generated project artifacts
    └── project_name_YYYYMMDD_HHMMSS/
        ├── step_01_document_analyzer.txt
        ├── step_02_code_generator.txt
        ├── step_03_test_runner.txt
        ├── test_report.md             # Technical test report
        ├── test_report_ui.md          # UI-optimized report
        └── generated_code/            # Complete project structure
```

## 🚀 How to Run

### 🖥️ CLI Mode (Interactive Terminal)

```bash
# Clone repository
git clone https://github.com/sourabh1007/bugbashagent.git
cd bugbashagent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your Azure OpenAI credentials

# Run interactive CLI
python main.py
```

**CLI Workflow:**
```bash
🤖 LangChain Multi-Agent Code Development Workflow
==================================================

Choose input method:
1. 📝 Enter text directly
2. 📄 Provide local file path  
3. 🌐 Provide URL (if supported)

Enter your choice (1/2/3): 1

📝 Enter your requirements:
> Create a TypeScript REST API for user management with authentication

🔄 Processing with 3-agent workflow...
✅ Document analysis complete (15.2s)
✅ Code generation with compilation complete (42.7s)  
✅ Test execution and analysis complete (8.9s)

📁 Output: workflow_outputs/user_management_api_20250911_143022/
```

### 🌐 Streamlit Web UI (Professional Interface)

```bash
# Start Streamlit application
streamlit run streamlit_app.py

# Or with specific port
streamlit run streamlit_app.py --server.port 8501
```

**Streamlit Features:**
- **🎨 Professional UI**: Modern design with real-time progress tracking
- **📊 Live Monitoring**: Agent status cards with progress bars and timing
- **⚙️ Configuration Panel**: Environment variables and agent settings management
- **📁 File Upload**: Drag-and-drop document processing (PDF, DOCX, TXT)
- **📈 Analytics Dashboard**: Workflow metrics, success rates, and performance insights
- **🔍 Results Explorer**: Interactive browsing of generated code and test reports
- **⏰ Auto-refresh**: Real-time updates during workflow execution

### 🔧 Advanced Configuration Commands

```bash
# Environment setup with custom configuration
export AZURE_OPENAI_API_KEY="your_api_key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export LANGCHAIN_TRACING_V2="true"  # Enable LangSmith tracing

# Development mode with verbose logging
export LANGCHAIN_VERBOSE="true"
python main.py

# Custom temperature and model settings
export TEMPERATURE="0.3"
export MODEL_NAME="gpt-4"
python main.py

# Validate language support and configurations
python -c "
from patterns.language_config import LanguageConfigManager
manager = LanguageConfigManager()
print('Supported Languages:', manager.get_supported_languages())
print('TypeScript Config:', manager.get_language_config('typescript'))
"

# Check compilation tools availability
python -c "
from tools.compilation.compiler_registry import CompilerRegistry
registry = CompilerRegistry()
print('Available Compilers:', registry.get_available_compilers())
"

# Streamlit with custom configuration
streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0

# Production deployment with gunicorn (for Streamlit)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker streamlit_app:app
```

### 🐳 Docker Deployment (Optional)

```bash
# Build Docker image
docker build -t bugbash-agent .

# Run with environment variables
docker run -e AZURE_OPENAI_API_KEY="your_key" \
           -e AZURE_OPENAI_ENDPOINT="your_endpoint" \
           -p 8501:8501 \
           bugbash-agent

# Or with environment file
docker run --env-file .env -p 8501:8501 bugbash-agent
```

## 🌍 Supported Languages

| Language | Version | Build Tool | Test Framework | Features | Status |
|----------|---------|------------|----------------|----------|---------|
| **TypeScript** | 5.0+ | npm/yarn/pnpm | Jest + ts-jest | Full type safety, decorators, async/await | ✅ Production |
| **JavaScript** | ES2020+ | npm/yarn/pnpm | Jest | Modern ES features, Node.js patterns | ✅ Production |
| **Python** | 3.8+ | pip/poetry | pytest | Type hints, async, dataclasses | ✅ Production |
| **C#** | .NET 6+ | dotnet | xUnit/NUnit | SOLID principles, dependency injection | ✅ Production |
| **Java** | 11+ | Maven/Gradle | JUnit 5 | Spring Boot, streams, modern features | ✅ Production |
| **Go** | 1.19+ | go mod | go test | Goroutines, interfaces, idiomatic Go | ✅ Production |
| **Rust** | 1.70+ | Cargo | cargo test | Ownership, async, zero-cost abstractions | ✅ Production |

## 📊 Example Output Structure

```
workflow_outputs/ecommerce_api_20250911_143022/
├── 00_workflow_summary.txt           # Executive summary
├── step_01_document_analyzer.txt     # Requirements analysis
├── step_02_code_generator.txt        # Code generation log
├── step_03_test_runner.txt           # Test execution results
├── test_report.md                    # Technical test report
├── test_report_ui.md                 # UI-friendly summary
├── test_results.json                 # Machine-readable results
└── generated_code/                   # Complete project
    ├── src/
    │   ├── controllers/               # API controllers
    │   ├── models/                    # Data models
    │   ├── services/                  # Business logic
    │   └── utils/                     # Utility functions
    ├── tests/
    │   ├── unit/                      # Unit tests
    │   ├── integration/               # Integration tests
    │   └── e2e/                       # End-to-end tests
    ├── package.json                   # Dependencies
    ├── tsconfig.json                  # TypeScript config
    ├── jest.config.js                 # Test configuration
    ├── .gitignore                     # Git ignore rules
    ├── README.md                      # Project documentation
    └── docker-compose.yml             # Container orchestration
```

## 🔍 Advanced Features

- **🧠 Intelligent Error Recovery**: Automatic compilation error detection and fixing
- **📈 Quality Scoring**: 0-100 quality scores with detailed breakdowns
- **🔄 Selective Regeneration**: Only regenerates failing code sections
- **📊 Real-time Monitoring**: Live progress tracking and performance metrics
- **🎯 Best Practices Enforcement**: Language-specific coding standards and patterns
- **🔍 Root Cause Analysis**: Automated failure classification and troubleshooting
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Performance Optimized**: Cached CSS, efficient state management, lazy loading

## 🤝 Contributing

1. **Fork & Clone**: `git clone https://github.com/yourusername/bugbashagent.git`
2. **Create Branch**: `git checkout -b feature/new-language-support`
3. **Develop & Test**: Add your changes with comprehensive testing
4. **Submit PR**: Detailed description with examples and validation results

## 📄 License

MIT License - see [LICENSE](LICENSE) for full details.

---

**🚀 Engineered with Vibe Coding principles using LangChain, Azure OpenAI GPT-4, and Streamlit**

*Transform natural language requirements into production-ready applications across 7 programming languages with intelligent multi-agent orchestration.*
