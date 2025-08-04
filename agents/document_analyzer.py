from typing import Dict, Any
import json
import os
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent


class DocumentAnalyzer(BaseAgent):
    """Agent responsible for analyzing documents and extracting key information"""
    
    def __init__(self, llm: Any):
        super().__init__("Document Analyzer", llm)
        self.prompt_template = PromptTemplate(
            input_variables=["document_content"],
            template="""
            You are a document analyzer agent. Your task is to analyze the provided document content and extract key information in a specific JSON format.
            
            Document Content:
            {document_content}
            
            Based on the document content, extract and determine:
            1. Programming language mentioned or most suitable for the project
            2. Product name or main technology/framework discussed
            3. Version information - Look for specific version numbers, release versions, or version identifiers in the document. If no specific version is mentioned, analyze the content to determine the most likely current version being discussed (e.g., if .NET 8 features are mentioned, use "8.0", if Python 3.11 syntax is shown, use "3.11", etc.)
            4. List of scenarios, test cases, or example prompts that could be used
            5. Project setup information including installation steps, dependencies, and configuration
            
            You must respond with ONLY a valid JSON object in this exact format:
            {{
                "language": "<programming_language>",
                "productName": "<product_or_technology_name>",
                "version": "<specific_version_number_or_identifier>",
                "scenarioList": ["<scenario1>", "<scenario2>", "<scenario3>"],
                "projectsetupInfo": {{
                    "installation": "<installation_steps>",
                    "dependencies": ["<dependency1>", "<dependency2>"],
                    "configuration": "<configuration_details>",
                    "gettingStarted": "<how_to_get_started>"
                }}
            }}
            
            IMPORTANT: For the version field, be specific:
            - If specific version numbers are mentioned (e.g., "Python 3.11", ".NET 8.0", "Node.js 18.x"), use those exact versions
            - If framework features suggest a specific version (e.g., async/await in Python suggests 3.7+, top-level programs in C# suggest .NET 6+), infer and specify that version
            - If modern syntax or recent features are shown, specify a recent stable version rather than "latest"
            - Only use "latest" if absolutely no version clues can be determined from the content
            
            Make sure the JSON is valid and complete. Do not include any other text or explanations.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Analyze the document content and generate structured JSON output"""
        self.log("Starting document analysis")
        
        try:
            # Get the analysis result from the LLM
            analysis_result = self.chain.invoke({"document_content": input_data})
            
            # Try to parse the JSON response
            try:
                parsed_result = json.loads(analysis_result["text"].strip())
            except json.JSONDecodeError as e:
                # If JSON parsing fails, log the error and re-raise
                self.log(f"Failed to parse JSON from LLM response: {str(e)}")
                self.log(f"Raw LLM response: {analysis_result['text']}")
                raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
            
            # Generate temporary JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "workflow_outputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            json_filename = f"{output_dir}/document_analysis_{timestamp}.json"
            
            # Write the structured output to a JSON file
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(parsed_result, f, indent=2, ensure_ascii=False)
            
            output = {
                "agent": self.name,
                "input": input_data,
                "output": parsed_result,
                "json_file": json_filename,
                "status": "success"
            }
            
            self.log(f"Document analysis completed successfully. JSON file created: {json_filename}")
            return output
            
        except Exception as e:
            self.log(f"Error during document analysis: {str(e)}")
            return {
                "agent": self.name,
                "input": input_data,
                "output": None,
                "status": "error",
                "error": str(e)
            }
