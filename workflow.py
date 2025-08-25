from typing import List, Dict, Any
import os
import json
from datetime import datetime
from agents import CodeGenerator, DocumentAnalyzer, LLMCompilerAgent


class AgentWorkflow:
    """Manages the workflow of multiple agents passing data sequentially"""
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.agents = self._initialize_agents()
        self.workflow_history = []
        self.output_folder = None
    
    def _initialize_agents(self) -> List[Any]:
        """Initialize all agents in the workflow"""
        return [
            DocumentAnalyzer(self.llm),
            CodeGenerator(self.llm),
            LLMCompilerAgent(self.llm)
        ]
    
    def _create_output_folder(self) -> str:
        """Create a timestamped output folder for this workflow run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"workflow_output_{timestamp}"
        output_path = os.path.join(os.getcwd(), "workflow_outputs", folder_name)
        
        # Create the directory structure
        os.makedirs(output_path, exist_ok=True)
        
        return output_path
    
    def _save_agent_output(self, agent_name: str, step_number: int, input_data: str, output_data: Any, status: str) -> str:
        """Save individual agent output to a file"""
        # Clean agent name for filename
        clean_name = agent_name.lower().replace(" ", "_")
        filename = f"step_{step_number:02d}_{clean_name}.txt"
        filepath = os.path.join(self.output_folder, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"AGENT: {agent_name}\n")
                f.write(f"STEP: {step_number}\n")
                f.write(f"STATUS: {status}\n")
                f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("INPUT:\n")
                f.write("-" * 40 + "\n")
                f.write(str(input_data) + "\n\n")
                
                f.write("OUTPUT:\n")
                f.write("-" * 40 + "\n")
                
                # Handle different output types
                if isinstance(output_data, dict):
                    # For dictionary outputs (like from Document Analyzer), format as JSON
                    f.write(json.dumps(output_data, indent=2, ensure_ascii=False) + "\n")
                else:
                    # For string outputs (like from other agents)
                    f.write(str(output_data) + "\n")
                
                # For LLM Compiler Agent, also include detailed error analysis
                if "compiler" in agent_name.lower() and isinstance(output_data, str):
                    # Get the full agent result for additional details
                    if hasattr(self, '_current_agent_result'):
                        agent_result = self._current_agent_result
                        if agent_result.get("error_analysis"):
                            f.write("\n" + "=" * 60 + "\n")
                            f.write("CONSOLIDATED COMPILATION ERROR ANALYSIS:\n")
                            f.write("=" * 60 + "\n\n")
                            
                            error_analysis = agent_result["error_analysis"]
                            
                            # Write error summary
                            if error_analysis.get("error_summary"):
                                f.write("📊 ERROR OVERVIEW:\n")
                                f.write(f"- Total Errors: {error_analysis.get('total_errors', '?')}\n")
                                f.write(f"- Error Categories: {len(error_analysis.get('error_categories', {}))}\n")
                                f.write(f"- Compilation Command: {error_analysis.get('compilation_command', '?')}\n\n")
                                
                                # Write error categories breakdown
                                f.write("🔥 ERROR BREAKDOWN:\n")
                                for category, count in error_analysis.get("error_categories", {}).items():
                                    f.write(f"- {category.replace('_', ' ').title()}: {count} errors\n")
                                f.write("\n")
                            
                            # Write step-by-step plan
                            if error_analysis.get("step_by_step_plan"):
                                f.write("🛠️ STEP-BY-STEP FIX PLAN:\n")
                                for i, step in enumerate(error_analysis.get("step_by_step_plan", []), 1):
                                    f.write(f"{i}. {step}\n")
                                f.write("\n")
                            
                            # Write consolidated fixes
                            if error_analysis.get("consolidated_fixes"):
                                f.write("💡 CONSOLIDATED FIXES:\n")
                                for fix in error_analysis.get("consolidated_fixes", []):
                                    f.write(f"- {fix}\n")
                                f.write("\n")
                            
                            # Write full LLM analysis if available
                            if error_analysis.get("llm_full_analysis"):
                                f.write("🧠 FULL LLM ANALYSIS:\n")
                                f.write("-" * 40 + "\n")
                                f.write(error_analysis["llm_full_analysis"] + "\n")
                                f.write("-" * 40 + "\n\n")
            
            print(f"💾 Saved {agent_name} output to: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving {agent_name} output: {str(e)}")
            return None
    
    def execute_workflow(self, initial_input: str) -> Dict[str, Any]:
        """Execute the complete workflow with all agents"""
        print("=" * 60)
        print("STARTING MULTI-AGENT WORKFLOW")
        print("=" * 60)
        
        # Create output folder for this workflow run
        self.output_folder = self._create_output_folder()
        print(f"📁 Output folder created: {self.output_folder}")
        
        current_input = initial_input
        workflow_results = {
            "initial_input": initial_input,
            "agent_outputs": [],
            "final_output": None,
            "workflow_status": "in_progress",
            "output_folder": self.output_folder,
            "saved_files": []
        }
        
        try:
            for i, agent in enumerate(self.agents, 1):
                print(f"\n--- Step {i}: {agent.name} ---")
                
                # Execute the current agent
                agent_result = agent.execute(current_input)
                workflow_results["agent_outputs"].append(agent_result)
                
                # Store current agent result for detailed output saving
                self._current_agent_result = agent_result
                
                # Save agent output to file
                if agent_result["status"] == "success":
                    saved_file = self._save_agent_output(
                        agent.name, 
                        i, 
                        current_input, 
                        agent_result["output"], 
                        agent_result["status"]
                    )
                    if saved_file:
                        workflow_results["saved_files"].append(saved_file)
                else:
                    # Save error output as well
                    error_output = f"ERROR: {agent_result.get('error', 'Unknown error')}"
                    saved_file = self._save_agent_output(
                        agent.name, 
                        i, 
                        current_input, 
                        error_output, 
                        agent_result["status"]
                    )
                    if saved_file:
                        workflow_results["saved_files"].append(saved_file)
                
                # Check if agent execution was successful
                if agent_result["status"] != "success":
                    workflow_results["workflow_status"] = "failed"
                    workflow_results["failed_at"] = agent.name
                    workflow_results["error"] = agent_result.get("error", "Unknown error")
                    print(f"❌ Workflow failed at {agent.name}")
                    
                    # Save final workflow summary even on failure
                    self._save_workflow_summary(workflow_results)
                    return workflow_results
                
                # Prepare input for next agent
                # For most agents, pass the output string, but for LLMCompilerAgent, pass the full result dict
                if i < len(self.agents) and hasattr(self.agents[i], 'name') and 'compiler' in self.agents[i].name.lower():
                    current_input = agent_result  # Pass full result dict to compiler agent
                else:
                    current_input = agent_result["output"]  # Use output string for other agents
                print(f"✅ {agent.name} completed successfully")
            
            # Set final results
            workflow_results["final_output"] = current_input
            workflow_results["workflow_status"] = "completed"
            
            # Save final workflow summary
            self._save_workflow_summary(workflow_results)
            
            print("\n" + "=" * 60)
            print("WORKFLOW COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"📂 All outputs saved in: {self.output_folder}")
            
            return workflow_results
            
        except Exception as e:
            workflow_results["workflow_status"] = "error"
            workflow_results["error"] = str(e)
            print(f"❌ Workflow error: {str(e)}")
            
            # Save workflow summary even on error
            self._save_workflow_summary(workflow_results)
            return workflow_results
    
    def _save_workflow_summary(self, results: Dict[str, Any]) -> str:
        """Save the complete workflow summary to a file"""
        summary_file = os.path.join(self.output_folder, "00_workflow_summary.txt")
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("LANGCHAIN MULTI-AGENT WORKFLOW SUMMARY\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Initial Input: {results['initial_input']}\n")
                f.write(f"Workflow Status: {results['workflow_status'].upper()}\n\n")
                
                f.write("AGENT EXECUTION SEQUENCE:\n")
                f.write("-" * 30 + "\n")
                
                for i, agent_output in enumerate(results['agent_outputs'], 1):
                    status_emoji = "✅" if agent_output['status'] == 'success' else "❌"
                    f.write(f"{i}. {agent_output['agent']}: {status_emoji} {agent_output['status']}\n")
                
                if results['workflow_status'] == 'completed':
                    f.write(f"\n✅ Final Output Generated Successfully\n")
                elif results['workflow_status'] == 'failed':
                    f.write(f"\n❌ Workflow Failed at: {results.get('failed_at', 'Unknown')}\n")
                    f.write(f"Error: {results.get('error', 'Unknown error')}\n")
                
                f.write(f"\nSAVED FILES:\n")
                f.write("-" * 15 + "\n")
                for file_path in results.get('saved_files', []):
                    filename = os.path.basename(file_path)
                    f.write(f"- {filename}\n")
                
                f.write(f"\nOUTPUT FOLDER: {self.output_folder}\n")
            
            print(f"💾 Workflow summary saved to: 00_workflow_summary.txt")
            return summary_file
            
        except Exception as e:
            print(f"❌ Error saving workflow summary: {str(e)}")
            return None

    def get_workflow_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary of the workflow execution"""
        summary = f"""
WORKFLOW EXECUTION SUMMARY
==========================

Initial Input: {results['initial_input']}
Status: {results['workflow_status'].upper()}

Agent Execution Results:
"""
        
        for i, agent_output in enumerate(results['agent_outputs'], 1):
            status_emoji = "✅" if agent_output['status'] == 'success' else "❌"
            summary += f"{i}. {agent_output['agent']}: {status_emoji} {agent_output['status']}\n"
        
        if results['workflow_status'] == 'completed':
            summary += f"\n✅ Final Output Generated Successfully\n"
        elif results['workflow_status'] == 'failed':
            summary += f"\n❌ Workflow Failed at: {results.get('failed_at', 'Unknown')}\n"
            summary += f"Error: {results.get('error', 'Unknown error')}\n"
        
        return summary
