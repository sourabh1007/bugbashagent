# Bug Bash Copilot - AI Coding Agent Instructions

## System Architecture Overview

This is a **multi-agent AI-powered code quality assessment system** with a 3-agent pipeline architecture:

```
React Frontend (port 3000) ↔ Flask+SocketIO Backend (port 5000) ↔ Agent Pipeline
                                                                     ├─ DocumentAnalyzer
                                                                     ├─ CodeGenerator  
                                                                     └─ TestRunner
```

### Core Components

- **`workflow.py`**: Orchestrates the 3-agent pipeline with real-time callbacks
- **`backend_server.py`**: Flask+SocketIO server with WebSocket real-time communication
- **`agents/`**: Three specialized AI agents inheriting from `BaseAgent`
- **`frontend/src/`**: React app with Material-UI and WebSocket integration
- **`patterns/`**: Language-specific configurations and best practices
- **`tools/`**: Code compilation, project generation, and file management utilities

## Key Development Patterns

### Agent Architecture
All agents extend `BaseAgent` and must implement:
```python
class MyAgent(BaseAgent):
    def execute(self, input_data: str) -> Dict[str, Any]:
        # Real-time status updates via callbacks
        self.update_status("running", "Processing...", 50.0)
        # Return structured output
        return {"agent": self.name, "output": result, "status": "success"}
```

### Language Normalization
The `DocumentAnalyzer` normalizes language names using `_normalize_language()`:
- "JavaScript", "JS", "node.js" → "javascript"  
- "TypeScript", "TS" → "typescript"
- "C#", ".NET" → "csharp"

### Multi-Language Support
Each language has a config in `patterns/languages/` defining:
- File extensions (`.cs`, `.py`, `.js`, `.ts`)
- Build/test commands (`dotnet build`, `npm test`, `pytest`)
- Framework configurations (NUnit, Jest, pytest)

### Real-time Communication
Backend uses SocketIO events:
- `start_workflow` → triggers agent pipeline
- `agent_status` → agent progress updates
- `workflow_status` → overall pipeline status
- `log` → real-time execution logs

## Critical Developer Workflows

### Backend Development
```bash
# Start backend server (auto-reloads on changes)
python backend_server.py

# Test individual agents
python -c "from agents import DocumentAnalyzer; agent = DocumentAnalyzer(llm); print(agent.execute('test input'))"
```

### Frontend Development  
```bash
cd frontend
npm start  # Connects to backend on port 5000
```

### Adding New Languages
1. Create `patterns/languages/newlang_config.py` with `LanguageConfig`
2. Add to `patterns/language_config.py` imports and `_initialize_configs()`
3. Create strategy in `strategies/languages/newlang_strategy.py`
4. Update `factories/prompt_factory.py` mapping
5. Add compilation config in `tools/compilation/code_compiler.py`

### Environment Setup
- Copy `.env.template` to `.env` with Azure OpenAI credentials
- Required: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME`
- Optional: LangSmith tracing with `LANGCHAIN_TRACING_V2=true`

## Project-Specific Conventions

### File Organization
- **Prompts**: Use `.prompty` format in `prompts/` (not `.md` or `.txt`)
- **Outputs**: Auto-generated in `workflow_outputs/project_YYYYMMDD_HHMMSS/`
- **Strategies**: Language-specific prompt generation in `strategies/languages/`
- **Tools**: Reusable utilities in `tools/` (compilation, file management, parsing)

### Code Generation Pattern
The `CodeGenerator` agent:
1. Uses language config from `LanguageConfigManager` for file extensions
2. Compiles generated code using `CodeCompiler` tool
3. Regenerates on compilation errors (max 3 attempts)
4. Creates proper project structure via `ProjectGenerator` classes

### State Management
- Backend: `WorkflowState` class tracks running workflows and agent status
- Frontend: React Context in `context/WorkflowContext.js` with WebSocket integration
- Persistence: No database - state is ephemeral and workflow-scoped

### Error Handling
- Agents return `{"status": "error", "error": "message"}` format
- Compilation errors trigger automatic regeneration attempts
- WebSocket disconnections auto-reconnect and restore progress

## Integration Points

### External Dependencies
- **Azure OpenAI**: Primary LLM via `integrations/azure_openai/`
- **LangSmith**: Optional tracing via `integrations/langsmith/`
- **Language Compilers**: `dotnet`, `python`, `node`, `tsc`, `mvn`, `go`, `cargo`

### Cross-Component Communication
- Workflow → Agents: Via `execute()` method with input passing
- Agents → Frontend: Via status callbacks through SocketIO
- Frontend → Backend: WebSocket events + REST endpoints

### File System Patterns
- Generated code: Language-specific extensions via `_get_file_extension_for_language()`
- Project structure: Each language has different patterns (`src/`, `Tests/`, etc.)
- Output organization: Timestamped folders with step-by-step agent outputs

## Development Commands

```bash
# Full system test
python main.py  # CLI interface

# Backend-only test  
python backend_server.py

# Frontend-only development
cd frontend && npm start

# Language validation test
python test_language_normalization.py

# Check compilation tools
python -c "from tools.compilation import CodeCompiler; print(CodeCompiler().compilation_configs.keys())"
```

When modifying agents, always maintain the callback pattern for real-time UI updates. When adding languages, follow the complete configuration chain from patterns → strategies → factories → tools.
