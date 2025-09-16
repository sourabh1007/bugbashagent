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
- **🎨 Modern Web Dashboard**: React.js + Material-UI interface with WebSocket real-time tracking
- **🔧 Intelligent Compilation Loop**: Real-time error detection, categorization, and selective regeneration
- **🐛 Bug Analysis**: Detailed issue categorization with severity levels and mitigation suggestions
- **📊 Quality Metrics**: Production readiness assessment with actionable insights
- **⚡ Real-time Updates**: Flask + SocketIO backend with WebSocket integration
- **🧪 Automated Test Discovery & Execution**: Framework-agnostic testing with LLM-powered failure analysis
- **📈 Advanced Monitoring**: LangSmith integration for workflow tracing and performance analytics
- **♻️ Resilient Architecture**: Graceful degradation, error recovery, and non-blocking failures
- **🎯 Language Normalization**: Intelligent language detection with 35+ language variant mapping
- **🔧 Configuration-Driven**: Pattern-based architecture with factories and strategies for extensibility

## 🏗️ System Architecture

### Application Stack

```
┌─────────────────────────────────────────────────┐
│              React Frontend (Port 3000)         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Input     │ │   Progress  │ │   Results   │ │
│  │  Section    │ │   Monitor   │ │  Dashboard  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │
│         │               │               │        │
│         └───────────────┼───────────────┘        │
│                    WebSocket + REST API          │
└─────────────────────┼───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│        Flask + SocketIO Backend (Port 5000)     │
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

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React 18 + Material-UI + WebSocket | Modern responsive interface with real-time updates |
| **Backend** | Flask + SocketIO + RESTful API | WebSocket communication + HTTP endpoints |
| **AI Framework** | LangChain + Azure OpenAI GPT-4 | Multi-agent orchestration with callbacks |
| **State Management** | React Context + WebSocket | Real-time state synchronization across agents |
| **Language Support** | Configuration-driven patterns | 7 languages with extensible architecture |
| **Testing** | Framework-agnostic dispatchers | Jest, pytest, xUnit, JUnit, go test, cargo test |
| **Monitoring** | LangSmith (optional) | Workflow tracing and performance analytics |
| **Compilation** | Multi-language toolchain | dotnet, npm, python, tsc, mvn, go, cargo |

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
BugBashAgent/
├── 🎯 main.py                      # CLI entry point for interactive workflows
├── 🌐 backend_server.py            # Flask + SocketIO backend server (port 5000)
├── ⚙️ workflow.py                 # Multi-agent orchestration engine
├── 🖥️ streamlit_app.py            # Alternative Streamlit interface
├── 
├── 🤖 agents/                     # Core AI agents with specialized roles
│   ├── base_agent.py              # Abstract base class with callback support
│   ├── document_analyzer.py       # Requirements analysis & language normalization
│   ├── code_generator.py          # Multi-language code generation & compilation
│   └── test_runner.py             # Test execution & intelligent failure analysis
├── 
├── 🎨 frontend/                   # React.js web interface (port 3000)
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
│   ├── langsmith/                 # LangSmith tracing & monitoring (optional)
│   ├── file_processing/           # Document parsing (PDF, DOCX, TXT)
│   └── web/                       # Web content extraction utilities
├── 
├── 🧬 patterns/                   # Language configuration system
│   ├── language_config.py         # Central language configuration manager
│   └── languages/                 # Language-specific configurations
│       ├── python_config.py       # Python patterns & best practices
│       ├── typescript_config.py   # TypeScript/Node.js configurations
│       ├── javascript_config.py   # JavaScript/ES6+ patterns
│       ├── csharp_config.py       # .NET & C# patterns
│       ├── java_config.py         # Java & Spring Boot configurations
│       ├── go_config.py           # Go patterns & conventions
│       └── rust_config.py         # Rust & Cargo configurations
├── 
├── 🛠️ tools/                      # Utility tools & generators
│   ├── compilation/               # Multi-language compilation & error analysis
│   │   └── code_compiler.py       # Language-specific compiler integration
│   ├── project_generators/        # Language-specific project scaffolding
│   ├── parsing/                   # Content & structure parsing utilities
│   ├── file_management/           # File operations & directory management
│   └── language_best_practices_manager.py # Best practices enforcement
├── 
├── 📝 prompts/                    # AI prompt templates (.prompty format)
│   ├── code_generator/            # Code generation prompt templates
│   │   ├── scenario_generation.prompty    # Scenario-based code generation
│   │   ├── error_fix_regeneration.prompty # Compilation error fixing
│   │   └── product_specific/      # Product-specific guidance
│   │       └── cosmos_db/         # Azure Cosmos DB patterns
│   │           ├── csharp_cosmos_guidance.prompty
│   │           └── typescript_cosmos_guidance.prompty
│   ├── document_analyzer/         # Requirements analysis prompts
│   │   └── scenario_extraction.prompty    # Scenario extraction with language normalization
│   └── test_runner/               # Test execution & analysis prompts
│       └── test_analysis.prompty          # Test failure analysis
├── 
├── 🎨 strategies/                 # Prompt generation strategies
│   ├── prompt_strategies.py       # Strategy pattern implementations
│   └── languages/                 # Language-specific prompt strategies
├── 
├── 🏭 factories/                  # Factory patterns for prompt generation
│   └── prompt_factory.py          # Centralized prompt generation with language mapping
├── 
├── ⚙️ config_package/             # Configuration & version management
│   ├── __init__.py                # Environment variable management
│   └── package_versions.py        # Language & framework version definitions
├── 
├── 📋 .github/                    # GitHub configuration
│   └── copilot-instructions.md    # AI agent productivity instructions
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
   git clone https://github.com/sourabh1007/bugbashagent.git
   cd bugbashagent
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
# Run interactive CLI
python main.py --input "your requirements here"

# Or run with interactive prompt
python main.py
```

