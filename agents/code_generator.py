from typing import Dict, Any, List
import os
import json
import subprocess
import threading
import time
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent

# Import the new tools
from tools.code_generator import (
    FileCreator,
    ProjectStructureParser,
    CodeBlockExtractor,
    ScenarioCategorizer,
    CSharpProjectGenerator,
    PythonProjectGenerator,
    JavaScriptProjectGenerator,
    JavaProjectGenerator,
    GoProjectGenerator,
    RustProjectGenerator
)

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
    
    🔄 NEW GENERATION MODE: SCENARIO-BY-SCENARIO
    -------------------------------------------
    Instead of generating all code at once, this agent now:
    • Processes each scenario individually for better focus
    • Provides progress tracking and error isolation
    • Allows for individual scenario validation
    • Consolidates results into unified implementation
    • Generates detailed reports for each scenario
    
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
    
    ✨ SCENARIO-BY-SCENARIO BENEFITS:
    --------------------------------
    ✅ Better Focus         - Each scenario gets dedicated attention
    ✅ Error Isolation      - Failed scenarios don't affect successful ones
    ✅ Progress Tracking    - Real-time progress monitoring
    ✅ Quality Control      - Individual validation and testing
    ✅ Detailed Reporting   - Comprehensive status reports per scenario
    ✅ Traceability         - Clear mapping from requirements to code
    
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
    5. REPORT GENERATION:    Create comprehensive status reports
    
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
    • tests.[ext]                - Consolidated test suite
    • Project configuration files (language-specific)
    """
    
    def __init__(self, llm: Any):
        super().__init__("Code Generator", llm)
        
        # Initialize tools
        self.file_creator = FileCreator()
        self.structure_parser = ProjectStructureParser()
        self.code_extractor = CodeBlockExtractor()
        self.scenario_categorizer = ScenarioCategorizer()
        
        # Initialize language-specific generators
        self.generators = {
            'csharp': CSharpProjectGenerator(),
            'c#': CSharpProjectGenerator(),
            'python': PythonProjectGenerator(),
            'javascript': JavaScriptProjectGenerator(),
            'node.js': JavaScriptProjectGenerator(),
            'js': JavaScriptProjectGenerator(),
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
    
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """Generate code one scenario at a time for better control and progress tracking"""
        self.log(f"Starting scenario-by-scenario code generation")
        
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
                        "projectsetupInfo": {
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
            setup_info = analysis_data.get("projectsetupInfo", {})
            
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
            
            # Generate code for each scenario individually
            self.log(f"🚀 Starting scenario-by-scenario code generation for {len(scenarios)} scenarios")
            scenario_results = self._generate_scenarios_individually(
                scenarios, language, product_name, version, setup_info, project_dir, analysis_data
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
            
            output = {
                "agent": self.name,
                "input": input_data,
                "output": consolidated_content,
                "project_files": project_files,
                "scenario_results": scenario_results,
                "language": language,
                "product_name": product_name,
                "simple_report": project_files.get("simple_report"),
                "status": "success",
                "generation_mode": "scenario_by_scenario",
                "total_scenarios_processed": len(scenario_results["successful"]) + len(scenario_results["failed"])
            }
            
            self.log("Scenario-by-scenario code generation completed successfully")
            return output
            
        except Exception as e:
            self.log(f"Error during scenario-by-scenario code generation: {str(e)}")
            return {
                "agent": self.name,
                "input": input_data,
                "output": None,
                "status": "error",
                "error": str(e)
            }
    
    def _generate_scenarios_individually(self, scenarios: list, language: str, product_name: str, version: str, setup_info: dict, project_dir: str, analysis_data: dict) -> Dict[str, Any]:
        """Generate code for each scenario individually with progress tracking"""
        results = {
            "successful": [],
            "failed": [],
            "total_processed": 0,
            "generation_details": []
        }
        
        self.log(f"🔄 Processing {len(scenarios)} scenarios individually...")
        
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
        
        # Get single-scenario prompt template
        single_scenario_prompt = self._get_single_scenario_prompt(language, context)
        
        if not single_scenario_prompt:
            results["failed"].append({
                "error": f"No single scenario prompt template available for language: {language}",
                "scenario_index": "all"
            })
            return results
        
        # Create prompt template for single scenario generation
        prompt_template = PromptTemplate(
            input_variables=["language", "product_name", "version", "scenario", "setup_info", "scenario_index", "total_scenarios"],
            template=single_scenario_prompt,
            template_format="jinja2"
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        # Process each scenario individually
        for i, scenario in enumerate(scenarios, 1):
            try:
                self.log(f"📝 Processing scenario {i}/{len(scenarios)}: {self._get_scenario_name(scenario)}")
                
                # Format single scenario for prompt
                scenario_text = self._format_single_scenario_for_prompt(scenario, i)
                setup_info_text = json.dumps(setup_info, indent=2)
                
                # Prepare prompt variables for single scenario
                prompt_vars = {
                    "language": language.upper(),
                    "product_name": product_name,
                    "version": version,
                    "scenario": scenario_text,
                    "setup_info": setup_info_text,
                    "scenario_index": i,
                    "total_scenarios": len(scenarios)
                }
                
                # Generate code for this specific scenario
                scenario_result = chain.invoke(prompt_vars)
                generated_content = scenario_result["text"]
                
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
                self.log(f"✅ Scenario {i} completed successfully ({files_count} code files created)")
                
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
                
                self.log(f"❌ Scenario {i} failed: {str(e)}")
            
            results["total_processed"] += 1
        
        # Log summary
        success_count = len(results["successful"])
        failure_count = len(results["failed"])
        
        self.log(f"🎯 Scenario Generation Summary:")
        self.log(f"  ✅ Successful: {success_count}/{len(scenarios)}")
        self.log(f"  ❌ Failed: {failure_count}/{len(scenarios)}")
        self.log(f"  📊 Success Rate: {(success_count/len(scenarios)*100):.1f}%")
        
        return results
    
    def _get_single_scenario_prompt(self, language: str, context: Dict[str, Any] = None) -> str:
        """Get a prompt template specifically designed for single scenario test code generation"""
        # This is a test-focused prompt template for single scenario
        base_prompt = """
