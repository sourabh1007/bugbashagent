#!/usr/bin/env python3
"""
LangChain Multi-Agent Code Development Workflow

This application demonstrates a workflow with 3 agents:
1. Document Analyzer - Analyzes requirements and extracts key information
2. Code Generator - Generates code based on the analyzed requirements  
3. Code Executor - Reviews and provides execution guidance for the generated code

Each agent passes its output to the next agent in sequence.
"""

import os
import sys
from langchain_openai import AzureChatOpenAI
# Import specific configuration items instead of the config module
from config_package import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    MODEL_NAME,
    TEMPERATURE
)
from workflow import AgentWorkflow


def check_azure_config():
    """Check if Azure OpenAI configuration is set up"""
    missing_configs = []
    
    if not AZURE_OPENAI_API_KEY:
        missing_configs.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_ENDPOINT:
        missing_configs.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_DEPLOYMENT_NAME:
        missing_configs.append("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if missing_configs:
        print("❌ Error: Missing Azure OpenAI configuration!")
        print("Please set the following in your .env file:")
        for config_name in missing_configs:
            print(f"  {config_name}=your_value_here")
        print("\nExample .env file:")
        print("AZURE_OPENAI_API_KEY=your_api_key")
        print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name")
        sys.exit(1)


def get_user_input():
    """Get requirements input from user"""
    print("🤖 LangChain Multi-Agent Code Development Workflow")
    print("=" * 50)
    
    requirements = input("\nEnter your project requirements or description: ").strip()
    
    if not requirements:
        print("❌ No requirements provided. Exiting.")
        sys.exit(1)
    
    return requirements


def save_results(results, filename="code_development_results.txt"):
    """Save workflow results to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("LANGCHAIN MULTI-AGENT CODE DEVELOPMENT RESULTS\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Initial Requirements: {results['initial_input']}\n")
            f.write(f"Workflow Status: {results['workflow_status']}\n\n")
            
            for i, agent_output in enumerate(results['agent_outputs'], 1):
                f.write(f"STEP {i}: {agent_output['agent']}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Status: {agent_output['status']}\n")
                if agent_output['status'] == 'success':
                    f.write(f"Output:\n{agent_output['output']}\n\n")
                else:
                    f.write(f"Error: {agent_output.get('error', 'Unknown error')}\n\n")
            
            if results['workflow_status'] == 'completed':
                f.write("FINAL CODE EXECUTION REPORT\n")
                f.write("=" * 30 + "\n")
                f.write(results['final_output'])
        
        print(f"📁 Results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")


def main():
    """Main application entry point"""
    try:
        # Check configuration
        check_azure_config()
        
        # Get user input
        requirements = get_user_input()
        
        # Initialize Azure OpenAI LLM
        print("\n🔧 Initializing Azure OpenAI Language Model...")
        llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=TEMPERATURE
        )
        
        # Create and execute workflow
        print("🚀 Starting multi-agent code development workflow...")
        workflow = AgentWorkflow(llm)
        results = workflow.execute_workflow(requirements)
        
        # Display summary
        print("\n" + workflow.get_workflow_summary(results))
        
        # Display final output if successful
        if results['workflow_status'] == 'completed':
            print("\n📋 FINAL CODE EXECUTION REPORT:")
            print("=" * 60)
            print(results['final_output'])
            print(f"\n📂 All intermediate and final outputs saved in:")
            print(f"   {results['output_folder']}")
        else:
            print(f"\n📂 Partial outputs saved in:")
            print(f"   {results['output_folder']}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n❌ Application error: {str(e)}")
        print(f"Debug traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
