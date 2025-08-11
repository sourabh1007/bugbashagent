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
    ProjectBuilder,
    ScenarioCategorizer,
    CompilationChecker,
    TestReporter,
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
    """Agent responsible for generating code based on analyzed requirements using modern pattern-based system"""
    
    def __init__(self, llm: Any):
        super().__init__("Code Generator", llm)
        
        # Initialize tools
        self.file_creator = FileCreator()
        self.structure_parser = ProjectStructureParser()
        self.code_extractor = CodeBlockExtractor()
        self.project_builder = ProjectBuilder()
        self.scenario_categorizer = ScenarioCategorizer()
        self.compilation_checker = CompilationChecker()
        self.test_reporter = TestReporter()
        
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
    
    def _get_language_specific_prompt(self, language: str, context: Dict[str, Any] = None) -> str:
        """Get language-specific prompt using the modern pattern-based system"""
        strategy = self.prompt_factory.create_strategy(language)
        if not strategy:
            self.log(f"No strategy found for {language}, using generic strategy")
            strategy = GenericPromptStrategy(language)
        
        return strategy.generate_prompt(context or {})
    
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
                    "error": f"Unsupported language: {language}. Supported languages: {', '.join(self.supported_languages)}"
                }
            
            # Format scenarios for the prompt
            scenarios_text = "\n".join([f"- {scenario}" for scenario in scenarios])
            setup_info_text = json.dumps(setup_info, indent=2)
            
            # Log the input analysis data
            self.log(f"📊 Input Analysis Summary:")
            self.log(f"  - Language: {language}")
            self.log(f"  - Product Name: {product_name}")
            self.log(f"  - Version: {version}")
            self.log(f"  - Number of scenarios: {len(scenarios)}")
            self.log(f"  - Scenarios: {scenarios[:3]}{'...' if len(scenarios) > 3 else ''}")  # Show first 3 scenarios
            
            self.log(f"Generating {language} code for {product_name} using pattern-based prompt system")
            
            # Get language-specific prompt using modern pattern-based system with dynamic dependencies
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
                'scenario_based_packages': True  # Flag to indicate dynamic package detection
            }
            
            # Log the context being passed to prompt generation
            self.log(f"🔧 Prompt Context for {language}:")
            self.log(f"  - Primary test framework: {primary_test_framework}")
            self.log(f"  - Test packages: {len(test_packages)} packages")
            self.log(f"  - Detected dependencies: {len(detected_dependencies.get(language.lower(), {}))} packages")
            self.log(f"  - Language versions: .NET {context['dotnet_version']}, Java {context['java_version']}, Node {context['node_version']}, Python {context['python_version']}")
            if detected_dependencies.get(language.lower()):
                dep_list = ', '.join(detected_dependencies.get(language.lower(), {}).keys())
                self.log(f"  - Scenario-based dependencies: {dep_list}")
            
            language_prompt_template = self._get_language_specific_prompt(language, context)
            if not language_prompt_template:
                return {
                    "agent": self.name,
                    "input": input_data,
                    "output": None,
                    "status": "error",
                    "error": f"No prompt template available for language: {language}"
                }
            
            # Log the prompt template being used
            self.log(f"📝 Using prompt template for {language}:")
            self.log(f"📝 {language_prompt_template}:")
            
            # Create language-specific chain
            prompt_template = PromptTemplate(
                input_variables=["language", "product_name", "version", "scenarios", "setup_info"],
                template=language_prompt_template,
                template_format="jinja2"
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            
            # Prepare the prompt variables
            prompt_vars = {
                "language": language.upper(),
                "product_name": product_name,
                "version": version,
                "scenarios": scenarios_text,
                "setup_info": setup_info_text
            }
            
            # Log the actual prompt that will be sent to LLM (placeholders resolved)
            try:
                # Prefer formatting via chain.prompt if available to mirror LLMChain behavior
                if hasattr(chain, 'prompt') and hasattr(chain.prompt, 'format'):
                    rendered_prompt = chain.prompt.format(**prompt_vars)
                else:
                    rendered_prompt = prompt_template.format(**prompt_vars)

                self.log("🎯 Actual prompt sent to LLM (placeholders resolved):")
                self.log(f"Prompt length: {len(rendered_prompt)} characters")
                self.log("🚀" * 40)
                # Print full prompt; if extremely long, it's fine to be verbose for debugging
                self.log(rendered_prompt)
                self.log("🚀" * 40)
            except Exception as e:
                self.log(f"⚠️ Could not format prompt for logging: {str(e)}")
            
            # Generate code using the language-specific LLM chain
            code_result = chain.invoke(prompt_vars)
            
            generated_content = code_result["text"]
            
            # Log the LLM response summary
            self.log(f"✨ LLM Response Received:")
            self.log(f"Generated content length: {len(generated_content)} characters")
            self.log(f"Response preview (first 300 chars):")
            self.log("-" * 60)
            self.log(generated_content[:300] + "..." if len(generated_content) > 300 else generated_content)
            self.log("-" * 60)
            
            # Create project using appropriate generator
            project_files = self._create_project(
                generated_content, 
                language, 
                product_name, 
                scenarios,
                analysis_data  # Pass analyzer output for CosmosDB version detection
            )
            
            # Always save the complete generated content to a main file
            self._save_complete_generated_content(
                generated_content,
                project_files.get("project_dir", os.path.join("workflow_outputs", f"{product_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")),
                language,
                product_name
            )
            
            # Parse and create additional files from LLM output
            parsed_files = self._parse_and_create_files_with_tools(
                project_files.get("final_generated_content", generated_content),
                project_files.get("project_dir", os.path.join("workflow_outputs", f"{product_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"))
            )
            
            # Merge parsed files with project files
            project_files.update(parsed_files)
            
            # Execute the generated code
            execution_result = self._execute_generated_code(
                project_files.get("project_dir", ""),
                language,
                product_name,
                project_files
            )
            project_files["execution_result"] = execution_result
            
            output = {
                "agent": self.name,
                "input": input_data,
                "output": generated_content,
                "project_files": project_files,
                "language": language,
                "product_name": product_name,
                "compilation_check": project_files.get("compilation_check"),
                "test_report": project_files.get("test_report"),
                "html_test_report_path": project_files.get("html_test_report"),
                "build_status": project_files.get("build_status"),
                "test_status": project_files.get("test_status"),
                "execution_result": project_files.get("execution_result"),
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
    
    def _create_project(self, generated_content: str, language: str, product_name: str, scenarios: list, analyzer_output: Dict[str, Any] = None) -> Dict[str, str]:
        """Create project using the modern tools"""
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
            
            # Check tool availability for building
            tool_availability = self.project_builder.check_tool_availability(language)
            self.log(f"Build tool availability for {language}: {tool_availability}")
            
            # Get build info
            build_info = self.project_builder.get_build_info(project_dir, language)
            self.log(f"Project build info: {build_info}")
            
            # Attempt to build project
            if any(tool_availability.values()):
                self.log(f"🔧 Starting build cycle for {language} project...")
                build_result = self.project_builder.full_build_cycle(project_dir, language)
                
                created_files["build_result"] = build_result
                
                if build_result['success']:
                    self.log(f"✅ Project built successfully!")
                    created_files["build_status"] = "success"
                    
                    # Step 1: Check compilation errors
                    self.log(f"🔍 Checking for compilation errors...")
                    compilation_result = self.compilation_checker.check_compilation(project_dir, language)
                    created_files["compilation_check"] = compilation_result
                    
                    if not compilation_result['success']:
                        self.log(f"❌ Compilation errors found: {len(compilation_result.get('errors', []))} errors")
                        # Generate fix suggestions
                        fix_suggestions = self.compilation_checker.suggest_fixes(compilation_result)
                        created_files["compilation_fixes"] = fix_suggestions
                        self.log(f"💡 Generated {len(fix_suggestions.get('critical_fixes', []))} critical fix suggestions")
                    else:
                        self.log(f"✅ No compilation errors found!")
                    
                    # Step 2: Run tests and generate test report
                    self.log(f"🧪 Running tests and generating test report...")
                    test_result = self.test_reporter.run_tests(project_dir, language, include_coverage=True)
                    created_files["test_report"] = test_result
                    
                    # Generate HTML test report
                    if test_result.get('success', False):
                        html_report_path = os.path.join(project_dir, "test_report.html")
                        html_report = self.test_reporter.generate_html_report(test_result, html_report_path)
                        created_files["html_test_report"] = html_report
                        self.log(f"📊 Generated HTML test report: {html_report}")
                        
                        # Log test summary
                        summary = test_result.get('summary', {}).get('test_results_summary', {})
                        total_tests = summary.get('total_tests_run', 0)
                        passed_tests = summary.get('passed_tests', 0)
                        success_rate = summary.get('success_rate_percentage', 0)
                        
                        self.log(f"🎯 Test Results: {passed_tests}/{total_tests} tests passed ({success_rate}% success rate)")
                        
                        if summary.get('all_tests_passed', False):
                            self.log(f"🎉 All tests passed successfully!")
                            created_files["test_status"] = "all_passed"
                        else:
                            failed_tests = summary.get('failed_tests', 0)
                            self.log(f"⚠️ {failed_tests} test(s) failed - check test report for details")
                            created_files["test_status"] = "some_failed"
                    else:
                        self.log(f"⚠️ Test execution had issues - check test report for details")
                        created_files["test_status"] = "execution_failed"
                    
                else:
                    self.log(f"⚠️ Build had issues, but project files were created. Check build_result for details.")
                    created_files["build_status"] = "partial"
            else:
                self.log(f"⚠️ Build tools not available for {language}. Project created but not built.")
                created_files["build_status"] = "tools_unavailable"
            
            created_files["final_generated_content"] = generated_content
            
            # Generate comprehensive final report
            final_report = self._generate_comprehensive_report(created_files, language, product_name, project_dir)
            created_files["comprehensive_report"] = final_report
            
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
    
    def _execute_generated_code(self, project_dir: str, language: str, product_name: str, project_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generated code based on language"""
        execution_result = {
            "executed": False,
            "language": language,
            "execution_method": "none",
            "stdout": "",
            "stderr": "",
            "return_code": None,
            "execution_time": 0,
            "error": None
        }
        
        if not project_dir or not os.path.exists(project_dir):
            execution_result["error"] = "Project directory does not exist"
            return execution_result
        
        try:
            self.log(f"🚀 Starting code execution for {language} project: {product_name}")
            start_time = time.time()
            
            # Change to project directory for execution
            original_cwd = os.getcwd()
            os.chdir(project_dir)
            
            try:
                if language.lower() in ['python']:
                    execution_result.update(self._execute_python_code(project_dir, project_files))
                elif language.lower() in ['csharp', 'c#']:
                    execution_result.update(self._execute_csharp_code(project_dir, project_files))
                elif language.lower() in ['javascript', 'js', 'node.js']:
                    execution_result.update(self._execute_javascript_code(project_dir, project_files))
                elif language.lower() == 'java':
                    execution_result.update(self._execute_java_code(project_dir, project_files))
                elif language.lower() == 'go':
                    execution_result.update(self._execute_go_code(project_dir, project_files))
                elif language.lower() == 'rust':
                    execution_result.update(self._execute_rust_code(project_dir, project_files))
                else:
                    execution_result["error"] = f"Code execution not supported for language: {language}"
                    self.log(f"⚠️ Code execution not supported for {language}")
            
            finally:
                os.chdir(original_cwd)
            
            execution_result["execution_time"] = time.time() - start_time
            
            if execution_result.get("executed", False):
                self.log(f"✅ Code execution completed successfully in {execution_result['execution_time']:.2f}s")
                if execution_result.get("stdout"):
                    self.log(f"📤 Output: {execution_result['stdout'][:500]}{'...' if len(execution_result.get('stdout', '')) > 500 else ''}")
            else:
                self.log(f"❌ Code execution failed: {execution_result.get('error', 'Unknown error')}")
                if execution_result.get("stderr"):
                    self.log(f"📥 Error output: {execution_result['stderr'][:500]}{'...' if len(execution_result.get('stderr', '')) > 500 else ''}")
            
        except Exception as e:
            execution_result["error"] = f"Execution failed with exception: {str(e)}"
            self.log(f"❌ Code execution failed with exception: {str(e)}")
        
        return execution_result
    
    def _execute_python_code(self, project_dir: str, project_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code"""
        result = {"execution_method": "python"}
        
        # Look for main Python files to execute
        main_files = []
        for filename in os.listdir(project_dir):
            if filename.endswith('.py') and not filename.startswith('test_'):
                main_files.append(filename)
        
        if not main_files:
            result["error"] = "No Python files found to execute"
            return result
        
        # Try to find main.py or similar entry point
        entry_file = None
        for preferred in ['main.py', 'app.py', 'run.py']:
            if preferred in main_files:
                entry_file = preferred
                break
        
        if not entry_file:
            entry_file = main_files[0]  # Use first available Python file
        
        try:
            # Execute the Python file
            process = subprocess.run(
                ['python', entry_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            result.update({
                "executed": True,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "executed_file": entry_file
            })
            
            if process.returncode == 0:
                self.log(f"✅ Python execution successful: {entry_file}")
            else:
                self.log(f"⚠️ Python execution completed with warnings: {entry_file}")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Python execution timed out after 30 seconds"
        except Exception as e:
            result["error"] = f"Python execution failed: {str(e)}"
        
        return result
    
    def _execute_csharp_code(self, project_dir: str, project_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute C# code"""
        result = {"execution_method": "dotnet run"}
        
        # Check if project was built successfully
        if not project_files.get("build_status") == "success":
            result["error"] = "Project not built successfully, cannot execute"
            return result
        
        try:
            # Execute using dotnet run
            process = subprocess.run(
                ['dotnet', 'run'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result.update({
                "executed": True,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode
            })
            
            if process.returncode == 0:
                self.log(f"✅ C# execution successful")
            else:
                self.log(f"⚠️ C# execution completed with warnings")
            
        except subprocess.TimeoutExpired:
            result["error"] = "C# execution timed out after 30 seconds"
        except Exception as e:
            result["error"] = f"C# execution failed: {str(e)}"
        
        return result
    
    def _execute_javascript_code(self, project_dir: str, project_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JavaScript/Node.js code"""
        result = {"execution_method": "node"}
        
        # Look for main JavaScript files to execute
        main_files = []
        for filename in os.listdir(project_dir):
            if filename.endswith('.js') and not filename.startswith('test'):
                main_files.append(filename)
        
        if not main_files:
            result["error"] = "No JavaScript files found to execute"
            return result
        
        # Try to find main entry point
        entry_file = None
        for preferred in ['index.js', 'main.js', 'app.js', 'server.js']:
            if preferred in main_files:
                entry_file = preferred
                break
        
        if not entry_file:
            entry_file = main_files[0]
        
        try:
            # Execute the JavaScript file
            process = subprocess.run(
                ['node', entry_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result.update({
                "executed": True,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "executed_file": entry_file
            })
            
            if process.returncode == 0:
                self.log(f"✅ JavaScript execution successful: {entry_file}")
            else:
                self.log(f"⚠️ JavaScript execution completed with warnings: {entry_file}")
            
        except subprocess.TimeoutExpired:
            result["error"] = "JavaScript execution timed out after 30 seconds"
        except Exception as e:
            result["error"] = f"JavaScript execution failed: {str(e)}"
        
        return result
    
    def _execute_java_code(self, project_dir: str, project_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Java code"""
        result = {"execution_method": "java"}
        
        # Check if project was built successfully
        if not project_files.get("build_status") == "success":
            result["error"] = "Project not built successfully, cannot execute"
            return result
        
        try:
            # Try to run using maven if pom.xml exists
            if os.path.exists('pom.xml'):
                process = subprocess.run(
                    ['mvn', 'exec:java'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Look for compiled .class files
                class_files = [f for f in os.listdir(project_dir) if f.endswith('.class')]
                if not class_files:
                    result["error"] = "No compiled Java classes found"
                    return result
                
                # Try to execute main class
                main_class = class_files[0].replace('.class', '')
                process = subprocess.run(
                    ['java', main_class],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            result.update({
                "executed": True,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode
            })
            
            if process.returncode == 0:
                self.log(f"✅ Java execution successful")
            else:
                self.log(f"⚠️ Java execution completed with warnings")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Java execution timed out after 30 seconds"
        except Exception as e:
            result["error"] = f"Java execution failed: {str(e)}"
        
        return result
    
    def _execute_go_code(self, project_dir: str, project_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Go code"""
        result = {"execution_method": "go run"}
        
        # Look for main Go files
        main_files = [f for f in os.listdir(project_dir) if f.endswith('.go') and not f.endswith('_test.go')]
        
        if not main_files:
            result["error"] = "No Go files found to execute"
            return result
        
        try:
            # Execute using go run
            process = subprocess.run(
                ['go', 'run'] + main_files,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result.update({
                "executed": True,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "executed_files": main_files
            })
            
            if process.returncode == 0:
                self.log(f"✅ Go execution successful")
            else:
                self.log(f"⚠️ Go execution completed with warnings")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Go execution timed out after 30 seconds"
        except Exception as e:
            result["error"] = f"Go execution failed: {str(e)}"
        
        return result
    
    def _execute_rust_code(self, project_dir: str, project_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Rust code"""
        result = {"execution_method": "cargo run"}
        
        # Check if Cargo.toml exists
        if not os.path.exists('Cargo.toml'):
            result["error"] = "No Cargo.toml found, cannot execute Rust project"
            return result
        
        try:
            # Execute using cargo run
            process = subprocess.run(
                ['cargo', 'run'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result.update({
                "executed": True,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode
            })
            
            if process.returncode == 0:
                self.log(f"✅ Rust execution successful")
            else:
                self.log(f"⚠️ Rust execution completed with warnings")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Rust execution timed out after 30 seconds"
        except Exception as e:
            result["error"] = f"Rust execution failed: {str(e)}"
        
        return result
