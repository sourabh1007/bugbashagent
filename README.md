# LangChain Multi-Agent Code Development Project

This project demonstrates a LangChain application with 3 agents that work together to develop code from requirements:

1. **Document Analyzer**: Analyzes project requirements and extracts key information
2. **Code Generator**: Generates clean, functional code based on the analyzed requirements
3. **Code Executor**: Reviews the generated code and provides execution guidance and testing recommendations

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Azure OpenAI configuration:

```env
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

3. Run the main application:

```bash
python main.py
```

## Output Files

The workflow automatically saves all intermediate and final outputs in timestamped folders:

- `workflow_outputs/workflow_output_YYYYMMDD_HHMMSS/`
  - `00_workflow_summary.txt` - Complete workflow summary
  - `step_01_document_analyzer.txt` - Document analysis output
  - `step_02_code_generator.txt` - Generated code output  
  - `step_03_code_executor.txt` - Code execution report

Each file contains:
- Agent name and step number
- Input and output data
- Status and timestamp
- Clear formatting for easy review

## Project Structure

- `main.py`: Main application entry point
- `agents/`: Directory containing agent implementations
  - `document_analyzer.py`: Document Analyzer agent
  - `code_generator.py`: Code Generator agent  
  - `code_executor.py`: Code Executor agent
  - `base_agent.py`: Base agent class
- `workflow.py`: Agent workflow orchestration
- `config.py`: Configuration settings
- `test_workflow.py`: Test script for the workflow
- `requirements.txt`: Python dependencies