**CLI Workflow:**

```bash
🤖 Bug Bash Copilot - AI-Powered Quality Assessment
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

📁 Output: workflow_outputs/user_management_api_20250916_143022/
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

### Current Application Interfaces

The Bug Bash Copilot provides multiple interfaces for different use cases:

1. **🌐 React Web Dashboard** (`http://localhost:3000`)
   - Modern Material-UI interface with real-time WebSocket updates
   - Interactive bug analysis with charts and visualizations
   - Comprehensive workflow monitoring and progress tracking
   - Multi-format input support (text, file upload, URL)

2. **⌨️ CLI Interface** (`python main.py`)
   - Interactive command-line tool for direct workflow execution
   - Perfect for automation, scripting, and headless environments
   - Full feature parity with web interface
   - Detailed console output and progress reporting

3. **📊 Streamlit Dashboard** (`streamlit run streamlit_app.py`)
   - Alternative web interface with Streamlit framework
   - Simplified interface for rapid prototyping and testing
   - Great for data science workflows and experimentation

### Adding New Languages

1. **Create Language Configuration**
   ```bash
   # Add language config in patterns/languages/
   touch patterns/languages/newlang_config.py
   ```

2. **Update Central Configuration**
   ```python
   # Add to patterns/language_config.py
   from .languages.newlang_config import NewLangConfig
   ```

3. **Create Prompt Strategy**
   ```bash
   # Add strategy in strategies/languages/
   touch strategies/languages/newlang_strategy.py
   ```

4. **Update Factories**
   ```python
   # Update factories/prompt_factory.py
   # Add language mapping and strategy integration
   ```

5. **Add Compilation Support**
   ```python
   # Update tools/compilation/code_compiler.py
   # Add compiler configuration for the new language
   ```

### Extending Agents

1. **Create New Agent**
   ```python
   # Implement in agents/
   class NewAgent(BaseAgent):
       def execute(self, input_data: str) -> Dict[str, Any]:
           # Implement agent logic with callbacks
           self.update_status("running", "Processing...", 50.0)
           return {"agent": self.name, "output": result, "status": "success"}
   ```

2. **Update Workflow**
   ```python
   # Add integration to workflow.py
   # Register agent in pipeline
   ```

3. **Update UI Components**
   ```javascript
   // Update frontend/src/ components
   // Add new agent status tracking
   ```

## 🔍 Advanced Features

- **🧠 Intelligent Error Recovery**: Automatic compilation error detection and fixing with selective regeneration
- **📈 Quality Scoring**: 0-100 quality scores with detailed production readiness breakdowns
- **🔄 Selective Regeneration**: Only regenerates failing code sections to maintain working components
- **📊 Real-time Monitoring**: Live progress tracking via WebSocket with agent status callbacks
- **🎯 Best Practices Enforcement**: Language-specific coding standards and architectural patterns
- **🔍 Root Cause Analysis**: Automated failure classification and intelligent troubleshooting
- **📱 Responsive Design**: Cross-platform compatibility (desktop, tablet, mobile)
- **⚡ Performance Optimized**: Efficient state management, lazy loading, and cached resources
- **🗣️ Language Normalization**: Intelligent detection of 35+ language variants with standardized mapping
- **🏗️ Configuration-Driven Architecture**: Extensible pattern-based system with factories and strategies
- **🔧 Multi-Interface Support**: React web dashboard, CLI interface, and Streamlit alternative
- **📋 Product-Specific Guidance**: Specialized patterns for Azure Cosmos DB, Express.js, FastAPI, and more
- **🛠️ Multi-Language Toolchain**: Integrated compilation support for all 7 programming languages

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Windows
.\setup_frontend.bat

# Linux/Mac  
./setup_frontend.sh
```

### Option 2: Manual Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Setup React frontend
cd frontend
npm install
cd ..

# 3. Configure environment
cp .env.template .env
# Edit .env with your Azure OpenAI credentials

# 4. Start backend server
python backend_server.py

# 5. Start frontend (in another terminal)
cd frontend && npm start
```

### Option 3: CLI Only

```bash
# Install dependencies and run CLI
pip install -r requirements.txt
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 🤖 AI Agent Development

For AI agents working on this codebase, comprehensive development instructions are available in `.github/copilot-instructions.md`. This includes:

- **System Architecture Overview**: Multi-agent pipeline patterns and real-time communication
- **Key Development Patterns**: Agent callbacks, language normalization, configuration-driven design
- **Critical Developer Workflows**: Backend/frontend development, language addition, environment setup
- **Project-Specific Conventions**: File organization, code generation patterns, error handling
- **Integration Points**: External dependencies, cross-component communication, compilation tools

These instructions ensure AI agents can be immediately productive and understand the complete system architecture.

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
