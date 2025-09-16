from typing import List, Dict, Any
import os
import json
from datetime import datetime
from agents import CodeGenerator, DocumentAnalyzer, TestRunner
from integrations.langsmith import trace_workflow_execution, LangSmithIntegration


class AgentWorkflow:
    """Manages the workflow of multiple agents passing data sequentially.

    Supports distinct LLM instances per agent (e.g., document analyzer vs code generator)
    to allow different model deployments / temperatures / token limits.
    """

    def __init__(self, llm: Any, code_llm: Any = None, test_llm: Any = None):
        self.llm = llm  # default / document analyzer llm
        self.code_llm = code_llm or llm
        self.test_llm = test_llm or llm
        self.agents = self._initialize_agents()
        self.output_folder = None
        self.status_callback = None  # Callback for workflow status updates
        self.agent_status_callback = None  # Callback for individual agent updates
    
    def _initialize_agents(self) -> List[Any]:
        """Initialize all agents in the workflow with their designated LLMs."""
        return [
            DocumentAnalyzer(self.llm),
            CodeGenerator(self.code_llm),
            TestRunner(self.test_llm)
        ]
    
    def set_status_callback(self, callback):
        """Set callback for workflow status updates"""
        self.status_callback = callback
    
    def set_agent_status_callback(self, callback):
        """Set callback for individual agent status updates"""
        self.agent_status_callback = callback
        # Set the callback for all agents
        for agent in self.agents:
            agent.set_status_callback(callback)
            agent.set_progress_callback(callback)  # Use same callback for progress
    
    def _notify_workflow_status(self, status: str, message: str = "", current_agent: str = None, step: int = None):
        """Notify workflow status change"""
        if self.status_callback:
            try:
                self.status_callback(
                    workflow_status=status,
                    message=message,
                    current_agent=current_agent,
                    current_step=step,
                    total_steps=len(self.agents)
                )
            except Exception as e:
                print(f"❌ Error in workflow status callback: {str(e)}")
    
    def _create_output_folder(self) -> str:
        """Create a timestamped output folder for this workflow run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"workflow_output_{timestamp}"
        output_path = os.path.join(os.getcwd(), "workflow_outputs", folder_name)
        
        # Create the directory structure
        os.makedirs(output_path, exist_ok=True)
        
        return output_path
    
    def _write_code_generator_output_with_compilation_details(self, agent_name: str, step_number: int, input_data: str, agent_result: Any, status: str) -> str:
        """Enhanced version that includes detailed compilation attempt analysis"""
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
                
                # Extract output data safely
                if isinstance(agent_result, dict):
                    output_data = agent_result.get("output", {})
                    # For CodeGenerator, compilation attempts might be in the root or in output
                    # Ensure output_data is a dict before calling .get() on it
                    if isinstance(output_data, dict):
                        compilation_attempts = agent_result.get("compilation_attempts", output_data.get("compilation_attempts", []))
                    else:
                        compilation_attempts = agent_result.get("compilation_attempts", [])
                else:
                    output_data = agent_result
                    compilation_attempts = []
                
                # Enhanced section: Compilation attempts analysis
                if compilation_attempts:
                    f.write("🔄 COMPILATION ATTEMPTS ANALYSIS\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write(f"📊 EXECUTIVE SUMMARY:\n")
                    f.write(f"- Total Attempts: {len(compilation_attempts)}\n")
                    
                    # Calculate attempt statistics
                    successful_attempts = sum(1 for attempt in compilation_attempts if attempt.get('status') == 'success')
                    failed_attempts = len(compilation_attempts) - successful_attempts
                    
                    f.write(f"- Successful: {successful_attempts}\n")
                    f.write(f"- Failed: {failed_attempts}\n")
                    
                    if len(compilation_attempts) > 0:
                        success_rate = (successful_attempts / len(compilation_attempts)) * 100
                        f.write(f"- Success Rate: {success_rate:.1f}%\n")
                    else:
                        f.write(f"- Success Rate: N/A (no compilation attempts)\n")
                    
                    # Show selective scenario regeneration info if available
                    if isinstance(output_data, dict) and output_data.get("selective_regeneration_used"):
                        regenerated_scenarios = output_data.get("regenerated_scenarios", [])
                        preserved_scenarios = output_data.get("preserved_scenarios", [])
                        f.write(f"- Selective Regeneration: ✅ USED\n")
                        f.write(f"- Scenarios Regenerated: {len(regenerated_scenarios)}\n")
                        f.write(f"- Scenarios Preserved: {len(preserved_scenarios)}\n")
                    else:
                        f.write(f"- Selective Regeneration: ❌ NOT USED\n")
                    
                    f.write("\n" + "=" * 50 + "\n\n")
                    
                    # Detailed attempt-by-attempt analysis
                    f.write("📋 DETAILED ATTEMPT ANALYSIS:\n")
                    f.write("-" * 40 + "\n")
                    
                    for i, attempt in enumerate(compilation_attempts, 1):
                        f.write(f"\n🔹 ATTEMPT #{i}:\n")
                        f.write(f"   Status: {attempt.get('status', 'unknown').upper()}\n")
                        f.write(f"   Timestamp: {attempt.get('timestamp', 'N/A')}\n")
                        
                        if attempt.get('status') == 'success':
                            f.write(f"   ✅ COMPILATION SUCCESSFUL\n")
                            if attempt.get('output'):
                                f.write(f"   Build Output: {attempt['output'][:200]}...\n")
                        else:
                            f.write(f"   ❌ COMPILATION FAILED\n")
                            
                            # Show error counts by category
                            error_analysis = attempt.get('error_analysis', {})
                            if error_analysis.get('error_categories'):
                                f.write(f"   Error Categories:\n")
                                for category, count in error_analysis['error_categories'].items():
                                    f.write(f"     - {category.replace('_', ' ').title()}: {count}\n")
                            
                            # Show top errors
                            parsed_errors = attempt.get('parsed_errors', [])
                            if parsed_errors:
                                f.write(f"   Top Errors:\n")
                                for error in parsed_errors[:3]:  # Show top 3
                                    f.write(f"     - {error.get('message', 'Unknown error')[:80]}...\n")
                            
                            # Show regenerated scenarios for this attempt
                            if attempt.get('regenerated_scenarios'):
                                f.write(f"   Regenerated Scenarios: {len(attempt['regenerated_scenarios'])}\n")
                                for scenario in attempt['regenerated_scenarios'][:3]:  # Show first 3
                                    f.write(f"     - {scenario}\n")
                        
                        f.write("\n")
                
                # Show final recommendations if available
                if isinstance(output_data, dict) and output_data.get("final_recommendations"):
                    f.write("💡 FINAL RECOMMENDATIONS:\n")
                    f.write("-" * 30 + "\n")
                    for rec in output_data["final_recommendations"]:
                        f.write(f"   {rec}\n")
                else:
                    f.write("💡 NEXT STEPS RECOMMENDED:\n")
                    f.write("-" * 30 + "\n")
                    f.write("   1. Review the detailed error analysis in the comprehensive report\n")
                    f.write("   2. Check the pattern suggestions for common fix approaches\n")
                    f.write("   3. Consider running additional generation attempts\n")
                    f.write("   4. Review and manually fix remaining compilation errors\n")
        
                f.write(f"\n📊 For complete analysis, see: COMPREHENSIVE_CODE_GENERATION_REPORT.md\n")
                code_path = output_data.get('code_path', 'project directory') if isinstance(output_data, dict) else 'project directory'
                f.write(f"📂 All files saved to: {code_path}\n")
        
                # Write final error message
                if status == "compilation_failed":
                    error_message = output_data.get("error", "Code generation completed but compilation failed") if isinstance(output_data, dict) else "Code generation completed but compilation failed"
                    f.write(f"\n❌ FINAL RESULT: {error_message}\n")
                elif status == "success":
                    successful_attempt = output_data.get("successful_attempt", len(compilation_attempts)) if isinstance(output_data, dict) else len(compilation_attempts)
                    f.write(f"\n✅ FINAL RESULT: Code generation successful on attempt #{successful_attempt}\n")
                
                f.write("\nINPUT:\n")
                f.write("-" * 40 + "\n")
                f.write(str(input_data) + "\n\n")
                
                f.write("OUTPUT:\n")
                f.write("-" * 40 + "\n")
                
                # Handle different output types
                if isinstance(output_data, dict):
                    # For dictionary outputs (like from Code Generator), format as JSON
                    f.write(json.dumps(output_data, indent=2, ensure_ascii=False) + "\n")
                else:
                    # For string outputs (like from other agents)
                    f.write(str(output_data) + "\n")
            
            print(f"💾 Saved {agent_name} output to: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving {agent_name} output: {str(e)}")
            return None

    def _write_test_runner_output_with_results(self, agent_name: str, step_number: int, input_data: str, agent_result: Any, status: str) -> str:
        """Enhanced version that includes detailed test execution analysis"""
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
                
                # Extract output data safely  
                if isinstance(agent_result, dict):
                    output_data = agent_result.get("output", {})
                else:
                    output_data = agent_result
                
                # Enhanced section: Test execution analysis
                if isinstance(output_data, dict) and "output" in output_data:
                    test_output = output_data["output"]
                    execution_summary = output_data.get("execution_summary", {})
                elif isinstance(agent_result, dict) and "output" in agent_result:
                    # Check if the test data is in the agent_result instead
                    test_output = agent_result["output"]
                    execution_summary = agent_result.get("execution_summary", {})
                else:
                    test_output = None
                    execution_summary = {}
                
                # Only proceed with test analysis if we have valid test output
                if test_output is not None:
                    f.write("🧪 TEST EXECUTION ANALYSIS\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write(f"📊 EXECUTIVE SUMMARY:\n")
                    f.write(f"- Total Tests: {execution_summary.get('total_tests', 0)}\n")
                    f.write(f"- Passed Tests: {execution_summary.get('passed_tests', 0)}\n")
                    f.write(f"- Failed Tests: {execution_summary.get('failed_tests', 0)}\n")
                    f.write(f"- Success Rate: {execution_summary.get('success_rate', 0):.1f}%\n")
                    f.write(f"- Execution Time: {execution_summary.get('execution_time', 0):.2f}s\n")
                    f.write("\n")
                    
                    # Test analysis section
                    if isinstance(test_output, dict) and "test_analysis" in test_output:
                        test_analysis = test_output["test_analysis"]
                        f.write("🤖 AI ANALYSIS:\n")
                        f.write("-" * 30 + "\n")
                        f.write(f"{test_analysis.get('llm_analysis', 'No analysis available')}\n\n")
                        
                        # Key insights
                        insights = test_analysis.get("key_insights", [])
                        if insights:
                            f.write("💡 KEY INSIGHTS:\n")
                            for insight in insights:
                                f.write(f"- {insight}\n")
                            f.write("\n")
                        
                        # Recommendations
                        recommendations = test_analysis.get("recommendations", [])
                        if recommendations:
                            f.write("📋 RECOMMENDATIONS:\n")
                            for rec in recommendations:
                                f.write(f"- {rec}\n")
                            f.write("\n")
                        
                        # Test quality score
                        quality_score = test_analysis.get("test_quality_score", 0)
                        f.write(f"⭐ TEST QUALITY SCORE: {quality_score}/100\n\n")
                    
                    # Comprehensive report link
                    if "comprehensive_report" in test_output:
                        f.write("📄 COMPREHENSIVE REPORT:\n")
                        f.write(f"HTML report available in test results directory\n\n")
                
                # Standard workflow sections
                f.write("INPUT:\n")
                f.write("-" * 40 + "\n")
                f.write(str(input_data) + "\n\n")
                
                f.write("OUTPUT:\n")
                f.write("-" * 40 + "\n")
                
                # Handle different output types
                if isinstance(output_data, dict):
                    f.write(json.dumps(output_data, indent=2, ensure_ascii=False) + "\n")
                else:
                    f.write(str(output_data) + "\n")
            
            print(f"💾 Saved {agent_name} output to: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving {agent_name} output: {str(e)}")
            return None

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
    
    @trace_workflow_execution
    def execute_workflow(self, initial_input: str) -> Dict[str, Any]:
        """Execute the complete workflow with all agents"""
        print("=" * 60)
        print("STARTING MULTI-AGENT WORKFLOW")
        print("=" * 60)
        
        # Create output folder for this workflow run
        self.output_folder = self._create_output_folder()
        print(f"📁 Output folder created: {self.output_folder}")
        
        # Set up prompt logging for all agents
        for agent in self.agents:
            agent.set_prompt_log_folder(self.output_folder)
        print(f"📝 Prompt logging enabled for all agents")
        
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
            # Notify workflow start
            self._notify_workflow_status("started", "Workflow execution initiated")
            
            for i, agent in enumerate(self.agents, 1):
                print(f"\n--- Step {i}: {agent.name} ---")
                
                # Notify current agent starting
                self._notify_workflow_status(
                    "running", 
                    f"Executing {agent.name}",
                    current_agent=agent.name,
                    step=i
                )
                
                # Execute the current agent with status tracking
                agent_result = agent.execute_with_status(current_input)
                workflow_results["agent_outputs"].append(agent_result)
                
                # Store current agent result for detailed output saving
                self._current_agent_result = agent_result
                
                # Save agent output to file with enhanced reporting for specific agents
                if agent_result["status"] == "success":
                    # Use enhanced reporting for Code Generator
                    if "code generator" in agent.name.lower():
                        status = agent_result.get("status", "success") if isinstance(agent_result, dict) else "success"
                        saved_file = self._write_code_generator_output_with_compilation_details(
                            agent.name, 
                            i, 
                            current_input, 
                            agent_result, 
                            status
                        )
                    # Use enhanced reporting for Test Runner
                    elif "test runner" in agent.name.lower():
                        status = agent_result.get("status", "success") if isinstance(agent_result, dict) else "success"
                        saved_file = self._write_test_runner_output_with_results(
                            agent.name, 
                            i, 
                            current_input, 
                            agent_result, 
                            status
                        )
                    else:
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
                    # Save error output as well with enhanced reporting for specific agents
                    if "code generator" in agent.name.lower():
                        status = agent_result.get("status", "error") if isinstance(agent_result, dict) else "error"
                        saved_file = self._write_code_generator_output_with_compilation_details(
                            agent.name, 
                            i, 
                            current_input, 
                            agent_result, 
                            status
                        )
                    elif "test runner" in agent.name.lower():
                        status = agent_result.get("status", "error") if isinstance(agent_result, dict) else "error"
                        saved_file = self._write_test_runner_output_with_results(
                            agent.name, 
                            i, 
                            current_input, 
                            agent_result, 
                            status
                        )
                    else:
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
                    
                    # Notify workflow failure
                    self._notify_workflow_status(
                        "failed",
                        f"Workflow failed at {agent.name}: {agent_result.get('error', 'Unknown error')}",
                        current_agent=agent.name,
                        step=i
                    )
                    
                    # Save final workflow summary even on failure
                    self._save_workflow_summary(workflow_results)
                    return workflow_results
                
                # Prepare input for next agent
                current_input = agent_result  # Pass full agent result to next agent
                print(f"✅ {agent.name} completed successfully")
            
            # Set final results
            workflow_results["final_output"] = current_input
            workflow_results["workflow_status"] = "completed"
            
            # Notify workflow completion
            self._notify_workflow_status(
                "completed",
                "All agents executed successfully",
                current_agent=None,
                step=len(self.agents)
            )
            
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
            
            # Notify workflow error
            self._notify_workflow_status(
                "error",
                f"Workflow error: {str(e)}"
            )
            
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
                
                # Add prompt summary
                f.write(f"\n📝 PROMPT LOGGING:\n")
                f.write("-" * 20 + "\n")
                prompts_folder = os.path.join(self.output_folder, "prompts")
                if os.path.exists(prompts_folder):
                    prompt_files = [f for f in os.listdir(prompts_folder) if f.endswith('.txt')]
                    f.write(f"Total prompts logged: {len(prompt_files)}\n")
                    f.write(f"Prompts saved in: prompts/\n")
                    f.write("Prompt files:\n")
                    for prompt_file in sorted(prompt_files):
                        f.write(f"  - {prompt_file}\n")
                else:
                    f.write("No prompts were logged during this workflow.\n")
            
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
