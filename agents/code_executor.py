from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent


class CodeExecutor(BaseAgent):
    """Agent responsible for executing and testing generated code"""
    
    def __init__(self, llm: Any):
        super().__init__("Code Executor", llm)
        self.prompt_template = PromptTemplate(
            input_variables=["generated_code"],
            template="""
            You are a code executor agent. Your task is to analyze the generated code and provide execution guidance and testing recommendations.
            
            Generated Code:
            {generated_code}
            
            Please provide:
            1. Code review and quality assessment
            2. Potential issues or improvements identified
            3. Step-by-step execution instructions
            4. Test cases or scenarios to validate the code
            5. Expected outputs or behaviors
            6. Debugging tips if issues are found
            7. Performance considerations
            8. Security considerations (if applicable)
            
            Format your response as a comprehensive execution and testing report with clear sections.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute and test the generated code"""
        self.log("Starting code execution and testing analysis")
        
        try:
            execution_result = self.chain.invoke({"generated_code": input_data})
            
            output = {
                "agent": self.name,
                "input": input_data,
                "output": execution_result["text"],
                "status": "success"
            }
            
            self.log("Code execution analysis completed successfully")
            return output
            
        except Exception as e:
            self.log(f"Error during code execution analysis: {str(e)}")
            return {
                "agent": self.name,
                "input": input_data,
                "output": None,
                "status": "error",
                "error": str(e)
            }
