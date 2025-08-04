from typing import Dict, Any, List
import os
import json
import re
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent

# Import the new tools
from tools.code_generator import (
    FileCreator,
    ProjectStructureParser,
    CodeBlockExtractor,
    ProjectBuilder,
    ScenarioCategorizer,
    CSharpProjectGenerator,
    PythonProjectGenerator,
    JavaScriptProjectGenerator,
    JavaProjectGenerator,
    GoProjectGenerator,
    RustProjectGenerator,
    GenericProjectGenerator
)


class CodeGenerator(BaseAgent):
    """Agent responsible for generating code based on analyzed requirements"""
    
    def __init__(self, llm: Any):
        super().__init__("Code Generator", llm)
        
        # Initialize tools
        self.file_creator = FileCreator()
        self.structure_parser = ProjectStructureParser()
        self.code_extractor = CodeBlockExtractor()
        self.project_builder = ProjectBuilder()
        self.scenario_categorizer = ScenarioCategorizer()
        
        # Initialize language-specific generators - supporting only C#, Java, Python, JavaScript, Go, and Rust
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
        
        # Supported languages list
        self.supported_languages = ['csharp', 'c#', 'python', 'javascript', 'node.js', 'js', 'java', 'go', 'rust']
        
        self.prompt_template = PromptTemplate(
            input_variables=["language", "product_name", "version", "scenarios", "setup_info"],
            template="""
            You are a test project generation agent. Your task is to generate a COMPLETE, buildable test project.

            SUPPORTED LANGUAGES: C#, Java, Python, JavaScript/Node.js, Go, Rust

            Language: {language}
            Product Name: {product_name}
            Version: {version}
            
            Test Scenarios to implement:
            {scenarios}
            
            Project Setup Information:
            {setup_info}

            Your task is to generate a complete, working project with:
                - Functional Test code implementation only based on the given scenarios
                - Appropriate project structure and naming conventions for the selected programming language

            CRITICAL IMPLEMENTATION RULES:

            1. **Complete Project Structure**: Generate the full project with all necessary files
            2. **Test Classes**: Create separate test classes for different scenario categories
            3. **Test Methods**: Each scenario gets a complete, implementable test method
            4. **Meaningful Names**: Use descriptive class names and test method names
            5. **Single Test Framework**: Use only one specific framework per language:
               - C#: NUnit framework only
               - Java: JUnit 5 only  
               - Python: pytest only
               - JavaScript: Jest only
               - Go: Built-in testing only
               - Rust: Built-in testing only

            LANGUAGE-SPECIFIC COMPLETE IMPLEMENTATION:

            If language is C#:
            - Create complete .csproj file with NUnit dependency
            - Create test classes with proper namespace and class names
            - Use descriptive class names like: {product_name}BasicTests, {product_name}PerformanceTests, etc.
            - Each test method should follow pattern: Test_[ScenarioDescription]
            - Include complete using statements and proper NUnit attributes

            If language is Java:
            - Create complete pom.xml with JUnit 5 dependency
            - Create test classes in src/test/java directory
            - Use descriptive class names following Java conventions
            - Each test method should follow pattern: test[ScenarioDescription]
            - Include complete imports and proper JUnit annotations

            If language is Python:
            - Create complete requirements.txt with pytest
            - Create test files in tests/ directory
            - Use descriptive file names like: test_[category]_[product_name].py
            - Each test function should follow pattern: test_[scenario_description]
            - Include proper imports and pytest conventions

            COMPLETE SCENARIO IMPLEMENTATION EXAMPLE:

            For each scenario, create a COMPLETE test method like this:

            C# Example:
            ```csharp
            [Test]
            public void Test_UserLoginWithValidCredentials()
            {{
                // Arrange
                string username = "testuser";
                string password = "validpassword";
                bool expectedResult = true;
                
                // Act
                // In a real implementation, this would call the actual login method
                // For now, we simulate the expected behavior
                bool actualResult = SimulateLogin(username, password);
                
                // Assert
                Assert.That(actualResult, Is.EqualTo(expectedResult), 
                    "Login should succeed with valid credentials");
            }}
            
            private bool SimulateLogin(string username, string password)
            {{
                // Simulation logic for testing purposes
                return !string.IsNullOrEmpty(username) && !string.IsNullOrEmpty(password);
            }}
            ```

            RESPONSE FORMAT:

            Your response must include the COMPLETE project structure:

            ## Test Project Structure
            [List ALL files and directories needed]

            ## Complete Test File Contents

            ### [ConfigFileName] (e.g., ProductName.csproj, pom.xml, requirements.txt)
            ```[language-config]
            [Complete configuration file content]
            ```

            ### [TestClassName1].cs/.java/.py/.js/.go/.rs
            ```[language]
            [Complete test class with ALL imports, class declaration, and ALL test methods for related scenarios]
            ```

            ### [TestClassName2].cs/.java/.py/.js/.go/.rs
            ```[language]
            [Complete additional test class if scenarios require categorization]
            ```

            ## Build Instructions
            [Complete step-by-step build commands]

            ## Test Execution
            [Complete commands to run all tests]

            SCENARIO IMPLEMENTATION REQUIREMENTS:

            1. **Group Related Scenarios**: Create logical test classes (Basic, Performance, Security, Integration, etc.)
            2. **Complete Test Methods**: Each scenario gets a full test method with Arrange-Act-Assert pattern
            3. **Meaningful Assertions**: Include specific assertions that would validate the scenario
            4. **Helper Methods**: Add simulation/helper methods as needed for test completeness
            5. **Descriptive Names**: Use clear, descriptive names for classes and methods
            6. **Framework Compliance**: Follow the specific test framework conventions exactly

            Generate a COMPLETE, compilation-ready test project that covers ALL scenarios with proper structure and naming.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """Generate code based on the analysis report from DocumentAnalyzer"""
        self.log(f"Starting code generation based on analysis")
        
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
                    "error": f"Unsupported language: {language}. Supported languages: C#, Java, Python, JavaScript, Go, Rust"
                }
            
            # Format scenarios for the prompt
            scenarios_text = "\n".join([f"- {scenario}" for scenario in scenarios])
            setup_info_text = json.dumps(setup_info, indent=2)
            
            self.log(f"Generating {language} code for {product_name}")
            
            # Generate code using the LLM
            code_result = self.chain.invoke({
                "language": language,
                "product_name": product_name,
                "version": version,
                "scenarios": scenarios_text,
                "setup_info": setup_info_text
            })
            
            generated_content = code_result["text"]
            
            # Create project using appropriate generator with retry logic for compilation errors
            project_files = self._create_project_with_retry(
                generated_content, 
                language, 
                product_name, 
                scenarios,
                max_retries=5
            )
            
            # Parse and create additional files from LLM output using tools
            parsed_files = self._parse_and_create_files_with_tools(
                project_files.get("final_generated_content", generated_content),
                project_files.get("project_dir", os.path.join("workflow_outputs", f"{product_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"))
            )
            
            # Merge parsed files with project files
            project_files.update(parsed_files)
            
            output = {
                "agent": self.name,
                "input": input_data,
                "output": generated_content,
                "project_files": project_files,
                "language": language,
                "product_name": product_name,
                "status": "success"
            }
            
            self.log("Code generation completed successfully")
            return output
            
        except Exception as e:
            self.log(f"Error during code generation: {str(e)}")
            return {
                "agent": self.name,
                "input": input_data,
                "output": None,
                "status": "error",
                "error": str(e)
            }
    
    def _create_project_with_tools(self, generated_content: str, language: str, product_name: str, scenarios: list) -> Dict[str, str]:
        """Create project using the new tools"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = product_name.replace(" ", "_").lower()
        
        # Create project directory
        project_dir = os.path.join("workflow_outputs", f"{project_name}_{timestamp}")
        os.makedirs(project_dir, exist_ok=True)
        
        created_files = {"project_dir": project_dir}
        
        try:
            # Get the appropriate generator
            generator = self.generators.get(language.lower())
            
            if not generator:
                self.log(f"No generator found for language: {language}")
                return created_files
            
            # All supported languages now have dedicated generators
            project_files = generator.generate_project(project_dir, product_name, scenarios, generated_content)
            
            created_files.update(project_files)
            
            # Create categorized scenario test files
            categorized_files = self.scenario_categorizer.create_categorized_test_files(
                project_dir, scenarios, language, product_name
            )
            
            created_files.update(categorized_files)
            
            # Get categorization summary
            categorization_summary = self.scenario_categorizer.get_categorization_summary(scenarios)
            self.log(f"Scenario categorization: {categorization_summary['distribution']}")
            
            # Check tool availability for building
            tool_availability = self.project_builder.check_tool_availability(language)
            self.log(f"Build tool availability for {language}: {tool_availability}")
            
            # Get build info
            build_info = self.project_builder.get_build_info(project_dir, language)
            self.log(f"Project build info: {build_info}")
            
            # Attempt to restore dependencies and build project
            if any(tool_availability.values()):
                self.log(f"🔧 Starting build cycle for {language} project...")
                build_result = self.project_builder.full_build_cycle(project_dir, language)
                
                created_files["build_result"] = build_result
                
                if build_result['success']:
                    self.log(f"✅ Project built successfully and is compilation-free!")
                    created_files["build_status"] = "success"
                else:
                    self.log(f"⚠️ Build had issues, but project files were created. Check build_result for details.")
                    created_files["build_status"] = "partial"
            else:
                self.log(f"⚠️ Build tools not available for {language}. Project created but not built.")
                created_files["build_status"] = "tools_unavailable"
            
            self.log(f"Project files created using {generator.__class__.__name__} for {language} in: {project_dir}")
            
        except Exception as e:
            self.log(f"Error creating project files: {str(e)}")
        
        return created_files
    
    def _create_project_with_retry(self, generated_content: str, language: str, product_name: str, scenarios: list, max_retries: int = 5) -> Dict[str, str]:
        """Create project with step-by-step approach and retry logic for compilation errors"""
        self.log(f"🔄 Starting step-by-step project creation (max {max_retries} attempts per step)")
        
        project_dir = None
        final_project_files = {}
        
        try:
            # Step 1: Create a basic "Hello World" project
            self.log("📝 Step 1: Creating basic 'Hello World' project...")
            step1_result = self._create_hello_world_project(language, product_name)
            
            if not step1_result.get('success', False):
                self.log("❌ Step 1 failed: Could not create basic Hello World project")
                return {"error": "Failed to create basic project", "retry_attempts": 0}
            
            project_dir = step1_result['project_dir']
            self.log(f"✅ Step 1 completed: Basic project created in {project_dir}")
            final_project_files.update(step1_result)
            
            # Step 2: Add test framework and create minimal test
            self.log("📝 Step 2: Adding test framework and creating minimal test...")
            step2_result = self._add_test_framework(project_dir, language, product_name)
            
            if not step2_result.get('success', False):
                self.log("❌ Step 2 failed: Could not add test framework")
                return {"error": "Failed to add test framework", "retry_attempts": 0, "project_dir": project_dir}
            
            self.log("✅ Step 2 completed: Test framework added and minimal test created")
            final_project_files.update(step2_result)
            
            # Step 3: Add scenario-based tests with retry logic
            self.log("📝 Step 3: Adding scenario-based tests...")
            step3_result = self._add_scenario_tests_with_retry(project_dir, language, product_name, scenarios, max_retries)
            
            if not step3_result.get('success', False):
                self.log("⚠️ Step 3 had issues but basic test project is functional")
            else:
                self.log("✅ Step 3 completed: All scenario tests added successfully")
            
            final_project_files.update(step3_result)
            final_project_files['project_dir'] = project_dir
            final_project_files['final_generated_content'] = generated_content
            final_project_files['step_by_step_success'] = True
            
            return final_project_files
            
        except Exception as e:
            self.log(f"❌ Error in step-by-step project creation: {str(e)}")
            return {
                "error": str(e), 
                "retry_attempts": 0, 
                "project_dir": project_dir,
                "step_by_step_success": False
            }
    
    def _create_hello_world_project(self, language: str, product_name: str) -> Dict[str, Any]:
        """Step 1: Create a basic Hello World project that compiles and runs"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = product_name.replace(" ", "_").lower()
        project_dir = os.path.join("workflow_outputs", f"{project_name}_{timestamp}")
        os.makedirs(project_dir, exist_ok=True)
        
        self.log(f"🏗️ Creating Hello World project for {language} in {project_dir}")
        
        try:
            # Get the appropriate generator
            generator = self.generators.get(language.lower())
            if not generator:
                return {"success": False, "error": f"No generator for {language}"}
            
            # Create minimal Hello World project
            hello_world_content = self._generate_hello_world_content(language, product_name)
            project_files = generator.generate_project(project_dir, product_name, ["Hello World test"], hello_world_content)
            
            # Build and test the Hello World project
            build_result = self._build_and_validate_project(project_dir, language, "Hello World")
            
            result = {
                "success": build_result.get('success', False),
                "project_dir": project_dir,
                "build_result": build_result,
                "step": "hello_world",
                **project_files
            }
            
            if result['success']:
                self.log("✅ Hello World project builds and runs successfully")
            else:
                self.log("❌ Hello World project failed to build")
            
            return result
            
        except Exception as e:
            self.log(f"❌ Error creating Hello World project: {str(e)}")
            return {"success": False, "error": str(e), "project_dir": project_dir}
    
    def _add_test_framework(self, project_dir: str, language: str, product_name: str) -> Dict[str, Any]:
        """Step 2: Add test framework and create a simple passing test"""
        self.log(f"🧪 Adding test framework for {language}")
        
        try:
            # Create test framework configuration
            test_config = self._create_test_framework_config(project_dir, language, product_name)
            
            # Create a simple passing test
            simple_test = self._create_simple_test(project_dir, language, product_name)
            
            # Build and validate with test framework
            build_result = self._build_and_validate_project(project_dir, language, "Test Framework")
            
            result = {
                "success": build_result.get('success', False),
                "build_result": build_result,
                "step": "test_framework",
                "test_config": test_config,
                "simple_test": simple_test
            }
            
            if result['success']:
                self.log("✅ Test framework added and simple test passes")
            else:
                self.log("❌ Test framework setup failed")
            
            return result
            
        except Exception as e:
            self.log(f"❌ Error adding test framework: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _add_scenario_tests_with_retry(self, project_dir: str, language: str, product_name: str, scenarios: list, max_retries: int) -> Dict[str, Any]:
        """Step 3: Add scenario-based tests with enhanced self-healing retry logic"""
        self.log(f"📋 Adding {len(scenarios)} scenario tests with self-healing capabilities")
        
        retry_count = 0
        last_error = None
        all_errors = []
        applied_fixes = []
        
        while retry_count <= max_retries:
            attempt_num = retry_count + 1
            self.log(f"🔄 Self-healing attempt {attempt_num}/{max_retries + 1}")
            
            try:
                # Create categorized scenario test files
                categorized_files = self.scenario_categorizer.create_categorized_test_files(
                    project_dir, scenarios, language, product_name
                )
                
                # Build and validate with scenario tests
                build_result = self._build_and_validate_project(project_dir, language, f"Scenario Tests (Attempt {attempt_num})")
                
                if build_result.get('success', False):
                    self.log(f"✅ All scenario tests added successfully on attempt {attempt_num}")
                    
                    # Create success report
                    if applied_fixes:
                        self._create_error_fix_report(project_dir, all_errors, applied_fixes, language)
                    
                    return {
                        "success": True,
                        "build_result": build_result,
                        "step": "scenario_tests",
                        "retry_attempts": retry_count,
                        "categorized_files": categorized_files,
                        "self_healing_applied": len(applied_fixes) > 0,
                        "total_fixes": len(applied_fixes)
                    }
                
                # If build failed, analyze errors and apply intelligent fixes
                compilation_errors = self._extract_compilation_errors(build_result)
                all_errors.extend(compilation_errors)
                
                if compilation_errors and retry_count < max_retries:
                    self.log(f"🔍 Analyzing {len(compilation_errors)} compilation errors for self-healing...")
                    
                    # Perform intelligent error analysis
                    error_analysis = self._intelligent_error_analysis(compilation_errors, language)
                    self.log(f"📊 Error analysis: {error_analysis['confidence_level']} confidence, categories: {', '.join(set(error_analysis['error_categories']))}")
                    
                    # Apply fixes based on analysis
                    fixes_this_round = self._apply_comprehensive_fixes(project_dir, language, product_name, compilation_errors, error_analysis)
                    applied_fixes.extend(fixes_this_round)
                    
                    if fixes_this_round:
                        self.log(f"🔧 Applied {len(fixes_this_round)} self-healing fixes in attempt {attempt_num}")
                    else:
                        self.log(f"⚠️ No automatic fixes could be applied for current errors")
                
                last_error = build_result.get('error', 'Build failed')
                retry_count += 1
                
            except Exception as e:
                self.log(f"❌ Error in self-healing attempt {attempt_num}: {str(e)}")
                last_error = str(e)
                retry_count += 1
        
        self.log(f"⚠️ Self-healing completed after {max_retries + 1} attempts. Some issues may remain.")
        
        # Create comprehensive error report
        if all_errors or applied_fixes:
            self._create_error_fix_report(project_dir, all_errors, applied_fixes, language)
        
        return {
            "success": False,
            "error": last_error,
            "step": "scenario_tests",
            "retry_attempts": retry_count,
            "self_healing_applied": len(applied_fixes) > 0,
            "total_fixes": len(applied_fixes),
            "remaining_errors": len(all_errors) - len(applied_fixes)
        }
    
    def _apply_comprehensive_fixes(self, project_dir: str, language: str, product_name: str, 
                                  errors: List[str], analysis: Dict[str, Any]) -> List[str]:
        """Apply comprehensive fixes based on error analysis"""
        fixes_applied = []
        
        try:
            # Apply file-level fixes
            file_fixes = self._fix_scenario_test_errors(project_dir, language, product_name, errors)
            if file_fixes:
                fixes_applied.extend(file_fixes)
            
            # Apply syntax-specific fixes
            if 'syntax' in analysis['error_categories']:
                syntax_fixes = self._apply_syntax_fixes(project_dir, language, errors)
                fixes_applied.extend(syntax_fixes)
            
            # Apply import/using statement fixes
            if 'imports' in analysis['error_categories']:
                import_fixes = self._apply_import_fixes(project_dir, language, errors)
                fixes_applied.extend(import_fixes)
            
            # Apply naming fixes
            if 'naming' in analysis['error_categories']:
                naming_fixes = self._apply_naming_fixes(project_dir, language, product_name, errors)
                fixes_applied.extend(naming_fixes)
            
            # Apply language-specific fixes
            lang_fixes = self._apply_language_specific_fixes(project_dir, language, errors)
            fixes_applied.extend(lang_fixes)
            
        except Exception as e:
            self.log(f"❌ Error applying comprehensive fixes: {str(e)}")
        
        return fixes_applied
    
    def _apply_syntax_fixes(self, project_dir: str, language: str, errors: List[str]) -> List[str]:
        """Apply syntax-specific fixes"""
        fixes = []
        
        # Find all relevant files
        file_extensions = {
            'csharp': '.cs',
            'c#': '.cs',
            'java': '.java',
            'python': '.py',
            'javascript': '.js',
            'js': '.js',
            'node.js': '.js'
        }
        
        ext = file_extensions.get(language.lower(), '.txt')
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith(ext):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Apply syntax fixes based on language
                        if language.lower() in ['csharp', 'c#', 'java']:
                            # Fix missing semicolons
                            content = re.sub(r'(\w+\s*=\s*[^;]+)(\s*\n)', r'\1;\2', content)
                            content = re.sub(r'(Assert\.[^;]+)(\s*\n)', r'\1;\2', content)
                            content = re.sub(r'(return\s+[^;]+)(\s*\n)', r'\1;\2', content)
                            
                            # Fix missing brackets
                            content = re.sub(r'(\bif\s*\([^)]+\)\s*)(\w)', r'\1{\n    \2', content)
                        
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            fixes.append(f"Fixed syntax in {file}")
                    
                    except Exception as e:
                        self.log(f"Error fixing syntax in {file}: {str(e)}")
        
        return fixes
    
    def _apply_import_fixes(self, project_dir: str, language: str, errors: List[str]) -> List[str]:
        """Apply import/using statement fixes"""
        fixes = []
        
        # Define required imports per language
        required_imports = {
            'csharp': ['using System;', 'using NUnit.Framework;'],
            'c#': ['using System;', 'using NUnit.Framework;'],
            'java': ['import org.junit.jupiter.api.*;', 'import static org.junit.jupiter.api.Assertions.*;'],
            'python': ['import pytest', 'import time'],
            'javascript': ['// Jest is configured in package.json'],
            'js': ['// Jest is configured in package.json'],
            'node.js': ['// Jest is configured in package.json']
        }
        
        imports = required_imports.get(language.lower(), [])
        
        # Find all relevant files and add missing imports
        file_extensions = {
            'csharp': '.cs',
            'c#': '.cs', 
            'java': '.java',
            'python': '.py',
            'javascript': '.js',
            'js': '.js',
            'node.js': '.js'
        }
        
        ext = file_extensions.get(language.lower(), '.txt')
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith(ext):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Add missing imports
                        for import_stmt in imports:
                            if import_stmt not in content and not import_stmt.startswith('//'):
                                content = import_stmt + '\n' + content
                        
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            fixes.append(f"Added imports to {file}")
                    
                    except Exception as e:
                        self.log(f"Error adding imports to {file}: {str(e)}")
        
        return fixes
    
    def _apply_naming_fixes(self, project_dir: str, language: str, product_name: str, errors: List[str]) -> List[str]:
        """Apply naming consistency fixes"""
        fixes = []
        
        # Apply class naming fixes
        if language.lower() in ['csharp', 'c#']:
            test_dir = os.path.join(project_dir, "Tests")
            if os.path.exists(test_dir):
                for filename in os.listdir(test_dir):
                    if filename.endswith('.cs'):
                        file_path = os.path.join(test_dir, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            original_content = content
                            content = self._fix_csharp_class_naming(content, product_name)
                            
                            if content != original_content:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                fixes.append(f"Fixed class naming in {filename}")
                        
                        except Exception as e:
                            self.log(f"Error fixing naming in {filename}: {str(e)}")
        
        elif language.lower() == 'java':
            test_dir = os.path.join(project_dir, "src", "test", "java")
            if os.path.exists(test_dir):
                for filename in os.listdir(test_dir):
                    if filename.endswith('.java'):
                        file_path = os.path.join(test_dir, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            original_content = content
                            content = self._fix_java_class_naming(content, product_name)
                            
                            if content != original_content:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                fixes.append(f"Fixed class naming in {filename}")
                        
                        except Exception as e:
                            self.log(f"Error fixing naming in {filename}: {str(e)}")
        
        return fixes
    
    def _apply_language_specific_fixes(self, project_dir: str, language: str, errors: List[str]) -> List[str]:
        """Apply language-specific fixes"""
        fixes = []
        
        try:
            if language.lower() in ['csharp', 'c#']:
                # Fix C# specific issues
                fixes.extend(self._apply_csharp_specific_fixes(project_dir, errors))
            elif language.lower() == 'java':
                # Fix Java specific issues  
                fixes.extend(self._apply_java_specific_fixes(project_dir, errors))
            elif language.lower() == 'python':
                # Fix Python specific issues
                fixes.extend(self._apply_python_specific_fixes(project_dir, errors))
            
        except Exception as e:
            self.log(f"Error applying language-specific fixes: {str(e)}")
        
        return fixes
    
    def _apply_csharp_specific_fixes(self, project_dir: str, errors: List[str]) -> List[str]:
        """Apply C# specific fixes"""
        fixes = []
        
        # Check if namespace issues exist
        for error in errors:
            if 'namespace' in error.lower():
                # Find .cs files and add namespace if missing
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        if file.endswith('.cs'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                if 'namespace' not in content:
                                    lines = content.split('\n')
                                    # Find first class declaration
                                    for i, line in enumerate(lines):
                                        if 'public class' in line:
                                            lines.insert(i, 'namespace TestProject {')
                                            break
                                    lines.append('}')
                                    
                                    with open(file_path, 'w', encoding='utf-8') as f:
                                        f.write('\n'.join(lines))
                                    fixes.append(f"Added namespace to {file}")
                            
                            except Exception as e:
                                self.log(f"Error adding namespace to {file}: {str(e)}")
        
        return fixes
    
    def _apply_java_specific_fixes(self, project_dir: str, errors: List[str]) -> List[str]:
        """Apply Java specific fixes"""
        fixes = []
        
        # Check if package declaration issues exist
        for error in errors:
            if 'package' in error.lower():
                # Find .java files and add package if missing
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        if file.endswith('.java'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                if not content.strip().startswith('package'):
                                    content = 'package com.test;\n\n' + content
                                    
                                    with open(file_path, 'w', encoding='utf-8') as f:
                                        f.write(content)
                                    fixes.append(f"Added package declaration to {file}")
                            
                            except Exception as e:
                                self.log(f"Error adding package to {file}: {str(e)}")
        
        return fixes
    
    def _apply_python_specific_fixes(self, project_dir: str, errors: List[str]) -> List[str]:
        """Apply Python specific fixes"""
        fixes = []
        
        # Fix common Python issues like indentation
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Fix common indentation issues
                        lines = content.split('\n')
                        fixed_lines = []
                        
                        for line in lines:
                            # Fix mixed tabs and spaces
                            if '\t' in line:
                                line = line.replace('\t', '    ')
                            fixed_lines.append(line)
                        
                        content = '\n'.join(fixed_lines)
                        
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            fixes.append(f"Fixed indentation in {file}")
                    
                    except Exception as e:
                        self.log(f"Error fixing Python file {file}: {str(e)}")
        
        return fixes
    
    def _generate_hello_world_content(self, language: str, product_name: str) -> str:
        """Generate comprehensive Hello World content for the specified language with complete project structure"""
        safe_name = product_name.replace(' ', '').replace('-', '')
        
        if language.lower() in ['csharp', 'c#']:
            return f'''## Test Project Structure
- Tests/
  - {safe_name}BasicTests.cs
  - {safe_name}PerformanceTests.cs
- {safe_name}.csproj

## Complete Test File Contents

### {safe_name}.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="NUnit" Version="3.13.3" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.2.1" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.3.2" />
  </ItemGroup>
</Project>
```

### {safe_name}BasicTests.cs
```csharp
using NUnit.Framework;
using System;

namespace {safe_name}.Tests
{{
    [TestFixture]
    public class {safe_name}BasicTests
    {{
        [Test]
        public void Test_HelloWorld()
        {{
            // Arrange
            string expectedMessage = "Hello World";
            
            // Act
            string actualMessage = GetHelloWorldMessage();
            
            // Assert
            Assert.That(actualMessage, Is.EqualTo(expectedMessage), 
                "Hello World message should match expected value");
            Console.WriteLine($"Test passed: {{actualMessage}}");
        }}
        
        [Test]
        public void Test_BasicMathOperations()
        {{
            // Arrange
            int a = 2;
            int b = 2;
            int expected = 4;
            
            // Act
            int result = PerformAddition(a, b);
            
            // Assert
            Assert.That(result, Is.EqualTo(expected), 
                "Basic addition should work correctly");
        }}
        
        private string GetHelloWorldMessage()
        {{
            return "Hello World";
        }}
        
        private int PerformAddition(int x, int y)
        {{
            return x + y;
        }}
    }}
}}
```

### {safe_name}PerformanceTests.cs
```csharp
using NUnit.Framework;
using System;
using System.Diagnostics;

namespace {safe_name}.Tests
{{
    [TestFixture]
    public class {safe_name}PerformanceTests
    {{
        [Test]
        public void Test_SimplePerformanceCheck()
        {{
            // Arrange
            var stopwatch = new Stopwatch();
            int maxExecutionTimeMs = 1000; // 1 second
            
            // Act
            stopwatch.Start();
            PerformSimpleOperation();
            stopwatch.Stop();
            
            // Assert
            Assert.That(stopwatch.ElapsedMilliseconds, Is.LessThan(maxExecutionTimeMs),
                $"Operation should complete in less than {{maxExecutionTimeMs}}ms");
        }}
        
        private void PerformSimpleOperation()
        {{
            // Simulate some work
            System.Threading.Thread.Sleep(100);
        }}
    }}
}}
```

## Build Instructions
dotnet restore && dotnet build

## Test Execution
dotnet test'''
        
        elif language.lower() == 'java':
            return f'''## Test Project Structure
- src/test/java/
  - {safe_name}BasicTests.java
  - {safe_name}PerformanceTests.java
- pom.xml

## Complete Test File Contents

### pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.{safe_name.lower()}</groupId>
    <artifactId>{safe_name.lower()}-tests</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <junit.version>5.9.2</junit.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${{junit.version}}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0-M9</version>
            </plugin>
        </plugins>
    </build>
</project>
```

### {safe_name}BasicTests.java
```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

public class {safe_name}BasicTests {{
    
    @Test
    @DisplayName("Hello World Test")
    void testHelloWorld() {{
        // Arrange
        String expectedMessage = "Hello World";
        
        // Act
        String actualMessage = getHelloWorldMessage();
        
        // Assert
        assertEquals(expectedMessage, actualMessage, 
            "Hello World message should match expected value");
        System.out.println("Test passed: " + actualMessage);
    }}
    
    @Test
    @DisplayName("Basic Math Operations Test")
    void testBasicMathOperations() {{
        // Arrange
        int a = 2;
        int b = 2;
        int expected = 4;
        
        // Act
        int result = performAddition(a, b);
        
        // Assert
        assertEquals(expected, result, 
            "Basic addition should work correctly");
    }}
    
    private String getHelloWorldMessage() {{
        return "Hello World";
    }}
    
    private int performAddition(int x, int y) {{
        return x + y;
    }}
}}
```

### {safe_name}PerformanceTests.java
```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

public class {safe_name}PerformanceTests {{
    
    @Test
    @DisplayName("Simple Performance Check")
    void testSimplePerformanceCheck() {{
        // Arrange
        long maxExecutionTimeMs = 1000; // 1 second
        
        // Act
        long startTime = System.currentTimeMillis();
        performSimpleOperation();
        long endTime = System.currentTimeMillis();
        long executionTime = endTime - startTime;
        
        // Assert
        assertTrue(executionTime < maxExecutionTimeMs,
            "Operation should complete in less than " + maxExecutionTimeMs + "ms");
    }}
    
    private void performSimpleOperation() {{
        try {{
            Thread.sleep(100); // Simulate some work
        }} catch (InterruptedException e) {{
            Thread.currentThread().interrupt();
        }}
    }}
}}
```

## Build Instructions
mvn compile test-compile

## Test Execution
mvn test'''
        
        elif language.lower() == 'python':
            return f'''## Test Project Structure
- tests/
  - test_{safe_name.lower()}_basic.py
  - test_{safe_name.lower()}_performance.py
- requirements.txt
- pytest.ini

## Complete Test File Contents

### requirements.txt
```
pytest==7.4.0
pytest-html==3.2.0
```

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --html=reports/report.html --self-contained-html
```

### test_{safe_name.lower()}_basic.py
```python
import pytest
import time

class Test{safe_name}Basic:
    """Basic test cases for {product_name}"""
    
    def test_hello_world(self):
        """Test basic Hello World functionality"""
        # Arrange
        expected_message = "Hello World"
        
        # Act
        actual_message = self._get_hello_world_message()
        
        # Assert
        assert actual_message == expected_message, f"Expected '{{expected_message}}', got '{{actual_message}}'"
        print(f"Test passed: {{actual_message}}")
    
    def test_basic_math_operations(self):
        """Test basic mathematical operations"""
        # Arrange
        a = 2
        b = 2
        expected = 4
        
        # Act
        result = self._perform_addition(a, b)
        
        # Assert
        assert result == expected, f"Expected {{expected}}, got {{result}}"
    
    def test_string_manipulation(self):
        """Test basic string operations"""
        # Arrange
        text = "hello"
        expected = "HELLO"
        
        # Act
        result = text.upper()
        
        # Assert
        assert result == expected, f"String uppercase failed: expected {{expected}}, got {{result}}"
    
    def _get_hello_world_message(self):
        """Helper method to get hello world message"""
        return "Hello World"
    
    def _perform_addition(self, x, y):
        """Helper method for addition"""
        return x + y
```

### test_{safe_name.lower()}_performance.py
```python
import pytest
import time

class Test{safe_name}Performance:
    """Performance test cases for {product_name}"""
    
    def test_simple_performance_check(self):
        """Test that operations complete within acceptable time"""
        # Arrange
        max_execution_time = 1.0  # 1 second
        
        # Act
        start_time = time.time()
        self._perform_simple_operation()
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert
        assert execution_time < max_execution_time, f"Operation took {{execution_time:.3f}}s, should be less than {{max_execution_time}}s"
    
    def test_memory_efficiency(self):
        """Test basic memory usage patterns"""
        # Arrange
        data_size = 1000
        
        # Act
        data = list(range(data_size))
        
        # Assert
        assert len(data) == data_size, f"Data size mismatch: expected {{data_size}}, got {{len(data)}}"
        assert all(isinstance(x, int) for x in data), "All data items should be integers"
    
    def _perform_simple_operation(self):
        """Helper method that simulates work"""
        time.sleep(0.1)  # Simulate some work
```

## Build Instructions
pip install -r requirements.txt

## Test Execution
pytest -v'''
        
        elif language.lower() in ['javascript', 'js', 'node.js']:
            return f'''## Test Project Structure
- tests/
  - {safe_name.lower()}.basic.test.js
  - {safe_name.lower()}.performance.test.js
- package.json
- jest.config.js

## Complete Test File Contents

### package.json
```json
{{
  "name": "{safe_name.lower()}-tests",
  "version": "1.0.0",
  "description": "Test project for {product_name}",
  "scripts": {{
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }},
  "devDependencies": {{
    "jest": "^29.5.0"
  }},
  "jest": {{
    "testEnvironment": "node",
    "testMatch": ["**/tests/**/*.test.js"],
    "collectCoverageFrom": ["tests/**/*.js"]
  }}
}}
```

### jest.config.js
```javascript
module.exports = {{
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js'],
  verbose: true,
  collectCoverage: true,
  coverageDirectory: 'coverage'
}};
```

### {safe_name.lower()}.basic.test.js
```javascript
describe('{safe_name} Basic Tests', () => {{
    
    test('Hello World Test', () => {{
        // Arrange
        const expectedMessage = 'Hello World';
        
        // Act
        const actualMessage = getHelloWorldMessage();
        
        // Assert
        expect(actualMessage).toBe(expectedMessage);
        console.log(`Test passed: ${{actualMessage}}`);
    }});
    
    test('Basic Math Operations', () => {{
        // Arrange
        const a = 2;
        const b = 2;
        const expected = 4;
        
        // Act
        const result = performAddition(a, b);
        
        // Assert
        expect(result).toBe(expected);
    }});
    
    test('String Manipulation', () => {{
        // Arrange
        const text = 'hello';
        const expected = 'HELLO';
        
        // Act
        const result = text.toUpperCase();
        
        // Assert
        expect(result).toBe(expected);
    }});
}});

// Helper functions
function getHelloWorldMessage() {{
    return 'Hello World';
}}

function performAddition(x, y) {{
    return x + y;
}}
```

### {safe_name.lower()}.performance.test.js
```javascript
describe('{safe_name} Performance Tests', () => {{
    
    test('Simple Performance Check', async () => {{
        // Arrange
        const maxExecutionTime = 1000; // 1 second in milliseconds
        
        // Act
        const startTime = Date.now();
        await performSimpleOperation();
        const endTime = Date.now();
        const executionTime = endTime - startTime;
        
        // Assert
        expect(executionTime).toBeLessThan(maxExecutionTime);
    }});
    
    test('Array Processing Performance', () => {{
        // Arrange
        const dataSize = 1000;
        const maxProcessingTime = 100; // milliseconds
        
        // Act
        const startTime = Date.now();
        const data = Array.from({{length: dataSize}}, (_, i) => i);
        const processed = data.map(x => x * 2);
        const endTime = Date.now();
        
        // Assert
        expect(processed.length).toBe(dataSize);
        expect(endTime - startTime).toBeLessThan(maxProcessingTime);
    }});
}});

// Helper functions
async function performSimpleOperation() {{
    return new Promise(resolve => {{
        setTimeout(resolve, 100); // Simulate some async work
    }});
}}
```

## Build Instructions
npm install

## Test Execution
npm test'''
        
        elif language.lower() == 'go':
            return f'''## Test Project Structure
- {safe_name.lower()}_basic_test.go
- {safe_name.lower()}_performance_test.go
- go.mod

## Complete Test File Contents

### go.mod
```go
module {safe_name.lower()}/tests

go 1.21
```

### {safe_name.lower()}_basic_test.go
```go
package main

import (
    "fmt"
    "strings"
    "testing"
)

func TestHelloWorld(t *testing.T) {{
    // Arrange
    expected := "Hello World"
    
    // Act
    actual := getHelloWorldMessage()
    
    // Assert
    if actual != expected {{
        t.Errorf("Expected '%s', got '%s'", expected, actual)
    }}
    fmt.Printf("Test passed: %s\\n", actual)
}}

func TestBasicMathOperations(t *testing.T) {{
    // Arrange
    a := 2
    b := 2
    expected := 4
    
    // Act
    result := performAddition(a, b)
    
    // Assert
    if result != expected {{
        t.Errorf("Expected %d, got %d", expected, result)
    }}
}}

func TestStringManipulation(t *testing.T) {{
    // Arrange
    text := "hello"
    expected := "HELLO"
    
    // Act
    result := strings.ToUpper(text)
    
    // Assert
    if result != expected {{
        t.Errorf("Expected '%s', got '%s'", expected, result)
    }}
}}

// Helper functions
func getHelloWorldMessage() string {{
    return "Hello World"
}}

func performAddition(x, y int) int {{
    return x + y
}}
```

### {safe_name.lower()}_performance_test.go
```go
package main

import (
    "testing"
    "time"
)

func TestSimplePerformanceCheck(t *testing.T) {{
    // Arrange
    maxExecutionTime := 1 * time.Second
    
    // Act
    start := time.Now()
    performSimpleOperation()
    elapsed := time.Since(start)
    
    // Assert
    if elapsed > maxExecutionTime {{
        t.Errorf("Operation took %v, should be less than %v", elapsed, maxExecutionTime)
    }}
}}

func TestArrayProcessingPerformance(t *testing.T) {{
    // Arrange
    dataSize := 1000
    maxProcessingTime := 100 * time.Millisecond
    
    // Act
    start := time.Now()
    data := make([]int, dataSize)
    for i := 0; i < dataSize; i++ {{
        data[i] = i * 2
    }}
    elapsed := time.Since(start)
    
    // Assert
    if len(data) != dataSize {{
        t.Errorf("Expected data size %d, got %d", dataSize, len(data))
    }}
    if elapsed > maxProcessingTime {{
        t.Errorf("Processing took %v, should be less than %v", elapsed, maxProcessingTime)
    }}
}}

// Helper functions
func performSimpleOperation() {{
    time.Sleep(100 * time.Millisecond) // Simulate some work
}}
```

## Build Instructions
go mod tidy

## Test Execution
go test -v'''
        
        elif language.lower() == 'rust':
            return f'''## Test Project Structure
- src/
  - lib.rs
- Cargo.toml

## Complete Test File Contents

### Cargo.toml
```toml
[package]
name = "{safe_name.lower()}_tests"
version = "0.1.0"
edition = "2021"

[dependencies]

[dev-dependencies]
```

### src/lib.rs
```rust
#[cfg(test)]
mod basic_tests {{
    use super::*;
    
    #[test]
    fn test_hello_world() {{
        // Arrange
        let expected = "Hello World";
        
        // Act
        let actual = get_hello_world_message();
        
        // Assert
        assert_eq!(actual, expected, "Hello World message should match expected value");
        println!("Test passed: {{}}", actual);
    }}
    
    #[test]
    fn test_basic_math_operations() {{
        // Arrange
        let a = 2;
        let b = 2;
        let expected = 4;
        
        // Act
        let result = perform_addition(a, b);
        
        // Assert
        assert_eq!(result, expected, "Basic addition should work correctly");
    }}
    
    #[test]
    fn test_string_manipulation() {{
        // Arrange
        let text = "hello";
        let expected = "HELLO";
        
        // Act
        let result = text.to_uppercase();
        
        // Assert
        assert_eq!(result, expected, "String uppercase should work correctly");
    }}
}}

#[cfg(test)]
mod performance_tests {{
    use super::*;
    use std::time::{{Duration, Instant}};
    
    #[test]
    fn test_simple_performance_check() {{
        // Arrange
        let max_execution_time = Duration::from_millis(1000);
        
        // Act
        let start = Instant::now();
        perform_simple_operation();
        let elapsed = start.elapsed();
        
        // Assert
        assert!(elapsed < max_execution_time, 
            "Operation took {{:?}}, should be less than {{:?}}", elapsed, max_execution_time);
    }}
    
    #[test]
    fn test_vector_processing_performance() {{
        // Arrange
        let data_size = 1000;
        let max_processing_time = Duration::from_millis(100);
        
        // Act
        let start = Instant::now();
        let data: Vec<i32> = (0..data_size).map(|x| x * 2).collect();
        let elapsed = start.elapsed();
        
        // Assert
        assert_eq!(data.len(), data_size, "Data size should match expected");
        assert!(elapsed < max_processing_time, 
            "Processing took {{:?}}, should be less than {{:?}}", elapsed, max_processing_time);
    }}
}}

// Helper functions
fn get_hello_world_message() -> &'static str {{
    "Hello World"
}}

fn perform_addition(x: i32, y: i32) -> i32 {{
    x + y
}}

fn perform_simple_operation() {{
    std::thread::sleep(Duration::from_millis(100)); // Simulate some work
}}
```

## Build Instructions
cargo build

## Test Execution
cargo test'''
        
        else:
            return f"# {safe_name} Comprehensive Test Project\n\nComplete test structure for {language}"
    
    def _create_test_framework_config(self, project_dir: str, language: str, product_name: str) -> str:
        """Create test framework configuration files"""
        if language.lower() in ['csharp', 'c#']:
            # NUnit configuration is already in the .csproj file
            return "NUnit framework configured in .csproj"
        
        elif language.lower() == 'java':
            # JUnit configuration in pom.xml
            return "JUnit 5 configured in pom.xml"
        
        elif language.lower() == 'python':
            # Create pytest.ini for configuration
            pytest_config = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v
"""
            config_path = os.path.join(project_dir, "pytest.ini")
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(pytest_config)
            return config_path
        
        elif language.lower() in ['javascript', 'js', 'node.js']:
            # Jest configuration is in package.json
            return "Jest configured in package.json"
        
        elif language.lower() == 'go':
            # Go uses built-in testing, no additional config needed
            return "Go built-in testing framework"
        
        elif language.lower() == 'rust':
            # Rust uses built-in testing, no additional config needed
            return "Rust built-in testing framework"
        
        return "Test framework configured"
    
    def _create_simple_test(self, project_dir: str, language: str, product_name: str) -> str:
        """Create a simple passing test to verify test framework works"""
        safe_name = product_name.replace(' ', '').replace('-', '')
        
        if language.lower() in ['csharp', 'c#']:
            test_content = f'''using NUnit.Framework;

namespace {safe_name}.Tests
{{
    [TestFixture]
    public class {safe_name}SimpleTests
    {{
        [Test]
        public void SimplePassingTest()
        {{
            Assert.That(true, Is.True, "This test should always pass");
        }}
        
        [Test]
        public void MathTest()
        {{
            int result = 2 + 2;
            Assert.That(result, Is.EqualTo(4), "Basic math should work");
        }}
    }}
}}'''
            
            test_dir = os.path.join(project_dir, "Tests")
            os.makedirs(test_dir, exist_ok=True)
            test_path = os.path.join(test_dir, f"{safe_name}SimpleTests.cs")
            
        elif language.lower() == 'python':
            test_content = f'''import pytest

def test_simple_passing():
    """A simple test that should always pass"""
    assert True

def test_basic_math():
    """Test basic math operations"""
    result = 2 + 2
    assert result == 4
'''
            
            test_dir = os.path.join(project_dir, "tests")
            os.makedirs(test_dir, exist_ok=True)
            test_path = os.path.join(test_dir, f"test_{safe_name.lower()}_simple.py")
            
        else:
            return "Simple test created in main test file"
        
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        self.log(f"📝 Created simple test: {test_path}")
        return test_path
    
    def _build_and_validate_project(self, project_dir: str, language: str, step_name: str) -> Dict[str, Any]:
        """Build and validate project at current step"""
        self.log(f"🔨 Building and validating: {step_name}")
        
        # Check tool availability
        tool_availability = self.project_builder.check_tool_availability(language)
        
        if not any(tool_availability.values()):
            self.log(f"⚠️ No build tools available for {language}")
            return {
                "success": False,
                "error": f"Build tools not available for {language}",
                "tool_availability": tool_availability
            }
        
        # Execute full build cycle
        build_result = self.project_builder.full_build_cycle(project_dir, language)
        
        if build_result.get('success', False):
            self.log(f"✅ {step_name}: Build successful")
        else:
            self.log(f"❌ {step_name}: Build failed")
            
            # Log specific errors for debugging
            if build_result.get('restore', {}).get('error'):
                self.log(f"   Restore error: {build_result['restore']['error'][:200]}...")
            if build_result.get('build', {}).get('error'):
                self.log(f"   Build error: {build_result['build']['error'][:200]}...")
        
        return build_result
    
    def _fix_scenario_test_errors(self, project_dir: str, language: str, product_name: str, errors: List[str]) -> None:
        """Apply fixes for scenario test compilation errors"""
        self.log(f"🔧 Applying fixes for {len(errors)} compilation errors")
        
        # Apply language-specific fixes
        if language.lower() in ['csharp', 'c#']:
            self._fix_csharp_test_files(project_dir, product_name, errors)
        elif language.lower() == 'java':
            self._fix_java_test_files(project_dir, product_name, errors)
        elif language.lower() == 'python':
            self._fix_python_test_files(project_dir, errors)
    
    def _fix_csharp_test_files(self, project_dir: str, product_name: str, errors: List[str]) -> None:
        """Fix C# test files"""
        test_dir = os.path.join(project_dir, "Tests")
        if not os.path.exists(test_dir):
            return
        
        for filename in os.listdir(test_dir):
            if filename.endswith('.cs'):
                file_path = os.path.join(test_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply common fixes
                fixed_content = self._fix_csharp_issues(content, product_name)
                
                if fixed_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    self.log(f"🔧 Fixed C# test file: {filename}")
    
    def _fix_java_test_files(self, project_dir: str, product_name: str, errors: List[str]) -> None:
        """Fix Java test files"""
        test_dir = os.path.join(project_dir, "src", "test", "java")
        if not os.path.exists(test_dir):
            return
        
        for filename in os.listdir(test_dir):
            if filename.endswith('.java'):
                file_path = os.path.join(test_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply common fixes
                fixed_content = self._fix_java_issues(content, product_name)
                
                if fixed_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    self.log(f"🔧 Fixed Java test file: {filename}")
    
    def _fix_python_test_files(self, project_dir: str, errors: List[str]) -> None:
        """Fix Python test files"""
        test_dir = os.path.join(project_dir, "tests")
        if not os.path.exists(test_dir):
            return
        
        for filename in os.listdir(test_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(test_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply common fixes
                fixed_content = self._fix_python_issues(content)
                
                if fixed_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    self.log(f"🔧 Fixed Python test file: {filename}")
    
    def _extract_compilation_errors(self, build_result: Dict[str, Any]) -> List[str]:
        """Extract compilation errors from build result"""
        errors = []
        
        # Check build phase errors
        build_info = build_result.get('build', {})
        if build_info.get('error'):
            build_errors = build_info['error'].strip()
            if build_errors and build_errors != 'No errors':
                errors.append(f"Build Error: {build_errors}")
        
        # Check restore phase errors  
        restore_info = build_result.get('restore', {})
        if restore_info.get('error'):
            restore_errors = restore_info['error'].strip()
            if restore_errors and restore_errors != 'No errors':
                errors.append(f"Restore Error: {restore_errors}")
        
        # Check for specific error patterns in output
        all_output = ""
        if build_info.get('output'):
            all_output += build_info['output']
        if restore_info.get('output'):
            all_output += restore_info['output']
        
        # Common compilation error patterns
        error_patterns = [
            r"error CS\d+:",  # C# compiler errors
            r"ERROR:",        # General errors
            r"error:",        # Lowercase errors
            r"compilation failed",
            r"build failed",
            r"cannot find symbol",  # Java errors
            r"undefined reference", # C/C++ linker errors
            r"SyntaxError:",        # Python syntax errors
            r"TypeError:",          # Python type errors
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern + r".*", all_output, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if match.strip() and match.strip() not in [e.split(': ', 1)[-1] for e in errors]:
                    errors.append(f"Compilation Issue: {match.strip()}")
        
        return errors[:10]  # Limit to top 10 errors to avoid overwhelming the LLM
    
    def _regenerate_code_with_fixes(self, original_content: str, language: str, product_name: str, 
                                   scenarios: list, compilation_errors: List[str], attempt_num: int) -> str:
        """Regenerate code with compilation error fixes"""
        try:
            self.log(f"🔨 Regenerating code to fix compilation errors (attempt {attempt_num})")
            
            # Create a fix-focused prompt
            error_summary = "\n".join([f"- {error}" for error in compilation_errors])
            
            fix_prompt = f"""
The previously generated {language} test project has compilation errors. Please fix these specific issues:

COMPILATION ERRORS TO FIX:
{error_summary}

CRITICAL REQUIREMENTS:
1. Class names MUST match their file names exactly (e.g., file "TestClass.cs" must contain "class TestClass")
2. Use correct namespace declarations
3. Include all necessary using statements
4. Fix any syntax errors
5. Ensure proper method signatures and access modifiers

Original failing code:
{original_content}

Please generate a corrected version that addresses all the compilation errors above.
Focus on:
- Fixing syntax errors
- Correcting class/file name mismatches
- Adding missing imports/using statements
- Ensuring proper language-specific conventions

Generate ONLY the corrected test project code with the same structure but fixed compilation issues.
"""
            
            # Use the existing LLM chain but with error-focused prompt
            temp_prompt = PromptTemplate(
                input_variables=["fix_content"],
                template="{fix_content}"
            )
            fix_chain = LLMChain(llm=self.llm, prompt=temp_prompt)
            
            fix_result = fix_chain.invoke({"fix_content": fix_prompt})
            fixed_content = fix_result["text"]
            
            # Apply additional automatic fixes
            fixed_content = self._apply_automatic_fixes(fixed_content, language, product_name)
            
            self.log(f"📝 Generated fixed content ({len(fixed_content)} characters)")
            return fixed_content
            
        except Exception as e:
            self.log(f"❌ Error during code regeneration: {str(e)}")
            return original_content
    
    def _enhance_class_naming(self, content: str, language: str, product_name: str) -> str:
        """Enhance class naming to match file names"""
        try:
            self.log("🏷️ Enhancing class naming to match file names")
            
            if language.lower() in ['csharp', 'c#']:
                # Fix C# class naming issues
                enhanced_content = self._fix_csharp_class_naming(content, product_name)
            elif language.lower() == 'java':
                # Fix Java class naming issues
                enhanced_content = self._fix_java_class_naming(content, product_name)
            else:
                # For other languages, return as-is
                enhanced_content = content
            
            if enhanced_content != content:
                self.log("✅ Applied class naming enhancements")
            else:
                self.log("ℹ️ No class naming changes needed")
            
            return enhanced_content
            
        except Exception as e:
            self.log(f"❌ Error enhancing class naming: {str(e)}")
            return content
    
    def _fix_csharp_class_naming(self, content: str, product_name: str) -> str:
        """Fix C# class naming to match file names"""
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            # Look for class declarations
            class_match = re.match(r'(\s*)public\s+class\s+(\w+)', line)
            if class_match:
                indent = class_match.group(1)
                class_name = class_match.group(2)
                
                # Ensure class name includes product name and appropriate suffix
                if not class_name.startswith(product_name.replace(' ', '').replace('-', '')):
                    # Try to infer the file name from context or use a standard pattern
                    if 'Basic' in line or 'basic' in content.lower():
                        new_class_name = f"{product_name.replace(' ', '').replace('-', '')}BasicTests"
                    elif 'Performance' in line or 'performance' in content.lower():
                        new_class_name = f"{product_name.replace(' ', '').replace('-', '')}PerformanceTests"
                    elif 'Integration' in line or 'integration' in content.lower():
                        new_class_name = f"{product_name.replace(' ', '').replace('-', '')}IntegrationTests"
                    elif 'Api' in line or 'api' in content.lower():
                        new_class_name = f"{product_name.replace(' ', '').replace('-', '')}ApiTests"
                    elif 'Security' in line or 'security' in content.lower():
                        new_class_name = f"{product_name.replace(' ', '').replace('-', '')}SecurityTests"
                    else:
                        new_class_name = f"{product_name.replace(' ', '').replace('-', '')}Tests"
                    
                    line = f"{indent}public class {new_class_name}"
                    self.log(f"🔧 Fixed class name: {class_name} → {new_class_name}")
            
            enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _fix_java_class_naming(self, content: str, product_name: str) -> str:
        """Fix Java class naming to match file names"""
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            # Look for class declarations
            class_match = re.match(r'(\s*)public\s+class\s+(\w+)', line)
            if class_match:
                indent = class_match.group(1)
                class_name = class_match.group(2)
                
                # Ensure class name follows Java conventions and includes product name
                if not class_name.startswith(product_name.replace(' ', '').replace('-', '')):
                    new_class_name = f"{product_name.replace(' ', '').replace('-', '')}Tests"
                    line = f"{indent}public class {new_class_name}"
                    self.log(f"🔧 Fixed Java class name: {class_name} → {new_class_name}")
            
            enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _apply_automatic_fixes(self, content: str, language: str, product_name: str) -> str:
        """Apply automatic fixes for common compilation issues"""
        self.log("🔧 Applying automatic fixes for common issues")
        
        fixed_content = content
        
        if language.lower() in ['csharp', 'c#']:
            # Fix common C# issues
            fixed_content = self._fix_csharp_issues(fixed_content, product_name)
        elif language.lower() == 'java':
            # Fix common Java issues
            fixed_content = self._fix_java_issues(fixed_content, product_name)
        elif language.lower() == 'python':
            # Fix common Python issues
            fixed_content = self._fix_python_issues(fixed_content)
        
        return fixed_content
    
    def _fix_csharp_issues(self, content: str, product_name: str) -> str:
        """Fix common C# compilation issues"""
        fixes_applied = []
        
        # Ensure proper using statements
        if 'using NUnit.Framework;' not in content:
            content = 'using NUnit.Framework;\nusing System;\nusing System.Threading.Tasks;\n\n' + content
            fixes_applied.append("Added missing using statements")
        
        # Fix namespace issues
        namespace_pattern = r'namespace\s+([^{]+)'
        if not re.search(namespace_pattern, content):
            safe_product_name = product_name.replace(' ', '').replace('-', '')
            content = content.replace('public class', f'namespace {safe_product_name}.Tests\n{{\n    public class', 1)
            content += '\n}'
            fixes_applied.append("Added missing namespace")
        
        # Fix class naming consistency
        content = self._fix_csharp_class_naming(content, product_name)
        
        # Fix method naming to follow C# conventions
        content = re.sub(r'public void test(\w+)', r'public void Test\1', content)
        fixes_applied.append("Fixed method naming conventions")
        
        if fixes_applied:
            self.log(f"🔧 Applied C# fixes: {', '.join(fixes_applied)}")
        
        return content
    
    def _fix_java_issues(self, content: str, product_name: str) -> str:
        """Fix common Java compilation issues"""
        fixes_applied = []
        
        # Ensure proper imports
        required_imports = [
            'import org.junit.jupiter.api.*;',
            'import static org.junit.jupiter.api.Assertions.*;'
        ]
        
        for import_stmt in required_imports:
            if import_stmt not in content:
                content = import_stmt + '\n' + content
                fixes_applied.append(f"Added {import_stmt}")
        
        # Fix package declaration
        if not content.strip().startswith('package'):
            safe_product_name = product_name.lower().replace(' ', '').replace('-', '')
            content = f'package com.{safe_product_name}.tests;\n\n' + content
            fixes_applied.append("Added package declaration")
        
        # Fix class naming
        content = self._fix_java_class_naming(content, product_name)
        
        if fixes_applied:
            self.log(f"🔧 Applied Java fixes: {', '.join(fixes_applied)}")
        
        return content
    
    def _fix_python_issues(self, content: str) -> str:
        """Fix common Python issues"""
        fixes_applied = []
        
        # Ensure proper imports
        if 'import pytest' not in content:
            content = 'import pytest\nimport asyncio\nimport time\nfrom typing import Dict, Any\n\n' + content
            fixes_applied.append("Added missing imports")
        
        # Fix method naming
        content = re.sub(r'def test([A-Z])', r'def test_\1', content)
        content = re.sub(r'def test_([A-Z])', lambda m: f'def test_{m.group(1).lower()}', content)
        
        if fixes_applied:
            self.log(f"🔧 Applied Python fixes: {', '.join(fixes_applied)}")
        
        return content
    
    def _parse_and_create_files_with_tools(self, generated_content: str, project_dir: str) -> Dict[str, str]:
        """Parse LLM output and create files using the new tools"""
        created_files = {}
        
        try:
            # Extract code blocks using the tool
            code_blocks = self.code_extractor.extract_code_blocks(generated_content)
            
            for filename, content, language in code_blocks:
                file_path = self.file_creator.create_file(project_dir, filename, content, language)
                if file_path:
                    created_files[f"llm_generated_{filename}"] = file_path
                    self.log(f"Created file from LLM output: {filename}")
            
            # Extract and create project structure using the tool
            project_structure = self.structure_parser.extract_project_structure(generated_content)
            if project_structure:
                normalized_structure = self.structure_parser.normalize_structure(project_structure)
                structure_paths = self.structure_parser.create_directory_structure(project_dir, normalized_structure)
                
                # Add structure info to created files
                if structure_paths.get('directories'):
                    created_files["created_directories"] = structure_paths['directories']
                if structure_paths.get('files'):
                    created_files["created_structure_files"] = structure_paths['files']
            
            # Create enhanced README using the tool
            enhanced_readme = self._create_enhanced_readme_with_tools(project_dir, generated_content, "Generated Project")
            if enhanced_readme:
                created_files["enhanced_readme"] = enhanced_readme
            
            # Create build summary if build was attempted
            if "build_result" in created_files:
                build_summary = self._create_build_summary(project_dir, created_files["build_result"], language)
                if build_summary:
                    created_files["build_summary"] = build_summary
            
        except Exception as e:
            self.log(f"Error parsing LLM output with tools: {str(e)}")
        
        return created_files
    
    def _create_enhanced_readme_with_tools(self, project_dir: str, generated_content: str, product_name: str) -> str:
        """Create an enhanced README using the file creator tool"""
        try:
            # Extract sections from generated content
            setup_pattern = r'##\s*Setup\s*Instructions\s*\n(.*?)(?=##|\Z)'
            setup_match = re.search(setup_pattern, generated_content, re.DOTALL | re.IGNORECASE)
            
            usage_pattern = r'##\s*Usage\s*Examples?\s*\n(.*?)(?=##|\Z)'
            usage_match = re.search(usage_pattern, generated_content, re.DOTALL | re.IGNORECASE)
            
            test_pattern = r'##\s*Test\s*Execution\s*\n(.*?)(?=##|\Z)'
            test_match = re.search(test_pattern, generated_content, re.DOTALL | re.IGNORECASE)
            
            # Extract project metadata using the structure parser
            structure = self.structure_parser.extract_project_structure(generated_content)
            metadata = self.structure_parser.get_project_metadata(structure)
            
            readme_content = f"""# {product_name} - Enhanced Documentation

This project was generated using AI-powered code generation tools.

## Project Metadata
- **Total Items**: {metadata['total_items']}
- **Directories**: {metadata['directories']}
- **Files**: {metadata['files']}
- **Languages**: {', '.join(metadata['languages']) if metadata['languages'] else 'Not detected'}
- **Has Tests**: {'Yes' if metadata['has_tests'] else 'No'}
- **Has Documentation**: {'Yes' if metadata['has_docs'] else 'No'}
- **Frameworks**: {', '.join(metadata['frameworks']) if metadata['frameworks'] else 'None detected'}

## Project Overview
{product_name} is a software project with comprehensive functionality and test coverage.

"""
            
            if setup_match:
                readme_content += f"""## Setup Instructions
{setup_match.group(1).strip()}

"""
            
            if usage_match:
                readme_content += f"""## Usage Examples
{usage_match.group(1).strip()}

"""
                
            if test_match:
                readme_content += f"""## Test Execution
{test_match.group(1).strip()}

"""
            
            # Add extracted dependencies
            dependencies = self.code_extractor.extract_project_dependencies(generated_content, "unknown")
            if dependencies:
                readme_content += f"""## Dependencies
{chr(10).join([f'- {dep}' for dep in dependencies])}

"""
            
            readme_content += f"""## Full Generated Content

Below is the complete output from the AI code generator:

{generated_content}
"""
            
            # Use the file creator tool to create the README
            enhanced_readme_path = self.file_creator.create_file(project_dir, "README_ENHANCED.md", readme_content, "markdown")
            
            if enhanced_readme_path:
                self.log("Created enhanced README with tools")
                return enhanced_readme_path
            else:
                self.log("Failed to create enhanced README")
                return None
            
        except Exception as e:
            self.log(f"Error creating enhanced README: {str(e)}")
            return None
    
    def _create_build_summary(self, project_dir: str, build_result: Dict[str, Any], language: str) -> str:
        """Create a build summary file with detailed build information"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            summary_content = f"""# Build Summary Report
Generated on: {timestamp}
Language: {language.title()}
Project Directory: {project_dir}

## Build Status
Overall Success: {'✅ YES' if build_result.get('success', False) else '❌ NO'}

## Build Steps

### 1. Dependency Restoration
"""
            
            restore_info = build_result.get('restore', {})
            summary_content += f"""
- Command: `{' '.join(restore_info.get('command', []))}`
- Success: {'✅' if restore_info.get('success', False) else '❌'}
- Return Code: {restore_info.get('return_code', 'N/A')}

**Output:**
```
{restore_info.get('output', 'No output')}
```

**Errors:**
```
{restore_info.get('error', 'No errors')}
```

### 2. Project Build
"""
            
            build_info = build_result.get('build', {})
            summary_content += f"""
- Command: `{' '.join(build_info.get('command', []))}`
- Success: {'✅' if build_info.get('success', False) else '❌'}
- Return Code: {build_info.get('return_code', 'N/A')}

**Output:**
```
{build_info.get('output', 'No output')}
```

**Errors:**
```
{build_info.get('error', 'No errors')}
```

### 3. Test Execution
"""
            
            test_info = build_result.get('test', {})
            summary_content += f"""
- Command: `{' '.join(test_info.get('command', []))}`
- Success: {'✅' if test_info.get('success', False) else '❌'}
- Return Code: {test_info.get('return_code', 'N/A')}

**Output:**
```
{test_info.get('output', 'No output')}
```

**Errors:**
```
{test_info.get('error', 'No errors')}
```

## Recommendations

"""
            
            # Add recommendations based on build results
            if build_result.get('success', False):
                summary_content += """
✅ **Project is compilation-free and ready to use!**

- All dependencies were successfully restored
- Project compiles without errors
- Test framework is properly configured

**Next Steps:**
1. Add your specific test implementations
2. Run tests with the appropriate command for your language
3. Implement actual functionality being tested

"""
            else:
                summary_content += """
⚠️ **Project needs attention before it's compilation-free**

**Issues to resolve:**
"""
                
                if not restore_info.get('success', False):
                    summary_content += """
- Dependency restoration failed - check your environment and tool installation
- Ensure all required SDKs/runtimes are installed
"""
                
                if not build_info.get('success', False):
                    summary_content += """
- Build compilation failed - check for syntax errors or missing dependencies
- Review the build output above for specific error messages
"""
                
                summary_content += """
**Recommended Actions:**
1. Install required development tools for {language}
2. Check project configuration files
3. Resolve any dependency conflicts
4. Fix compilation errors shown in the build output

"""
            
            # Language-specific quick start commands
            quick_start_commands = {
                'csharp': ['dotnet restore', 'dotnet build', 'dotnet test'],
                'java': ['mvn dependency:resolve', 'mvn compile test-compile', 'mvn test'],
                'python': ['pip install -r requirements.txt', 'python -m pytest'],
                'javascript': ['npm install', 'npm test'],
                'go': ['go mod download', 'go build ./...', 'go test ./...'],
                'rust': ['cargo fetch', 'cargo build', 'cargo test']
            }
            
            commands = quick_start_commands.get(language.lower(), [])
            if commands:
                summary_content += f"""
## Quick Start Commands

To manually build and test this project, run these commands in the project directory:

```bash
{chr(10).join(commands)}
```

"""
            
            summary_content += f"""
## Build Configuration

Check these files for project configuration:
"""
            
            # Language-specific config files
            config_files = {
                'csharp': ['*.csproj', '*.sln'],
                'java': ['pom.xml', 'build.gradle'],
                'python': ['requirements.txt', 'setup.py', 'pyproject.toml'],
                'javascript': ['package.json'],
                'go': ['go.mod'],
                'rust': ['Cargo.toml']
            }
            
            files = config_files.get(language.lower(), [])
            for config_file in files:
                summary_content += f"- {config_file}\n"
            
            summary_content += f"""

---
*This build summary was automatically generated by the Bug Bash Agent*
"""
            
            # Create the build summary file
            build_summary_path = self.file_creator.create_file(project_dir, "BUILD_SUMMARY.md", summary_content, "markdown")
            
            if build_summary_path:
                self.log("Created build summary report")
                return build_summary_path
            else:
                self.log("Failed to create build summary")
                return None
                
        except Exception as e:
            self.log(f"Error creating build summary: {str(e)}")
            return None
    
    def _fix_javascript_issues(self, content: str) -> str:
        """Fix common JavaScript/Node.js issues"""
        fixes_applied = []
        
        # Ensure proper test structure
        if 'describe(' not in content and 'test(' not in content:
            content = f"describe('Test Suite', () => {{\n{content}\n}});"
            fixes_applied.append("Added describe block")
        
        # Fix missing semicolons
        content = re.sub(r'(\w+\([^)]*\))(\s*\n)', r'\1;\2', content)
        fixes_applied.append("Fixed missing semicolons")
        
        if fixes_applied:
            self.log(f"🔧 Applied JavaScript fixes: {', '.join(fixes_applied)}")
        
        return content
    
    def _fix_go_issues(self, content: str) -> str:
        """Fix common Go issues"""
        fixes_applied = []
        
        # Ensure proper package declaration
        if not content.strip().startswith('package'):
            content = 'package main\n\n' + content
            fixes_applied.append("Added package declaration")
        
        # Ensure proper imports
        if 'import' not in content and 'testing' in content:
            content = content.replace('package main\n', 'package main\n\nimport (\n    "testing"\n)\n')
            fixes_applied.append("Added testing import")
        
        if fixes_applied:
            self.log(f"🔧 Applied Go fixes: {', '.join(fixes_applied)}")
        
        return content
    
    def _fix_rust_issues(self, content: str) -> str:
        """Fix common Rust issues"""
        fixes_applied = []
        
        # Ensure proper test module structure
        if '#[cfg(test)]' not in content:
            content = f"#[cfg(test)]\nmod tests {{\n    use super::*;\n\n{content}\n}}"
            fixes_applied.append("Added test module structure")
        
        # Fix test attribute syntax
        content = re.sub(r'@test', '#[test]', content)
        if '@test' in content:
            fixes_applied.append("Fixed test attributes")
        
        if fixes_applied:
            self.log(f"🔧 Applied Rust fixes: {', '.join(fixes_applied)}")
        
        return content
    
    def _intelligent_error_analysis(self, errors: List[str], language: str) -> Dict[str, Any]:
        """Analyze errors intelligently to provide targeted fixes"""
        analysis = {
            'error_categories': [],
            'suggested_fixes': [],
            'confidence_level': 'low'
        }
        
        syntax_errors = 0
        import_errors = 0
        naming_errors = 0
        
        for error in errors:
            error_lower = error.lower()
            
            # Categorize errors
            if any(word in error_lower for word in ['syntax', 'expected', 'missing', ';', '{', '}']):
                syntax_errors += 1
                analysis['error_categories'].append('syntax')
            
            if any(word in error_lower for word in ['import', 'using', 'cannot find', 'does not exist']):
                import_errors += 1
                analysis['error_categories'].append('imports')
            
            if any(word in error_lower for word in ['class', 'name', 'identifier']):
                naming_errors += 1
                analysis['error_categories'].append('naming')
        
        # Generate targeted suggestions
        if syntax_errors > 0:
            analysis['suggested_fixes'].append("Fix syntax errors (missing semicolons, brackets, etc.)")
        
        if import_errors > 0:
            analysis['suggested_fixes'].append(f"Add missing {self._get_import_statement_type(language)} statements")
        
        if naming_errors > 0:
            analysis['suggested_fixes'].append("Fix class and method naming inconsistencies")
        
        # Determine confidence level
        total_errors = len(errors)
        if total_errors <= 3:
            analysis['confidence_level'] = 'high'
        elif total_errors <= 7:
            analysis['confidence_level'] = 'medium'
        else:
            analysis['confidence_level'] = 'low'
        
        return analysis
    
    def _get_import_statement_type(self, language: str) -> str:
        """Get the import statement type for a language"""
        import_types = {
            'csharp': 'using',
            'c#': 'using',
            'java': 'import',
            'python': 'import',
            'javascript': 'import/require',
            'js': 'import/require',
            'node.js': 'import/require',
            'go': 'import',
            'rust': 'use'
        }
        return import_types.get(language.lower(), 'import')
    
    def _create_error_fix_report(self, project_dir: str, errors: List[str], fixes_applied: List[str], language: str) -> str:
        """Create a detailed error fix report"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            report_content = f"""# Error Fix Report
Generated on: {timestamp}
Language: {language.title()}
Project Directory: {project_dir}

## Error Analysis Summary
- **Total Errors Detected**: {len(errors)}
- **Fixes Applied**: {len(fixes_applied)}
- **Language**: {language}

## Detected Errors
"""
            
            for i, error in enumerate(errors, 1):
                report_content += f"{i}. {error}\n"
            
            report_content += f"""
## Applied Fixes
"""
            
            for i, fix in enumerate(fixes_applied, 1):
                report_content += f"{i}. {fix}\n"
            
            # Add error analysis
            analysis = self._intelligent_error_analysis(errors, language)
            
            report_content += f"""
## Error Analysis
- **Error Categories**: {', '.join(set(analysis['error_categories']))}
- **Confidence Level**: {analysis['confidence_level']}

## Suggested Actions
"""
            
            for suggestion in analysis['suggested_fixes']:
                report_content += f"- {suggestion}\n"
            
            report_content += f"""

## Self-Healing Status
The code generator has applied automatic fixes based on detected compilation errors.
If errors persist, the system will attempt additional regeneration cycles.

---
*This report was automatically generated by the self-healing code generator*
"""
            
            # Create the error fix report
            report_path = self.file_creator.create_file(project_dir, "ERROR_FIX_REPORT.md", report_content, "markdown")
            
            if report_path:
                self.log("Created error fix report")
                return report_path
            else:
                self.log("Failed to create error fix report")
                return None
                
        except Exception as e:
            self.log(f"Error creating error fix report: {str(e)}")
            return None