You are an expert {{language}} test developer. Generate comprehensive TEST CODE ONLY for a SINGLE specific scenario.

**Project Information:**
- Product Name: {{product_name}}
- Language: {{language}}
- Version: {{version}}
- Current Scenario: {{scenario_index}}/{{total_scenarios}}

**Single Scenario to Test:**
{{scenario}}

**Project Setup Information:**
{{setup_info}}

**Requirements for this specific scenario:**
1. Create ONLY TEST CODE for this specific scenario - NO main implementation classes
2. Focus on comprehensive test coverage for the scenario
3. Include test setup, execution, and verification
4. Create multiple test cases (positive, negative, edge cases)
5. Follow {{language}} testing best practices and conventions
6. Include clear test descriptions and comments
7. Use the correct test framework for {{language}}: 
   - C#: NUnit (using [Test], [TestFixture], Assert.That)
   - Python: pytest or unittest 
   - JavaScript: Jest
   - Java: JUnit 5
   - Go: built-in testing package
   - Rust: built-in test framework

**Output Format:**
Generate the test code in the following format:

### Test Implementation  
```{{language.lower()}}
// Comprehensive test code for the scenario
// Include multiple test methods covering different aspects
// Focus on behavior verification, not implementation details
```

**Important:** 
- Generate ONLY test code - no main implementation classes
- Focus on testing the scenario requirements and expected outcomes
- Include proper test setup, execution, and assertion phases
- Test both successful cases and error conditions
- Use descriptive test method names that explain what is being tested
- Include TODO comments for any additional test cases that might be needed
"""
        
        return base_prompt
    
    def _format_single_scenario_for_prompt(self, scenario: Any, index: int) -> str:
        """Format a single scenario for the LLM prompt"""
        if isinstance(scenario, str):
            return f"**Scenario {index}:** {scenario}"
        elif isinstance(scenario, dict):
            name = scenario.get("name", f"Scenario {index}")
            description = scenario.get("description", "No description provided")
            purpose = scenario.get("purpose", "No purpose specified")
            category = scenario.get("category", "unknown")
            priority = scenario.get("priority", "medium")
            expected_outcome = scenario.get("expectedOutcome", "No expected outcome specified")
            
            return f"""**Scenario {index}: {name}** [{category.upper()}/{priority.upper()}]

**Description:** {description}

**Purpose:** {purpose}

**Expected Outcome:** {expected_outcome}

**Implementation Focus:** Create code that specifically addresses this scenario's requirements and validates the expected outcome."""
        else:
            return f"**Scenario {index}:** {str(scenario)}"
    
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
        consolidated_parts.append("3. Integrate the test cases into a comprehensive test suite")
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
            all_test_code = []
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
                
                # Extract test code
                test_code_pattern = r'### Test Implementation.*?```[a-zA-Z]*\n(.*?)```'
                test_matches = re.findall(test_code_pattern, content, re.DOTALL | re.IGNORECASE)
                for match in test_matches:
                    if match.strip():
                        all_test_code.append(f"// Test for scenario: {scenario_name}\n{match.strip()}\n")
                
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
            
            # Create consolidated test file
            if all_test_code:
                test_file_path = os.path.join(project_dir, f"tests{default_extension}")
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"// Consolidated Tests for {language.upper()}\n")
                    f.write(f"// Generated from {len(scenario_results['successful'])} scenarios\n")
                    f.write(f"// Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("\n\n".join(all_test_code))
                
                self.log(f"✅ Created consolidated test file: tests{default_extension}")
            
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
                    file_path = scenario.get("file_path", "Unknown")
                    generation_time = scenario.get("generation_time", "Unknown")
                    
                    report_parts.append(f"### {scenario.get('scenario_index', '?')}. {name}")
                    report_parts.append(f"- **Content Length:** {content_length} characters")
                    report_parts.append(f"- **Generated At:** {generation_time}")
                    report_parts.append(f"- **File:** {os.path.basename(file_path)}")
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
