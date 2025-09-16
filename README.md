# 🤖 Bug Bash Copilot - AI-Powered Code Quality Assessment

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-Enabled-orange.svg)](https://azure.microsoft.com/services/cognitive-services/openai-service/)

> **Built with Vibe Coding** - An intuitive, AI-first development approach that transforms requirements into production-ready code through intelligent multi-agent orchestration.

## � Overview

Bug Bash Copilot is an intelligent **AI-powered assistant** for automated software quality assessment and bug detection. It analyzes requirements, generates test scenarios, and performs comprehensive code quality evaluation before production deployment.

### 🎯 Key Features

- **🔄 3-Agent Pipeline Architecture**: Document Analyzer → Code Generator → Test Runner
- **🌍 Multi-Language Code Generation**: TypeScript, JavaScript, Python, C#, Java, Go, Rust
- **🎨 Modern Web Dashboard**: React.js interface with real-time progress tracking
- **🔧 Intelligent Compilation Loop**: Real-time error detection, categorization, and selective regeneration
- **🐛 Bug Analysis**: Detailed issue categorization with severity levels and mitigation suggestions
- **� Quality Metrics**: Production readiness assessment with actionable insights
- **⚡ Real-time Updates**: WebSocket integration for live progress monitoring
- **🧪 Automated Test Discovery & Execution**: Framework-agnostic testing with LLM-powered failure analysis
- **� Advanced Monitoring**: LangSmith integration for workflow tracing and performance analytics
- **♻️ Resilient Architecture**: Graceful degradation, error recovery, and non-blocking failures
## 🏗️ System Architecture

### Frontend (React.js)
```
┌─────────────────────────────────────────────────┐
│                React Frontend                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Input     │ │   Progress  │ │   Results   │ │
│  │  Section    │ │   Monitor   │ │  Dashboard  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │
│         │               │               │        │
│         └───────────────┼───────────────┘        │
│                    WebSocket                     │
└─────────────────────┼───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              Backend (Flask + SocketIO)          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │  Document   │ │    Code     │ │    Test     │ │
│  │  Analyzer   │ │  Generator  │ │   Runner    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │
│         │               │               │        │
│         ▼               ▼               ▼        │
│   Requirements    Generated Code   Quality Report │
│     Analysis        & Test Cases    & Bug Findings│
└─────────────────────────────────────────────────┘
```

### Multi-Agent Pipeline
1. **Document Analyzer**: Parses requirements and extracts test scenarios
2. **Code Generator**: Creates code implementations with compilation validation
3. **Test Runner**: Executes tests and generates comprehensive bug analysis reports

| Agent | Primary Function | Key Outputs | Technologies |
|-------|------------------|-------------|--------------|
| **📄 Document Analyzer** | Requirements parsing, language detection, scenario extraction | Structured JSON, test scenarios, setup instructions | LangChain, Azure OpenAI GPT-4, PromptyLoader |
| **🔨 Code Generator** | Multi-language code generation, compilation validation, project scaffolding | Source code, build configurations, compilation reports | Language compilers, project generators, error analysis |
| **🧪 Test Runner** | Test discovery, execution, failure analysis, quality reporting | Test results, coverage reports, quality scores (0-100) | Framework dispatchers, LLM analysis, dual reporting |

### Supported Languages

- **TypeScript** - Full type safety with Node.js/Express patterns
- **JavaScript** - Modern ES6+ with async/await support
- **Python** - Type hints with FastAPI/Flask frameworks
- **C#** - .NET 6+ with Entity Framework integration
- **Java** - Spring Boot with JPA/Hibernate support
- **Go** - Idiomatic Go with goroutines and channels
- **Rust** - Systems programming with Tokio async support

## 📁 Project Structure & Responsibilities

```
bugbash-copilot/
├── 🎯 main.py                      # CLI entry point for interactive workflows
├── 🌐 backend_server.py            # Flask + SocketIO backend server with WebSocket support
├── ⚙️ workflow.py                 # Multi-agent orchestration engine
├── 
├── 🤖 agents/                     # Core AI agents with specialized roles
│   ├── base_agent.py              # Abstract base class with callback support
│   ├── document_analyzer.py       # Requirements analysis & language detection
│   ├── code_generator.py          # Multi-language code generation & compilation
│   └── test_runner.py             # Test execution & intelligent failure analysis
├── 
├── 🎨 frontend/                   # React.js web interface
│   ├── public/                    # Static assets
│   ├── src/                       # React source code
│   │   ├── components/            # React components
│   │   │   ├── Header.js
│   │   │   ├── InputSection.js
│   │   │   ├── WorkflowProgress.js
│   │   │   ├── AgentPipeline.js
│   │   │   ├── RealTimeLogs.js
│   │   │   └── TestRunnerResults.js
│   │   ├── context/               # React context for state management
│   │   │   └── WorkflowContext.js
│   │   ├── App.js                 # Main React app
│   │   └── index.js               # React entry point
│   ├── package.json               # Frontend dependencies
│   └── package-lock.json
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

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Azure OpenAI API key**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sourabh1007/bugbash-copilot.git
   cd bugbash-copilot
   ```

2. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your Azure OpenAI credentials
   ```

3. **Run setup script**
   ```bash
   # Windows
   .\setup_frontend.bat
   
   # Linux/Mac
   ./setup_frontend.sh
   ```

4. **Start the application**
   ```bash
   # Terminal 1: Start backend
   python backend_server.py
   
   # Terminal 2: Start frontend
   cd frontend && npm start
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 🎯 Usage

### Web Interface

1. **Input Requirements**: Paste text, upload documents, or provide URLs
2. **Monitor Progress**: Watch real-time agent execution
3. **Review Results**: Interactive bug bash dashboard with:
   - Quality metrics and production readiness scores
   - Detailed bug findings with severity levels
   - Mitigation suggestions and fix recommendations

### CLI Mode

```bash
<<<<<<< HEAD
# Clone repository
git clone https://github.com/sourabh1007/bugbash-copilot.git
cd bugbash-copilot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your Azure OpenAI credentials

# Run interactive CLI
python main.py --input "your requirements here"
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

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your Azure OpenAI configuration:

```bash
# Required
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=BugBashCopilot
```

## 🐛 Bug Bash Dashboard Features

The React frontend provides a comprehensive bug bash quality assessment interface:

### Quality Metrics

- **Total Scenarios**: Number of test scenarios executed
- **Scenarios Passed**: Features working correctly  
- **Issues Found**: Bugs discovered during analysis
- **Quality Score**: Overall production readiness percentage

### Bug Analysis

- **Severity Classification**: Critical, High, Medium priority levels
- **Category Grouping**: Security, Configuration, Connectivity, Functional
- **Mitigation Suggestions**: Actionable fix recommendations
- **Production Readiness**: Deployment recommendations

### Real-time Monitoring

- **Agent Progress**: Live status of each pipeline stage
- **Execution Logs**: Detailed operation logging
- **WebSocket Updates**: Instant status synchronization

### Interactive Components

- **Input Section**: Multi-format input (text, file upload, URL)
- **Workflow Progress**: Visual pipeline status with real-time updates
- **Agent Pipeline**: Step-by-step agent execution tracking
- **Real-time Logs**: Live scrolling execution logs with timestamps
- **Test Results Dashboard**: Interactive charts and detailed bug analysis
  - Pie charts for test results distribution
  - Bar charts for severity analysis
  - Detailed bug findings with categorization
  - Mitigation suggestions with priority levels

## 🔧 Development

### Adding New Languages

1. Create configuration in `patterns/languages/`
2. Add language-specific prompts in `prompts/`
3. Update strategy mappings in `strategies/`

### Extending Agents

1. Implement new agent in `agents/`
2. Add integration to `workflow.py`
3. Update UI components in `frontend/src/`

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

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain** for the AI agent framework
- **Azure OpenAI** for language model capabilities
- **React & Material-UI** for the modern web interface
- **Flask & SocketIO** for real-time backend services

---

🚀 **Engineered with Vibe Coding principles using LangChain, Azure OpenAI GPT-4, and React**

*Transform natural language requirements into production-ready applications across 7 programming languages with intelligent multi-agent orchestration.*
