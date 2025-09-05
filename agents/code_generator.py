from typing import Dict, Any, List
import os
import json
import subprocess
import threading
import time
from datetime import datetime
import jinja2
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .base_agent import BaseAgent
from integrations.langsmith import trace_agent_execution

# Import the new tools
from tools.file_management import FileCreator
from tools.parsing import ProjectStructureParser, CodeBlockExtractor, ScenarioCategorizer
from tools.compilation import CodeCompiler
from tools.language_best_practices_manager import LanguageBestPracticesManager
from tools.project_generators import (
    CSharpProjectGenerator,
    PythonProjectGenerator,
    JavaScriptProjectGenerator,
    TypeScriptProjectGenerator,
    JavaProjectGenerator,
    GoProjectGenerator,
    RustProjectGenerator
)
from tools.prompt_loader import PromptyLoader

# Import pattern-based components
from factories.prompt_factory import PromptStrategyFactory, GenericPromptStrategy
from patterns.language_config import LanguageConfigManager

# Import centralized package versions configuration
from config_package.package_versions import PackageVersions


class CodeGenerator(BaseAgent):
    """
    ╔══════════════════════════════════════════════════════════════════════════════════════╗
    ║                       SCENARIO-BY-SCENARIO CODE GENERATOR                           ║
    ║                    Advanced AI-Powered Code Generation System                        ║
    ╚══════════════════════════════════════════════════════════════════════════════════════╝
    
    🎯 PURPOSE:
    -----------
    The CodeGenerator agent transforms business requirements and scenarios into complete,
    executable, production-ready applications across multiple programming languages using
    a SCENARIO-BY-SCENARIO approach for better control and quality assurance.
    
    🔄 NEW GENERATION MODE: SCENARIO-BY-SCENARIO WITH COMPILATION FEEDBACK
    ----------------------------------------------------------------
    Instead of generating all code at once, this agent now:
    • Processes each scenario individually for better focus
    • Compiles generated code and captures compilation errors
    • Automatically regenerates code when compilation errors are found
    • Uses compilation feedback to improve code quality in subsequent attempts
    • Provides progress tracking and error isolation
    • Allows for individual scenario validation
    • Consolidates results into unified implementation
    • Generates detailed reports for each scenario and compilation attempt
    
    📊 WORKFLOW DIAGRAM:
    -------------------
    
    Input (From DocumentAnalyzer)           Scenario-by-Scenario Process            Output
    ┌─────────────────────────┐           ┌─────────────────────────────┐           ┌──────────────────────┐
    │ • Product Name          │──────────▶│  FOR EACH SCENARIO:         │──────────▶│ • Individual Scenario│
    │ • Programming Language  │           │  1. Extract Single Scenario │           │   Code Files         │
    │ • Business Scenarios    │           │  2. Generate Focused Code   │           │ • Consolidated       │
    │ • Setup Information     │           │  3. Validate & Save         │           │   Implementation     │
    │ • Dependencies          │           │  4. Track Progress          │           │ • Unified Project    │
    └─────────────────────────┘           │                             │           │ • Detailed Reports   │
                                          │  AFTER ALL SCENARIOS:       │           │ • Error Analysis     │
                                          │  5. Consolidate Code        │           └──────────────────────┘
                                          │  6. Create Unified Project  │                      │
                                          │  7. Generate Reports        │                      │
                                          └─────────────────────────────┘                      │
                                                                                               ▼
                                                                               ┌──────────────────────┐
                                                                               │ Ready for Execution  │
                                                                               │ with Full Traceability│
                                                                               └──────────────────────┘
    
    🛠️ CORE TOOLS & COMPONENTS:
    ----------------------------
    
    📁 FILE MANAGEMENT TOOLS:
    • FileCreator           - Creates individual source files with proper encoding
    • ProjectStructureParser - Parses LLM output to understand project organization  
    • CodeBlockExtractor     - Extracts code blocks and files from generated content
    • CodeCompiler           - Compiles generated code and captures compilation errors
    
    🏗️ PROJECT GENERATION TOOLS:
    • CSharpProjectGenerator     - .NET/C# projects (.csproj, NuGet packages)
    • PythonProjectGenerator     - Python projects (requirements.txt, setup.py)
    • JavaScriptProjectGenerator - Node.js projects (package.json, npm)
    • JavaProjectGenerator       - Maven Java projects (pom.xml)
    • GoProjectGenerator         - Go modules (go.mod)
    • RustProjectGenerator       - Cargo Rust projects (Cargo.toml)
    
    🎯 ANALYSIS TOOLS:
    • ScenarioCategorizer   - Analyzes business scenarios for better code generation
    • PackageVersions       - Dynamic dependency detection and version management
    
    🎨 PROMPT SYSTEM:
    • PromptStrategyFactory - Creates language-specific prompt strategies
    • LanguageConfigManager - Manages configurations for supported languages
    
    ✨ SCENARIO-BY-SCENARIO WITH COMPILATION FEEDBACK BENEFITS:
    ----------------------------------------------------------
    ✅ Better Focus         - Each scenario gets dedicated attention
    ✅ Error Isolation      - Failed scenarios don't affect successful ones
    ✅ Progress Tracking    - Real-time progress monitoring
    ✅ Quality Control      - Individual validation and testing
    ✅ Compilation Feedback - Automatic error detection and fixing
    ✅ Self-Healing Code    - Regenerates code until it compiles successfully
    ✅ Detailed Reporting   - Comprehensive status reports per scenario and attempt
    ✅ Traceability         - Clear mapping from requirements to working code
    
    🔄 EXECUTION PROCESS:
    --------------------
    1. INPUT PARSING:        Parse DocumentAnalyzer output (JSON with scenarios)
    2. SCENARIO ITERATION:   Process each scenario individually:
       a. Extract scenario details
       b. Generate focused code
       c. Validate implementation
       d. Save individual results
       e. Track progress
    3. CONSOLIDATION:        Merge all successful scenarios
    4. PROJECT CREATION:     Generate unified project structure
    5. CODE COMPILATION:     Compile generated code and capture errors
    6. REPORT GENERATION:    Create comprehensive status reports
    
    📋 SUPPORTED LANGUAGES:
    -----------------------
    • C#/.NET (8.0+)      - Console apps, web APIs, with NuGet packages
    • Python (3.11+)      - Scripts, web apps, with pip packages  
    • JavaScript (Node 18+) - Console apps, servers, with npm packages
    • Java (17+)          - Maven projects, Spring apps
    • Go (1.21+)          - Modules, web servers
    • Rust (1.70+)        - Cargo projects, CLI tools
    
    📄 OUTPUT FILES:
    ---------------
    • scenario_XX_code.md        - Individual scenario implementations
    • CONSOLIDATED_IMPLEMENTATION.md - Unified code from all scenarios
    • SCENARIO_SUMMARY_REPORT.md - Detailed processing report
    • main.[ext]                 - Consolidated main implementation
    • Individual test files      - Separate test files for each scenario
    • Project configuration files (language-specific)
    """
    
    def __init__(self, llm: Any):
        super().__init__("Code Generator", llm)
        
        # Initialize prompt loader for external prompty files
        self.prompty_loader = PromptyLoader()
        
        # Initialize language best practices manager
        self.language_best_practices_manager = LanguageBestPracticesManager()
        
        # Initialize tools
        self.file_creator = FileCreator()
        self.structure_parser = ProjectStructureParser()
        self.code_extractor = CodeBlockExtractor()
        self.scenario_categorizer = ScenarioCategorizer()
        self.code_compiler = CodeCompiler()  # Add compilation tool
        
        # Initialize language-specific generators
        self.generators = {
            'csharp': CSharpProjectGenerator(),
            'c#': CSharpProjectGenerator(),
            'python': PythonProjectGenerator(),
            'javascript': JavaScriptProjectGenerator(),
            'node.js': JavaScriptProjectGenerator(),
            'js': JavaScriptProjectGenerator(),
            'typescript': TypeScriptProjectGenerator(),
            'ts': TypeScriptProjectGenerator(),
            'java': JavaProjectGenerator(),
            'go': GoProjectGenerator(),
            'rust': RustProjectGenerator()
        }
        
        # Initialize pattern-based prompt system
        self.prompt_factory = PromptStrategyFactory()
        self.config_manager = LanguageConfigManager()
        self.supported_languages = self.prompt_factory.get_all_language_aliases()
        self.log("Using pattern-based prompt generation system")
        
        # Default prompt template (will be set dynamically)
        self.prompt_template = None
        self.chain = None
    
    def _format_scenarios_for_prompt(self, scenarios: list) -> str:
        """Format scenarios for the LLM prompt, handling both simple strings and detailed objects"""
        if not scenarios:
            return "No specific scenarios provided"
        
        formatted_scenarios = []
        
        for i, scenario in enumerate(scenarios, 1):
            if isinstance(scenario, str):
                # Handle old format (simple strings)
                formatted_scenarios.append(f"{i}. {scenario}")
            elif isinstance(scenario, dict):
                # Handle new format (detailed objects)
                name = scenario.get("name", "Unnamed Scenario")
                description = scenario.get("description", "No description provided")
                purpose = scenario.get("purpose", "No purpose specified")
                category = scenario.get("category", "unknown")
                priority = scenario.get("priority", "medium")
                expected_outcome = scenario.get("expectedOutcome", "No expected outcome specified")
                
                scenario_text = f"""{i}. **{name}** [{category.upper()}/{priority.upper()}]
   Description: {description}
   Purpose: {purpose}
   Expected Outcome: {expected_outcome}"""
                formatted_scenarios.append(scenario_text)
            else:
                # Fallback for unexpected format
                formatted_scenarios.append(f"{i}. {str(scenario)}")
        
        return "\n\n".join(formatted_scenarios)
    
    def _log_scenario_summary(self, scenarios: list) -> None:
        """Log a detailed summary of scenarios"""
        if not scenarios:
            self.log("  - No scenarios provided")
            return
        
        # Check if scenarios are detailed objects or simple strings
        if scenarios and isinstance(scenarios[0], dict):
            # New detailed format
            categories = {}
            priorities = {}
            
            self.log("  📋 Detailed Scenarios:")
            for i, scenario in enumerate(scenarios, 1):
                name = scenario.get("name", "Unnamed")
                category = scenario.get("category", "unknown")
                priority = scenario.get("priority", "medium")
                
                categories[category] = categories.get(category, 0) + 1
                priorities[priority] = priorities.get(priority, 0) + 1
                
                self.log(f"     {i}. {name} [{category}/{priority}]")
            
            self.log(f"  - Categories: {dict(categories)}")
            self.log(f"  - Priorities: {dict(priorities)}")
        else:
            # Old simple format
            scenario_preview = [str(s)[:50] + "..." if len(str(s)) > 50 else str(s) for s in scenarios[:3]]
            self.log(f"  - Scenarios: {scenario_preview}{'...' if len(scenarios) > 3 else ''}")
    
    def _get_language_specific_prompt(self, language: str, context: Dict[str, Any] = None) -> str:
        """Get language-specific prompt using the modern pattern-based system"""
        strategy = self.prompt_factory.create_strategy(language)
        if not strategy:
            self.log(f"No strategy found for {language}, using generic strategy")
            strategy = GenericPromptStrategy(language)
        
        return strategy.generate_prompt(context or {})
    
    @trace_agent_execution("Code Generator")
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """Generate code one scenario at a time with compilation feedback loop"""
        self.log(f"Starting scenario-by-scenario code generation with compilation feedback")
        
        try:
            # Parse the input from DocumentAnalyzer
            if isinstance(input_data, dict):
                analysis_data = input_data
            elif isinstance(input_data, str):
                try:
                    analysis_data = json.loads(input_data)
                except json.JSONDecodeError:
                    # If it's not JSON, treat as raw text (fallback to Python as it's supported)
                    analysis_data = {
                        "language": "python",
                        "productName": "Unknown",
                        "version": "latest", 
                        "scenarioList": ["Basic functionality"],
                        "setupInstructions": {
                            "installation": "Standard installation",
                            "dependencies": [],
                            "configuration": "Default configuration",
                            "gettingStarted": "Run the test file"
                        }
                    }
            else:
                raise ValueError("Input data must be either a dictionary or JSON string")
            
            # Extract information from analysis
            language = analysis_data.get("language", "python").lower()
            product_name = analysis_data.get("productName", "Unknown")
            version = analysis_data.get("version", "latest")
            scenarios = analysis_data.get("scenarioList", [])
            setup_info = analysis_data.get("setupInstructions", {})
            
            # Validate language support
            if language not in self.supported_languages:
                self.log(f"Unsupported language: {language}. Supported languages: {', '.join(self.supported_languages)}")
                return {
                    "agent": self.name,
                    "input": input_data,
                    "output": None,
                    "status": "error",
                    "error": f"Unsupported language: {language}. Supported languages: {', '.join(self.supported_languages)}"
                }
            
            # Log the input analysis data
            self.log(f"📊 Input Analysis Summary:")
            self.log(f"  - Language: {language}")
            self.log(f"  - Product Name: {product_name}")
            self.log(f"  - Version: {version}")
            self.log(f"  - Number of scenarios: {len(scenarios)}")
            self._log_scenario_summary(scenarios)
            
            # Initialize project structure first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = product_name.replace(" ", "_").lower()
            project_dir = os.path.join("workflow_outputs", f"{project_name}_{timestamp}")
            os.makedirs(project_dir, exist_ok=True)
            
            # Execute the compilation feedback loop
            final_result = self._execute_with_compilation_feedback(
                scenarios, language, product_name, version, setup_info, project_dir, analysis_data
            )
            
            self.log("Code generation with compilation feedback completed")
            return final_result
            
        except Exception as e:
            self.log(f"Error during code generation with compilation feedback: {str(e)}")
            return {
                "agent": self.name,
                "input": input_data,
                "output": None,
                "status": "error",
                "error": str(e)
            }
    
    def _execute_with_compilation_feedback(self, scenarios: list, language: str, product_name: str, 
                                         version: str, setup_info: dict, project_dir: str, 
                                         analysis_data: dict) -> Dict[str, Any]:
        """
        Execute code generation with compilation feedback loop.
        Regenerates code until it compiles successfully or max attempts reached.
        """
        MAX_COMPILATION_ATTEMPTS = 3
        compilation_attempts = []
        
        for attempt in range(1, MAX_COMPILATION_ATTEMPTS + 1):
            self.log(f"🔄 Compilation attempt {attempt}/{MAX_COMPILATION_ATTEMPTS}")
            
            if attempt == 1:
                # FIRST ATTEMPT: Generate all code based on document analyzer scenarios
                self.log(f"🚀 First attempt: Generating all scenarios from document analysis ({len(scenarios)} scenarios)")
                scenario_results = self._generate_scenarios_individually(
                    scenarios, language, product_name, version, setup_info, project_dir, analysis_data, attempt=1
                )
                
                # Consolidate all generated code
                consolidated_content = self._consolidate_scenario_code(scenario_results, language, product_name)
                
                # Create final project structure with consolidated code
                project_files = self._create_consolidated_project(
                    consolidated_content,
                    scenario_results,
                    language,
                    product_name,
                    scenarios,
                    project_dir,
                    analysis_data
                )
                
                # Log that compilation happened during project creation
                self.log(f"🔨 [Attempt {attempt}] Initial compilation completed during project creation")
                
            else:
                # SUBSEQUENT ATTEMPTS: Only fix scenarios with compilation errors
                self.log(f"🔧 Attempt {attempt}: Fixing ONLY scenarios with compilation errors (selective retry)")
                
                # Identify which specific scenarios have compilation errors
                scenarios_with_errors = self._identify_scenarios_with_compilation_errors(
                    compilation_result, scenarios, project_dir, language
                )
                
                if scenarios_with_errors:
                    self.log(f"📋 Found {len(scenarios_with_errors)} scenarios with compilation errors to fix")
                    
                    # Only regenerate the problematic scenarios, keep others unchanged
                    updated_scenario_results = self._regenerate_only_failed_scenarios(
                        scenarios_with_errors, scenario_results, language, 
                        product_name, version, setup_info, project_dir, analysis_data, compilation_result, attempt
                    )
                    
                    # Update only the files for scenarios that were regenerated
                    project_files = self._update_project_files_for_fixed_scenarios(
                        project_files, updated_scenario_results, scenarios_with_errors, 
                        language, project_dir
                    )
                    
                    # Merge the fixed scenarios back into the main results
                    self._merge_fixed_scenarios_into_results(scenario_results, updated_scenario_results)
                    
                else:
                    self.log("⚠️ No specific scenarios identified with errors - performing minimal global fixes")
                    # Apply global fixes without regenerating any scenarios
                    project_files = self._apply_global_compilation_fixes(
                        project_files, compilation_result, language, project_dir
                    )
            
            # CRITICAL: Always re-compile after any changes to verify fixes
            self.log(f"🔨 [Attempt {attempt}] Running compilation to verify changes...")
            fresh_compilation_result = self._compile_generated_project(project_dir, language)
            project_files["compilation_result"] = fresh_compilation_result
            compilation_result = fresh_compilation_result
            
            # Enhanced compilation attempt tracking with detailed error information
            attempt_info = {
                "attempt": attempt,
                "compilation_result": compilation_result,
                "timestamp": datetime.now().isoformat(),
                "scenario_count": len(scenarios),
                "enhanced_scenarios": [self._extract_scenario_summary(scenario, i+1) for i, scenario in enumerate(scenarios)],
                "detailed_error_analysis": self._create_detailed_error_analysis(compilation_result, attempt),
                "changes_from_previous": self._analyze_changes_from_previous_attempt(compilation_attempts, compilation_result) if attempt > 1 else None
            }
            compilation_attempts.append(attempt_info)
            
            # Check if compilation was successful
            if compilation_result.get("success", False):
                self.log(f"✅ Code compiled successfully on attempt {attempt}")
                
                # Return successful result
                final_result = {
                    "agent": self.name,
                    "input": analysis_data,
                    "output": consolidated_content,
                    "project_files": project_files,
                    "scenario_results": scenario_results,
                    "language": language,
                    "product_name": product_name,
                    "simple_report": project_files.get("simple_report"),
                    "code_path": project_dir,
                    "status": "success",
                    "generation_mode": "scenario_by_scenario_with_compilation_feedback",
                    "total_scenarios_processed": len(scenario_results["successful"]) + len(scenario_results["failed"]),
                    "compilation_attempts": compilation_attempts,
                    "successful_attempt": attempt
                }
                
                # Create enhanced scenario summary report with compilation details
                self._create_enhanced_scenario_summary_report(scenario_results, compilation_attempts, project_dir, language)
                
                return final_result
            
            else:
                # Compilation failed - prepare for next attempt
                error_count = compilation_result.get("error_analysis", {}).get("total_errors", 0)
                warning_count = compilation_result.get("error_analysis", {}).get("total_warnings", 0)
                self.log(f"❌ Compilation failed on attempt {attempt}: {error_count} errors, {warning_count} warnings")
                
                if attempt < MAX_COMPILATION_ATTEMPTS:
                    self.log(f"🔧 Preparing for next attempt with selective scenario regeneration...")
                    
                    # Note: We don't enhance all scenarios globally anymore
                    # Instead, we identify and fix only the problematic ones in the next iteration
                    
                    # Clean up failed files for next attempt
                    self._cleanup_failed_compilation_files(project_dir, language)
                    
                else:
                    self.log(f"🚫 Maximum compilation attempts ({MAX_COMPILATION_ATTEMPTS}) reached. Returning with compilation errors.")
        
        # FINAL COMPILATION CHECK: Ensure we have the most recent compilation status
        self.log(f"🔨 Final compilation check to confirm current status...")
        final_compilation_result = self._compile_generated_project(project_dir, language)
        project_files["compilation_result"] = final_compilation_result
        compilation_result = final_compilation_result
        
        # All attempts failed - return with compilation errors
        final_result = {
            "agent": self.name,
            "input": analysis_data,
            "output": consolidated_content,
            "project_files": project_files,
            "scenario_results": scenario_results,
            "language": language,
            "product_name": product_name,
            "simple_report": project_files.get("simple_report"),
            "code_path": project_dir,
            "status": "compilation_failed",
            "generation_mode": "scenario_by_scenario_with_compilation_feedback",
            "total_scenarios_processed": len(scenario_results["successful"]) + len(scenario_results["failed"]),
            "compilation_attempts": compilation_attempts,
            "final_compilation_errors": compilation_result,
            "error": f"Code generation completed but compilation failed after {MAX_COMPILATION_ATTEMPTS} attempts"
        }
        
        # Create enhanced scenario summary report with compilation details
        self._create_enhanced_scenario_summary_report(scenario_results, compilation_attempts, project_dir, language)
        
        return final_result
    
    def _generate_scenarios_individually(self, scenarios: list, language: str, product_name: str, version: str, setup_info: dict, project_dir: str, analysis_data: dict, attempt: int = 1) -> Dict[str, Any]:
        """Generate code for each scenario individually with progress tracking"""
        results = {
            "successful": [],
            "failed": [],
            "total_processed": 0,
            "generation_details": []
        }
        
        self.log(f"🔄 Processing {len(scenarios)} scenarios individually (Attempt {attempt} - {'Initial Code Generation' if attempt == 1 else 'Error Fixing'})...")
        
        # Get context for prompt generation
        detected_dependencies = PackageVersions.detect_dependencies_from_scenario(analysis_data)
        test_packages = PackageVersions.get_test_packages_with_cosmosdb(language, analysis_data)
        primary_test_framework = PackageVersions.get_primary_test_framework(language)
        
        context = {
            'dotnet_version': PackageVersions.get_language_version('dotnet'),
            'java_version': PackageVersions.get_language_version('java'),
            'node_version': PackageVersions.get_language_version('node'),
            'python_version': PackageVersions.get_language_version('python'),
            'go_version': PackageVersions.get_language_version('go'),
            'rust_version': PackageVersions.get_language_version('rust'),
            'test_packages': test_packages,
            'dependencies': detected_dependencies.get(language.lower(), {}),
            'primary_test_framework': primary_test_framework,
            'scenario_based_packages': True
        }
        
        # Load scenario generation prompt from prompty file
        if context and context.get('errors'):
            # Use error fix regeneration prompt for scenarios with compilation errors
            prompt_template = self.prompty_loader.create_prompt_template(
                "code_generator", "error_fix_regeneration"
            )
            # Get LLM with prompty-specific settings
            llm_for_chain = self.prompty_loader.create_llm_with_prompty_settings(
                self.llm, "code_generator", "error_fix_regeneration"
            )
        else:
            # Use standard scenario generation prompt
            prompt_template = self.prompty_loader.create_prompt_template(
                "code_generator", "scenario_generation"
            )
            # Get LLM with prompty-specific settings
            llm_for_chain = self.prompty_loader.create_llm_with_prompty_settings(
                self.llm, "code_generator", "scenario_generation"
            )
        
        if not prompt_template:
            results["failed"].append({
                "error": f"No prompt template available for language: {language}",
                "scenario_index": "all"
            })
            return results
        
        # Load scenario generation prompt from prompty file
        if context and context.get('errors'):
            # Use error fix regeneration prompt for scenarios with compilation errors
            prompt_template = self.prompty_loader.create_prompt_template(
                "code_generator", "error_fix_regeneration"
            )
        else:
            # Use standard scenario generation prompt
            prompt_template = self.prompty_loader.create_prompt_template(
                "code_generator", "scenario_generation"
            )
        
        chain = prompt_template | llm_for_chain | StrOutputParser()
        
        # Process each scenario individually
        for i, scenario in enumerate(scenarios, 1):
            try:
                self.log(f"📝 [Attempt {attempt}] {'🆕 Generating' if attempt == 1 else '🔧 Fixing'} scenario {i}/{len(scenarios)}: {self._get_scenario_name(scenario)}")
                
                # Format single scenario for prompt
                scenario_text = self._format_single_scenario_for_prompt(scenario, i)
                setup_info_text = json.dumps(setup_info, indent=2)
                
                # Get language-specific testing framework and best practices
                testing_framework = self._get_testing_framework(language)
                # Build unified, non-redundant language guidelines
                language_guidelines = self.language_best_practices_manager.get_language_guidelines(
                    language=language,
                    testing_framework=testing_framework
                )
                product_specific_guidance = self._get_product_specific_guidance(product_name, language, version)
                
                # Prepare prompt variables for single scenario
                prompt_vars = {
                    "language": language.upper(),
                    "product_name": product_name,
                    "testing_framework": testing_framework,
                    "language_guidelines": language_guidelines,
                    "product_specific_guidance": product_specific_guidance,
                    "version": version,
                    "scenario": scenario_text,
                    "setup_info": setup_info_text,
                    "scenario_index": i,
                    "total_scenarios": len(scenarios)
                }
                
                # Log the actual prompt that will be sent to LLM
                # Use Jinja2 rendering since prompt_template uses jinja2 format
                jinja_template = jinja2.Template(prompt_template.template)
                actual_prompt = jinja_template.render(**prompt_vars)
                scenario_name = self._get_scenario_name(scenario).replace(" ", "_").replace("/", "_")
                self.log_prompt_to_file(
                    actual_prompt, 
                    "scenario_generation", 
                    f"scenario_{i}_{scenario_name}"
                )
                
                # Generate code for this specific scenario
                generated_content = chain.invoke(prompt_vars)
                
                # Extract and save individual code files for this scenario
                scenario_files = self._extract_scenario_code_files(
                    generated_content, project_dir, language, i, self._get_scenario_name(scenario)
                )
                
                # Track successful generation
                scenario_detail = {
                    "scenario_index": i,
                    "scenario_name": self._get_scenario_name(scenario),
                    "generated_content": generated_content,
                    "code_files": scenario_files,
                    "content_length": len(generated_content),
                    "generation_time": datetime.now().isoformat()
                }
                
                results["successful"].append(scenario_detail)
                results["generation_details"].append(scenario_detail)
                
                files_count = len(scenario_files)
                self.log(f"✅ [Attempt {attempt}] Scenario {i} completed successfully ({files_count} code files created)")
                
                # Small delay between scenarios to avoid overwhelming the LLM
                time.sleep(0.5)
                
            except Exception as e:
                error_detail = {
                    "scenario_index": i,
                    "scenario_name": self._get_scenario_name(scenario),
                    "error": str(e),
                    "generation_time": datetime.now().isoformat()
                }
                
                results["failed"].append(error_detail)
                results["generation_details"].append(error_detail)
                
                self.log(f"❌ [Attempt {attempt}] Scenario {i} failed: {str(e)}")
            
            results["total_processed"] += 1
        
        # Log summary
        success_count = len(results["successful"])
        failure_count = len(results["failed"])
        total_scenarios = len(scenarios)
        
        self.log(f"🎯 [Attempt {attempt}] Scenario Generation Summary:")
        self.log(f"  ✅ Successful: {success_count}/{total_scenarios}")
        self.log(f"  ❌ Failed: {failure_count}/{total_scenarios}")
        
        # Avoid division by zero
        if total_scenarios > 0:
            success_rate = (success_count / total_scenarios * 100)
            self.log(f"  📊 Success Rate: {success_rate:.1f}%")
        else:
            self.log(f"  📊 Success Rate: N/A (no scenarios to process)")
        
        return results
    
    def _format_single_scenario_for_prompt(self, scenario: Any, index: int) -> str:
        """Format a single scenario for the LLM prompt, including compilation error context if available"""
        if isinstance(scenario, str):
            return f"**Scenario {index}:** {scenario}"
        elif isinstance(scenario, dict):
            name = scenario.get("name", f"Scenario {index}")
            description = scenario.get("description", "No description provided")
            purpose = scenario.get("purpose", "No purpose specified")
            category = scenario.get("category", "unknown")
            priority = scenario.get("priority", "medium")
            expected_outcome = scenario.get("expectedOutcome", "No expected outcome specified")
            
            # Check for compilation context from previous attempts
            compilation_context = scenario.get("compilation_context", {})
            
            scenario_text = f"""**Scenario {index}: {name}** [{category.upper()}/{priority.upper()}]

**Description:** {description}

**Purpose:** {purpose}

**Expected Outcome:** {expected_outcome}

**Implementation Focus:** Create code that specifically addresses this scenario's requirements and validates the expected outcome."""
            
            # Add compilation error context if available
            if compilation_context:
                regenerate_mode = compilation_context.get("regenerate_mode", "regenerate")
                previous_errors = compilation_context.get("previous_errors", [])
                parsed_error_details = compilation_context.get("parsed_error_details", [])
                detailed_error_breakdown = compilation_context.get("detailed_error_breakdown", {})
                error_summary = compilation_context.get("error_summary", "")
                fix_instructions = compilation_context.get("fix_instructions", [])
                specific_code_fixes = compilation_context.get("specific_code_fixes", [])
                
                if regenerate_mode == "fix_existing_code":
                    scenario_text += f"""

**🚨 CRITICAL: FIX COMPILATION ERRORS - FOCUS ON ERROR RESOLUTION**

{error_summary}

**🔧 DETAILED COMPILATION ERRORS TO FIX ({len(previous_errors)} total):**
"""
                    for i, error in enumerate(previous_errors[:10], 1):  # Show top 10 errors
                        scenario_text += f"{i}. {error}\n"
                    
                    # Add parsed error details for better understanding
                    if parsed_error_details:
                        scenario_text += f"""
**📋 ERROR ANALYSIS WITH SUGGESTED FIXES:**
"""
                        for i, error_detail in enumerate(parsed_error_details[:5], 1):  # Show top 5 parsed errors
                            scenario_text += f"{i}. **{error_detail.get('error_code', 'Unknown')}** in {error_detail.get('file_name', 'unknown file')}\n"
                            scenario_text += f"   Error: {error_detail.get('description', 'No description')}\n"
                            if error_detail.get('suggested_fix'):
                                scenario_text += f"   Fix: {error_detail.get('suggested_fix')}\n"
                            scenario_text += "\n"
                    
                    # Add error breakdown summary
                    if detailed_error_breakdown:
                        critical_errors = detailed_error_breakdown.get("critical_errors", [])
                        if critical_errors:
                            scenario_text += f"""
**🚨 CRITICAL ERRORS BLOCKING COMPILATION ({len(critical_errors)}):**
"""
                            for critical_error in critical_errors:
                                scenario_text += f"- {critical_error.get('error', 'Unknown error')} at {critical_error.get('location', 'unknown location')}\n"
                                scenario_text += f"  → {critical_error.get('fix', 'No fix suggested')}\n"
                    
                    if specific_code_fixes:
                        scenario_text += f"""
**💡 EXACT CODE FIXES REQUIRED:**
"""
                        for fix in specific_code_fixes:
                            scenario_text += f"- {fix}\n"
                    
                    if fix_instructions:
                        scenario_text += f"""
**📋 GENERAL FIX INSTRUCTIONS:**
"""
                        for instruction in fix_instructions:
                            scenario_text += f"- {instruction}\n"
                    
                    scenario_text += f"""
**⚠️ MANDATORY REQUIREMENTS FOR THIS COMPILATION FIX ATTEMPT:**
1. **Address EACH compilation error listed above specifically**
2. **Use the exact error messages to understand what needs to be fixed**
3. **Follow the suggested fixes provided for each error**
4. **Ensure ALL required using/import statements are present**
5. **Verify ALL method calls exist in the target SDK before using them**
6. **Use proper type conversions and safe operations**
7. **Handle collections correctly (no direct indexing on iterators)**
8. **Add proper NuGet package/dependency references in comments**
9. **Test your generated code logic against the specific error patterns**
10. **Focus on COMPILATION SUCCESS - the code must compile without errors**
11. **Verify referred function or variable is actually exist, you can Cosmos DB official doc for this.**

**🎯 SUCCESS CRITERIA:**
- ALL {len(previous_errors)} compilation errors are resolved
- Code compiles successfully without any warnings
- All SDK method calls are verified to exist
- Proper error handling and type safety implemented
- Clean, working code that passes compilation"""
                else:
                    # Fallback to regeneration mode with error context
                    scenario_text += f"""

**⚠️ COMPILATION FEEDBACK FROM PREVIOUS ATTEMPT:**

{error_summary}

**Previous Compilation Errors to Address:**
"""
                    for i, error in enumerate(previous_errors[:5], 1):  # Show top 5 errors
                        scenario_text += f"{i}. {error}\n"
                    
                    if fix_instructions:
                        scenario_text += f"""
**🔧 Specific Fix Instructions:**
"""
                        for instruction in fix_instructions:
                            scenario_text += f"- {instruction}\n"
                    
                    scenario_text += f"""
**IMPORTANT:** Please regenerate the code addressing these compilation errors. Focus on:
1. Fixing the specific errors mentioned above
2. Ensuring proper syntax and type safety
3. Adding missing imports/dependencies
4. Following language best practices
5. Verifying all method calls exist in the target SDK"""
            
            return scenario_text
        else:
            return f"**Scenario {index}:** {str(scenario)}"
    
    def _get_testing_framework(self, language: str) -> str:
        """Get the appropriate testing framework for the given language"""
        language_lower = language.lower()
        
        testing_frameworks = {
            'c#': 'NUnit testing framework with [Test], [TestFixture], Assert.That() syntax',
            'csharp': 'NUnit testing framework with [Test], [TestFixture], Assert.That() syntax',
            'python': 'pytest with fixtures and assert statements',
            'javascript': 'Jest with describe(), it(), expect() patterns',
            'node.js': 'Jest with describe(), it(), expect() patterns',
            'js': 'Jest with describe(), it(), expect() patterns',
            'java': 'JUnit 5 with @Test, assertEquals() methods',
            'go': 'built-in testing package with Test functions',
            'rust': 'built-in test framework with #[test] attributes'
        }
        
        return testing_frameworks.get(language_lower, f'the standard testing framework for {language}')
    
    def _get_language_best_practices(self, language: str, testing_framework: str = None) -> str:
        """Deprecated: retained for backward-compatibility; use get_language_guidelines instead."""
        if testing_framework is None:
            testing_framework = self._get_testing_framework(language)
        return self.language_best_practices_manager.get_language_guidelines(
            language=language,
            testing_framework=testing_framework
        )
    
    def _get_product_specific_guidance(self, product_name: str, language: str = "", version: str = "") -> str:
        """Get product-specific guidance for SDK/API usage."""
        return self.language_best_practices_manager.get_product_specific_guidance(
            product_name, language, version
        )

    def _extract_scenario_code_files(self, generated_content: str, project_dir: str, language: str, scenario_index: int, scenario_name: str) -> List[str]:
        """Extract and save only test files for each scenario in the same project directory"""
        import re
        
        extension_mapping = {
            'csharp': '.cs', 'c#': '.cs', 'python': '.py', 
            'javascript': '.js', 'node.js': '.js', 'js': '.js',
            'java': '.java', 'go': '.go', 'rust': '.rs'
        }
        
        default_extension = extension_mapping.get(language.lower(), '.txt')
        created_files = []
        
        try:
            # Use the main project directory (no scenario-specific subdirectories)
            scenario_dir = project_dir
            
            # Create a clean class name from scenario name for the test
            clean_scenario_name = self._create_class_name_from_scenario(scenario_name)
            
            # Extract ONLY test implementation - skip main implementation
            test_pattern = r'### Test Implementation.*?```[a-zA-Z]*\n(.*?)```'
            test_matches = re.findall(test_pattern, generated_content, re.DOTALL | re.IGNORECASE)
            
            if test_matches:
                test_file = os.path.join(scenario_dir, f"{clean_scenario_name}Test{default_extension}")
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(f"// {clean_scenario_name}Test - Test for scenario: {scenario_name}\n")
                    f.write(f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    # Replace generic test class names with our clean scenario name
                    test_content = test_matches[0].strip()
                    test_content = self._update_test_class_names_in_code(test_content, clean_scenario_name, language)
                    f.write(test_content)
                created_files.append(test_file)
                self.log(f"🧪 Created test file: {clean_scenario_name}Test{default_extension}")
            else:
                # If no specific test pattern found, look for any test-related code blocks
                test_keywords = ['test', 'Test', 'TEST', 'spec', 'Spec']
                code_blocks = re.findall(rf'```(?:{language}|[a-zA-Z]*)\n(.*?)```', generated_content, re.DOTALL)
                
                for block in code_blocks:
                    # Check if this block contains test-related keywords
                    if any(keyword in block for keyword in test_keywords):
                        test_file = os.path.join(scenario_dir, f"{clean_scenario_name}Test{default_extension}")
                        with open(test_file, 'w', encoding='utf-8') as f:
                            f.write(f"// {clean_scenario_name}Test - Test for scenario: {scenario_name}\n")
                            f.write(f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                            
                            # Update class names in test code
                            updated_test_code = self._update_test_class_names_in_code(block.strip(), clean_scenario_name, language)
                            f.write(updated_test_code)
                        created_files.append(test_file)
                        self.log(f"🧪 Created test file: {clean_scenario_name}Test{default_extension}")
                        break  # Only create one test file per scenario
            
            # Extract configuration files only if they are test-related (e.g., test configurations)
            test_config_patterns = [
                r'### ([^#\n]*test[^#\n]*\.(?:json|xml|toml|yml|yaml|config|properties))[^#\n]*.*?```[a-zA-Z]*\n(.*?)```',
                r'### ([^#\n]*Test[^#\n]*\.(?:json|xml|toml|yml|yaml|config|properties))[^#\n]*.*?```[a-zA-Z]*\n(.*?)```'
            ]
            
            for pattern in test_config_patterns:
                config_matches = re.findall(pattern, generated_content, re.DOTALL | re.IGNORECASE)
                for filename, config_content in config_matches:
                    filename = self._sanitize_filename(filename.strip())
                    # Prefix config files with test scenario name
                    config_filename = f"{clean_scenario_name}Test_{filename}" if not filename.startswith(clean_scenario_name) else filename
                    config_file = os.path.join(scenario_dir, config_filename)
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(config_content.strip())
                    created_files.append(config_file)
                    self.log(f"⚙️ Created test config file: {config_filename}")
            
            # If no test files were created, create a basic test file from scenario description
            if not created_files:
                test_file = os.path.join(scenario_dir, f"{clean_scenario_name}Test{default_extension}")
                
                # Create a basic test template based on the language
                test_template = self._create_basic_test_template(clean_scenario_name, scenario_name, language)
                
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(f"// {clean_scenario_name}Test - Test for scenario: {scenario_name}\n")
                    f.write(f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(test_template)
                
                created_files.append(test_file)
                self.log(f"🧪 Created basic test file: {clean_scenario_name}Test{default_extension}")
            
            self.log(f"📁 Created {len(created_files)} test files in project directory for scenario: {clean_scenario_name}")
            
        except Exception as e:
            self.log(f"❌ Error extracting test files for scenario {scenario_index}: {str(e)}")
        
        return created_files
    
    def _create_class_name_from_scenario(self, scenario_name: str) -> str:
        """Create a valid class name from scenario name"""
        import re
        
        # Remove common prefixes and clean up the name
        clean_name = scenario_name.strip()
        
        # Remove common test-related words that might be at the beginning
        prefixes_to_remove = ['test', 'verify', 'ensure', 'check', 'validate']
        words = clean_name.split()
        
        if words and words[0].lower() in prefixes_to_remove:
            words = words[1:]
        
        # Join words and create PascalCase
        if words:
            clean_name = ''.join(word.capitalize() for word in words)
        else:
            clean_name = scenario_name.replace(' ', '')
        
        # Remove invalid characters for class names
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', clean_name)
        
        # Ensure it starts with a letter
        if clean_name and not clean_name[0].isalpha():
            clean_name = 'Scenario' + clean_name
            
        # Ensure it's not empty
        if not clean_name:
            clean_name = 'ScenarioImplementation'
            
        return clean_name
    
    def _update_class_names_in_code(self, code_content: str, class_name: str, language: str) -> str:
        """Update generic class names in code to use the specific scenario class name"""
        import re
        
        # Common generic class names to replace
        generic_names = [
            'MainImplementation', 'Implementation', 'MainClass', 'TestClass',
            'ExampleClass', 'SampleClass', 'MyClass', 'Program', 'Main'
        ]
        
        updated_code = code_content
        
        for generic_name in generic_names:
            if language.lower() in ['csharp', 'c#']:
                # Replace class declarations
                updated_code = re.sub(
                    rf'\bclass\s+{generic_name}\b',
                    f'class {class_name}',
                    updated_code,
                    flags=re.IGNORECASE
                )
                # Replace constructor calls
                updated_code = re.sub(
                    rf'\bnew\s+{generic_name}\s*\(',
                    f'new {class_name}(',
                    updated_code,
                    flags=re.IGNORECASE
                )
            elif language.lower() == 'python':
                # Replace class declarations
                updated_code = re.sub(
                    rf'\bclass\s+{generic_name}\b',
                    f'class {class_name}',
                    updated_code,
                    flags=re.IGNORECASE
                )
            elif language.lower() in ['java']:
                # Replace class declarations and constructors
                updated_code = re.sub(
                    rf'\bclass\s+{generic_name}\b',
                    f'class {class_name}',
                    updated_code,
                    flags=re.IGNORECASE
                )
                # Replace constructor declarations
                updated_code = re.sub(
                    rf'\bpublic\s+{generic_name}\s*\(',
                    f'public {class_name}(',
                    updated_code,
                    flags=re.IGNORECASE
                )
        
        return updated_code
    
    def _update_test_class_names_in_code(self, test_code: str, base_class_name: str, language: str) -> str:
        """Update generic test class names to match the scenario"""
        import re
        
        test_class_name = f"{base_class_name}Tests"
        
        # Common generic test class names
        generic_test_names = [
            'MainImplementationTests', 'ImplementationTests', 'MainClassTests',
            'TestClass', 'Tests', 'UnitTests', 'TestSuite'
        ]
        
        updated_code = test_code
        
        for generic_name in generic_test_names:
            if language.lower() in ['csharp', 'c#']:
                # Replace test class declarations
                updated_code = re.sub(
                    rf'\bclass\s+{generic_name}\b',
                    f'class {test_class_name}',
                    updated_code,
                    flags=re.IGNORECASE
                )
            elif language.lower() == 'python':
                # Replace test class declarations
                updated_code = re.sub(
                    rf'\bclass\s+{generic_name}\b',
                    f'class {test_class_name}',
                    updated_code,
                    flags=re.IGNORECASE
                )
            elif language.lower() == 'java':
                # Replace test class declarations
                updated_code = re.sub(
                    rf'\bclass\s+{generic_name}\b',
                    f'class {test_class_name}',
                    updated_code,
                    flags=re.IGNORECASE
                )
        
        # Also update references to the main class
        main_class_references = [
            'MainImplementation', 'Implementation', 'MainClass'
        ]
        
        for ref in main_class_references:
            updated_code = re.sub(
                rf'\b{ref}\b',
                base_class_name,
                updated_code,
                flags=re.IGNORECASE
            )
        
        return updated_code

    def _create_basic_test_template(self, class_name: str, scenario_name: str, language: str) -> str:
        """Create a basic test template when no specific test code is found"""
        
        if language.lower() in ['csharp', 'c#']:
            return f"""using System;
using NUnit.Framework;

namespace TestProject.Tests
{{
    [TestFixture]
    public class {class_name}Test
    {{
        [Test]
        public void {class_name}_ShouldExecuteSuccessfully()
        {{
            // Arrange
            // TODO: Set up test data and dependencies for: {scenario_name}
            
            // Act
            // TODO: Execute the scenario logic
            
            // Assert
            // TODO: Verify the expected outcome
            Assert.That(true, Is.True, "Test implementation needed for: {scenario_name}");
        }}
        
        [Test]
        public void {class_name}_ShouldHandleEdgeCases()
        {{
            // Arrange
            // TODO: Set up edge case test data
            
            // Act & Assert
            // TODO: Test boundary conditions and error cases
            Assert.That(true, Is.True, "Edge case testing needed for: {scenario_name}");
        }}
    }}
}}"""
        
        elif language.lower() == 'python':
            return f"""import unittest

class {class_name}Test(unittest.TestCase):
    \"\"\"Test class for scenario: {scenario_name}\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures before each test method.\"\"\"
        # TODO: Initialize test data and dependencies
        pass
    
    def test_{class_name.lower()}_should_execute_successfully(self):
        \"\"\"Test successful execution of {scenario_name}\"\"\"
        # Arrange
        # TODO: Set up test data and dependencies
        
        # Act
        # TODO: Execute the scenario logic
        
        # Assert
        # TODO: Verify the expected outcome
        self.assertTrue(True, "Test implementation needed for: {scenario_name}")
    
    def test_{class_name.lower()}_should_handle_edge_cases(self):
        \"\"\"Test edge cases for {scenario_name}\"\"\"
        # Arrange
        # TODO: Set up edge case test data
        
        # Act & Assert
        # TODO: Test boundary conditions and error cases
        self.assertTrue(True, "Edge case testing needed for: {scenario_name}")
    
    def tearDown(self):
        \"\"\"Clean up after each test method.\"\"\"
        # TODO: Clean up test data and resources
        pass

if __name__ == '__main__':
    unittest.main()"""
        
        elif language.lower() in ['javascript', 'js', 'node.js']:
            return f"""const {{ describe, it, expect, beforeEach, afterEach }} = require('jest');

describe('{class_name}Test', () => {{
    beforeEach(() => {{
        // TODO: Set up test data and dependencies before each test
    }});
    
    afterEach(() => {{
        // TODO: Clean up after each test
    }});
    
    it('should execute {scenario_name} successfully', () => {{
        // Arrange
        // TODO: Set up test data and dependencies
        
        // Act
        // TODO: Execute the scenario logic
        
        // Assert
        // TODO: Verify the expected outcome
        expect(true).toBe(true); // TODO: Replace with actual test
    }});
    
    it('should handle edge cases for {scenario_name}', () => {{
        // Arrange
        // TODO: Set up edge case test data
        
        // Act & Assert
        // TODO: Test boundary conditions and error cases
        expect(true).toBe(true); // TODO: Replace with actual test
    }});
}});"""
        
        elif language.lower() == 'java':
            return f"""import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

class {class_name}Test {{
    
    @BeforeEach
    void setUp() {{
        // TODO: Set up test data and dependencies before each test
    }}
    
    @AfterEach
    void tearDown() {{
        // TODO: Clean up after each test
    }}
    
    @Test
    void {class_name.lower()}_ShouldExecuteSuccessfully() {{
        // Arrange
        // TODO: Set up test data and dependencies for: {scenario_name}
        
        // Act
        // TODO: Execute the scenario logic
        
        // Assert
        // TODO: Verify the expected outcome
        assertTrue(true, "Test implementation needed for: {scenario_name}");
    }}
    
    @Test
    void {class_name.lower()}_ShouldHandleEdgeCases() {{
        // Arrange
        // TODO: Set up edge case test data
        
        // Act & Assert
        // TODO: Test boundary conditions and error cases
        assertTrue(true, "Edge case testing needed for: {scenario_name}");
    }}
}}"""
        
        else:
            # Generic template for other languages
            return f"""// {class_name}Test - Test for scenario: {scenario_name}
// TODO: Implement test logic for this scenario

// Test case 1: Successful execution
// TODO: Set up test data and dependencies
// TODO: Execute the scenario logic
// TODO: Verify the expected outcome

// Test case 2: Edge cases and error handling
// TODO: Test boundary conditions
// TODO: Test error scenarios
// TODO: Verify proper error handling

// Notes:
// - Scenario: {scenario_name}
// - Language: {language}
// - Generated test template - needs actual implementation"""

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be safe for file system"""
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:95] + ext
        
        return filename
    
    def _get_scenario_name(self, scenario: Any) -> str:
        """Extract a readable name from a scenario"""
        if isinstance(scenario, str):
            return scenario[:50] + "..." if len(scenario) > 50 else scenario
        elif isinstance(scenario, dict):
            return scenario.get("name", "Unnamed Scenario")
        else:
            return str(scenario)[:50] + "..." if len(str(scenario)) > 50 else str(scenario)
    
    def _consolidate_scenario_code(self, scenario_results: Dict[str, Any], language: str, product_name: str) -> str:
        """Consolidate all individual scenario code into a unified implementation"""
        self.log("🔗 Consolidating individual scenario code into unified implementation...")
        
        if not scenario_results["successful"]:
            self.log("❌ No successful scenarios to consolidate")
            return f"# {product_name} - No Code Generated\n\nNo scenarios were successfully processed."
        
        # Start building consolidated content
        consolidated_parts = []
        
        # Header section
        consolidated_parts.append(f"# {product_name} - Complete Implementation")
        consolidated_parts.append(f"**Language:** {language.upper()}")
        consolidated_parts.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        consolidated_parts.append(f"**Scenarios Processed:** {len(scenario_results['successful'])}/{len(scenario_results['successful']) + len(scenario_results['failed'])}")
        consolidated_parts.append("")
        consolidated_parts.append("This implementation was generated scenario-by-scenario for better control and validation.")
        consolidated_parts.append("")
        consolidated_parts.append("---")
        consolidated_parts.append("")
        
        # Table of contents
        consolidated_parts.append("## Table of Contents")
        for i, scenario in enumerate(scenario_results["successful"], 1):
            scenario_name = scenario.get("scenario_name", f"Scenario {i}")
            consolidated_parts.append(f"{i}. [{scenario_name}](#scenario-{i}-{scenario_name.lower().replace(' ', '-').replace('(', '').replace(')', '')})")
        consolidated_parts.append("")
        
        # Individual scenario implementations
        for i, scenario in enumerate(scenario_results["successful"], 1):
            scenario_name = scenario.get("scenario_name", f"Scenario {i}")
            
            consolidated_parts.append(f"## Scenario {i}: {scenario_name}")
            consolidated_parts.append("")
            
            # Show information about generated code files
            if 'code_files' in scenario and scenario['code_files']:
                consolidated_parts.append(f"**Generated {len(scenario['code_files'])} code files:**")
                consolidated_parts.append("")
                for file_path in scenario['code_files']:
                    file_name = os.path.basename(file_path)
                    relative_path = os.path.relpath(file_path, os.getcwd())
                    consolidated_parts.append(f"- `{file_name}` - {relative_path}")
                consolidated_parts.append("")
                
                # Include file contents in documentation
                for file_path in scenario['code_files']:
                    if file_path.endswith('.md'):  # Skip README files in main consolidation
                        continue
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_name = os.path.basename(file_path)
                            file_ext = os.path.splitext(file_name)[1][1:]  # Remove the dot
                            consolidated_parts.append(f"### {file_name}")
                            consolidated_parts.append(f"```{file_ext}")
                            consolidated_parts.append(content)
                            consolidated_parts.append("```")
                            consolidated_parts.append("")
                    except Exception as e:
                        consolidated_parts.append(f"Error reading {file_path}: {str(e)}")
                        consolidated_parts.append("")
            else:
                # Fallback to old content-based approach if no code files
                content = scenario.get("generated_content", "")
                consolidated_parts.append(content)
            
            consolidated_parts.append("")
            consolidated_parts.append("---")
            consolidated_parts.append("")
        
        # Failed scenarios section (if any)
        if scenario_results["failed"]:
            consolidated_parts.append("## Failed Scenarios")
            consolidated_parts.append("")
            consolidated_parts.append("The following scenarios could not be generated:")
            consolidated_parts.append("")
            for i, failed in enumerate(scenario_results["failed"], 1):
                scenario_name = failed.get("scenario_name", f"Unknown Scenario {i}")
                error = failed.get("error", "Unknown error")
                consolidated_parts.append(f"- **{scenario_name}:** {error}")
            consolidated_parts.append("")
        
        # Integration notes
        consolidated_parts.append("## Integration Notes")
        consolidated_parts.append("")
        consolidated_parts.append("Each scenario was generated independently. To create a complete application:")
        consolidated_parts.append("1. Review each scenario's implementation")
        consolidated_parts.append("2. Extract common functionality into shared modules")
        consolidated_parts.append("3. Use the individual test files for each scenario (no consolidated test file)")
        consolidated_parts.append("4. Ensure proper dependency management across scenarios")
        consolidated_parts.append("")
        
        consolidated_content = "\n".join(consolidated_parts)
        
        self.log(f"✅ Consolidated {len(scenario_results['successful'])} scenarios into unified implementation")
        self.log(f"📊 Total consolidated content: {len(consolidated_content)} characters")
        
        return consolidated_content
    
    def _create_consolidated_project(self, consolidated_content: str, scenario_results: Dict[str, Any], 
                                   language: str, product_name: str, scenarios: list, 
                                   project_dir: str, analysis_data: Dict[str, Any]) -> Dict[str, str]:
        """Create the final project structure with consolidated code from individual scenarios"""
        created_files = {"project_dir": project_dir}
        
        try:
            # Save the consolidated implementation
            consolidated_file = os.path.join(project_dir, "CONSOLIDATED_IMPLEMENTATION.md")
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                f.write(consolidated_content)
            created_files["consolidated_implementation"] = consolidated_file
            
            # Create project structure using appropriate generator
            generator = self.generators.get(language.lower())
            if generator:
                # Pass all scenario results for more comprehensive project generation
                project_files = generator.generate_project(
                    project_dir, product_name, scenarios, consolidated_content, analysis_data
                )
                created_files.update(project_files)
                self.log(f"✅ Created project structure using {generator.__class__.__name__}")
            
            # Extract and save individual code files from all successful scenarios
            self._extract_consolidated_code_files(scenario_results, project_dir, language)
            
            # Compile the generated project and capture any compilation errors
            compilation_result = self._compile_generated_project(project_dir, language)
            created_files["compilation_result"] = compilation_result
            
            # Create scenario summary report
            summary_report = self._create_scenario_summary_report(scenario_results, project_dir)
            created_files["scenario_summary"] = summary_report
            
            # Generate final report
            final_report = self._generate_scenario_based_report(
                created_files, scenario_results, language, product_name, project_dir
            )
            created_files["simple_report"] = final_report
            
            self.log(f"✅ Consolidated project created successfully in: {project_dir}")
            
        except Exception as e:
            self.log(f"❌ Error creating consolidated project: {str(e)}")
            created_files["error"] = str(e)
        
        return created_files
    
    def _extract_consolidated_code_files(self, scenario_results: Dict[str, Any], project_dir: str, language: str) -> None:
        """Extract and consolidate actual code files from individual scenario results"""
        try:
            import re
            
            extension_mapping = {
                'csharp': '.cs', 'c#': '.cs', 'python': '.py', 
                'javascript': '.js', 'node.js': '.js', 'js': '.js',
                'java': '.java', 'go': '.go', 'rust': '.rs'
            }
            
            default_extension = extension_mapping.get(language.lower(), '.txt')
            
            # Collect all code blocks from successful scenarios
            all_main_code = []
            all_config_files = {}
            
            for scenario in scenario_results["successful"]:
                content = scenario.get("generated_content", "")
                scenario_name = scenario.get("scenario_name", "Unknown")
                
                # Extract main implementation code
                main_code_pattern = r'### Main Implementation.*?```[a-zA-Z]*\n(.*?)```'
                main_matches = re.findall(main_code_pattern, content, re.DOTALL | re.IGNORECASE)
                for match in main_matches:
                    if match.strip():
                        all_main_code.append(f"// Code from scenario: {scenario_name}\n{match.strip()}\n")
                
                # Extract configuration files
                config_patterns = [
                    r'### ([^#\n]*\.(?:json|xml|toml|yml|yaml|config))[^#\n]*.*?```[a-zA-Z]*\n(.*?)```',
                    r'###\s+([^\n]+\.(?:json|xml|toml|yml|yaml|config))\s*```[a-zA-Z]*\n(.*?)```'
                ]
                
                for pattern in config_patterns:
                    config_matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                    for filename, config_content in config_matches:
                        filename = filename.strip()
                        if filename not in all_config_files:
                            all_config_files[filename] = []
                        all_config_files[filename].append(f"# From scenario: {scenario_name}\n{config_content.strip()}")
            
            # Create consolidated main implementation file
            if all_main_code:
                main_file_path = os.path.join(project_dir, f"main{default_extension}")
                with open(main_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"// Consolidated Main Implementation for {language.upper()}\n")
                    f.write(f"// Generated from {len(scenario_results['successful'])} scenarios\n")
                    f.write(f"// Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("\n\n".join(all_main_code))
                
                self.log(f"✅ Created consolidated main implementation: main{default_extension}")
            
            # Create configuration files
            for filename, content_list in all_config_files.items():
                config_file_path = os.path.join(project_dir, filename)
                os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
                
                with open(config_file_path, 'w', encoding='utf-8') as f:
                    if filename.endswith('.json'):
                        # For JSON files, try to merge if possible, otherwise use the first valid one
                        f.write(content_list[0].split('\n', 1)[1] if '\n' in content_list[0] else content_list[0])
                    else:
                        f.write("\n\n".join(content_list))
                
                self.log(f"✅ Created configuration file: {filename}")
            
            self.log(f"📁 Extracted and consolidated code from {len(scenario_results['successful'])} scenarios")
            
        except Exception as e:
            self.log(f"❌ Error extracting consolidated code files: {str(e)}")
    
    def _create_scenario_summary_report(self, scenario_results: Dict[str, Any], project_dir: str) -> str:
        """Create a detailed summary report of scenario processing"""
        try:
            report_path = os.path.join(project_dir, "SCENARIO_SUMMARY_REPORT.md")
            
            report_parts = []
            report_parts.append("# Scenario-by-Scenario Generation Report")
            report_parts.append("")
            report_parts.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_parts.append(f"**Total Scenarios Processed:** {scenario_results['total_processed']}")
            report_parts.append(f"**Successful Generations:** {len(scenario_results['successful'])}")
            report_parts.append(f"**Failed Generations:** {len(scenario_results['failed'])}")
            report_parts.append(f"**Success Rate:** {(len(scenario_results['successful'])/scenario_results['total_processed']*100):.1f}%")
            report_parts.append("")
            report_parts.append("---")
            report_parts.append("")
            
            # Successful scenarios
            if scenario_results["successful"]:
                report_parts.append("## ✅ Successfully Generated Scenarios")
                report_parts.append("")
                for scenario in scenario_results["successful"]:
                    name = scenario.get("scenario_name", "Unknown")
                    content_length = scenario.get("content_length", 0)
                    code_files = scenario.get("code_files", [])
                    generation_time = scenario.get("generation_time", "Unknown")
                    
                    report_parts.append(f"### {scenario.get('scenario_index', '?')}. {name}")
                    report_parts.append(f"- **Content Length:** {content_length} characters")
                    report_parts.append(f"- **Generated At:** {generation_time}")
                    
                    # Display generated files
                    if code_files:
                        if len(code_files) == 1:
                            report_parts.append(f"- **File:** {os.path.basename(code_files[0])}")
                        else:
                            report_parts.append(f"- **Files:** {len(code_files)} files created")
                            for file_path in code_files:
                                report_parts.append(f"  - {os.path.basename(file_path)}")
                    else:
                        report_parts.append(f"- **File:** No files created")
                    report_parts.append("")
            
            # Failed scenarios
            if scenario_results["failed"]:
                report_parts.append("## ❌ Failed Scenarios")
                report_parts.append("")
                for scenario in scenario_results["failed"]:
                    name = scenario.get("scenario_name", "Unknown")
                    error = scenario.get("error", "Unknown error")
                    generation_time = scenario.get("generation_time", "Unknown")
                    
                    report_parts.append(f"### {scenario.get('scenario_index', '?')}. {name}")
                    report_parts.append(f"- **Error:** {error}")
                    report_parts.append(f"- **Failed At:** {generation_time}")
                    report_parts.append("")
            
            # Write report to file
            report_content = "\n".join(report_parts)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.log(f"✅ Created scenario summary report: SCENARIO_SUMMARY_REPORT.md")
            return report_path
            
        except Exception as e:
            self.log(f"❌ Error creating scenario summary report: {str(e)}")
            return ""
    
    def _create_enhanced_scenario_summary_report(self, scenario_results: Dict[str, Any], 
                                               compilation_attempts: List[Dict[str, Any]], 
                                               project_dir: str, language: str) -> str:
        """Create a comprehensive scenario summary report with detailed compilation attempts, errors, and fixes"""
        try:
            report_path = os.path.join(project_dir, "COMPREHENSIVE_CODE_GENERATION_REPORT.md")
            
            report_parts = []
            
            # Header section
            report_parts.append("# 📊 Comprehensive Code Generation Report")
            report_parts.append("## Scenario-by-Scenario Generation with Compilation Feedback Analysis")
            report_parts.append("")
            report_parts.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_parts.append(f"**Language:** {language.upper()}")
            report_parts.append(f"**Project Directory:** {project_dir}")
            report_parts.append("")
            
            # Executive Summary
            total_scenarios = scenario_results.get('total_processed', 0)
            successful_scenarios = len(scenario_results.get('successful', []))
            failed_scenarios = len(scenario_results.get('failed', []))
            success_rate = (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
            
            report_parts.append("## 📋 Executive Summary")
            report_parts.append("")
            report_parts.append(f"| Metric | Value |")
            report_parts.append(f"|--------|-------|")
            report_parts.append(f"| Total Scenarios | {total_scenarios} |")
            report_parts.append(f"| Successful Generations | {successful_scenarios} |")
            report_parts.append(f"| Failed Generations | {failed_scenarios} |")
            report_parts.append(f"| Success Rate | {success_rate:.1f}% |")
            report_parts.append(f"| Compilation Attempts | {len(compilation_attempts)} |")
            
            # Determine final status
            final_attempt = compilation_attempts[-1] if compilation_attempts else {}
            final_compilation_success = final_attempt.get("compilation_result", {}).get("success", False)
            
            report_parts.append(f"| Final Compilation Status | {'✅ Successful' if final_compilation_success else '❌ Failed'} |")
            report_parts.append("")
            report_parts.append("---")
            report_parts.append("")
            
            # Detailed Compilation Attempts Analysis
            if compilation_attempts:
                report_parts.append("## 🔄 Detailed Compilation Attempts Analysis")
                report_parts.append("")
                
                for i, attempt_info in enumerate(compilation_attempts, 1):
                    attempt_num = attempt_info.get("attempt", i)
                    timestamp = attempt_info.get("timestamp", "Unknown")
                    compilation_result = attempt_info.get("compilation_result", {})
                    enhanced_scenarios = attempt_info.get("enhanced_scenarios", [])
                    detailed_error_analysis = attempt_info.get("detailed_error_analysis", {})
                    changes_from_previous = attempt_info.get("changes_from_previous", {})
                    
                    success = compilation_result.get("success", False)
                    status_icon = "✅" if success else "❌"
                    
                    report_parts.append(f"### {status_icon} Attempt {attempt_num} - {'SUCCESS' if success else 'FAILED'}")
                    report_parts.append(f"**Timestamp:** {timestamp}")
                    report_parts.append(f"**Attempt Type:** {'Initial Generation' if attempt_num == 1 else 'Selective Scenario Retry'}")
                    report_parts.append("")
                    
                    # Compilation Results
                    if success:
                        report_parts.append("#### ✅ Compilation Status: SUCCESSFUL")
                        report_parts.append("- All code compiled without errors")
                        report_parts.append("- Ready for execution and testing")
                    else:
                        error_analysis = compilation_result.get("error_analysis", {})
                        total_errors = error_analysis.get("total_errors", 0)
                        total_warnings = error_analysis.get("total_warnings", 0)
                        error_categories = error_analysis.get("error_categories", {})
                        detailed_errors = error_analysis.get("detailed_errors", [])
                        
                        report_parts.append("#### ❌ Compilation Status: FAILED")
                        report_parts.append(f"- **Total Errors:** {total_errors}")
                        report_parts.append(f"- **Total Warnings:** {total_warnings}")
                        report_parts.append("")
                        
                        # Error Categories Breakdown
                        if error_categories:
                            report_parts.append("#### 📊 Error Categories Breakdown")
                            report_parts.append("")
                            for category, count in error_categories.items():
                                percentage = (count / total_errors * 100) if total_errors > 0 else 0
                                report_parts.append(f"- **{category.replace('_', ' ').title()}:** {count} errors ({percentage:.1f}%)")
                            report_parts.append("")
                        
                        # Detailed Error Analysis
                        if detailed_error_analysis:
                            report_parts.append("#### 🔍 Detailed Error Analysis")
                            report_parts.append("")
                            
                            categorized_errors = detailed_error_analysis.get("categorized_errors", {})
                            if categorized_errors:
                                for error_type, errors in categorized_errors.items():
                                    if errors:
                                        report_parts.append(f"**{error_type.replace('_', ' ').title()} ({len(errors)} errors):**")
                                        for j, error in enumerate(errors[:3], 1):  # Show top 3 per category
                                            truncated_error = error[:120] + "..." if len(error) > 120 else error
                                            report_parts.append(f"  {j}. {truncated_error}")
                                        if len(errors) > 3:
                                            report_parts.append(f"     ... and {len(errors) - 3} more {error_type} errors")
                                        report_parts.append("")
                            
                            # Pattern Suggestions
                            pattern_suggestions = detailed_error_analysis.get("pattern_suggestions", [])
                            if pattern_suggestions:
                                report_parts.append("**🔧 Suggested Fix Patterns:**")
                                for suggestion in pattern_suggestions:
                                    report_parts.append(f"- {suggestion}")
                                report_parts.append("")
                        
                        # Top Critical Errors
                        if detailed_errors:
                            report_parts.append("#### 🚨 Top Critical Compilation Errors")
                            report_parts.append("")
                            for j, error in enumerate(detailed_errors[:5], 1):
                                truncated_error = error[:200] + "..." if len(error) > 200 else error
                                report_parts.append(f"**{j}.** `{truncated_error}`")
                                report_parts.append("")
                    
                    # Changes from Previous Attempt
                    if changes_from_previous and attempt_num > 1:
                        report_parts.append("#### 🔄 Changes from Previous Attempt")
                        report_parts.append("")
                        
                        resolved_errors = changes_from_previous.get("resolved_errors", [])
                        new_errors = changes_from_previous.get("new_errors", [])
                        persistent_errors = changes_from_previous.get("persistent_errors", [])
                        
                        report_parts.append(f"- **Resolved Errors:** {len(resolved_errors)}")
                        report_parts.append(f"- **New Errors:** {len(new_errors)}")
                        report_parts.append(f"- **Persistent Errors:** {len(persistent_errors)}")
                        
                        if resolved_errors:
                            report_parts.append("")
                            report_parts.append("**✅ Successfully Resolved:**")
                            for error in resolved_errors[:3]:
                                truncated_error = error[:100] + "..." if len(error) > 100 else error
                                report_parts.append(f"  - {truncated_error}")
                            if len(resolved_errors) > 3:
                                report_parts.append(f"  - ... and {len(resolved_errors) - 3} more resolved errors")
                        
                        if new_errors:
                            report_parts.append("")
                            report_parts.append("**🆕 New Errors Introduced:**")
                            for error in new_errors[:3]:
                                truncated_error = error[:100] + "..." if len(error) > 100 else error
                                report_parts.append(f"  - {truncated_error}")
                        
                        if persistent_errors:
                            report_parts.append("")
                            report_parts.append("**🔄 Still Need Fixing:**")
                            for error in persistent_errors[:3]:
                                truncated_error = error[:100] + "..." if len(error) > 100 else error
                                report_parts.append(f"  - {truncated_error}")
                        
                        report_parts.append("")
                    
                    # Scenario Enhancement Analysis
                    if attempt_num > 1:
                        report_parts.append("#### 🎯 Scenario Enhancement Analysis")
                        report_parts.append("")
                        
                        scenarios_with_context = sum(1 for s in enhanced_scenarios if s.get("has_compilation_context", False))
                        scenarios_without_context = len(enhanced_scenarios) - scenarios_with_context
                        
                        report_parts.append(f"- **Total Scenarios in Attempt:** {len(enhanced_scenarios)}")
                        report_parts.append(f"- **Scenarios with Error Context:** {scenarios_with_context}")
                        report_parts.append(f"- **Original Scenarios (Unchanged):** {scenarios_without_context}")
                        
                        if scenarios_with_context > 0:
                            report_parts.append("")
                            report_parts.append("**🔧 Scenarios Enhanced with Error Context:**")
                            for scenario in enhanced_scenarios:
                                if scenario.get("has_compilation_context", False):
                                    name = scenario.get("name", "Unknown")
                                    error_count = scenario.get("previous_errors_count", 0)
                                    error_categories = scenario.get("error_categories", [])
                                    
                                    report_parts.append(f"  - **{name}:** {error_count} compilation errors")
                                    if error_categories:
                                        categories_str = ", ".join(error_categories[:3])
                                        if len(error_categories) > 3:
                                            categories_str += f" +{len(error_categories) - 3} more"
                                        report_parts.append(f"    - Error types: {categories_str}")
                    
                    report_parts.append("")
                    report_parts.append("---")
                    report_parts.append("")
                
                # Overall Compilation Progress Summary
                report_parts.append("## 📈 Compilation Progress Summary")
                report_parts.append("")
                
                if len(compilation_attempts) > 1:
                    first_attempt = compilation_attempts[0]
                    last_attempt = compilation_attempts[-1]
                    
                    first_errors = first_attempt.get("compilation_result", {}).get("error_analysis", {}).get("total_errors", 0)
                    last_errors = last_attempt.get("compilation_result", {}).get("error_analysis", {}).get("total_errors", 0)
                    
                    error_reduction = first_errors - last_errors
                    error_reduction_percent = (error_reduction / first_errors * 100) if first_errors > 0 else 0
                    
                    report_parts.append(f"- **Initial Errors (Attempt 1):** {first_errors}")
                    report_parts.append(f"- **Final Errors (Attempt {len(compilation_attempts)}):** {last_errors}")
                    report_parts.append(f"- **Error Reduction:** {error_reduction} errors ({error_reduction_percent:.1f}% improvement)")
                    report_parts.append(f"- **Final Status:** {'✅ Success - All errors resolved' if last_errors == 0 else f'❌ {last_errors} errors remaining'}")
                else:
                    first_attempt = compilation_attempts[0] if compilation_attempts else {}
                    first_errors = first_attempt.get("compilation_result", {}).get("error_analysis", {}).get("total_errors", 0)
                    success = first_attempt.get("compilation_result", {}).get("success", False)
                    
                    report_parts.append(f"- **Single Attempt Results:** {'✅ Success on first try' if success else f'❌ {first_errors} errors on first attempt'}")
                
                report_parts.append("")
                report_parts.append("---")
                report_parts.append("")
            
            # Scenario Generation Results (Enhanced)
            if scenario_results.get("successful") or scenario_results.get("failed"):
                report_parts.append("## 📝 Individual Scenario Generation Results")
                report_parts.append("")
                
                # Successful Scenarios
                if scenario_results.get("successful"):
                    report_parts.append("### ✅ Successfully Generated Scenarios")
                    report_parts.append("")
                    
                    for scenario in scenario_results["successful"]:
                        name = scenario.get("scenario_name", "Unknown")
                        content_length = scenario.get("content_length", 0)
                        code_files = scenario.get("code_files", [])
                        generation_time = scenario.get("generation_time", "Unknown")
                        scenario_index = scenario.get("scenario_index", "?")
                        
                        # Check if this was a fix attempt
                        is_fix_attempt = scenario.get("fix_attempt", False)
                        original_errors = scenario.get("original_errors", [])
                        
                        report_parts.append(f"#### {scenario_index}. {name}")
                        
                        if is_fix_attempt:
                            report_parts.append(f"**🔧 Regenerated due to compilation errors**")
                            report_parts.append(f"- **Original Errors Fixed:** {len(original_errors)}")
                        
                        report_parts.append(f"- **Content Length:** {content_length:,} characters")
                        report_parts.append(f"- **Generated Files:** {len(code_files)}")
                        report_parts.append(f"- **Generation Time:** {generation_time}")
                        
                        if code_files:
                            report_parts.append("- **Files Created:**")
                            for file_path in code_files:
                                file_name = os.path.basename(file_path)
                                report_parts.append(f"  - {file_name}")
                        
                        report_parts.append("")
                
                # Failed Scenarios
                if scenario_results.get("failed"):
                    report_parts.append("### ❌ Failed Scenario Generations")
                    report_parts.append("")
                    
                    for scenario in scenario_results["failed"]:
                        name = scenario.get("scenario_name", "Unknown")
                        error = scenario.get("error", "Unknown error")
                        generation_time = scenario.get("generation_time", "Unknown")
                        scenario_index = scenario.get("scenario_index", "?")
                        
                        report_parts.append(f"#### {scenario_index}. {name}")
                        report_parts.append(f"- **Error:** {error}")
                        report_parts.append(f"- **Generation Time:** {generation_time}")
                        report_parts.append("")
            
            # Selective Fixes Summary (if any)
            selective_fixes_found = False
            for attempt in compilation_attempts:
                if attempt.get("attempt", 1) > 1:
                    selective_fixes_found = True
                    break
            
            if selective_fixes_found:
                report_parts.append("## 🎯 Selective Scenario Regeneration Summary")
                report_parts.append("")
                report_parts.append("This section shows which scenarios were selectively regenerated due to compilation errors:")
                report_parts.append("")
                
                for attempt_num, attempt in enumerate(compilation_attempts, 1):
                    if attempt_num == 1:
                        continue  # Skip first attempt
                    
                    enhanced_scenarios = attempt.get("enhanced_scenarios", [])
                    scenarios_with_errors = [s for s in enhanced_scenarios if s.get("has_compilation_context", False)]
                    
                    if scenarios_with_errors:
                        report_parts.append(f"### Attempt {attempt_num} - Regenerated Scenarios")
                        report_parts.append("")
                        
                        for scenario in scenarios_with_errors:
                            name = scenario.get("name", "Unknown")
                            error_count = scenario.get("previous_errors_count", 0)
                            error_categories = scenario.get("error_categories", [])
                            
                            report_parts.append(f"- **{name}**")
                            report_parts.append(f"  - Compilation errors: {error_count}")
                            if error_categories:
                                report_parts.append(f"  - Error types: {', '.join(error_categories[:3])}")
                        
                        report_parts.append("")
            
            # Final Recommendations
            report_parts.append("## 🎯 Recommendations and Next Steps")
            report_parts.append("")
            
            if final_compilation_success:
                report_parts.append("### ✅ Success! Your code is ready")
                report_parts.append("- All compilation errors have been resolved")
                report_parts.append("- Generated code files are ready for testing and deployment")
                report_parts.append("- Consider running unit tests to validate functionality")
            else:
                last_attempt = compilation_attempts[-1] if compilation_attempts else {}
                remaining_errors = last_attempt.get("compilation_result", {}).get("error_analysis", {}).get("total_errors", 0)
                
                report_parts.append("### ⚠️ Additional Work Needed")
                report_parts.append(f"- {remaining_errors} compilation errors still need to be resolved")
                report_parts.append("- Review the detailed error analysis above")
                report_parts.append("- Consider manual fixes or additional regeneration attempts")
                
                # Suggest most common error patterns for manual fixing
                last_detailed_analysis = last_attempt.get("detailed_error_analysis", {})
                pattern_suggestions = last_detailed_analysis.get("pattern_suggestions", [])
                if pattern_suggestions:
                    report_parts.append("- **Priority fixes:**")
                    for suggestion in pattern_suggestions[:3]:
                        report_parts.append(f"  - {suggestion}")
            
            report_parts.append("")
            report_parts.append("---")
            report_parts.append("")
            report_parts.append(f"**Report generated by BugBashAgent Code Generator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
            
            # Write the report
            report_content = "\n".join(report_parts)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.log(f"📊 Comprehensive code generation report created: {report_path}")
            return report_path
            
        except Exception as e:
            self.log(f"❌ Error creating enhanced scenario summary report: {str(e)}")
            return None

    def _generate_scenario_based_report(self, created_files: Dict, scenario_results: Dict[str, Any], 
                                      language: str, product_name: str, project_dir: str) -> Dict[str, Any]:
        """Generate a comprehensive report for scenario-based generation"""
        report = {
            "project_info": {
                "product_name": product_name,
                "language": language,
                "project_directory": project_dir,
                "generation_timestamp": datetime.now().isoformat(),
                "generation_mode": "scenario_by_scenario"
            },
            "scenario_summary": {
                "total_scenarios": scenario_results["total_processed"],
                "successful_scenarios": len(scenario_results["successful"]),
                "failed_scenarios": len(scenario_results["failed"]),
                "success_rate_percentage": round((len(scenario_results["successful"])/scenario_results["total_processed"]*100), 1) if scenario_results["total_processed"] > 0 else 0
            },
            "files_created": len([k for k in created_files.keys() if k not in ["project_dir", "simple_report"]]),
            "overall_status": "GENERATED_BY_SCENARIO",
            "summary": f"Successfully generated {language.upper()} project for {product_name} using scenario-by-scenario approach"
        }
        
        # Add detailed scenario breakdown
        if scenario_results["successful"]:
            report["successful_scenarios"] = [
                {
                    "index": s.get("scenario_index"),
                    "name": s.get("scenario_name"),
                    "content_length": s.get("content_length"),
                    "file": os.path.basename(s.get("file_path", ""))
                }
                for s in scenario_results["successful"]
            ]
        
        if scenario_results["failed"]:
            report["failed_scenarios"] = [
                {
                    "index": s.get("scenario_index"),
                    "name": s.get("scenario_name"),
                    "error": s.get("error")
                }
                for s in scenario_results["failed"]
            ]
        
        return report
    
    def _create_project(self, generated_content: str, language: str, product_name: str, scenarios: list, analyzer_output: Dict[str, Any] = None) -> Dict[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = product_name.replace(" ", "_").lower()
        
        # Create project directory
        project_dir = os.path.join("workflow_outputs", f"{project_name}_{timestamp}")
        os.makedirs(project_dir, exist_ok=True)
        
        created_files = {"project_dir": project_dir}
        
        try:
            # Get the appropriate generator - but SKIP automatic file generation
            # Only use LLM-generated content and extract real implementations
            generator = self.generators.get(language.lower())
            
            if generator:
                # Only create basic project structure (README, etc.) - no dummy tests
                # Pass analyzer output for CosmosDB version detection
                project_files = generator.generate_project(project_dir, product_name, scenarios, generated_content, analyzer_output)
                created_files.update(project_files)
                self.log(f"✅ Created minimal project structure using {generator.__class__.__name__}")
                
                # Log CosmosDB version if detected
                if analyzer_output:
                    cosmosdb_version = PackageVersions.get_cosmosdb_version()
                    if cosmosdb_version and cosmosdb_version != '3.35.4':  # Not default version
                        self.log(f"🌟 Using CosmosDB version from analyzer: {cosmosdb_version}")
            else:
                self.log(f"⚠️ No generator found for language: {language} - using LLM content only")
            
            # SKIP automatic dummy test file generation entirely
            self.log("⚠️ Skipping automatic dummy test file generation - only extracting real implementations from LLM output")
            
            # Get categorization summary
            categorization_summary = self.scenario_categorizer.get_categorization_summary(scenarios)
            self.log(f"Scenario categorization: {categorization_summary['distribution']}")
            
            created_files["final_generated_content"] = generated_content
            
            # Generate simple final report
            final_report = self._generate_simple_report(created_files, language, product_name, project_dir)
            created_files["simple_report"] = final_report
            
            self.log(f"Project files created using {generator.__class__.__name__} for {language} in: {project_dir}")
            
        except Exception as e:
            self.log(f"Error creating project files: {str(e)}")
            created_files["error"] = str(e)
        
        return created_files
    
    def _parse_and_create_files_with_tools(self, generated_content: str, project_dir: str) -> Dict[str, str]:
        """Parse generated content and create additional files using tools"""
        created_files = {}
        
        try:
            # Parse project structure from generated content
            parsed_structure = self.structure_parser.parse_project_structure(generated_content)
            self.log(f"Parsed project structure: {parsed_structure}")
            
            # Extract code blocks from generated content
            code_blocks = self.code_extractor.extract_code_blocks(generated_content)
            self.log(f"Extracted {len(code_blocks)} code blocks")
            
            # Create files using file creator
            for block in code_blocks:
                if 'filename' in block and 'content' in block:
                    file_path = os.path.join(project_dir, block['filename'])
                    result = self.file_creator.create_file(file_path, block['content'])
                    if result['success']:
                        created_files[block['filename']] = file_path
                        self.log(f"Created file: {block['filename']}")
                    else:
                        self.log(f"Failed to create file {block['filename']}: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            self.log(f"Error parsing and creating files: {str(e)}")
            created_files["parse_error"] = str(e)
        
        return created_files
    
    def _save_complete_generated_content(self, generated_content: str, project_dir: str, language: str, product_name: str) -> None:
        """Save the complete generated content to ensure nothing is lost"""
        try:
            # Create the project directory if it doesn't exist
            os.makedirs(project_dir, exist_ok=True)
            
            # Save complete generated content
            complete_file_path = os.path.join(project_dir, f"COMPLETE_GENERATED_SOLUTION.md")
            with open(complete_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Complete Generated Solution: {product_name}\n")
                f.write(f"**Language:** {language.upper()}\n")
                f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(generated_content)
            
            self.log(f"✅ Complete generated content saved to: COMPLETE_GENERATED_SOLUTION.md")
            
            # Also extract and save individual files using improved parsing
            self._extract_and_save_individual_files(generated_content, project_dir, language)
            
        except Exception as e:
            self.log(f"❌ Error saving complete generated content: {str(e)}")
    
    def _extract_and_save_individual_files(self, generated_content: str, project_dir: str, language: str) -> None:
        """Extract and save individual files from the generated content using improved parsing"""
        try:
            import re
            
            # Define file extension mappings
            extension_mapping = {
                'csharp': '.cs',
                'c#': '.cs', 
                'python': '.py',
                'javascript': '.js',
                'node.js': '.js',
                'js': '.js',
                'java': '.java',
                'go': '.go',
                'rust': '.rs'
            }
            
            default_extension = extension_mapping.get(language.lower(), '.txt')
            
            # Pattern to match file sections (more flexible than just code blocks)
            patterns = [
                # Pattern for ### FileName.ext format
                r'###\s+([^\n]+?\.(?:cs|py|js|java|go|rs|json|xml|toml|txt|md|yml|yaml))\s*\n```[a-zA-Z]*\n(.*?)```',
                # Pattern for ## FileName.ext format  
                r'##\s+([^\n]+?\.(?:cs|py|js|java|go|rs|json|xml|toml|txt|md|yml|yaml))\s*\n```[a-zA-Z]*\n(.*?)```',
                # Pattern for **FileName.ext** format
                r'\*\*([^\n]+?\.(?:cs|py|js|java|go|rs|json|xml|toml|txt|md|yml|yaml))\*\*\s*\n```[a-zA-Z]*\n(.*?)```',
                # Pattern for generic file mentions
                r'(?:File:|Create file:|Generate file:)\s*([^\n]+?\.(?:cs|py|js|java|go|rs|json|xml|toml|txt|md|yml|yaml))\s*\n```[a-zA-Z]*\n(.*?)```',
                # Enhanced patterns specifically for test files
                r'###\s+(.*?[Tt]est.*?\.(?:cs|py|js|java|go|rs))\s*\n```[a-zA-Z]*\n(.*?)```',
                r'##\s+(.*?[Tt]est.*?\.(?:cs|py|js|java|go|rs))\s*\n```[a-zA-Z]*\n(.*?)```',
                # Pattern for test class files with explicit test indicators
                r'(?:Test file:|Test class:|Unit test:|Integration test:)\s*([^\n]+?\.(?:cs|py|js|java|go|rs))\s*\n```[a-zA-Z]*\n(.*?)```'
            ]
            
            files_created = 0
            
            for pattern in patterns:
                matches = re.findall(pattern, generated_content, re.DOTALL | re.IGNORECASE)
                for filename, content in matches:
                    # Clean up filename
                    filename = filename.strip()
                    if filename.startswith('/') or filename.startswith('\\'):
                        filename = filename[1:]
                    
                    # Create directory structure if needed
                    file_path = os.path.join(project_dir, filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Clean up content
                    content = content.strip()
                    
                    # Validate that test files contain actual test implementations
                    if self._is_test_file(filename) and not self._contains_real_test_implementation(content, language):
                        self.log(f"⚠️ Skipping {filename} - appears to be a dummy/placeholder test file")
                        continue
                    
                    # Save the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    files_created += 1
                    self.log(f"✅ Extracted and saved: {filename}")
            
            # If no files were extracted using patterns, try to create a main implementation file
            if files_created == 0:
                self._create_fallback_implementation_file(generated_content, project_dir, language, default_extension)
            
            self.log(f"📁 Total files extracted and saved: {files_created}")
            
        except Exception as e:
            self.log(f"❌ Error extracting individual files: {str(e)}")
            
    def _create_fallback_implementation_file(self, generated_content: str, project_dir: str, language: str, extension: str) -> None:
        """Create a fallback main implementation file if no files were extracted"""
        try:
            # Extract code blocks without specific filenames
            import re
            
            code_blocks = re.findall(r'```(?:' + language + r'|[a-zA-Z]*)\n(.*?)```', generated_content, re.DOTALL)
            
            if code_blocks:
                # Combine all code blocks
                combined_code = '\n\n'.join([block.strip() for block in code_blocks if block.strip()])
                
                if combined_code:
                    main_file_name = f"main{extension}"
                    main_file_path = os.path.join(project_dir, main_file_name)
                    
                    with open(main_file_path, 'w', encoding='utf-8') as f:
                        f.write(f"// Generated {language.upper()} Implementation\n")
                        f.write(f"// Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(combined_code)
                    
                    self.log(f"✅ Created fallback implementation file: {main_file_name}")
            else:
                # If no code blocks found, save the entire content as a text file
                fallback_file = os.path.join(project_dir, "generated_solution.txt")
                with open(fallback_file, 'w', encoding='utf-8') as f:
                    f.write(generated_content)
                self.log(f"✅ Saved complete solution as text file: generated_solution.txt")
                
        except Exception as e:
            self.log(f"❌ Error creating fallback implementation file: {str(e)}")
    
    def _is_test_file(self, filename: str) -> bool:
        """Check if a filename indicates it's a test file"""
        filename_lower = filename.lower()
        test_indicators = [
            'test', 'tests', 'spec', 'specs', 
            '_test.', '.test.', 'test_', 'unittest', 'integrationtest'
        ]
        return any(indicator in filename_lower for indicator in test_indicators)
    
    def _contains_real_test_implementation(self, content: str, language: str) -> bool:
        """Check if the content contains real test implementations rather than placeholder/dummy tests"""
        content_lower = content.lower()
        
        # Look for indicators of placeholder/dummy content
        dummy_indicators = [
            'add your actual test logic here',
            'this is a placeholder',
            'simulate some work',
            'todo: implement',
            'todo implement',
            'not implemented',
            'dummy test',
            'placeholder test',
            'sample test',
            'example test'
        ]
        
        # If it contains obvious dummy content, reject it
        if any(indicator in content_lower for indicator in dummy_indicators):
            return False
        
        # Look for language-specific test patterns that indicate real implementation
        if language.lower() in ['csharp', 'c#']:
            real_test_patterns = [
                # Real assertions beyond just basic checks
                r'Assert\.\w+\([^,)]+,\s*[^,)]+,',  # Assert with actual expected values
                r'\.Should\(\)\.', # FluentAssertions
                r'new\s+\w+\([^)]*\)', # Object instantiation
                r'Mock<\w+>', # Mocking frameworks
                r'Setup\([^)]*\)\.Returns', # Mock setup
                # Avoid basic placeholder assertions
                r'(?!Assert\.That\(result, Is\.Not\.Null)'  # Not just null checks
            ]
        elif language.lower() == 'python':
            real_test_patterns = [
                r'assert\s+\w+\s*==\s*[^,\s]+',  # Specific value assertions
                r'self\.assertEqual\([^,]+,\s*[^,)]+\)',  # unittest assertions with values
                r'@patch\(', # Mocking
                r'mock\.\w+', # Mock usage
                r'with\s+pytest\.raises\(', # Exception testing
            ]
        elif language.lower() in ['javascript', 'js']:
            real_test_patterns = [
                r'expect\([^)]+\)\.to\w+\([^)]+\)', # chai assertions with values
                r'expect\([^)]+\)\.toBe\([^)]+\)', # jest assertions with values
                r'sinon\.', # sinon mocking
                r'jest\.mock\(', # jest mocking
                r'\.mockResolvedValue\(', # mock implementations
            ]
        elif language.lower() == 'java':
            real_test_patterns = [
                r'assertEquals\([^,]+,\s*[^,)]+\)', # JUnit assertions with values
                r'assertThat\([^)]+\)\.', # Hamcrest matchers
                r'Mockito\.\w+\(', # Mockito usage
                r'@Mock\s+\w+', # Mock annotations
                r'when\([^)]+\)\.thenReturn\(', # Mock behavior
            ]
        else:
            # Generic patterns for other languages
            real_test_patterns = [
                r'assert\s+\w+\s*==\s*[^,\s]+',
                r'expect\([^)]+\)',
                r'test\w*\([^)]*\)\s*{[^}]{50,}',  # Test functions with substantial bodies
            ]
        
        # Check if content contains real test patterns
        import re
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in real_test_patterns)
    
    def _generate_simple_report(self, created_files: Dict, language: str, product_name: str, project_dir: str) -> Dict[str, Any]:
        """Generate a simple report of the code generation process without build/test details"""
        report = {
            "project_info": {
                "product_name": product_name,
                "language": language,
                "project_directory": project_dir,
                "generation_timestamp": datetime.now().isoformat()
            },
            "files_created": len([k for k in created_files.keys() if k not in ["project_dir", "final_generated_content", "simple_report"]]),
            "overall_status": "GENERATED",
            "summary": f"Successfully generated {language.upper()} project for {product_name}"
        }
        
        return report
    
    def _generate_comprehensive_report(self, created_files: Dict, language: str, product_name: str, project_dir: str) -> Dict[str, Any]:
        """Generate a comprehensive report of the entire code generation process"""
        report = {
            "project_info": {
                "product_name": product_name,
                "language": language,
                "project_directory": project_dir,
                "generation_timestamp": datetime.now().isoformat()
            },
            "build_summary": {},
            "compilation_summary": {},
            "test_summary": {},
            "overall_status": "unknown",
            "recommendations": [],
            "quality_metrics": {}
        }
        
        try:
            # Build Summary
            build_result = created_files.get("build_result", {})
            build_status = created_files.get("build_status", "unknown")
            
            report["build_summary"] = {
                "status": build_status,
                "build_successful": build_result.get("success", False),
                "restore_successful": build_result.get("restore", {}).get("success", False),
                "compilation_successful": build_result.get("build", {}).get("success", False)
            }
            
            # Compilation Summary
            compilation_check = created_files.get("compilation_check", {})
            if compilation_check:
                error_summary = compilation_check.get("error_summary", {})
                report["compilation_summary"] = {
                    "no_compilation_errors": compilation_check.get("success", False),
                    "total_errors": error_summary.get("total_errors", 0),
                    "total_warnings": error_summary.get("total_warnings", 0),
                    "critical_errors": error_summary.get("critical_errors", 0),
                    "files_checked": len(compilation_check.get("files_checked", []))
                }
            
            # Test Summary
            test_report = created_files.get("test_report", {})
            if test_report and test_report.get("success", False):
                test_summary = test_report.get("summary", {}).get("test_results_summary", {})
                report["test_summary"] = {
                    "tests_executed": test_report.get("success", False),
                    "total_tests": test_summary.get("total_tests_run", 0),
                    "passed_tests": test_summary.get("passed_tests", 0),
                    "failed_tests": test_summary.get("failed_tests", 0),
                    "success_rate": test_summary.get("success_rate_percentage", 0),
                    "all_tests_passed": test_summary.get("all_tests_passed", False)
                }
            else:
                report["test_summary"] = {
                    "tests_executed": False,
                    "reason": "No tests found or test execution failed"
                }
            
            # Overall Status Assessment
            build_ok = report["build_summary"]["build_successful"]
            compilation_ok = report["compilation_summary"].get("no_compilation_errors", True)
            tests_ok = report["test_summary"].get("all_tests_passed", True)
            
            if build_ok and compilation_ok and tests_ok:
                report["overall_status"] = "EXCELLENT"
            elif build_ok and compilation_ok:
                report["overall_status"] = "GOOD"
            elif build_ok:
                report["overall_status"] = "FAIR"
            else:
                report["overall_status"] = "POOR"
            
            # Generate Recommendations
            recommendations = []
            
            if not build_ok:
                recommendations.append({
                    "type": "build_failure",
                    "priority": "critical",
                    "message": "Project build failed - fix build errors before proceeding"
                })
            
            if not compilation_ok:
                error_count = report["compilation_summary"]["total_errors"]
                recommendations.append({
                    "type": "compilation_errors",
                    "priority": "critical",
                    "message": f"Fix {error_count} compilation error(s) before deployment"
                })
            
            if report["test_summary"].get("tests_executed", False):
                if not tests_ok:
                    failed_count = report["test_summary"]["failed_tests"]
                    recommendations.append({
                        "type": "test_failures",
                        "priority": "high",
                        "message": f"Fix {failed_count} failing test(s) for better code quality"
                    })
                
                success_rate = report["test_summary"]["success_rate"]
                if success_rate < 80:
                    recommendations.append({
                        "type": "low_test_success",
                        "priority": "medium",
                        "message": f"Test success rate ({success_rate}%) is below recommended threshold"
                    })
            else:
                recommendations.append({
                    "type": "no_tests",
                    "priority": "medium",
                    "message": "No tests found - consider adding test cases for better quality assurance"
                })
            
            report["recommendations"] = recommendations
            
            # Quality Metrics
            report["quality_metrics"] = {
                "build_quality": "Good" if build_ok else "Poor",
                "code_quality": "Good" if compilation_ok else "Poor",
                "test_quality": "Good" if tests_ok else ("Fair" if report["test_summary"].get("tests_executed", False) else "Unknown"),
                "overall_readiness": report["overall_status"]
            }
            
        except Exception as e:
            report["error"] = f"Failed to generate comprehensive report: {str(e)}"
        
        return report
    
    def _compile_generated_project(self, project_dir: str, language: str) -> Dict[str, Any]:
        """
        Compile the generated project and capture compilation errors
        
        Args:
            project_dir: Path to the generated project directory
            language: Programming language of the project
            
        Returns:
            Dictionary containing compilation results and error analysis
        """
        self.log(f"🔧 Compiling generated {language.upper()} project...")
        
        try:
            # Use the code compiler to compile the project
            compilation_result = self.code_compiler.compile_project(project_dir, language)
            
            # Save compilation results to a file
            compilation_file = os.path.join(project_dir, "compilation_results.json")
            with open(compilation_file, 'w', encoding='utf-8') as f:
                json.dump(compilation_result, f, indent=2, ensure_ascii=False)
            
            # Log compilation status
            if compilation_result.get("success", False):
                self.log(f"✅ Project compilation successful")
            else:
                error_count = compilation_result.get("error_analysis", {}).get("total_errors", 0)
                warning_count = compilation_result.get("error_analysis", {}).get("total_warnings", 0)
                self.log(f"❌ Project compilation failed: {error_count} errors, {warning_count} warnings")
                
                # Log error categories for quick overview
                error_categories = compilation_result.get("error_analysis", {}).get("error_categories", {})
                if error_categories:
                    self.log(f"📊 Error breakdown: {dict(error_categories)}")
            
            # Also compile individual files for more detailed analysis
            code_files = self._get_code_files_in_project(project_dir, language)
            if code_files:
                individual_results = self.code_compiler.compile_individual_files(code_files, language)
                compilation_result["individual_file_results"] = individual_results
                
                # Log individual file results
                successful_files = len(individual_results.get("successful_files", []))
                failed_files = len(individual_results.get("failed_files", []))
                self.log(f"📄 Individual file compilation: {successful_files} successful, {failed_files} failed")
            
            return compilation_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Compilation process failed: {str(e)}",
                "project_dir": project_dir,
                "language": language,
                "exception": str(e)
            }
            
            self.log(f"❌ Compilation process error: {str(e)}")
            return error_result
    
    def _get_code_files_in_project(self, project_dir: str, language: str) -> List[str]:
        """
        Get all code files in the project directory for the specified language
        
        Args:
            project_dir: Project directory path
            language: Programming language
            
        Returns:
            List of code file paths
        """
        extensions = {
            'csharp': ['.cs'],
            'c#': ['.cs'],
            'python': ['.py'],
            'javascript': ['.js'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs']
        }
        
        target_extensions = extensions.get(language.lower(), [])
        if not target_extensions:
            return []
        
        code_files = []
        
        try:
            for root, dirs, files in os.walk(project_dir):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['bin', 'obj', 'target', 'node_modules', '__pycache__', '.git']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in target_extensions):
                        file_path = os.path.join(root, file)
                        code_files.append(file_path)
        
        except Exception as e:
            self.log(f"Error scanning for code files: {str(e)}")
        
        return code_files
    
    def _enhance_scenarios_with_compilation_errors(self, scenarios: list, compilation_result: Dict[str, Any], 
                                                 language: str) -> list:
        """
        Enhance scenarios with compilation error information to guide the next generation attempt
        
        Args:
            scenarios: Original scenarios list
            compilation_result: Results from compilation attempt
            language: Programming language
            
        Returns:
            Enhanced scenarios with compilation error context
        """
        self.log("🔧 Enhancing scenarios with compilation error feedback...")
        
        # Extract compilation error information
        error_analysis = compilation_result.get("error_analysis", {})
        detailed_errors = error_analysis.get("detailed_errors", [])
        error_categories = error_analysis.get("error_categories", {})
        total_errors = error_analysis.get("total_errors", 0)
        
        if total_errors == 0:
            self.log("⚠️ No compilation errors found in analysis, but compilation failed. This indicates an issue with error parsing.")
            # Force re-analysis if errors are missing
            stdout = compilation_result.get("stdout", "")
            stderr = compilation_result.get("stderr", "")
            if stdout or stderr:
                self.log("🔍 Re-analyzing compilation output for missed errors...")
                error_analysis = self.code_compiler._analyze_compilation_errors(stderr, stdout, language)
                detailed_errors = error_analysis.get("detailed_errors", [])
                error_categories = error_analysis.get("error_categories", {})
                total_errors = error_analysis.get("total_errors", 0)
                self.log(f"🔍 Re-analysis found {total_errors} errors")
        
        # Create compilation error summary
        error_summary = self._create_compilation_error_summary(error_analysis, language)
        
        # Generate specific code fixes based on actual errors
        code_fixes = self._generate_specific_code_fixes(detailed_errors, language)
        
        # Enhance each scenario with compilation context
        enhanced_scenarios = []
        
        for i, scenario in enumerate(scenarios):
            if isinstance(scenario, str):
                # Convert string scenario to enhanced object
                enhanced_scenario = {
                    "name": f"Scenario {i+1}",
                    "description": scenario,
                    "purpose": f"Implement functionality: {scenario}",
                    "category": "functionality",
                    "priority": "medium",
                    "expectedOutcome": f"Working implementation of: {scenario}",
                    "has_compilation_context": True,
                    "previous_errors_count": total_errors,
                    "error_categories": list(error_categories.keys()),
                    "compilation_context": {
                        "previous_errors": detailed_errors[:5],  # Top 5 errors
                        "error_categories": dict(error_categories),
                        "total_errors": total_errors,
                        "error_summary": error_summary,
                        "fix_instructions": self._generate_fix_instructions(error_analysis, language),
                        "specific_code_fixes": code_fixes,
                        "regenerate_mode": "fix_existing_code"  # Important: fix instead of regenerate
                    }
                }
            elif isinstance(scenario, dict):
                # Enhance existing scenario object
                enhanced_scenario = scenario.copy()
                enhanced_scenario["has_compilation_context"] = True
                enhanced_scenario["previous_errors_count"] = total_errors
                enhanced_scenario["error_categories"] = list(error_categories.keys())
                enhanced_scenario["compilation_context"] = {
                    "previous_errors": detailed_errors[:5],
                    "error_categories": dict(error_categories),
                    "total_errors": total_errors,
                    "error_summary": error_summary,
                    "fix_instructions": self._generate_fix_instructions(error_analysis, language),
                    "specific_code_fixes": code_fixes,
                    "regenerate_mode": "fix_existing_code"
                }
            else:
                # Fallback for unexpected scenario format
                enhanced_scenario = {
                    "name": f"Scenario {i+1}",
                    "description": str(scenario),
                    "purpose": f"Implement: {str(scenario)}",
                    "category": "functionality",
                    "priority": "medium",
                    "expectedOutcome": f"Working implementation",
                    "has_compilation_context": True,
                    "previous_errors_count": total_errors,
                    "error_categories": list(error_categories.keys()),
                    "compilation_context": {
                        "previous_errors": detailed_errors[:5],
                        "error_categories": dict(error_categories),
                        "total_errors": total_errors,
                        "error_summary": error_summary,
                        "fix_instructions": self._generate_fix_instructions(error_analysis, language),
                        "specific_code_fixes": code_fixes,
                        "regenerate_mode": "fix_existing_code"
                    }
                }
            
            enhanced_scenarios.append(enhanced_scenario)
        
        self.log(f"✅ Enhanced {len(enhanced_scenarios)} scenarios with compilation error context")
        self.log(f"📊 Total errors to address: {total_errors}")
        if error_categories:
            self.log(f"📊 Error categories: {dict(error_categories)}")
        
        return enhanced_scenarios
    
    def _create_compilation_error_summary(self, error_analysis: Dict[str, Any], language: str) -> str:
        """Create a human-readable summary of compilation errors"""
        
        total_errors = error_analysis.get("total_errors", 0)
        error_categories = error_analysis.get("error_categories", {})
        
        if total_errors == 0:
            return "No compilation errors found."
        
        summary_parts = [
            f"Found {total_errors} compilation errors in the {language.upper()} code."
        ]
        
        if error_categories:
            summary_parts.append("Error breakdown:")
            for category, count in error_categories.items():
                summary_parts.append(f"  - {category}: {count} errors")
        
        return "\n".join(summary_parts)
    
    def _generate_fix_instructions(self, error_analysis: Dict[str, Any], language: str) -> List[str]:
        """Generate specific fix instructions based on error analysis"""
        
        instructions = []
        error_categories = error_analysis.get("error_categories", {})
        detailed_errors = error_analysis.get("detailed_errors", [])
        
        # Generic fix instructions based on common error patterns
        for error in detailed_errors:
            error_lower = error.lower()
            
            # Syntax errors (universal)
            if any(keyword in error_lower for keyword in ['syntax', 'expected', 'missing', 'unexpected']):
                instructions.append("Fix syntax errors: check for missing brackets, parentheses, semicolons, or colons")
            
            # Undefined/undeclared identifiers (universal)
            elif any(keyword in error_lower for keyword in ['undefined', 'undeclared', 'not found', 'does not exist', 'cannot find']):
                instructions.append("Undefined identifier: ensure proper imports/using statements and check spelling")
                instructions.append("Verify the identifier exists in the target SDK/library documentation")
            
            # Type-related errors (universal)
            elif any(keyword in error_lower for keyword in ['type', 'cannot convert', 'incompatible', 'mismatch']):
                instructions.append("Type error: ensure variable types match expected types and use proper casting")
            
            # Method/property access errors (universal)
            elif any(keyword in error_lower for keyword in ['does not contain', 'no such method', 'attribute error']):
                instructions.append("Method/property doesn't exist: verify API documentation and method signatures")
                instructions.append("Check that the object type supports the called method or property")
        
        # Category-based generic instructions
        if 'Syntax error' in error_categories or 'Syntax Error' in error_categories:
            instructions.append(f"Review {language} syntax rules: proper indentation, statement terminators, and block structure")
        
        if any('undefined' in cat.lower() or 'not found' in cat.lower() for cat in error_categories.keys()):
            instructions.append(f"Add all required import/using statements for {language}")
            instructions.append("Install missing packages/libraries using the appropriate package manager")
        
        if any('type' in cat.lower() for cat in error_categories.keys()):
            instructions.append(f"Ensure type safety following {language} conventions")
            instructions.append("Use explicit type declarations where supported by the language")
        
        # Language-specific common issues (keep minimal and generic)
        if language.lower() in ['csharp', 'c#']:
            instructions.extend([
                "Ensure all using statements are at the top of the file",
                "Use proper async/await patterns for asynchronous operations",
                "Add NuGet package references to the .csproj file if needed"
            ])
        elif language.lower() == 'python':
            instructions.extend([
                "Check indentation (use 4 spaces consistently)",
                "Install packages using: pip install package_name",
                "Use proper import syntax: from module import class"
            ])
        elif language.lower() in ['javascript', 'js', 'node.js']:
            instructions.extend([
                "Install packages using: npm install package_name",
                "Use proper import/require syntax for modules",
                "Check for proper function and variable declarations"
            ])
        elif language.lower() == 'java':
            instructions.extend([
                "Add import statements for all external classes",
                "Ensure proper package declarations",
                "Check Maven/Gradle dependencies"
            ])
        elif language.lower() == 'go':
            instructions.extend([
                "Add import statements in the import block",
                "Run 'go mod tidy' to resolve dependencies",
                "Use proper Go naming conventions"
            ])
        elif language.lower() == 'rust':
            instructions.extend([
                "Add dependencies to Cargo.toml",
                "Use proper 'use' statements for imports",
                "Follow Rust ownership and borrowing rules"
            ])
        
        # Generic catch-all instructions
        if not instructions:
            instructions.extend([
                f"Review the compilation errors carefully for {language}",
                "Fix syntax errors first, then address logical errors",
                "Ensure all dependencies are properly declared",
                "Verify all API calls against official documentation",
                "Use only verified, existing methods and properties"
            ])
        
        return instructions
    
    def _generate_specific_code_fixes(self, detailed_errors: List[str], language: str) -> List[str]:
        """Generate specific code fixes based on actual compilation errors"""
        
        code_fixes = []
        
        # Process errors based on language with enhanced context awareness
        if language.lower() in ['csharp', 'c#']:
            for error in detailed_errors:
                if "CS1026" in error and ") expected" in error:
                    # Extract file and line info
                    if ".cs(" in error:
                        file_line = error.split(".cs(")[1].split(")")[0] if ".cs(" in error else "unknown"
                        code_fixes.append(f"Line {file_line}: Add missing closing parenthesis ')' - check method calls and expressions")
                
                elif "CS0103" in error and "does not exist" in error:
                    # Extract the undefined name
                    var_name = error.split("'")[1] if "'" in error else "unknown variable"
                    if "Microsoft" in var_name or "Azure" in var_name or "Cosmos" in var_name:
                        code_fixes.append(f"Add 'using Microsoft.Azure.Cosmos;' for '{var_name}' and ensure NuGet package Microsoft.Azure.Cosmos is installed")
                    else:
                        code_fixes.append(f"Define variable '{var_name}' before use or add proper using/import statements")
                
                elif "CS0246" in error and "could not be found" in error:
                    # Extract the missing type
                    type_name = error.split("'")[1] if "'" in error else "unknown type"
                    if "Cosmos" in type_name or "Container" in type_name or "Database" in type_name:
                        code_fixes.append(f"Add 'using Microsoft.Azure.Cosmos;' and install NuGet package for type '{type_name}'")
                    else:
                        code_fixes.append(f"Add proper using statements or NuGet package reference for type '{type_name}'")
                
                elif "CS1061" in error and "does not contain a definition" in error:
                    if "FeedResponse" in error and "indexer" in error:
                        code_fixes.append("Replace FeedResponse[index] with FeedResponse.ToList()[index] or use foreach iteration over FeedResponse")
                    elif "ItemResponse" in error:
                        code_fixes.append("Use ItemResponse<T>.Resource to access the actual item data instead of direct casting")
                    else:
                        code_fixes.append("Method/property doesn't exist - verify API documentation and use correct method names with proper parameters")
                
                elif "CS0029" in error and "cannot implicitly convert" in error:
                    if "ItemResponse" in error and "Document" in error:
                        code_fixes.append("Use ItemResponse<T>.Resource property to access the document data")
                    else:
                        code_fixes.append("Use explicit type conversion or verify type compatibility")
                
                elif "CS0019" in error and "operator" in error:
                    code_fixes.append("Operator cannot be applied - check operand types and use appropriate comparison methods")
                
                elif "CS1503" in error and "argument" in error:
                    code_fixes.append("Method parameter mismatch - verify parameter types and count match the method signature")
        
        elif language.lower() == 'python':
            for error in detailed_errors:
                if 'SyntaxError' in error:
                    if 'invalid syntax' in error:
                        code_fixes.append("Fix Python syntax: check for missing colons, parentheses, or proper indentation")
                    elif 'unexpected EOF' in error:
                        code_fixes.append("Fix incomplete code: ensure all brackets/parentheses are properly closed")
                    else:
                        code_fixes.append("Fix Python syntax: ensure proper indentation and colons after function/class definitions")
                
                elif 'ImportError' in error or 'ModuleNotFoundError' in error:
                    if 'azure' in error.lower():
                        code_fixes.append("Install Azure SDK: pip install azure-cosmos azure-identity")
                    elif 'pytest' in error.lower():
                        code_fixes.append("Install pytest: pip install pytest")
                    else:
                        code_fixes.append("Install missing packages with pip install or fix import statements")
                
                elif 'NameError' in error:
                    var_name = error.split("'")[1] if "'" in error else "unknown"
                    code_fixes.append(f"Define variable '{var_name}' before use - check for typos in variable names")
                
                elif 'AttributeError' in error:
                    if 'object has no attribute' in error:
                        attr_name = error.split("'")[-2] if "'" in error else "unknown"
                        code_fixes.append(f"Method/attribute '{attr_name}' doesn't exist - verify object has the called method or check API documentation")
                    else:
                        code_fixes.append("Method/attribute doesn't exist - verify object has the called method")
                
                elif 'TypeError' in error:
                    if 'takes' in error and 'positional arguments' in error:
                        code_fixes.append("Function parameter mismatch - check number and types of arguments passed")
                    else:
                        code_fixes.append("Type error - verify parameter types and method signatures")
        
        elif language.lower() in ['javascript', 'js', 'node.js']:
            for error in detailed_errors:
                if 'SyntaxError' in error:
                    if 'unexpected token' in error:
                        code_fixes.append("Fix JavaScript syntax: check for missing/extra brackets, semicolons, or parentheses")
                    else:
                        code_fixes.append("Fix JavaScript syntax: ensure proper bracket matching and semicolon usage")
                
                elif 'ReferenceError' in error:
                    if 'is not defined' in error:
                        var_name = error.split("'")[1] if "'" in error else error.split()[0]
                        code_fixes.append(f"Variable/function '{var_name}' not defined - ensure proper declaration before use")
                    else:
                        code_fixes.append("Variable/function not defined - ensure proper declaration before use")
                
                elif 'TypeError' in error:
                    if 'is not a function' in error:
                        code_fixes.append("Object is not a function - verify the object is callable and properly imported")
                    else:
                        code_fixes.append("Type mismatch - verify object types and method availability")
        
        elif language.lower() == 'java':
            for error in detailed_errors:
                if 'cannot find symbol' in error.lower():
                    if 'class' in error:
                        code_fixes.append("Class not found - add proper import statements or check classpath")
                    elif 'method' in error:
                        code_fixes.append("Method not found - verify method name, parameters, and import statements")
                    else:
                        code_fixes.append("Symbol not found - add proper import statements or check spelling")
                
                elif 'incompatible types' in error.lower():
                    code_fixes.append("Type mismatch - ensure variable types match expected types or use proper casting")
                
                elif 'method does not exist' in error.lower():
                    code_fixes.append("Method doesn't exist - verify method name, parameters, and class inheritance")
        
        # Add language-agnostic fixes based on common error patterns
        for error in detailed_errors:
            error_lower = error.lower()
            
            # Common SDK/Library specific fixes
            if 'cosmos' in error_lower and 'microsoft' in error_lower:
                code_fixes.append("Azure Cosmos DB error - ensure Microsoft.Azure.Cosmos package is installed and using statements are added")
            
            elif 'unauthorized' in error_lower or 'authentication' in error_lower:
                code_fixes.append("Authentication error - verify connection strings and credentials")
            
            elif 'timeout' in error_lower:
                code_fixes.append("Timeout error - increase timeout values or check network connectivity")
            
            elif 'null' in error_lower and 'reference' in error_lower:
                code_fixes.append("Null reference - add null checks before accessing object properties/methods")
        
        # Add generic fixes if no specific ones were found
        if not code_fixes:
            code_fixes.extend([
                f"Review each compilation error carefully and fix syntax issues for {language}",
                "Ensure all required imports/using statements are present at the top of files",
                "Verify method calls match the actual API signatures from official documentation",
                "Add missing dependencies to the project configuration",
                "Check for typos in variable names, method names, and type names",
                "Ensure proper exception handling for external API calls"
            ])
        
        # Deduplicate and limit fixes
        unique_fixes = list(dict.fromkeys(code_fixes))  # Remove duplicates while preserving order
        return unique_fixes[:15]  # Limit to top 15 fixes
    
    def _cleanup_failed_compilation_files(self, project_dir: str, language: str):
        """Clean up generated files from failed compilation attempt"""
        try:
            # Remove compiled artifacts but keep source files for reference
            artifacts_to_remove = []
            
            if language.lower() in ['csharp', 'c#']:
                artifacts_to_remove.extend(['bin', 'obj'])
            elif language.lower() == 'java':
                artifacts_to_remove.extend(['target', '*.class'])
            elif language.lower() == 'javascript':
                artifacts_to_remove.extend(['node_modules', 'dist'])
            elif language.lower() == 'python':
                artifacts_to_remove.extend(['__pycache__', '*.pyc'])
            elif language.lower() == 'go':
                artifacts_to_remove.extend(['*.exe', '*.out'])
            elif language.lower() == 'rust':
                artifacts_to_remove.extend(['target'])
            
            for artifact in artifacts_to_remove:
                artifact_path = os.path.join(project_dir, artifact)
                if os.path.exists(artifact_path):
                    if os.path.isdir(artifact_path):
                        import shutil
                        shutil.rmtree(artifact_path)
                        self.log(f"🧹 Cleaned up directory: {artifact}")
                    else:
                        os.remove(artifact_path)
                        self.log(f"🧹 Cleaned up file: {artifact}")
        
        except Exception as e:
            self.log(f"⚠️ Warning: Could not clean up some compilation artifacts: {str(e)}")
    
    def _extract_scenario_summary(self, scenario: Any, index: int) -> Dict[str, Any]:
        """Extract key information from a scenario for tracking purposes"""
        if isinstance(scenario, str):
            return {
                "index": index,
                "name": f"Scenario {index}",
                "description": scenario[:100] + "..." if len(scenario) > 100 else scenario,
                "has_compilation_context": False
            }
        elif isinstance(scenario, dict):
            compilation_context = scenario.get("compilation_context", {})
            return {
                "index": index,
                "name": scenario.get("name", f"Scenario {index}"),
                "description": (scenario.get("description", "")[:100] + "...") if len(scenario.get("description", "")) > 100 else scenario.get("description", ""),
                "has_compilation_context": bool(compilation_context),
                "previous_errors_count": len(compilation_context.get("previous_errors", [])) if compilation_context else 0,
                "error_categories": list(compilation_context.get("error_categories", {}).keys()) if compilation_context else []
            }
        else:
            return {
                "index": index,
                "name": f"Scenario {index}",
                "description": str(scenario)[:100] + "..." if len(str(scenario)) > 100 else str(scenario),
                "has_compilation_context": False
            }
    
    def _create_detailed_error_analysis(self, compilation_result: Dict[str, Any], attempt_number: int) -> Dict[str, Any]:
        """Create detailed error analysis for compilation attempt tracking"""
        error_analysis = compilation_result.get("error_analysis", {})
        
        # Extract key error information
        detailed_errors = error_analysis.get("detailed_errors", [])
        error_categories = error_analysis.get("error_categories", {})
        suggestions = error_analysis.get("suggestions", [])
        
        # Categorize errors for better analysis
        categorized_errors = {
            "missing_imports": [],
            "type_errors": [],
            "method_errors": [],
            "assembly_errors": [],
            "syntax_errors": [],
            "other_errors": []
        }
        
        for error in detailed_errors:
            error_lower = error.lower()
            if "using directive" in error_lower or "namespace" in error_lower:
                categorized_errors["missing_imports"].append(error)
            elif "type" in error_lower and ("not found" in error_lower or "does not exist" in error_lower):
                categorized_errors["type_errors"].append(error)
            elif "does not contain a definition for" in error_lower or "method" in error_lower:
                categorized_errors["method_errors"].append(error)
            elif "assembly reference" in error_lower or "could not be found" in error_lower:
                categorized_errors["assembly_errors"].append(error)
            elif "syntax" in error_lower or "expected" in error_lower:
                categorized_errors["syntax_errors"].append(error)
            else:
                categorized_errors["other_errors"].append(error)
        
        # Generate specific suggestions based on error patterns
        pattern_suggestions = []
        if categorized_errors["missing_imports"]:
            pattern_suggestions.append("Add missing using/import directives at the top of files")
        if categorized_errors["type_errors"]:
            pattern_suggestions.append("Install required NuGet packages or add assembly references")
        if categorized_errors["method_errors"]:
            pattern_suggestions.append("Verify method signatures and use correct SDK API calls")
        if categorized_errors["assembly_errors"]:
            pattern_suggestions.append("Check project file for missing package references")
        
        return {
            "attempt_number": attempt_number,
            "total_errors": error_analysis.get("total_errors", 0),
            "total_warnings": error_analysis.get("total_warnings", 0),
            "detailed_errors": detailed_errors[:15],  # Limit to top 15 errors
            "categorized_errors": categorized_errors,
            "error_categories": error_categories,
            "original_suggestions": suggestions[:10],  # Limit to top 10 suggestions
            "pattern_suggestions": pattern_suggestions,
            "compilation_success": compilation_result.get("success", False),
            "compilation_error": compilation_result.get("error", "Unknown error"),
            "error_summary": self._create_error_summary(categorized_errors, error_analysis.get("total_errors", 0))
        }
    
    def _analyze_changes_from_previous_attempt(self, compilation_attempts: List[Dict[str, Any]], 
                                             current_compilation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what changed between the current and previous compilation attempt"""
        if not compilation_attempts:
            return None
            
        previous_attempt = compilation_attempts[-1]
        previous_errors = previous_attempt.get("compilation_result", {}).get("error_analysis", {}).get("detailed_errors", [])
        current_errors = current_compilation_result.get("error_analysis", {}).get("detailed_errors", [])
        
        # Convert to sets for comparison
        previous_error_set = set(previous_errors)
        current_error_set = set(current_errors)
        
        # Find resolved and new errors
        resolved_errors = list(previous_error_set - current_error_set)
        new_errors = list(current_error_set - previous_error_set)
        persistent_errors = list(previous_error_set & current_error_set)
        
        # Analyze error count changes
        prev_total = previous_attempt.get("compilation_result", {}).get("error_analysis", {}).get("total_errors", 0)
        curr_total = current_compilation_result.get("error_analysis", {}).get("total_errors", 0)
        error_count_change = curr_total - prev_total
        
        # Determine the type of progress made
        progress_type = "no_change"
        if error_count_change < 0:
            progress_type = "improvement"
        elif error_count_change > 0:
            progress_type = "regression"
        elif resolved_errors and new_errors:
            progress_type = "mixed_changes"
        elif not resolved_errors and not new_errors:
            progress_type = "same_errors"
        
        return {
            "resolved_errors": resolved_errors[:10],  # Limit to top 10
            "new_errors": new_errors[:10],  # Limit to top 10
            "persistent_errors": persistent_errors[:5],  # Limit to top 5
            "error_count_change": error_count_change,
            "previous_error_count": prev_total,
            "current_error_count": curr_total,
            "progress_type": progress_type,
            "improvement_percentage": ((prev_total - curr_total) / prev_total * 100) if prev_total > 0 else 0,
            "change_summary": self._create_change_summary(resolved_errors, new_errors, error_count_change)
        }
    
    def _create_error_summary(self, categorized_errors: Dict[str, List[str]], total_errors: int) -> str:
        """Create a human-readable summary of compilation errors"""
        if total_errors == 0:
            return "No compilation errors"
        
        summary_parts = []
        
        for category, errors in categorized_errors.items():
            if errors:
                category_name = category.replace("_", " ").title()
                summary_parts.append(f"{len(errors)} {category_name}")
        
        if summary_parts:
            return f"Build failed with {total_errors} errors: " + ", ".join(summary_parts)
        else:
            return f"Build failed with {total_errors} compilation errors"
    
    def _create_change_summary(self, resolved_errors: List[str], new_errors: List[str], error_count_change: int) -> str:
        """Create a summary of changes between compilation attempts"""
        if error_count_change == 0 and not resolved_errors and not new_errors:
            return "No changes in compilation errors - same error pattern"
        
        summary_parts = []
        
        if resolved_errors:
            summary_parts.append(f"Fixed {len(resolved_errors)} errors")
        
        if new_errors:
            summary_parts.append(f"Introduced {len(new_errors)} new errors")
        
        if error_count_change < 0:
            summary_parts.append(f"Overall improvement: {abs(error_count_change)} fewer errors")
        elif error_count_change > 0:
            summary_parts.append(f"Regression: {error_count_change} more errors")
        
        return "; ".join(summary_parts) if summary_parts else "Attempted different fixes for similar error patterns"
    
    def _identify_scenarios_with_compilation_errors(self, compilation_result: Dict[str, Any], 
                                                  scenarios: list, project_dir: str, language: str) -> List[Dict[str, Any]]:
        """Identify which specific scenarios have compilation errors (more targeted than file-based approach)"""
        
        detailed_errors = compilation_result.get("error_analysis", {}).get("detailed_errors", [])
        scenarios_with_errors = []
        scenario_error_map = {}
        
        # Parse compilation errors and map them to scenarios
        for error in detailed_errors:
            scenario_info = self._parse_compilation_error_for_scenario(error, scenarios, project_dir, language)
            if scenario_info:
                scenario_name = scenario_info["scenario_name"]
                scenario_index = scenario_info["scenario_index"]
                
                if scenario_name not in scenario_error_map:
                    scenario_error_map[scenario_name] = {
                        "scenario_name": scenario_name,
                        "scenario_index": scenario_index,
                        "scenario_data": scenarios[scenario_index] if scenario_index < len(scenarios) else None,
                        "errors": [],
                        "error_categories": set(),
                        "files_affected": set()
                    }
                
                scenario_error_map[scenario_name]["errors"].append(error)
                scenario_error_map[scenario_name]["error_categories"].add(scenario_info.get("category", "unknown"))
                if "file_path" in scenario_info:
                    scenario_error_map[scenario_name]["files_affected"].add(scenario_info["file_path"])
        
        # Convert to list and finalize
        for scenario_name, info in scenario_error_map.items():
            info["error_categories"] = list(info["error_categories"])
            info["files_affected"] = list(info["files_affected"])
            info["error_count"] = len(info["errors"])
            scenarios_with_errors.append(info)
        
        self.log(f"🎯 Identified {len(scenarios_with_errors)} specific scenarios with compilation errors")
        for scenario_info in scenarios_with_errors:
            self.log(f"  - {scenario_info['scenario_name']}: {scenario_info['error_count']} errors")
        
        return scenarios_with_errors

    def _parse_compilation_error_for_scenario(self, error: str, scenarios: list, project_dir: str, language: str) -> Dict[str, Any]:
        """Parse a compilation error to extract scenario information"""
        
        # Language-specific error parsing to identify scenarios
        if language.lower() in ["c#", "csharp"]:
            # C# error format: "path\ScenarioNameTest.cs(line,col): error CS0103: ..."
            import re
            match = re.search(r'([^:]+\.cs)\(\d+,\d+\):\s*error\s+(\w+):\s*(.+)', error)
            if match:
                file_path = match.group(1)
                error_code = match.group(2)
                error_message = match.group(3)
                
                # Extract scenario name from file path (remove Test suffix and .cs extension)
                file_name = os.path.basename(file_path)
                scenario_name = file_name.replace("Test.cs", "").replace(".cs", "")
                
                # Find the scenario index in the original scenarios list
                scenario_index = self._find_scenario_index_by_name(scenario_name, scenarios)
                
                return {
                    "file_path": os.path.join(project_dir, file_path),
                    "scenario_name": scenario_name,
                    "scenario_index": scenario_index,
                    "error": error,
                    "error_code": error_code,
                    "error_message": error_message,
                    "category": self._categorize_error(error_message)
                }
        
        elif language.lower() == "python":
            # Python error format: File "ScenarioNameTest.py", line X
            import re
            match = re.search(r'File "([^"]+\.py)", line \d+', error)
            if match:
                file_path = match.group(1)
                file_name = os.path.basename(file_path)
                scenario_name = file_name.replace("Test.py", "").replace("_test.py", "").replace(".py", "")
                
                # Find the scenario index in the original scenarios list
                scenario_index = self._find_scenario_index_by_name(scenario_name, scenarios)
                
                return {
                    "file_path": file_path,
                    "scenario_name": scenario_name,
                    "scenario_index": scenario_index,
                    "error": error,
                    "category": self._categorize_error(error)
                }
        
        # Add more language-specific parsing as needed
        return None

    def _find_scenario_index_by_name(self, scenario_name: str, scenarios: list) -> int:
        """Find the index of a scenario by its generated name"""
        
        for i, scenario in enumerate(scenarios):
            # Get the scenario name that would be generated for this scenario
            generated_name = self._create_class_name_from_scenario(self._get_scenario_name(scenario))
            
            if generated_name == scenario_name:
                return i
        
        # If exact match not found, try partial matching
        for i, scenario in enumerate(scenarios):
            scenario_text = self._get_scenario_name(scenario).lower()
            if scenario_name.lower() in scenario_text or scenario_text in scenario_name.lower():
                return i
        
        return -1  # Not found

    def _regenerate_only_failed_scenarios(self, scenarios_with_errors: List[Dict[str, Any]], 
                                        original_scenario_results: Dict[str, Any], language: str, 
                                        product_name: str, version: str, setup_info: dict, 
                                        project_dir: str, analysis_data: dict, 
                                        compilation_result: Dict[str, Any], attempt: int = 2) -> Dict[str, Any]:
        """Regenerate ONLY the scenarios that had compilation errors"""
        
        updated_results = {
            "successful": [],
            "failed": [],
            "total_processed": 0,
            "generation_details": [],
            "selective_fixes": []
        }
        
        self.log(f"🎯 [Attempt {attempt}] Regenerating only {len(scenarios_with_errors)} scenarios with errors (keeping {len(original_scenario_results.get('successful', []))} working scenarios unchanged)")
        
        # Process only scenarios that had compilation errors
        for scenario_error_info in scenarios_with_errors:
            scenario_index = scenario_error_info["scenario_index"]
            scenario_name = scenario_error_info["scenario_name"]
            original_scenario = scenario_error_info["scenario_data"]
            
            if original_scenario is None or scenario_index == -1:
                self.log(f"⚠️ Could not find original scenario data for {scenario_name}, skipping...")
                continue
            
            self.log(f"🛠️ [Attempt {attempt}] 🔧 Fixing scenario with errors: {scenario_name} (index {scenario_index})")
            
            # Enhance this specific scenario with its specific error context
            enhanced_scenario = self._enhance_single_scenario_with_specific_errors(
                original_scenario, scenario_error_info, compilation_result, language
            )
            
            # Regenerate code for this specific scenario with error fixes
            try:
                # Get context for prompt generation
                detected_dependencies = PackageVersions.detect_dependencies_from_scenario(analysis_data)
                test_packages = PackageVersions.get_test_packages_with_cosmosdb(language, analysis_data)
                primary_test_framework = PackageVersions.get_primary_test_framework(language)
                
                context = {
                    'dotnet_version': PackageVersions.get_language_version('dotnet'),
                    'java_version': PackageVersions.get_language_version('java'),
                    'node_version': PackageVersions.get_language_version('node'),
                    'python_version': PackageVersions.get_language_version('python'),
                    'go_version': PackageVersions.get_language_version('go'),
                    'rust_version': PackageVersions.get_language_version('rust'),
                    'test_packages': test_packages,
                    'dependencies': detected_dependencies.get(language.lower(), {}),
                    'primary_test_framework': primary_test_framework,
                    'scenario_based_packages': True
                }
                
                # Generate the fixed code for this scenario
                scenario_result = self._generate_single_scenario_with_error_context(
                    enhanced_scenario, scenario_index + 1, language, product_name, version, 
                    setup_info, analysis_data, context, attempt
                )
                
                if scenario_result:
                    # Extract and save the regenerated code files
                    scenario_files = self._extract_scenario_code_files(
                        scenario_result, project_dir, language, scenario_index + 1, scenario_name
                    )
                    
                    scenario_detail = {
                        "scenario_index": scenario_index + 1,
                        "scenario_name": scenario_name,
                        "generated_content": scenario_result,
                        "code_files": scenario_files,
                        "content_length": len(scenario_result),
                        "generation_time": datetime.now().isoformat(),
                        "fix_attempt": True,
                        "original_errors": scenario_error_info["errors"]
                    }
                    
                    updated_results["successful"].append(scenario_detail)
                    updated_results["selective_fixes"].append({
                        "scenario_name": scenario_name,
                        "scenario_index": scenario_index,
                        "errors_addressed": len(scenario_error_info["errors"]),
                        "fix_status": "success"
                    })
                    self.log(f"✅ [Attempt {attempt}] Successfully regenerated scenario: {scenario_name} (fixed {len(scenario_error_info['errors'])} errors)")
                else:
                    updated_results["failed"].append({
                        "scenario_index": scenario_index + 1,
                        "scenario_name": scenario_name,
                        "error": "Failed to generate fixed code",
                        "original_errors": scenario_error_info["errors"]
                    })
                    self.log(f"❌ [Attempt {attempt}] Failed to regenerate scenario: {scenario_name}")
                        
            except Exception as e:
                self.log(f"❌ [Attempt {attempt}] Error regenerating scenario {scenario_name}: {str(e)}")
                updated_results["failed"].append({
                    "scenario_index": scenario_index + 1,
                    "scenario_name": scenario_name,
                    "error": str(e),
                    "original_errors": scenario_error_info["errors"]
                })
            
            updated_results["total_processed"] += 1
        
        success_count = len(updated_results["successful"])
        fail_count = len(updated_results["failed"])
        self.log(f"📊 Selective regeneration results: {success_count} fixed, {fail_count} failed")
        return updated_results

    def _enhance_single_scenario_with_specific_errors(self, scenario: Any, scenario_error_info: Dict[str, Any], 
                                                    compilation_result: Dict[str, Any], language: str) -> Any:
        """Enhance a single scenario with its specific compilation error context"""
        
        if isinstance(scenario, str):
            # Convert string scenario to enhanced object with error context
            enhanced_scenario = {
                "name": scenario_error_info["scenario_name"],
                "description": scenario,
                "purpose": f"Fix compilation errors in: {scenario}",
                "category": "error_fix",
                "priority": "high",
                "expectedOutcome": f"Compile successfully without errors"
            }
        elif isinstance(scenario, dict):
            # Copy existing scenario and enhance with error context
            enhanced_scenario = scenario.copy()
        else:
            # Fallback
            enhanced_scenario = {
                "name": scenario_error_info["scenario_name"],
                "description": str(scenario),
                "purpose": f"Fix compilation errors",
                "category": "error_fix",
                "priority": "high"
            }
        
        # Extract detailed compilation error messages for this specific scenario
        raw_error_messages = scenario_error_info["errors"]
        parsed_errors = self._parse_errors_for_scenario_context(raw_error_messages, language)
        
        # Create comprehensive error context with detailed error messages
        enhanced_scenario["compilation_context"] = {
            "regenerate_mode": "fix_existing_code",
            "scenario_specific_errors": raw_error_messages,  # Raw error messages from compiler
            "parsed_error_details": parsed_errors,  # Structured error information
            "error_categories": scenario_error_info["error_categories"],
            "files_affected": scenario_error_info["files_affected"],
            "error_count": scenario_error_info["error_count"],
            "error_summary": self._create_scenario_error_summary(scenario_error_info, parsed_errors),
            "fix_instructions": self._generate_fix_instructions_for_scenario_errors(raw_error_messages, language),
            "specific_code_fixes": self._generate_specific_code_fixes(raw_error_messages, language),
            "previous_errors": raw_error_messages,  # Ensure compatibility with existing prompt template
            "detailed_error_breakdown": self._create_detailed_error_breakdown(parsed_errors, language)
        }
        
        return enhanced_scenario

    def _parse_errors_for_scenario_context(self, errors: List[str], language: str) -> List[Dict[str, Any]]:
        """Parse raw compilation errors into structured format for better LLM understanding"""
        
        parsed_errors = []
        
        for error in errors:
            error_info = {
                "raw_message": error,
                "error_type": "unknown",
                "error_code": "",
                "line_number": "",
                "column_number": "",
                "file_name": "",
                "description": "",
                "suggested_fix": ""
            }
            
            if language.lower() in ["c#", "csharp"]:
                # Parse C# compiler errors
                # Format: "path\file.cs(line,col): error CS0103: The name 'SomeClass' does not exist in the current context"
                import re
                
                # Extract file, line, column, error code, and message
                match = re.search(r'([^\\/:*?"<>|]+\.cs)\((\d+),(\d+)\):\s*error\s+(CS\d+):\s*(.+)', error)
                if match:
                    error_info.update({
                        "file_name": match.group(1),
                        "line_number": match.group(2),
                        "column_number": match.group(3),
                        "error_code": match.group(4),
                        "description": match.group(5),
                        "error_type": self._categorize_csharp_error(match.group(4), match.group(5)),
                        "suggested_fix": self._suggest_csharp_fix(match.group(4), match.group(5))
                    })
                
            elif language.lower() == "python":
                # Parse Python errors
                # Format: "File "script.py", line 10, in <module> NameError: name 'undefined_var' is not defined"
                import re
                
                # Extract file and line number
                file_match = re.search(r'File "([^"]+\.py)", line (\d+)', error)
                if file_match:
                    error_info["file_name"] = file_match.group(1)
                    error_info["line_number"] = file_match.group(2)
                
                # Extract error type and message
                error_match = re.search(r'(\w+Error):\s*(.+)', error)
                if error_match:
                    error_info.update({
                        "error_code": error_match.group(1),
                        "description": error_match.group(2),
                        "error_type": self._categorize_python_error(error_match.group(1), error_match.group(2)),
                        "suggested_fix": self._suggest_python_fix(error_match.group(1), error_match.group(2))
                    })
            
            # Add more language-specific parsing as needed
            
            parsed_errors.append(error_info)
        
        return parsed_errors

    def _categorize_csharp_error(self, error_code: str, description: str) -> str:
        """Categorize C# compilation errors"""
        error_map = {
            "CS0103": "missing_reference",
            "CS1061": "method_not_found", 
            "CS0246": "type_not_found",
            "CS0029": "type_conversion",
            "CS1503": "argument_mismatch",
            "CS0117": "member_not_found",
            "CS0234": "namespace_not_found"
        }
        return error_map.get(error_code, "syntax_error")

    def _suggest_csharp_fix(self, error_code: str, description: str) -> str:
        """Suggest specific fixes for C# compilation errors"""
        
        fix_suggestions = {
            "CS0103": "Add missing using statement or verify the class/variable name exists",
            "CS1061": "Check if the method exists in the class or add the correct NuGet package",
            "CS0246": "Add missing using statement or install the required NuGet package",
            "CS0029": "Use explicit type conversion or check if types are compatible",
            "CS1503": "Check method parameter types and count",
            "CS0117": "Verify the member exists in the class or use the correct syntax",
            "CS0234": "Add missing using statement or check namespace spelling"
        }
        
        suggestion = fix_suggestions.get(error_code, "Review the error message and fix accordingly")
        
        # Add context-specific suggestions based on description
        if "FeedResponse" in description and "indexer" in description:
            suggestion += ". Replace FeedResponse[index] with FeedResponse.ToList()[index] or use foreach iteration"
        elif "Microsoft.Azure.Cosmos" in description:
            suggestion += ". Add 'using Microsoft.Azure.Cosmos;' and ensure the NuGet package is installed"
        elif "ItemResponse" in description and "cannot convert" in description:
            suggestion += ". Use ItemResponse<T>.Resource to access the actual item data"
        
        return suggestion

    def _categorize_python_error(self, error_type: str, description: str) -> str:
        """Categorize Python errors"""
        error_map = {
            "NameError": "missing_reference",
            "AttributeError": "method_not_found",
            "ImportError": "missing_import",
            "ModuleNotFoundError": "missing_module",
            "TypeError": "type_error",
            "ValueError": "value_error",
            "SyntaxError": "syntax_error"
        }
        return error_map.get(error_type, "runtime_error")

    def _suggest_python_fix(self, error_type: str, description: str) -> str:
        """Suggest specific fixes for Python errors"""
        
        fix_suggestions = {
            "NameError": "Define the variable or import the required module",
            "AttributeError": "Check if the method/attribute exists or import the correct module", 
            "ImportError": "Install the required package with pip install",
            "ModuleNotFoundError": "Install the missing module or check the import path",
            "TypeError": "Check argument types and function signatures",
            "ValueError": "Verify the value is valid for the operation",
            "SyntaxError": "Fix the syntax error in the code"
        }
        
        return fix_suggestions.get(error_type, "Review the error message and fix accordingly")

    def _create_scenario_error_summary(self, scenario_error_info: Dict[str, Any], parsed_errors: List[Dict[str, Any]]) -> str:
        """Create a comprehensive error summary for the scenario"""
        
        scenario_name = scenario_error_info["scenario_name"]
        error_count = scenario_error_info["error_count"]
        
        summary = f"Scenario '{scenario_name}' has {error_count} compilation error(s) that need to be fixed:\n\n"
        
        # Group errors by type
        error_groups = {}
        for error in parsed_errors:
            error_type = error["error_type"]
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # Add detailed breakdown by error type
        for error_type, type_errors in error_groups.items():
            summary += f"**{error_type.replace('_', ' ').title()} Errors ({len(type_errors)}):**\n"
            for i, error in enumerate(type_errors[:3], 1):  # Show max 3 errors per type
                summary += f"{i}. {error['description']}\n"
                if error['suggested_fix']:
                    summary += f"   → Suggested fix: {error['suggested_fix']}\n"
            if len(type_errors) > 3:
                summary += f"   ... and {len(type_errors) - 3} more {error_type} errors\n"
            summary += "\n"
        
        return summary

    def _create_detailed_error_breakdown(self, parsed_errors: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """Create a detailed breakdown of errors for the LLM prompt"""
        
        breakdown = {
            "total_errors": len(parsed_errors),
            "error_types": {},
            "critical_errors": [],
            "common_patterns": [],
            "quick_fixes": []
        }
        
        # Count errors by type
        for error in parsed_errors:
            error_type = error["error_type"]
            breakdown["error_types"][error_type] = breakdown["error_types"].get(error_type, 0) + 1
        
        # Identify critical errors that prevent compilation
        critical_error_codes = ["CS0103", "CS0246", "CS1061", "NameError", "ImportError", "ModuleNotFoundError"]
        for error in parsed_errors:
            if error["error_code"] in critical_error_codes:
                breakdown["critical_errors"].append({
                    "error": error["description"],
                    "fix": error["suggested_fix"],
                    "location": f"{error['file_name']}:{error['line_number']}" if error['line_number'] else error['file_name']
                })
        
        # Identify common error patterns
        if language.lower() in ["c#", "csharp"]:
            if any("Microsoft.Azure.Cosmos" in error["description"] for error in parsed_errors):
                breakdown["common_patterns"].append("Missing Azure Cosmos DB SDK references")
            if any("FeedResponse" in error["description"] for error in parsed_errors):
                breakdown["common_patterns"].append("Incorrect FeedResponse usage patterns")
        
        # Generate quick fixes
        for error in parsed_errors[:5]:  # Top 5 errors
            if error["suggested_fix"]:
                breakdown["quick_fixes"].append(f"Fix {error['error_code']}: {error['suggested_fix']}")
        
        return breakdown

    def _generate_fix_instructions_for_scenario_errors(self, errors: List[str], language: str) -> List[str]:
        """Generate specific fix instructions for the errors in this scenario"""
        
        instructions = []
        
        for error in errors:
            if language.lower() in ["c#", "csharp"]:
                if "CS0103" in error and "name" in error and "does not exist" in error:
                    instructions.append("Add missing using statements or verify class/method names exist in the SDK")
                elif "CS1061" in error and "does not contain a definition" in error:
                    instructions.append("Verify the method exists in the target class and check parameter types")
                elif "CS0246" in error and "type or namespace" in error:
                    instructions.append("Add missing NuGet package references and using statements")
                elif "indexer" in error.lower() and "feedresponse" in error.lower():
                    instructions.append("Replace FeedResponse indexing with proper iteration (.ToList() or foreach)")
                elif "cannot convert" in error.lower():
                    instructions.append("Fix type conversion - use proper casting or access .Resource property")
            
            elif language.lower() == "python":
                if "ImportError" in error or "ModuleNotFoundError" in error:
                    instructions.append("Add missing import statements or install required packages")
                elif "AttributeError" in error:
                    instructions.append("Verify the attribute/method exists on the object")
                elif "TypeError" in error:
                    instructions.append("Check method parameters and return types")
        
        # Add general instructions if no specific ones found
        if not instructions:
            instructions.append(f"Review and fix {language} syntax errors according to language best practices")
            instructions.append("Ensure all required imports/dependencies are included")
            instructions.append("Verify all method calls use correct parameters and exist in the target SDK")
        
        return instructions

    def _merge_fixed_scenarios_into_results(self, original_results: Dict[str, Any], fixed_results: Dict[str, Any]) -> None:
        """Merge the fixed scenarios back into the main scenario results, replacing the failed ones"""
        
        if not fixed_results["successful"]:
            return
        
        # Create a map of fixed scenarios by index for quick lookup
        fixed_scenarios_map = {}
        for fixed_scenario in fixed_results["successful"]:
            scenario_index = fixed_scenario["scenario_index"]
            fixed_scenarios_map[scenario_index] = fixed_scenario
        
        # Replace the failed scenarios in original results with fixed versions
        updated_successful = []
        for scenario in original_results.get("successful", []):
            scenario_index = scenario["scenario_index"]
            if scenario_index in fixed_scenarios_map:
                # Replace with fixed version
                updated_successful.append(fixed_scenarios_map[scenario_index])
                self.log(f"🔄 Replaced scenario {scenario_index} with fixed version")
            else:
                # Keep original successful scenario
                updated_successful.append(scenario)
        
        # Add any newly fixed scenarios that weren't in the original successful list
        for scenario_index, fixed_scenario in fixed_scenarios_map.items():
            if not any(s["scenario_index"] == scenario_index for s in updated_successful):
                updated_successful.append(fixed_scenario)
                self.log(f"➕ Added newly fixed scenario {scenario_index}")
        
        # Update the original results
        original_results["successful"] = updated_successful
        
        # Remove fixed scenarios from failed list
        original_failed = original_results.get("failed", [])
        updated_failed = [s for s in original_failed if s.get("scenario_index") not in fixed_scenarios_map]
        original_results["failed"] = updated_failed
        
        self.log(f"🔄 Merged results: {len(updated_successful)} successful, {len(updated_failed)} failed")

    def _update_project_files_for_fixed_scenarios(self, project_files: Dict[str, Any], 
                                                 fixed_results: Dict[str, Any], 
                                                 scenarios_with_errors: List[Dict[str, Any]], 
                                                 language: str, project_dir: str) -> Dict[str, Any]:
        """Update project files only for the scenarios that were fixed"""
        
        self.log(f"📝 Updating project files for {len(fixed_results['successful'])} fixed scenarios")
        
        # The project files should already be updated by the _extract_scenario_code_files method
        # called during regeneration, so we mainly need to update metadata
        
        # Update project metadata to reflect the fixes
        if "compilation_attempts" not in project_files:
            project_files["compilation_attempts"] = []
        
        # Add information about which scenarios were fixed
        project_files["selective_fixes"] = fixed_results.get("selective_fixes", [])
        project_files["scenarios_regenerated"] = len(fixed_results["successful"])
        project_files["scenarios_kept_unchanged"] = len([s for s in scenarios_with_errors if s["scenario_name"] not in [f["scenario_name"] for f in fixed_results["successful"]]])
        
        self.log(f"✅ Project files updated with selective fixes for {project_files['scenarios_regenerated']} scenarios")
        return project_files

    def _generate_single_scenario_with_error_context(self, enhanced_scenario: Any, scenario_index: int, 
                                                   language: str, product_name: str, version: str, 
                                                   setup_info: dict, analysis_data: dict, context: dict, attempt: int = 2) -> str:
        """Generate code for a single scenario with compilation error context"""
        
        scenario_name = enhanced_scenario.get("scenario_name", "Unknown") if isinstance(enhanced_scenario, dict) else "Unknown"
        self.log(f"🔧 [Attempt {attempt}] Fixing errors in scenario: {scenario_name} (Scenario {scenario_index})")
        
        # Get single-scenario prompt template with error fixing context
        # Load error fix regeneration prompt from prompty file for failed scenarios
        prompt_template = self.prompty_loader.create_prompt_template(
            "code_generator", "error_fix_regeneration"
        )
        
        if not prompt_template:
            self.log(f"❌ No prompt template available for language: {language}")
            return None
        
        # Get LLM with prompty-specific settings for error fix regeneration
        llm_for_chain = self.prompty_loader.create_llm_with_prompty_settings(
            self.llm, "code_generator", "error_fix_regeneration"
        )
        
        chain = prompt_template | llm_for_chain | StrOutputParser()
        
        # Format scenario for prompt (this will include error context)
        scenario_text = self._format_single_scenario_for_prompt(enhanced_scenario, scenario_index)
        setup_info_text = json.dumps(setup_info, indent=2)
        
        # Get language-specific testing framework and unified guidelines for error fix
        testing_framework = self._get_testing_framework(language)
        language_guidelines = self.language_best_practices_manager.get_language_guidelines(
            language=language,
            testing_framework=testing_framework
        )
        product_specific_guidance = self._get_product_specific_guidance(product_name, language, version)
        
        # Prepare prompt variables for single scenario
        prompt_vars = {
            "language": language.upper(),
            "product_name": product_name,
            "testing_framework": testing_framework,
            "language_guidelines": language_guidelines,
            "product_specific_guidance": product_specific_guidance,
            "version": version,
            "scenario": scenario_text,
            "setup_info": setup_info_text,
            "scenario_index": scenario_index,
            "total_scenarios": 1,  # Since we're only regenerating one scenario
            "error_context": self._extract_error_context_for_prompt(enhanced_scenario)
        }
        
        # Log the actual prompt that will be sent to LLM for error fixing
        # Use Jinja2 rendering since prompt_template uses jinja2 format
        jinja_template = jinja2.Template(prompt_template.template)
        actual_prompt = jinja_template.render(**prompt_vars)
        scenario_name = enhanced_scenario.get("scenario_name", "unknown").replace(" ", "_").replace("/", "_")
        self.log_prompt_to_file(
            actual_prompt, 
            "error_fix_regeneration", 
            f"scenario_{scenario_index}_{scenario_name}"
        )
        
        # Generate code for this specific scenario with error fixes
        return chain.invoke(prompt_vars)

    def _extract_error_context_for_prompt(self, enhanced_scenario: Any) -> str:
        """Extract error context from enhanced scenario for the prompt template"""
        if not isinstance(enhanced_scenario, dict):
            return "No specific error context available"
        
        compilation_context = enhanced_scenario.get("compilation_context", {})
        if not compilation_context:
            return "No compilation errors detected"
        
        # Format error context for the prompt
        error_parts = []
        
        # Add error summary
        error_summary = compilation_context.get("error_summary", "")
        if error_summary:
            error_parts.append(f"ERROR SUMMARY:\n{error_summary}")
        
        # Add specific error messages
        raw_errors = compilation_context.get("scenario_specific_errors", [])
        if raw_errors:
            error_parts.append("COMPILATION ERRORS:")
            for i, error in enumerate(raw_errors, 1):
                error_parts.append(f"{i}. {error}")
        
        # Add fix instructions
        fix_instructions = compilation_context.get("fix_instructions", "")
        if fix_instructions:
            error_parts.append(f"FIX INSTRUCTIONS:\n{fix_instructions}")
        
        # Add specific code fixes
        specific_fixes = compilation_context.get("specific_code_fixes", "")
        if specific_fixes:
            error_parts.append(f"SPECIFIC CODE FIXES:\n{specific_fixes}")
        
        return "\n\n".join(error_parts) if error_parts else "No specific error context available"

    def _identify_files_with_compilation_errors(self, compilation_result: Dict[str, Any], 
                                              project_dir: str, language: str) -> List[Dict[str, Any]]:
        """Identify specific files that have compilation errors"""
        
        detailed_errors = compilation_result.get("error_analysis", {}).get("detailed_errors", [])
        files_with_errors = []
        
        # Parse compilation errors to identify problematic files
        for error in detailed_errors:
            error_info = self._parse_compilation_error_for_file(error, project_dir, language)
            if error_info:
                files_with_errors.append(error_info)
        
        # Group errors by file and deduplicate
        file_error_map = {}
        for error_info in files_with_errors:
            file_path = error_info["file_path"]
            if file_path not in file_error_map:
                file_error_map[file_path] = {
                    "file_path": file_path,
                    "scenario_name": error_info.get("scenario_name", ""),
                    "errors": [],
                    "error_categories": set()
                }
            
            file_error_map[file_path]["errors"].append(error_info["error"])
            file_error_map[file_path]["error_categories"].add(error_info.get("category", "unknown"))
        
        # Convert to list and add metadata
        result = []
        for file_path, info in file_error_map.items():
            info["error_categories"] = list(info["error_categories"])
            info["error_count"] = len(info["errors"])
            result.append(info)
        
        self.log(f"🔍 Identified {len(result)} files with compilation errors")
        return result
    
    def _parse_compilation_error_for_file(self, error: str, project_dir: str, language: str) -> Dict[str, Any]:
        """Parse a compilation error to extract file information"""
        
        # Language-specific error parsing
        if language.lower() == "c#":
            # C# error format: "path\file.cs(line,col): error CS0103: ..."
            import re
            match = re.search(r'([^:]+\.cs)\(\d+,\d+\):\s*error\s+(\w+):\s*(.+)', error)
            if match:
                file_path = match.group(1)
                error_code = match.group(2)
                error_message = match.group(3)
                
                # Extract scenario name from file path
                scenario_name = os.path.basename(file_path).replace(".cs", "").replace("Test", "")
                
                return {
                    "file_path": os.path.join(project_dir, file_path),
                    "scenario_name": scenario_name,
                    "error": error,
                    "error_code": error_code,
                    "error_message": error_message,
                    "category": self._categorize_error(error_message)
                }
        
        elif language.lower() == "python":
            # Python error format parsing
            import re
            match = re.search(r'File "([^"]+\.py)", line \d+', error)
            if match:
                file_path = match.group(1)
                scenario_name = os.path.basename(file_path).replace(".py", "").replace("_test", "")
                
                return {
                    "file_path": file_path,
                    "scenario_name": scenario_name,
                    "error": error,
                    "category": self._categorize_error(error)
                }
        
        # Add more language-specific parsing as needed
        return None
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message for better handling"""
        error_lower = error_message.lower()
        
        if "using directive" in error_lower or "namespace" in error_lower:
            return "missing_imports"
        elif "type" in error_lower and ("not found" in error_lower or "does not exist" in error_lower):
            return "type_errors"
        elif "does not contain a definition for" in error_lower:
            return "method_errors"
        elif "assembly reference" in error_lower:
            return "assembly_errors"
        elif "cannot convert" in error_lower or "cannot implicitly convert" in error_lower:
            return "type_conversion"
        else:
            return "other"
    
    def _fix_scenarios_with_compilation_errors(self, scenarios: List[Any], files_with_errors: List[Dict[str, Any]], 
                                             original_scenario_results: Dict[str, Any], language: str, 
                                             product_name: str, version: str, setup_info: dict, 
                                             project_dir: str, analysis_data: dict, 
                                             compilation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fix only the scenarios that have compilation errors"""
        
        updated_results = {
            "successful": [],
            "failed": [],
            "total_processed": 0,
            "generation_details": [],
            "selective_fixes": []
        }
        
        # Map scenario names to files with errors
        error_scenario_names = {info["scenario_name"] for info in files_with_errors}
        
        self.log(f"🔧 Fixing scenarios with errors: {', '.join(error_scenario_names)}")
        
        # Process only scenarios that had compilation errors
        for scenario in scenarios:
            scenario_name = self._extract_scenario_name(scenario)
            
            if scenario_name in error_scenario_names:
                self.log(f"🛠️ Regenerating scenario with compilation fixes: {scenario_name}")
                
                # Get specific errors for this scenario
                scenario_errors = [info for info in files_with_errors if info["scenario_name"] == scenario_name]
                
                # Enhance scenario with specific error context
                enhanced_scenario = self._enhance_single_scenario_with_errors(
                    scenario, scenario_errors, compilation_result, language
                )
                
                # Regenerate code for this scenario with error fixes
                try:
                    scenario_code = self._generate_single_scenario_code(
                        enhanced_scenario, language, product_name, version, 
                        setup_info, analysis_data, fix_mode=True
                    )
                    
                    if scenario_code:
                        updated_results["successful"].append({
                            "scenario": enhanced_scenario,
                            "code": scenario_code,
                            "status": "fixed",
                            "original_errors": scenario_errors
                        })
                        updated_results["selective_fixes"].append({
                            "scenario_name": scenario_name,
                            "errors_addressed": len(scenario_errors),
                            "fix_status": "success"
                        })
                        self.log(f"✅ Successfully fixed scenario: {scenario_name}")
                    else:
                        updated_results["failed"].append({
                            "scenario": enhanced_scenario,
                            "error": "Failed to generate fixed code",
                            "original_errors": scenario_errors
                        })
                        updated_results["selective_fixes"].append({
                            "scenario_name": scenario_name,
                            "errors_addressed": len(scenario_errors),
                            "fix_status": "failed"
                        })
                        self.log(f"❌ Failed to fix scenario: {scenario_name}")
                        
                except Exception as e:
                    self.log(f"❌ Error fixing scenario {scenario_name}: {str(e)}")
                    updated_results["failed"].append({
                        "scenario": scenario,
                        "error": str(e),
                        "original_errors": scenario_errors
                    })
                
                updated_results["total_processed"] += 1
        
        self.log(f"📊 Selective fix results: {len(updated_results['successful'])} fixed, {len(updated_results['failed'])} failed")
        return updated_results
    
    def _extract_scenario_name(self, scenario: Any) -> str:
        """Extract scenario name for mapping to files"""
        if isinstance(scenario, dict):
            return scenario.get("name", "Unknown")
        elif isinstance(scenario, str):
            return scenario[:50]  # First 50 chars as name
        else:
            return str(scenario)[:50]
    
    def _enhance_single_scenario_with_errors(self, scenario: Any, scenario_errors: List[Dict[str, Any]], 
                                           compilation_result: Dict[str, Any], language: str) -> Any:
        """Enhance a single scenario with specific error context for fixing"""
        
        if isinstance(scenario, dict):
            enhanced_scenario = scenario.copy()
        else:
            enhanced_scenario = {"original_content": scenario}
        
        # Add compilation error context
        enhanced_scenario["compilation_context"] = {
            "regenerate_mode": "fix_existing_code",
            "specific_errors": scenario_errors,
            "error_summary": f"Fix {len(scenario_errors)} compilation errors in this scenario",
            "fix_instructions": self._generate_specific_fix_instructions(scenario_errors, language),
            "error_categories": list(set(error["category"] for error in scenario_errors if "category" in error))
        }
        
        return enhanced_scenario
    
    def _generate_specific_fix_instructions(self, scenario_errors: List[Dict[str, Any]], language: str) -> List[str]:
        """Generate specific fix instructions based on error analysis"""
        
        instructions = []
        error_categories = {}
        
        # Group errors by category
        for error in scenario_errors:
            category = error.get("category", "other")
            if category not in error_categories:
                error_categories[category] = []
            error_categories[category].append(error)
        
        # Generate category-specific instructions
        if "missing_imports" in error_categories:
            if language.lower() == "c#":
                instructions.append("Add missing using directives: using Microsoft.Azure.Cosmos; using NUnit.Framework;")
            elif language.lower() == "python":
                instructions.append("Add missing import statements at the top of the file")
        
        if "type_errors" in error_categories:
            instructions.append("Verify all type names and ensure required packages are referenced")
        
        if "method_errors" in error_categories:
            instructions.append("Check method signatures and use correct SDK API calls")
        
        if "type_conversion" in error_categories:
            instructions.append("Fix type conversion issues and use proper casting")
        
        return instructions
    
    def _update_project_files_selectively(self, project_files: Dict[str, Any], 
                                         updated_scenario_results: Dict[str, Any], 
                                         files_with_errors: List[Dict[str, Any]], 
                                         language: str, project_dir: str) -> Dict[str, Any]:
        """Update only the specific files that were fixed"""
        
        self.log(f"📝 Updating {len(files_with_errors)} files selectively")
        
        # Update individual test files
        for success_info in updated_scenario_results["successful"]:
            scenario = success_info["scenario"]
            code = success_info["code"]
            scenario_name = self._extract_scenario_name(scenario)
            
            # Find the corresponding file and update it
            for file_info in files_with_errors:
                if file_info["scenario_name"] == scenario_name:
                    file_path = file_info["file_path"]
                    
                    try:
                        # Write the fixed code to the file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(code)
                        
                        self.log(f"✅ Updated file: {os.path.basename(file_path)}")
                        
                    except Exception as e:
                        self.log(f"❌ Failed to update file {file_path}: {str(e)}")
        
        # Recompile to get updated compilation results
        updated_compilation_result = self._compile_project(project_dir, language)
        project_files["compilation_result"] = updated_compilation_result
        
        return project_files
    
    def _apply_global_compilation_fixes(self, project_files: Dict[str, Any], 
                                      compilation_result: Dict[str, Any], 
                                      language: str, project_dir: str) -> Dict[str, Any]:
        """Apply global fixes when specific file errors can't be identified"""
        
        self.log("🔧 Applying global compilation fixes")
        
        error_analysis = compilation_result.get("error_analysis", {})
        detailed_errors = error_analysis.get("detailed_errors", [])
        
        # Apply common fixes based on error patterns
        global_fixes_applied = []
        
        if language.lower() == "c#":
            # Check for common C# issues
            missing_usings = []
            for error in detailed_errors:
                if "Microsoft" in error and "using directive" in error:
                    missing_usings.append("using Microsoft.Azure.Cosmos;")
                elif "NUnit" in error or "Assert" in error:
                    missing_usings.append("using NUnit.Framework;")
            
            if missing_usings:
                # Add missing using statements to all .cs files
                self._add_using_statements_to_cs_files(project_dir, missing_usings)
                global_fixes_applied.extend(missing_usings)
        
        # Recompile after global fixes
        if global_fixes_applied:
            self.log(f"✅ Applied {len(global_fixes_applied)} global fixes")
            updated_compilation_result = self._compile_project(project_dir, language)
            project_files["compilation_result"] = updated_compilation_result
        
        return project_files
    
    def _add_using_statements_to_cs_files(self, project_dir: str, using_statements: List[str]):
        """Add using statements to all C# files"""
        
        import glob
        cs_files = glob.glob(os.path.join(project_dir, "*.cs"))
        
        for cs_file in cs_files:
            try:
                with open(cs_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if using statements are already present
                new_usings = []
                for using_stmt in using_statements:
                    if using_stmt not in content:
                        new_usings.append(using_stmt)
                
                if new_usings:
                    # Add new using statements at the top
                    using_block = '\n'.join(new_usings) + '\n'
                    updated_content = using_block + content
                    
                    with open(cs_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    self.log(f"✅ Added using statements to {os.path.basename(cs_file)}")
                    
            except Exception as e:
                self.log(f"❌ Error updating {cs_file}: {str(e)}")
    
    def _compile_project(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Compile the project and return compilation results"""
        
        # Use the existing code compiler
        compiler = CodeCompiler()
        return compiler.compile_project(project_dir, language)
    
    def _generate_single_scenario_code(self, scenario: Any, language: str, product_name: str, 
                                     version: str, setup_info: dict, analysis_data: dict, 
                                     fix_mode: bool = False) -> str:
        """Generate code for a single scenario (used for fixing specific scenarios)"""
        
        try:
            # Get context for prompt generation
            detected_dependencies = PackageVersions.detect_dependencies_from_scenario(analysis_data)
            test_packages = PackageVersions.get_test_packages_with_cosmosdb(language, analysis_data)
            primary_test_framework = PackageVersions.get_primary_test_framework(language)
            
            context = {
                'dotnet_version': PackageVersions.get_language_version('dotnet'),
                'java_version': PackageVersions.get_language_version('java'),
                'node_version': PackageVersions.get_language_version('node'),
                'python_version': PackageVersions.get_language_version('python'),
                'go_version': PackageVersions.get_language_version('go'),
                'rust_version': PackageVersions.get_language_version('rust'),
                'test_packages': test_packages,
                'dependencies': detected_dependencies.get(language.lower(), {}),
                'primary_test_framework': primary_test_framework,
                'scenario_based_packages': True,
                'fix_mode': fix_mode
            }
            
            # Load scenario generation prompt from prompty file
            prompt_template = self.prompty_loader.create_prompt_template(
                "code_generator", "scenario_generation"
            )
            
            if not prompt_template:
                self.log(f"❌ No prompt template available for language: {language}")
                return None
            
            # Get LLM with prompty-specific settings for scenario generation
            llm_for_chain = self.prompty_loader.create_llm_with_prompty_settings(
                self.llm, "code_generator", "scenario_generation"
            )
            
            chain = prompt_template | llm_for_chain | StrOutputParser()

            # Format scenario for prompt
            formatted_scenario = self._format_single_scenario_for_prompt(scenario, 1)

            # Get language-specific testing framework and unified guidelines
            testing_framework = self._get_testing_framework(language)
            language_guidelines = self.language_best_practices_manager.get_language_guidelines(
                language=language,
                testing_framework=testing_framework
            )
            product_specific_guidance = self._get_product_specific_guidance(product_name, language, version)

            # Prepare prompt variables for logging
            prompt_vars = {
                "language": language,
                "product_name": product_name,
                "testing_framework": testing_framework,
                "language_guidelines": language_guidelines,
                "product_specific_guidance": product_specific_guidance,
                "version": version,
                "scenario": formatted_scenario,
                "setup_info": setup_info,
                "scenario_index": 1,
                "total_scenarios": 1
            }
            
            # Log the actual prompt that will be sent to LLM
            # Use Jinja2 rendering since prompt_template uses jinja2 format
            jinja_template = jinja2.Template(prompt_template.template)
            actual_prompt = jinja_template.render(**prompt_vars)
            scenario_name = self._get_scenario_name(scenario).replace(" ", "_").replace("/", "_")
            self.log_prompt_to_file(
                actual_prompt, 
                "test_generation", 
                f"test_{scenario_name}"
            )
            
            # Generate code
            generated = chain.invoke(prompt_vars)

            if generated and isinstance(generated, str) and generated.strip():
                # Extract code from result if needed
                extracted_code = self._extract_code_from_result(generated, language)
                return extracted_code if extracted_code else generated
            else:
                self.log(f"❌ Empty result from LLM for scenario")
                return None
                
        except Exception as e:
            self.log(f"❌ Error generating single scenario code: {str(e)}")
            return None
    
    def _extract_code_from_result(self, result: str, language: str) -> str:
        """Extract actual code from LLM result"""
        
        # Look for code blocks in the result
        import re
        
        # Language-specific code block patterns
        if language.lower() == "c#":
            # Look for C# code blocks
            patterns = [
                r'```c#\s*(.*?)\s*```',
                r'```csharp\s*(.*?)\s*```',
                r'```cs\s*(.*?)\s*```'
            ]
        elif language.lower() == "python":
            patterns = [r'```python\s*(.*?)\s*```', r'```py\s*(.*?)\s*```']
        elif language.lower() == "javascript":
            patterns = [r'```javascript\s*(.*?)\s*```', r'```js\s*(.*?)\s*```']
        elif language.lower() == "java":
            patterns = [r'```java\s*(.*?)\s*```']
        elif language.lower() == "go":
            patterns = [r'```go\s*(.*?)\s*```']
        elif language.lower() == "rust":
            patterns = [r'```rust\s*(.*?)\s*```', r'```rs\s*(.*?)\s*```']
        else:
            patterns = [r'```\w*\s*(.*?)\s*```']
        
        # Try each pattern
        for pattern in patterns:
            matches = re.findall(pattern, result, re.DOTALL | re.IGNORECASE)
            if matches:
                # Return the first (usually largest) code block
                return matches[0].strip()
        
        # If no code blocks found, return the original result
        return result.strip()
