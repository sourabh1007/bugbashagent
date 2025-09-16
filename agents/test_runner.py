"""
Test Runner Agent

This agent is responsible for:
1. Running tests on generated code projects
2. Analyzing test results and failures
3. Generating comprehensive reports using LLM analysis
4. Providing actionable insights and fix recommendations

Supports multiple programming languages with language-specific test runners.
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from agents.base_agent import BaseAgent
from tools.prompt_loader.prompty_loader import PromptyLoader
from integrations.azure_openai.client import get_agent_azure_openai_client


class TestRunner(BaseAgent):
    """
    Agent responsible for running tests and generating comprehensive reports
    """
    
    def __init__(self, llm=None):
        llm_instance = llm or get_agent_azure_openai_client("test_runner")
        super().__init__("Test Runner", llm_instance)
        # Initialize prompt loader (best practice manager not required for test execution)
        self.prompty_loader = PromptyLoader()

        # Test execution tools
        self.test_executors = {
            'csharp': self._run_csharp_tests,
            'python': self._run_python_tests,
            'javascript': self._run_javascript_tests,
            'typescript': self._run_typescript_tests,
            'java': self._run_java_tests,
            'go': self._run_go_tests,
            'rust': self._run_rust_tests
        }
    
    def _normalize_language(self, language):
        """Normalize language names to standard format"""
        if not language:
            return "python"  # Default fallback
        
        # Language mappings for common variations
        language_mappings = {
            "c#": "csharp",
            "cs": "csharp", 
            "c-sharp": "csharp",
            "js": "javascript",
            "ts": "typescript",
            "py": "python",
            "go": "go",
            "golang": "go",
            "rs": "rust"
        }
        
        normalized = language.lower().strip()
        return language_mappings.get(normalized, normalized)
        
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Main execution method for the Test Runner Agent
        
        Args:
            input_data: Can be either:
                - Dictionary from CodeGenerator with keys: code_path, language, product_name, etc.
                - String (JSON or plain text) that needs to be parsed
                
        Returns:
            Dictionary containing test results and analysis
        """
        try:
            self.log("🧪 Starting Test Runner Agent...")
            
            # Initial progress update
            self.update_progress(15.0, "Initializing test execution environment")
            
            # Initialize validation issues list to track problems without failing
            validation_issues = []
            
            # Handle different input types with robust error handling
            self.update_progress(20.0, "Parsing input data from code generator")
            
            if isinstance(input_data, dict):
                # Check if this is a full agent result (from workflow) or direct data
                if "agent" in input_data and "output" in input_data and "status" in input_data:
                    # This is a full agent result from the workflow
                    if input_data["status"] != "success":
                        validation_issues.append(f"Previous agent ({input_data.get('agent', 'Unknown')}) failed: {input_data.get('error', 'Unknown error')}")
                        # Continue processing with available data instead of failing
                    
                    # For code generator results, the important data is at the root level, not in "output"
                    # The "output" field contains consolidated content (string), but we need the other fields
                    self.log(f"📥 Received input from agent: {input_data.get('agent', 'Unknown')}")
                    
                    # Extract the data we need from the root level of the code generator result
                    parsed_data = {
                        "project_files": input_data.get("project_files", {}),
                        "language": input_data.get("language", "python"),
                        "product_name": input_data.get("product_name", "Unknown"),
                        "code_path": input_data.get("code_path", ""),
                        "scenario_results": input_data.get("scenario_results", {}),
                        "consolidated_content": input_data.get("output", ""),  # This is the consolidated markdown
                        "compilation_attempts": input_data.get("compilation_attempts", []),
                        "generation_mode": input_data.get("generation_mode", "unknown")
                    }
                else:
                    # This is direct data
                    parsed_data = input_data
            elif isinstance(input_data, str):
                try:
                    parsed_data = json.loads(input_data)
                except json.JSONDecodeError:
                    # If it's not JSON, create a minimal structure for testing
                    self.log("⚠️ Input is not JSON, treating as raw output from CodeGenerator")
                    validation_issues.append("Input is not valid JSON - using fallback parsing")
                    # Extract information from the string if possible
                    parsed_data = {
                        "language": "python",  # Default to python as fallback
                        "product_name": "Unknown",
                        "code_path": "",
                        "scenario_results": {},
                        "raw_output": input_data  # Store the raw input for potential parsing
                    }
            else:
                validation_issues.append(f"Input data must be either a dictionary or string, got {type(input_data)}")
                # Create fallback structure
                parsed_data = {
                    "language": "python",
                    "product_name": "Unknown",
                    "code_path": "",
                    "scenario_results": {},
                    "raw_data": str(input_data)
                }
            
            # Ensure parsed_data is a dictionary before proceeding
            if not isinstance(parsed_data, dict):
                self.log(f"⚠️ Parsed data is not a dictionary, got {type(parsed_data)}. Creating fallback structure.")
                validation_issues.append(f"Parsed data is not a dictionary, got {type(parsed_data)}")
                parsed_data = {
                    "language": "python",
                    "product_name": "Unknown", 
                    "code_path": "",
                    "scenario_results": {},
                    "raw_data": str(parsed_data)
                }
            
            # Extract input parameters with safe defaults and validation
            self.update_progress(25.0, "Extracting project parameters and validating structure")
            
            project_files = parsed_data.get("project_files", {})
            raw_language = parsed_data.get("language", "python")
            product_name = parsed_data.get("product_name", "Unknown")
            code_path = parsed_data.get("code_path", "")
            scenario_results = parsed_data.get("scenario_results", {})
            
            # Normalize language names using the dedicated method
            language = self._normalize_language(raw_language)
            if language != raw_language.lower().strip():
                self.log(f"🔄 Normalized language '{raw_language}' to '{language}'")
            
            # Validate inputs with non-failing approach
            self.update_progress(30.0, f"Validating test environment for {language} project")
            
            if not code_path or not os.path.exists(code_path):
                validation_issues.append(f"Invalid or missing code path: {code_path}")
                # Try to find a suitable code path
                if not code_path:
                    code_path = os.getcwd()
                    self.log(f"⚠️ Using current directory as code path: {code_path}")
                
            if language not in self.test_executors:
                validation_issues.append(f"Unsupported language: {language}")
                # Default to csharp if we detect C# files, otherwise python
                try:
                    if code_path and os.path.exists(code_path):
                        files_in_path = os.listdir(code_path)
                        if any(f.endswith('.cs') for f in files_in_path if os.path.isfile(os.path.join(code_path, f))):
                            language = "csharp"
                            self.log(f"⚠️ Detected C# files, using csharp language")
                        elif any(f.endswith('.py') for f in files_in_path if os.path.isfile(os.path.join(code_path, f))):
                            language = "python"
                            self.log(f"⚠️ Detected Python files, using python language")
                        elif any(f.endswith('.js') for f in files_in_path if os.path.isfile(os.path.join(code_path, f))):
                            language = "javascript"
                            self.log(f"⚠️ Detected JavaScript files, using javascript language")
                        elif any(f.endswith('.ts') for f in files_in_path if os.path.isfile(os.path.join(code_path, f))):
                            language = "typescript"
                            self.log(f"⚠️ Detected TypeScript files, using typescript language")
                        elif any(f.endswith('.java') for f in files_in_path if os.path.isfile(os.path.join(code_path, f))):
                            language = "java"
                            self.log(f"⚠️ Detected Java files, using java language")
                        elif any(f.endswith('.go') for f in files_in_path if os.path.isfile(os.path.join(code_path, f))):
                            language = "go"
                            self.log(f"⚠️ Detected Go files, using go language")
                        elif any(f.endswith('.rs') for f in files_in_path if os.path.isfile(os.path.join(code_path, f))):
                            language = "rust"
                            self.log(f"⚠️ Detected Rust files, using rust language")
                        else:
                            language = "python"
                            self.log(f"⚠️ No specific language files detected, defaulting to python")
                    else:
                        language = "python"
                        self.log(f"⚠️ Code path invalid, defaulting to python")
                except Exception as e:
                    language = "python"
                    self.log(f"⚠️ Error detecting language from files: {e}, defaulting to python")
                    validation_issues.append(f"Language detection error: {e}")
            
            self.log(f"📋 Test execution details:")
            self.log(f"  - Language: {language.upper()}")
            self.log(f"  - Product: {product_name}")
            self.log(f"  - Code Path: {code_path}")
            self.log(f"  - Scenarios: {len(scenario_results.get('successful', []))} successful, {len(scenario_results.get('failed', []))} failed")
            if validation_issues:
                self.log(f"  - Validation Issues: {len(validation_issues)} issues detected")
                for issue in validation_issues:
                    self.log(f"    ⚠️ {issue}")
            
            # Step 1: Discover and analyze test structure (with robust error handling)
            self.update_progress(40.0, "Discovering test files and structure")
            
            try:
                test_discovery = self._discover_tests(code_path, language)
                self.log(f"🔍 Discovered {test_discovery['total_tests']} tests in {test_discovery['test_files_count']} files")
            except Exception as e:
                validation_issues.append(f"Test discovery failed: {str(e)}")
                self.log(f"⚠️ Test discovery failed: {str(e)}")
                test_discovery = {
                    "test_files": [],
                    "test_files_count": 0,
                    "total_tests": 0,
                    "test_structure": {},
                    "test_frameworks": ["unknown"],
                    "discovery_error": str(e)
                }
            
            # Step 2: Execute tests (with robust error handling)
            self.update_progress(60.0, f"Executing {test_discovery.get('total_tests', 0)} tests")
            
            try:
                test_results = self._execute_tests(code_path, language, test_discovery)
            except Exception as e:
                validation_issues.append(f"Test execution failed: {str(e)}")
                self.log(f"⚠️ Test execution failed: {str(e)}")
                test_results = {
                    "success": False,
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "success_rate": 0.0,
                    "execution_time": 0.0,
                    "test_output": f"Test execution failed: {str(e)}",
                    "execution_error": str(e)
                }
            
            # Step 3: Analyze results with LLM (with robust error handling)
            self.update_progress(80.0, "Analyzing test results with LLM")
            
            try:
                test_analysis = self._analyze_test_results_with_llm(
                    test_results, test_discovery, language, product_name, scenario_results
                )
            except Exception as e:
                validation_issues.append(f"LLM analysis failed: {str(e)}")
                self.log(f"⚠️ LLM analysis failed: {str(e)}")
                test_analysis = {
                    "analysis_summary": f"Analysis failed due to error: {str(e)}",
                    "test_quality_assessment": "Unable to assess due to analysis failure",
                    "failed_tests_analysis": [],
                    "recommendations": [
                        f"Address analysis failure: {str(e)}",
                        "Review test setup and configuration",
                        "Check input data validity"
                    ],
                    "scenario_coverage": {},
                    "analysis_error": str(e)
                }
            
            # Step 4: Generate comprehensive report (always succeeds with fallback)
            self.update_progress(90.0, "Generating comprehensive test report")
            
            try:
                comprehensive_report = self._generate_comprehensive_report(
                    test_results, test_analysis, test_discovery, language, product_name, code_path
                )
            except Exception as e:
                validation_issues.append(f"Report generation failed: {str(e)}")
                self.log(f"⚠️ Report generation failed: {str(e)}")
                comprehensive_report = self._generate_fallback_report(
                    test_results, test_analysis, test_discovery, language, product_name, code_path, validation_issues, str(e)
                )
            
            # Step 5: Save results (with error handling)
            self.update_progress(95.0, "Saving test results and reports")
            
            try:
                self._save_test_results(code_path, {
                    "test_results": test_results,
                    "test_analysis": test_analysis,
                    "comprehensive_report": comprehensive_report,
                    "test_discovery": test_discovery,
                    "validation_issues": validation_issues
                })
            except Exception as e:
                self.log(f"⚠️ Failed to save results: {str(e)}")
                validation_issues.append(f"Result saving failed: {str(e)}")
            
            # Always return success with detailed analysis (including failures)
            # This ensures the workflow continues even if tests fail
            overall_status = "success"  # Always success - failures are captured in the report
            
            return {
                "agent": self.name,
                "input": input_data,
                "output": {
                    "test_results": test_results,
                    "test_analysis": test_analysis,
                    "comprehensive_report": comprehensive_report,
                    "test_discovery": test_discovery,
                    "validation_issues": validation_issues
                },
                "status": overall_status,
                "test_execution_path": code_path,
                "language": language,
                "product_name": product_name,
                "validation_issues": validation_issues,
                "execution_summary": {
                    "total_tests": test_results.get("total_tests", 0),
                    "passed_tests": test_results.get("passed_tests", 0),
                    "failed_tests": test_results.get("failed_tests", 0),
                    "success_rate": test_results.get("success_rate", 0.0),
                    "execution_time": test_results.get("execution_time", 0.0),
                    "validation_issues_count": len(validation_issues),
                    "workflow_success": True  # Workflow always succeeds, test failures are analyzed
                }
            }
            
        except Exception as e:
            error_msg = f"Test Runner Agent encountered an error: {str(e)}"
            self.log(f"❌ {error_msg}")
            
            # Even in case of major failure, return a detailed analysis
            return {
                "agent": self.name,
                "input": input_data,
                "output": {
                    "test_results": {
                        "success": False,
                        "total_tests": 0,
                        "passed_tests": 0,
                        "failed_tests": 0,
                        "success_rate": 0.0,
                        "execution_time": 0.0,
                        "test_output": f"Critical failure: {str(e)}",
                        "critical_error": str(e)
                    },
                    "test_analysis": {
                        "analysis_summary": f"Critical failure prevented analysis: {str(e)}",
                        "test_quality_assessment": "Unable to assess due to critical failure",
                        "failed_tests_analysis": [],
                        "recommendations": [
                            f"Address critical failure: {str(e)}",
                            "Review input data structure and validity",
                            "Check test environment setup",
                            "Verify code path and language configuration"
                        ],
                        "scenario_coverage": {},
                        "critical_error": str(e)
                    },
                    "comprehensive_report": f"# Test Runner Critical Failure Report\n\n**Error:** {str(e)}\n\n**Recommendations:**\n- Review input data structure\n- Verify test environment setup\n- Check code path validity\n- Ensure language support is available",
                    "test_discovery": {
                        "test_files": [],
                        "test_files_count": 0,
                        "total_tests": 0,
                        "test_structure": {},
                        "test_frameworks": ["unknown"],
                        "critical_error": str(e)
                    },
                    "validation_issues": [f"Critical failure: {str(e)}"]
                },
                "status": "success",  # Always return success to continue workflow
                "error_details": error_msg,
                "test_execution_path": getattr(locals(), 'code_path', 'unknown'),
                "language": getattr(locals(), 'language', 'unknown'),
                "product_name": getattr(locals(), 'product_name', 'unknown'),
                "validation_issues": [f"Critical failure: {str(e)}"],
                "execution_summary": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "success_rate": 0.0,
                    "execution_time": 0.0,
                    "validation_issues_count": 1,
                    "workflow_success": True,  # Workflow continues despite test failure
                    "critical_failure": True
                }
            }
    
    def _discover_tests(self, code_path: str, language: str) -> Dict[str, Any]:
        """Discover test files and structure in the project"""
        self.log(f"🔍 Discovering tests for {language.upper()} project...")
        
        test_patterns = {
            'csharp': ['*Test.cs', '*Tests.cs', 'Test*.cs'],
            'python': ['test_*.py', '*_test.py', '*_tests.py', 'tests.py'],
            'javascript': ['*.test.js', '*.spec.js', 'test/*.js', 'tests/*.js'],
            'typescript': ['*.test.ts', '*.spec.ts', 'test/*.ts', 'tests/*.ts'],
            'java': ['*Test.java', '*Tests.java', 'Test*.java'],
            'go': ['*_test.go'],
            'rust': ['*_test.rs', 'tests/*.rs']
        }
        
        patterns = test_patterns.get(language, ['*test*'])
        test_files = []
        
        for pattern in patterns:
            for root, dirs, files in os.walk(code_path):
                for file in files:
                    if self._matches_pattern(file, pattern.split('/')[-1]):
                        test_files.append(os.path.join(root, file))
        
        # Analyze test structure
        test_analysis = {
            "test_files": test_files,
            "test_files_count": len(test_files),
            "total_tests": 0,
            "test_structure": {},
            "test_frameworks": self._detect_test_frameworks(code_path, language, test_files)
        }
        
        # Count individual tests
        for test_file in test_files:
            test_count = self._count_tests_in_file(test_file, language)
            test_analysis["total_tests"] += test_count
            test_analysis["test_structure"][test_file] = {
                "test_count": test_count,
                "relative_path": os.path.relpath(test_file, code_path)
            }
        
        return test_analysis
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the given pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _count_tests_in_file(self, test_file: str, language: str) -> int:
        """Count the number of test methods/functions in a test file"""
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            test_patterns = {
                'csharp': [r'\[Test\]', r'\[Fact\]', r'\[Theory\]'],
                'python': [r'def test_', r'async def test_'],
                'javascript': [r'test\(', r'it\(', r'describe\('],
                'typescript': [r'test\(', r'it\(', r'describe\('],
                'java': [r'@Test'],
                'go': [r'func Test'],
                'rust': [r'#\[test\]']
            }
            
            import re
            count = 0
            patterns = test_patterns.get(language, [])
            
            for pattern in patterns:
                count += len(re.findall(pattern, content, re.IGNORECASE))
            
            return count
            
        except Exception as e:
            self.log(f"⚠️ Error counting tests in {test_file}: {str(e)}")
            return 0
    
    def _detect_test_frameworks(self, code_path: str, language: str, test_files: List[str]) -> List[str]:
        """Detect which test frameworks are being used"""
        frameworks = []
        
        framework_indicators = {
            'csharp': {
                'NUnit': ['using NUnit', '[Test]', '[TestFixture]'],
                'xUnit': ['using Xunit', '[Fact]', '[Theory]'],
                'MSTest': ['using Microsoft.VisualStudio.TestTools', '[TestMethod]']
            },
            'python': {
                'pytest': ['import pytest', 'def test_', 'pytest.mark'],
                'unittest': ['import unittest', 'class.*TestCase', 'def test_'],
                'nose': ['import nose', 'from nose']
            },
            'javascript': {
                'Jest': ['jest', 'describe(', 'test(', 'expect('],
                'Mocha': ['mocha', 'describe(', 'it('],
                'Jasmine': ['jasmine', 'describe(', 'it(', 'expect(']
            },
            'typescript': {
                'Jest': ['jest', 'describe(', 'test(', 'expect('],
                'Mocha': ['mocha', 'describe(', 'it('],
                'Jasmine': ['jasmine', 'describe(', 'it(', 'expect(']
            },
            'java': {
                'JUnit': ['import org.junit', '@Test'],
                'TestNG': ['import org.testng', '@Test']
            },
            'go': {
                'testing': ['import "testing"', 'func Test'],
                'testify': ['github.com/stretchr/testify']
            },
            'rust': {
                'built-in': ['#[test]', '#[cfg(test)]']
            }
        }
        
        if language in framework_indicators:
            # Check project files for framework indicators
            all_files = test_files + self._get_source_files(code_path, language)
            
            for framework_name, indicators in framework_indicators[language].items():
                framework_found = False
                
                for file_path in all_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        import re
                        for indicator in indicators:
                            if re.search(indicator, content, re.IGNORECASE):
                                framework_found = True
                                break
                        
                        if framework_found:
                            break
                            
                    except Exception:
                        continue
                
                if framework_found:
                    frameworks.append(framework_name)
        
        return frameworks if frameworks else ['unknown']
    
    def _get_source_files(self, code_path: str, language: str) -> List[str]:
        """Get source files for framework detection"""
        extensions = {
            'csharp': ['.cs'],
            'python': ['.py'],
            'javascript': ['.js'],
            'typescript': ['.ts'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs']
        }
        
        exts = extensions.get(language, [])
        source_files = []
        
        for root, dirs, files in os.walk(code_path):
            for file in files:
                if any(file.endswith(ext) for ext in exts):
                    source_files.append(os.path.join(root, file))
        
        return source_files[:10]  # Limit to first 10 files for performance
    
    def _execute_tests(self, code_path: str, language: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tests using the appropriate test runner for the language"""
        self.log(f"🏃 Executing {language.upper()} tests...")
        
        start_time = time.time()
        
        try:
            # Execute tests using language-specific runner
            executor = self.test_executors[language]
            test_results = executor(code_path, test_discovery)
            
            execution_time = time.time() - start_time
            test_results["execution_time"] = execution_time
            
            # Calculate success rate
            total_tests = test_results.get("total_tests", 0)
            passed_tests = test_results.get("passed_tests", 0)
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            test_results["success_rate"] = success_rate
            
            self.log(f"📊 Test execution completed in {execution_time:.2f}s")
            self.log(f"  ✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
            
            return test_results
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {
                "success": False,
                "total_tests": test_discovery.get("total_tests", 0),
                "passed_tests": 0,
                "failed_tests": test_discovery.get("total_tests", 0),
                "execution_time": execution_time,
                "success_rate": 0.0,
                "error": str(e),
                "detailed_results": [],
                "output": "",
                "framework_output": ""
            }
            
            self.log(f"❌ Test execution failed: {str(e)}")
            return error_result
    
    # Language-specific test execution methods
    
    def _run_csharp_tests(self, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Run C# tests using dotnet test"""
        self.log("🔧 Running C# tests with dotnet test...")
        
        try:
            # Check if this is a dotnet project
            csproj_files = list(Path(code_path).rglob("*.csproj"))
            if not csproj_files:
                return self._create_no_tests_result("No .csproj files found")
            
            # Run dotnet test with detailed output
            cmd = ["dotnet", "test", "--logger", "trx", "--results-directory", os.path.join(code_path, "TestResults")]
            result = subprocess.run(cmd, cwd=code_path, capture_output=True, text=True, timeout=300)
            
            return self._parse_dotnet_test_results(result, code_path, test_discovery)
            
        except subprocess.TimeoutExpired:
            return self._create_error_result("Test execution timed out after 5 minutes")
        except Exception as e:
            return self._create_error_result(f"C# test execution failed: {str(e)}")
    
    def _run_python_tests(self, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Run Python tests using pytest or unittest"""
        self.log("🐍 Running Python tests...")
        
        try:
            frameworks = test_discovery.get("test_frameworks", [])
            
            # Try pytest first (more detailed output)
            if "pytest" in frameworks or "pytest" in str(frameworks).lower():
                cmd = ["python", "-m", "pytest", "-v", "--tb=short", "--json-report", "--json-report-file=test_results.json"]
            else:
                # Fallback to unittest
                cmd = ["python", "-m", "unittest", "discover", "-v"]
            
            result = subprocess.run(cmd, cwd=code_path, capture_output=True, text=True, timeout=300)
            
            return self._parse_python_test_results(result, code_path, test_discovery)
            
        except subprocess.TimeoutExpired:
            return self._create_error_result("Test execution timed out after 5 minutes")
        except Exception as e:
            return self._create_error_result(f"Python test execution failed: {str(e)}")
    
    def _run_javascript_tests(self, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Run JavaScript tests using npm test or yarn test"""
        self.log("📜 Running JavaScript tests...")
        
        try:
            # Check for package.json
            package_json = os.path.join(code_path, "package.json")
            if not os.path.exists(package_json):
                return self._create_no_tests_result("No package.json found")
            
            # Try npm test first, then yarn test
            commands = [
                ["npm", "test"],
                ["yarn", "test"]
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, cwd=code_path, capture_output=True, text=True, timeout=300)
                    return self._parse_javascript_test_results(result, code_path, test_discovery)
                except FileNotFoundError:
                    continue
            
            return self._create_error_result("Neither npm nor yarn found")
            
        except subprocess.TimeoutExpired:
            return self._create_error_result("Test execution timed out after 5 minutes")
        except Exception as e:
            return self._create_error_result(f"JavaScript test execution failed: {str(e)}")
    
    def _run_typescript_tests(self, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Run TypeScript tests"""
        self.log("📘 Running TypeScript tests...")
        
        try:
            # Check for package.json and tsconfig.json
            package_json = os.path.join(code_path, "package.json")
            tsconfig = os.path.join(code_path, "tsconfig.json")
            
            if not os.path.exists(package_json):
                return self._create_no_tests_result("No package.json found")
            
            # Try different TypeScript test commands
            commands = [
                ["npm", "run", "test"],
                ["yarn", "test"],
                ["npx", "jest"],
                ["npx", "mocha", "dist/**/*.test.js"]
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, cwd=code_path, capture_output=True, text=True, timeout=300)
                    if result.returncode == 0 or "test" in result.stdout.lower():
                        return self._parse_typescript_test_results(result, code_path, test_discovery)
                except FileNotFoundError:
                    continue
            
            return self._create_error_result("No suitable TypeScript test runner found")
            
        except subprocess.TimeoutExpired:
            return self._create_error_result("Test execution timed out after 5 minutes")
        except Exception as e:
            return self._create_error_result(f"TypeScript test execution failed: {str(e)}")
    
    def _run_java_tests(self, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Run Java tests using Maven or Gradle"""
        self.log("☕ Running Java tests...")
        
        try:
            # Check for build files
            maven_file = os.path.join(code_path, "pom.xml")
            gradle_file = os.path.join(code_path, "build.gradle")
            
            if os.path.exists(maven_file):
                cmd = ["mvn", "test"]
            elif os.path.exists(gradle_file):
                cmd = ["gradle", "test"]
            else:
                return self._create_no_tests_result("No Maven (pom.xml) or Gradle (build.gradle) build file found")
            
            result = subprocess.run(cmd, cwd=code_path, capture_output=True, text=True, timeout=600)
            
            return self._parse_java_test_results(result, code_path, test_discovery)
            
        except subprocess.TimeoutExpired:
            return self._create_error_result("Test execution timed out after 10 minutes")
        except Exception as e:
            return self._create_error_result(f"Java test execution failed: {str(e)}")
    
    def _run_go_tests(self, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Run Go tests using go test"""
        self.log("🐹 Running Go tests...")
        
        try:
            # Check for go.mod
            go_mod = os.path.join(code_path, "go.mod")
            if not os.path.exists(go_mod):
                return self._create_no_tests_result("No go.mod found")
            
            cmd = ["go", "test", "-v", "./..."]
            result = subprocess.run(cmd, cwd=code_path, capture_output=True, text=True, timeout=300)
            
            return self._parse_go_test_results(result, code_path, test_discovery)
            
        except subprocess.TimeoutExpired:
            return self._create_error_result("Test execution timed out after 5 minutes")
        except Exception as e:
            return self._create_error_result(f"Go test execution failed: {str(e)}")
    
    def _run_rust_tests(self, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Run Rust tests using cargo test"""
        self.log("🦀 Running Rust tests...")
        
        try:
            # Check for Cargo.toml
            cargo_toml = os.path.join(code_path, "Cargo.toml")
            if not os.path.exists(cargo_toml):
                return self._create_no_tests_result("No Cargo.toml found")
            
            cmd = ["cargo", "test", "--", "--nocapture"]
            result = subprocess.run(cmd, cwd=code_path, capture_output=True, text=True, timeout=300)
            
            return self._parse_rust_test_results(result, code_path, test_discovery)
            
        except subprocess.TimeoutExpired:
            return self._create_error_result("Test execution timed out after 5 minutes")
        except Exception as e:
            return self._create_error_result(f"Rust test execution failed: {str(e)}")
    
    # Result parsing methods
    
    def _create_no_tests_result(self, reason: str) -> Dict[str, Any]:
        """Create a result for when no tests are found or can be run"""
        return {
            "success": True,  # No tests is not a failure
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "detailed_results": [],
            "output": f"No tests to run: {reason}",
            "framework_output": "",
            "reason": reason
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create an error result"""
        return {
            "success": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "detailed_results": [],
            "output": error_message,
            "framework_output": "",
            "error": error_message
        }
    
    def _parse_dotnet_test_results(self, result: subprocess.CompletedProcess, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Parse dotnet test results"""
        output = result.stdout + result.stderr
        
        # Parse test results from output
        import re
        
        # Look for test result summary
        passed_match = re.search(r'Passed:\s*(\d+)', output)
        failed_match = re.search(r'Failed:\s*(\d+)', output)
        skipped_match = re.search(r'Skipped:\s*(\d+)', output)
        
        passed_tests = int(passed_match.group(1)) if passed_match else 0
        failed_tests = int(failed_match.group(1)) if failed_match else 0
        skipped_tests = int(skipped_match.group(1)) if skipped_match else 0
        total_tests = passed_tests + failed_tests + skipped_tests
        
        # Extract individual test results
        detailed_results = self._extract_dotnet_test_details(output)
        
        return {
            "success": result.returncode == 0 and failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "detailed_results": detailed_results,
            "output": output,
            "framework_output": output,
            "return_code": result.returncode
        }
    
    def _parse_python_test_results(self, result: subprocess.CompletedProcess, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Python test results"""
        output = result.stdout + result.stderr
        
        # Try to parse pytest JSON report first
        json_report_path = os.path.join(code_path, "test_results.json")
        if os.path.exists(json_report_path):
            try:
                with open(json_report_path, 'r') as f:
                    json_data = json.load(f)
                return self._parse_pytest_json_results(json_data, output)
            except Exception:
                pass
        
        # Fallback to parsing text output
        import re
        
        # Pytest pattern
        pytest_match = re.search(r'(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?', output)
        if pytest_match:
            passed_tests = int(pytest_match.group(1))
            failed_tests = int(pytest_match.group(2)) if pytest_match.group(2) else 0
            skipped_tests = int(pytest_match.group(3)) if pytest_match.group(3) else 0
        else:
            # Unittest pattern
            unittest_match = re.search(r'Ran (\d+) tests.*\n.*(?:OK|FAILED)', output)
            total_tests = int(unittest_match.group(1)) if unittest_match else 0
            failed_tests = len(re.findall(r'FAIL:', output))
            passed_tests = total_tests - failed_tests
            skipped_tests = len(re.findall(r'SKIP:', output))
        
        total_tests = passed_tests + failed_tests + skipped_tests
        detailed_results = self._extract_python_test_details(output)
        
        return {
            "success": result.returncode == 0 and failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "detailed_results": detailed_results,
            "output": output,
            "framework_output": output,
            "return_code": result.returncode
        }
    
    def _parse_javascript_test_results(self, result: subprocess.CompletedProcess, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JavaScript test results"""
        output = result.stdout + result.stderr
        
        import re
        
        # Jest pattern
        jest_match = re.search(r'Tests:\s*(\d+) failed(?:, (\d+) passed)?|Tests:\s*(\d+) passed', output)
        if jest_match:
            if jest_match.group(1):  # Failed tests found
                failed_tests = int(jest_match.group(1))
                passed_tests = int(jest_match.group(2)) if jest_match.group(2) else 0
            else:  # Only passed tests
                failed_tests = 0
                passed_tests = int(jest_match.group(3))
        else:
            # Mocha/Jasmine pattern
            passed_match = re.search(r'(\d+) passing', output)
            failed_match = re.search(r'(\d+) failing', output)
            
            passed_tests = int(passed_match.group(1)) if passed_match else 0
            failed_tests = int(failed_match.group(1)) if failed_match else 0
        
        total_tests = passed_tests + failed_tests
        detailed_results = self._extract_javascript_test_details(output)
        
        return {
            "success": result.returncode == 0 and failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": 0,  # JS frameworks don't typically report skipped
            "detailed_results": detailed_results,
            "output": output,
            "framework_output": output,
            "return_code": result.returncode
        }
    
    def _parse_typescript_test_results(self, result: subprocess.CompletedProcess, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Parse TypeScript test results (similar to JavaScript)"""
        return self._parse_javascript_test_results(result, code_path, test_discovery)
    
    def _parse_java_test_results(self, result: subprocess.CompletedProcess, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Java test results"""
        output = result.stdout + result.stderr
        
        import re
        
        # Maven Surefire pattern
        maven_match = re.search(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', output)
        if maven_match:
            total_tests = int(maven_match.group(1))
            failures = int(maven_match.group(2))
            errors = int(maven_match.group(3))
            skipped_tests = int(maven_match.group(4))
            failed_tests = failures + errors
            passed_tests = total_tests - failed_tests - skipped_tests
        else:
            # Gradle pattern
            gradle_match = re.search(r'(\d+) tests completed(?:, (\d+) failed)?', output)
            total_tests = int(gradle_match.group(1)) if gradle_match else 0
            failed_tests = int(gradle_match.group(2)) if gradle_match and gradle_match.group(2) else 0
            passed_tests = total_tests - failed_tests
            skipped_tests = 0
        
        detailed_results = self._extract_java_test_details(output)
        
        return {
            "success": result.returncode == 0 and failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "detailed_results": detailed_results,
            "output": output,
            "framework_output": output,
            "return_code": result.returncode
        }
    
    def _parse_go_test_results(self, result: subprocess.CompletedProcess, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Go test results"""
        output = result.stdout + result.stderr
        
        import re
        
        # Count PASS and FAIL lines
        passed_tests = len(re.findall(r'--- PASS:', output))
        failed_tests = len(re.findall(r'--- FAIL:', output))
        total_tests = passed_tests + failed_tests
        
        detailed_results = self._extract_go_test_details(output)
        
        return {
            "success": result.returncode == 0 and failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": 0,
            "detailed_results": detailed_results,
            "output": output,
            "framework_output": output,
            "return_code": result.returncode
        }
    
    def _parse_rust_test_results(self, result: subprocess.CompletedProcess, code_path: str, test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Rust test results"""
        output = result.stdout + result.stderr
        
        import re
        
        # Rust test summary pattern
        summary_match = re.search(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored', output)
        if summary_match:
            passed_tests = int(summary_match.group(2))
            failed_tests = int(summary_match.group(3))
            skipped_tests = int(summary_match.group(4))
            total_tests = passed_tests + failed_tests + skipped_tests
        else:
            passed_tests = len(re.findall(r'test .* \.\.\. ok', output))
            failed_tests = len(re.findall(r'test .* \.\.\. FAILED', output))
            skipped_tests = len(re.findall(r'test .* \.\.\. ignored', output))
            total_tests = passed_tests + failed_tests + skipped_tests
        
        detailed_results = self._extract_rust_test_details(output)
        
        return {
            "success": result.returncode == 0 and failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "detailed_results": detailed_results,
            "output": output,
            "framework_output": output,
            "return_code": result.returncode
        }

    def _extract_dotnet_test_details(self, output: str) -> List[Dict[str, Any]]:
        """Extract individual test details from .NET test output"""
        details = []
        import re
        
        # Extract failed test details
        failed_pattern = r'Failed\s+(.+?)\s*\[(\d+)\s*ms\]'
        for match in re.finditer(failed_pattern, output):
            details.append({
                "name": match.group(1).strip(),
                "status": "failed",
                "duration": f"{match.group(2)}ms",
                "error": self._extract_error_from_output(output, match.group(1))
            })
        
        return details

    def _extract_python_test_details(self, output: str) -> List[Dict[str, Any]]:
        """Extract individual test details from Python test output"""
        details = []
        import re
        
        # Extract pytest details
        pytest_pattern = r'(.+?)::.+? (PASSED|FAILED|SKIPPED)'
        for match in re.finditer(pytest_pattern, output):
            details.append({
                "name": match.group(1),
                "status": match.group(2).lower(),
                "error": self._extract_error_from_output(output, match.group(1)) if match.group(2) == "FAILED" else None
            })
        
        return details

    def _extract_javascript_test_details(self, output: str) -> List[Dict[str, Any]]:
        """Extract individual test details from JavaScript test output"""
        details = []
        import re
        
        # Extract Jest/Mocha test details
        test_pattern = r'✓|✗\s+(.+?)(?:\s+\((\d+ms)\))?'
        for match in re.finditer(test_pattern, output):
            status = "passed" if "✓" in match.group(0) else "failed"
            details.append({
                "name": match.group(1).strip(),
                "status": status,
                "duration": match.group(2) if match.group(2) else None,
                "error": self._extract_error_from_output(output, match.group(1)) if status == "failed" else None
            })
        
        return details

    def _extract_java_test_details(self, output: str) -> List[Dict[str, Any]]:
        """Extract individual test details from Java test output"""
        details = []
        import re
        
        # Extract Maven/Gradle test details
        test_pattern = r'([\w\.]+)\s+Time elapsed:\s+([\d\.]+)\s+sec\s+<<<\s+(FAILURE|ERROR)?'
        for match in re.finditer(test_pattern, output):
            status = "failed" if match.group(3) else "passed"
            details.append({
                "name": match.group(1),
                "status": status,
                "duration": f"{match.group(2)}s",
                "error": self._extract_error_from_output(output, match.group(1)) if status == "failed" else None
            })
        
        return details

    def _extract_go_test_details(self, output: str) -> List[Dict[str, Any]]:
        """Extract individual test details from Go test output"""
        details = []
        import re
        
        # Extract Go test details
        test_pattern = r'--- (PASS|FAIL):\s+(\w+)\s+\(([\d\.]+s)\)'
        for match in re.finditer(test_pattern, output):
            status = match.group(1).lower()
            details.append({
                "name": match.group(2),
                "status": "passed" if status == "pass" else "failed",
                "duration": match.group(3),
                "error": self._extract_error_from_output(output, match.group(2)) if status == "fail" else None
            })
        
        return details

    def _extract_rust_test_details(self, output: str) -> List[Dict[str, Any]]:
        """Extract individual test details from Rust test output"""
        details = []
        import re
        
        # Extract Rust test details
        test_pattern = r'test (.+?) \.\.\. (ok|FAILED|ignored)'
        for match in re.finditer(test_pattern, output):
            status_map = {"ok": "passed", "FAILED": "failed", "ignored": "skipped"}
            status = status_map.get(match.group(2), "unknown")
            details.append({
                "name": match.group(1),
                "status": status,
                "error": self._extract_error_from_output(output, match.group(1)) if status == "failed" else None
            })
        
        return details

    def _extract_error_from_output(self, output: str, test_name: str) -> Optional[str]:
        """Extract error message for a specific test from output"""
        try:
            lines = output.split('\n')
            error_lines = []
            capturing = False
            
            for line in lines:
                if test_name in line and any(keyword in line.lower() for keyword in ['fail', 'error', 'exception']):
                    capturing = True
                    continue
                
                if capturing:
                    if line.strip() and not line.startswith(' '):
                        break
                    error_lines.append(line)
            
            return '\n'.join(error_lines).strip() if error_lines else None
            
        except Exception:
            return None

    def _analyze_test_results_with_llm(self, test_results: Dict[str, Any], test_discovery: Dict[str, Any], 
                                     language: str, product_name: str, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results using LLM to provide insights and recommendations
        
        THIS IS WHERE test_analysis.prompty IS USED - through the prompty_loader.create_prompt_template call
        """
        self.log("🤖 Analyzing test results with LLM...")
        
        try:
            # Create prompt template for test analysis - THIS IS WHERE test_analysis.prompty IS USED
            prompt_template = self.prompty_loader.create_prompt_template(
                "test_runner", "test_analysis"
            )
            
            if not prompt_template:
                self.log("⚠️ No test analysis prompt template found, using default analysis")
                return self._create_default_analysis(test_results, test_discovery, language)
            
            # Get LLM with prompty-specific settings
            llm_for_chain = self.prompty_loader.create_llm_with_prompty_settings(
                self.llm, "test_runner", "test_analysis"
            )
            
            from langchain_core.output_parsers import StrOutputParser
            chain = prompt_template | llm_for_chain | StrOutputParser()
            
            # Generate scenario-based analysis data for product quality focus
            scenario_analysis = self._generate_scenario_analysis(test_results, scenario_results, test_discovery)
            failed_tests_summary = self._summarize_failed_scenarios(test_results, scenario_results)
            test_coverage_analysis = self._analyze_scenario_coverage(test_discovery, scenario_results)
            
            prompt_vars = {
                "language": language.upper(),
                "product_name": product_name,
                "total_tests": test_results.get("total_tests", 0),
                "passed_tests": test_results.get("passed_tests", 0),
                "failed_tests": test_results.get("failed_tests", 0),
                "success_rate": test_results.get("success_rate", 0),
                "execution_time": test_results.get("execution_time", 0),
                "test_frameworks": ', '.join(test_discovery.get("test_frameworks", ["unknown"])),
                # Scenario-based variables for product quality analysis
                "scenario_count": scenario_analysis["total_scenarios"],
                "scenarios_passed": scenario_analysis["scenarios_passed"],
                "scenarios_failed": scenario_analysis["scenarios_failed"],
                "scenario_success_rate": scenario_analysis["scenario_success_rate"],
                "failed_scenarios_details": scenario_analysis["failed_scenarios_details"],
                "failed_tests_summary": failed_tests_summary,
                "test_coverage_analysis": test_coverage_analysis,
                "test_output": test_results.get("output", "")[:2000],  # Limit output size
                "overall_success": scenario_analysis["product_quality_acceptable"]
            }
            
            # Generate analysis
            analysis_result = chain.invoke(prompt_vars)
            
            return {
                "llm_analysis": analysis_result,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_model": "Azure OpenAI",
                "key_insights": self._extract_key_insights(analysis_result),
                "recommendations": self._extract_recommendations(analysis_result),
                "failure_analysis": self._create_failure_analysis(test_results),
                "test_quality_score": self._calculate_test_quality_score(test_results, test_discovery)
            }
            
        except Exception as e:
            self.log(f"⚠️ LLM analysis failed: {str(e)}, using default analysis")
            return self._create_default_analysis(test_results, test_discovery, language)

    def _generate_scenario_analysis(self, test_results: Dict[str, Any], scenario_results: Dict[str, Any], test_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scenario-based analysis for product quality assessment."""
        detailed_results = test_results.get("detailed_results", [])
        
        # Map test results to business scenarios
        scenarios = self._map_tests_to_scenarios(detailed_results, scenario_results)
        
        total_scenarios = len(scenarios)
        scenarios_passed = sum(1 for scenario in scenarios.values() if scenario["passed"])
        scenarios_failed = total_scenarios - scenarios_passed
        scenario_success_rate = (scenarios_passed / total_scenarios * 100) if total_scenarios > 0 else 0
        
        # Generate detailed analysis of failed scenarios
        failed_scenarios_details = self._analyze_failed_scenarios(scenarios)
        
        # Determine product quality acceptability
        product_quality_acceptable = scenario_success_rate >= 80  # 80% scenario success threshold
        
        return {
            "total_scenarios": total_scenarios,
            "scenarios_passed": scenarios_passed,
            "scenarios_failed": scenarios_failed,
            "scenario_success_rate": round(scenario_success_rate, 2),
            "failed_scenarios_details": failed_scenarios_details,
            "product_quality_acceptable": product_quality_acceptable,
            "scenarios": scenarios
        }
    
    def _map_tests_to_scenarios(self, detailed_results: List[Dict[str, Any]], scenario_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Map individual test results to business scenarios."""
        scenarios = {}
        
        # Group tests by scenario (based on test name patterns or modules)
        for test in detailed_results:
            test_name = test.get("name", "Unknown Test")
            scenario_name = self._extract_scenario_from_test_name(test_name)
            
            if scenario_name not in scenarios:
                scenarios[scenario_name] = {
                    "name": scenario_name,
                    "tests": [],
                    "passed": True,
                    "critical_failures": [],
                    "business_impact": "Low"
                }
            
            scenarios[scenario_name]["tests"].append(test)
            
            # If any test in scenario fails, scenario fails
            if test.get("status") == "failed":
                scenarios[scenario_name]["passed"] = False
                scenarios[scenario_name]["critical_failures"].append({
                    "test": test_name,
                    "error": test.get("error", "No error available"),
                    "business_impact": self._assess_business_impact(test_name, test.get("error", ""))
                })
        
        # Update business impact based on failures
        for scenario in scenarios.values():
            if scenario["critical_failures"]:
                impact_levels = [f["business_impact"] for f in scenario["critical_failures"]]
                if "Critical" in impact_levels:
                    scenario["business_impact"] = "Critical"
                elif "High" in impact_levels:
                    scenario["business_impact"] = "High"
                else:
                    scenario["business_impact"] = "Medium"
        
        return scenarios
    
    def _extract_scenario_from_test_name(self, test_name: str) -> str:
        """Extract business scenario name from test name."""
        # Common patterns for scenario extraction
        test_name_lower = test_name.lower()
        
        if "login" in test_name_lower or "auth" in test_name_lower:
            return "User Authentication"
        elif "payment" in test_name_lower or "checkout" in test_name_lower:
            return "Payment Processing"
        elif "search" in test_name_lower:
            return "Search Functionality"
        elif "profile" in test_name_lower or "account" in test_name_lower:
            return "User Profile Management"
        elif "api" in test_name_lower:
            return "API Integration"
        elif "database" in test_name_lower or "db" in test_name_lower:
            return "Data Management"
        elif "security" in test_name_lower:
            return "Security Features"
        elif "performance" in test_name_lower:
            return "Performance & Scalability"
        elif "ui" in test_name_lower or "interface" in test_name_lower:
            return "User Interface"
        else:
            # Extract from module or class name
            parts = test_name.split("::")
            if len(parts) > 1:
                return parts[0].replace("_", " ").title()
            return "Core Functionality"
    
    def _assess_business_impact(self, test_name: str, error: str) -> str:
        """Assess business impact of a test failure."""
        test_name_lower = test_name.lower()
        error_lower = error.lower()
        
        # Critical impact keywords
        critical_keywords = ["payment", "security", "login", "auth", "crash", "exception", "timeout"]
        if any(keyword in test_name_lower or keyword in error_lower for keyword in critical_keywords):
            return "Critical"
        
        # High impact keywords  
        high_keywords = ["api", "database", "integration", "checkout", "profile"]
        if any(keyword in test_name_lower or keyword in error_lower for keyword in high_keywords):
            return "High"
        
        # Default to medium impact
        return "Medium"
    
    def _analyze_failed_scenarios(self, scenarios: Dict[str, Dict[str, Any]]) -> str:
        """Generate detailed analysis of failed scenarios."""
        failed_scenarios = [s for s in scenarios.values() if not s["passed"]]
        
        if not failed_scenarios:
            return "No failed scenarios detected. All business scenarios are functioning correctly."
        
        analysis_parts = []
        
        # Group by business impact
        critical_scenarios = [s for s in failed_scenarios if s["business_impact"] == "Critical"]
        high_impact_scenarios = [s for s in failed_scenarios if s["business_impact"] == "High"] 
        medium_impact_scenarios = [s for s in failed_scenarios if s["business_impact"] == "Medium"]
        
        if critical_scenarios:
            analysis_parts.append("🚨 CRITICAL BUSINESS SCENARIOS FAILING:")
            for scenario in critical_scenarios:
                analysis_parts.append(f"• {scenario['name']}: {len(scenario['critical_failures'])} critical issues")
                for failure in scenario['critical_failures'][:2]:  # Top 2 failures
                    analysis_parts.append(f"  - {failure['test']}: {failure['error'][:100]}...")
        
        if high_impact_scenarios:
            analysis_parts.append("\n⚠️ HIGH IMPACT SCENARIOS:")
            for scenario in high_impact_scenarios:
                analysis_parts.append(f"• {scenario['name']}: {len(scenario['critical_failures'])} issues")
        
        if medium_impact_scenarios:
            analysis_parts.append(f"\n📋 {len(medium_impact_scenarios)} medium impact scenarios also affected")
        
        return "\n".join(analysis_parts)
    
    def _summarize_failed_scenarios(self, test_results: Dict[str, Any], scenario_results: Dict[str, Any]) -> str:
        """Summarize failed scenarios for prompt context (scenario-focused version)."""
        detailed_results = test_results.get("detailed_results", [])
        failed_tests = [result for result in detailed_results if result.get("status") == "failed"]
        
        if not failed_tests:
            return "No failed scenarios to summarize."
        
        # Group failures by scenario
        scenario_failures = {}
        for test in failed_tests:
            scenario = self._extract_scenario_from_test_name(test.get("name", "Unknown"))
            if scenario not in scenario_failures:
                scenario_failures[scenario] = []
            scenario_failures[scenario].append(test)
        
        summary_parts = []
        for scenario, failures in list(scenario_failures.items())[:5]:  # Top 5 scenarios
            summary_parts.append(f"• {scenario}: {len(failures)} failures")
            if failures:
                error = failures[0].get("error", "No error available")
                clean_error = error.replace('\n', ' ').replace('\r', '')[:150]
                summary_parts.append(f"  Sample: {clean_error}...")
        
        return "\n".join(summary_parts)

    def _analyze_scenario_coverage(self, test_discovery: Dict[str, Any], scenario_results: Dict[str, Any]) -> str:
        """Analyze scenario coverage for product quality assessment."""
        analysis = []
        
        total_test_files = test_discovery.get("total_test_files", 0)
        test_frameworks = test_discovery.get("test_frameworks", [])
        successful_scenarios = len(scenario_results.get("successful", []))
        
        analysis.append(f"Scenario Coverage Analysis:")
        analysis.append(f"- Test files discovered: {total_test_files}")
        analysis.append(f"- Test frameworks detected: {', '.join(test_frameworks) if test_frameworks else 'None'}")
        analysis.append(f"- Business scenarios covered: {successful_scenarios}")
        
        if total_test_files == 0:
            analysis.append("- Coverage Risk: No test files found - product quality cannot be verified")
        elif successful_scenarios > 0:
            ratio = total_test_files / successful_scenarios
            if ratio < 0.5:
                analysis.append("- Coverage Risk: Insufficient tests per business scenario")
            elif ratio > 2:
                analysis.append("- Coverage Strength: Comprehensive testing per business scenario")
            else:
                analysis.append("- Coverage Status: Adequate testing per business scenario")
        
        return "\n".join(analysis)

    def _summarize_failed_tests(self, detailed_results: List[Dict[str, Any]]) -> str:
        """Create a summary of failed tests for LLM analysis"""
        failed_tests = [test for test in detailed_results if test.get("status") == "failed"]
        
        if not failed_tests:
            return "No test failures detected."
        
        summary = f"Failed Tests Summary ({len(failed_tests)} failures):\n"
        for i, test in enumerate(failed_tests[:10], 1):  # Limit to first 10 failures
            summary += f"{i}. {test.get('name', 'Unknown Test')}\n"
            if test.get('error'):
                summary += f"   Error: {test['error'][:200]}...\n"  # Truncate long errors
            summary += "\n"
        
        if len(failed_tests) > 10:
            summary += f"... and {len(failed_tests) - 10} more failures\n"
        
        return summary

    def _analyze_test_coverage(self, test_discovery: Dict[str, Any], scenario_results: Dict[str, Any]) -> str:
        """Analyze test coverage and relationship to generated scenarios"""
        analysis = []
        
        total_test_files = test_discovery.get("total_test_files", 0)
        test_frameworks = test_discovery.get("test_frameworks", [])
        successful_scenarios = len(scenario_results.get("successful", []))
        
        analysis.append(f"Test Coverage Analysis:")
        analysis.append(f"- Test files discovered: {total_test_files}")
        analysis.append(f"- Test frameworks detected: {', '.join(test_frameworks) if test_frameworks else 'None'}")
        analysis.append(f"- Generated scenarios: {successful_scenarios}")
        
        if total_test_files == 0:
            analysis.append("- Coverage concern: No test files found")
        elif successful_scenarios > 0:
            ratio = total_test_files / successful_scenarios
            if ratio < 0.5:
                analysis.append("- Coverage concern: Low test file to scenario ratio")
            elif ratio > 2:
                analysis.append("- Coverage strength: High test file to scenario ratio")
            else:
                analysis.append("- Coverage balance: Moderate test file to scenario ratio")
        
        return "\n".join(analysis)

    def _extract_key_insights(self, analysis_result: str) -> List[str]:
        """Extract key insights from LLM analysis"""
        insights = []
        lines = analysis_result.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['insight:', 'key:', 'important:', 'notable:']):
                insights.append(line)
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                insights.append(line)
        
        return insights[:5]  # Limit to top 5 insights

    def _extract_recommendations(self, analysis_result: str) -> List[str]:
        """Extract recommendations from LLM analysis"""
        recommendations = []
        lines = analysis_result.split('\n')
        
        capturing = False
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                capturing = True
                recommendations.append(line)
            elif capturing and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                recommendations.append(line)
            elif capturing and not line:
                capturing = False
        
        return recommendations[:5]  # Limit to top 5 recommendations

    def _create_failure_analysis(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured failure analysis"""
        detailed_results = test_results.get("detailed_results", [])
        failed_tests = [test for test in detailed_results if test.get("status") == "failed"]
        
        failure_patterns = {}
        for test in failed_tests:
            error = test.get("error", "")
            # Simple pattern detection
            if "assertion" in error.lower():
                failure_patterns["assertion_failures"] = failure_patterns.get("assertion_failures", 0) + 1
            elif "null" in error.lower() or "none" in error.lower():
                failure_patterns["null_pointer_errors"] = failure_patterns.get("null_pointer_errors", 0) + 1
            elif "timeout" in error.lower():
                failure_patterns["timeout_errors"] = failure_patterns.get("timeout_errors", 0) + 1
            else:
                failure_patterns["other_errors"] = failure_patterns.get("other_errors", 0) + 1
        
        return {
            "total_failures": len(failed_tests),
            "failure_patterns": failure_patterns,
            "most_common_failure": max(failure_patterns.items(), key=lambda x: x[1])[0] if failure_patterns else None
        }

    def _calculate_test_quality_score(self, test_results: Dict[str, Any], test_discovery: Dict[str, Any]) -> float:
        """Calculate a test quality score based on various metrics"""
        score = 0.0
        
        # Success rate (40% of score)
        success_rate = test_results.get("success_rate", 0)
        score += success_rate * 0.4
        
        # Test coverage (30% of score)
        total_tests = test_results.get("total_tests", 0)
        if total_tests > 0:
            coverage_score = min(total_tests / 10, 1.0)  # Assume 10+ tests is good coverage
            score += coverage_score * 0.3
        
        # Framework diversity (20% of score)
        frameworks = test_discovery.get("test_frameworks", [])
        framework_score = min(len(frameworks) / 2, 1.0)  # Having 2+ frameworks is good
        score += framework_score * 0.2
        
        # Execution efficiency (10% of score)
        execution_time = test_results.get("execution_time", float('inf'))
        if execution_time < 30:  # Less than 30 seconds is good
            efficiency_score = 1.0
        elif execution_time < 60:  # Less than 1 minute is okay
            efficiency_score = 0.5
        else:
            efficiency_score = 0.1
        score += efficiency_score * 0.1
        
        return round(score, 2)

    def _create_default_analysis(self, test_results: Dict[str, Any], test_discovery: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Create a default analysis when LLM analysis fails"""
        failed_tests = test_results.get("failed_tests", 0)
        total_tests = test_results.get("total_tests", 0)
        success_rate = test_results.get("success_rate", 0)
        
        default_analysis = f"""
        Default Test Analysis for {language.upper()}:
        
        Test Execution Summary:
        - Total tests: {total_tests}
        - Failed tests: {failed_tests}
        - Success rate: {success_rate:.1%}
        
        {"✅ All tests passed successfully!" if failed_tests == 0 else f"❌ {failed_tests} test(s) failed and need attention."}
        
        Recommendations:
        - Review failed test output for specific error details
        - Consider adding more comprehensive test coverage
        - Ensure test environments are properly configured
        """
        
        return {
            "llm_analysis": default_analysis.strip(),
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_model": "Default Analysis",
            "key_insights": ["Default analysis due to LLM unavailability"],
            "recommendations": ["Review test failures manually", "Ensure proper test setup"],
            "failure_analysis": self._create_failure_analysis(test_results),
            "test_quality_score": self._calculate_test_quality_score(test_results, test_discovery)
        }

    def _generate_comprehensive_report(self, test_results: Dict[str, Any], test_analysis: Dict[str, Any], 
                                     test_discovery: Dict[str, Any], language: str, product_name: str, code_path: str) -> str:
        """Generate a comprehensive test report with detailed analysis"""
        try:
            success_rate = test_results.get("success_rate", 0)
            total_tests = test_results.get("total_tests", 0)
            passed_tests = test_results.get("passed_tests", 0)
            failed_tests = test_results.get("failed_tests", 0)
            execution_time = test_results.get("execution_time", 0)
            
            # Status emoji and summary
            status_emoji = "✅" if success_rate >= 0.8 else "⚠️" if success_rate >= 0.5 else "❌"
            overall_status = "Excellent" if success_rate >= 0.8 else "Needs Attention" if success_rate >= 0.5 else "Critical Issues"
            
            report = f"""# Test Execution Report: {product_name}

## 📊 Executive Summary
**Language:** {language.upper()}  
**Status:** {status_emoji} {overall_status}  
**Success Rate:** {success_rate:.1%}  
**Execution Time:** {execution_time:.2f}s  

## 🔢 Test Statistics
- **Total Tests:** {total_tests}
- **Passed:** {passed_tests} ✅
- **Failed:** {failed_tests} ❌
- **Test Files:** {test_discovery.get('test_files_count', 0)}
- **Frameworks:** {', '.join(test_discovery.get('test_frameworks', ['Unknown']))}

## 🎯 Test Quality Score: {test_analysis.get('test_quality_score', 0):.2f}/1.00

## 📋 Key Insights
{chr(10).join(['- ' + insight for insight in test_analysis.get('key_insights', ['No insights available'])])}

## 💡 Recommendations
{chr(10).join(['- ' + rec for rec in test_analysis.get('recommendations', ['No recommendations available'])])}
"""

            # Add failure analysis if there are failures
            if failed_tests > 0:
                failure_analysis = test_analysis.get('failure_analysis', {})
                report += f"""
## ❌ Failure Analysis
- **Total Failures:** {failure_analysis.get('total_failures', failed_tests)}
- **Failure Patterns:** {failure_analysis.get('failure_patterns', {})}
- **Most Common Issue:** {failure_analysis.get('most_common_failure', 'Unknown')}

### Failed Test Details
"""
                # Add individual failed test details
                detailed_results = test_results.get("detailed_results", [])
                failed_test_details = [test for test in detailed_results if test.get("status") == "failed"]
                
                for i, test in enumerate(failed_test_details[:5], 1):  # Show first 5 failures
                    report += f"""
**{i}. {test.get('name', 'Unknown Test')}**
```
{test.get('error', 'No error details available')[:300]}{'...' if len(test.get('error', '')) > 300 else ''}
```
"""
                
                if len(failed_test_details) > 5:
                    report += f"\n*... and {len(failed_test_details) - 5} more failures (check full test output for details)*\n"

            # Add LLM analysis
            if test_analysis.get('llm_analysis'):
                report += f"""
## 🤖 Detailed Analysis
{test_analysis['llm_analysis']}
"""

            # Add technical details
            report += f"""
## 🔧 Technical Details
- **Code Path:** `{code_path}`
- **Analysis Model:** {test_analysis.get('analysis_model', 'Unknown')}
- **Timestamp:** {test_analysis.get('analysis_timestamp', 'Unknown')}
- **Test Discovery:** {test_discovery.get('test_files_count', 0)} files, {total_tests} tests

---
*Report generated by Test Runner Agent*
"""
            
            return report
            
        except Exception as e:
            self.log(f"⚠️ Comprehensive report generation failed: {str(e)}")
            return self._generate_fallback_report(test_results, test_analysis, test_discovery, language, product_name, code_path, [], str(e))

    def _generate_fallback_report(self, test_results: Dict[str, Any], test_analysis: Dict[str, Any], 
                                test_discovery: Dict[str, Any], language: str, product_name: str, code_path: str,
                                validation_issues: List[str], error_context: str = None) -> str:
        """Generate a fallback report when comprehensive report generation fails"""
        
        # Extract basic info with safe defaults
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        failed_tests = test_results.get("failed_tests", 0)
        success_rate = test_results.get("success_rate", 0.0)
        execution_time = test_results.get("execution_time", 0.0)
        
        # Determine status
        if total_tests == 0:
            status = "⚠️ No Tests Found"
        elif failed_tests == 0:
            status = "✅ All Tests Passed"
        else:
            status = f"❌ {failed_tests} Tests Failed"
        
        report = f"""# Test Runner Fallback Report: {product_name}

## 📊 Basic Summary
**Language:** {language.upper()}  
**Status:** {status}  
**Success Rate:** {success_rate:.1%}  
**Execution Time:** {execution_time:.2f}s  

## 🔢 Test Statistics
- **Total Tests:** {total_tests}
- **Passed:** {passed_tests} ✅
- **Failed:** {failed_tests} ❌
- **Test Files Found:** {test_discovery.get('test_files_count', 0)}

## ⚠️ Issues Encountered
"""
        
        # Add validation issues
        if validation_issues:
            report += "### Validation Issues:\n"
            for issue in validation_issues:
                report += f"- {issue}\n"
            report += "\n"
        
        # Add error context if provided
        if error_context:
            report += f"### Report Generation Error:\n- {error_context}\n\n"
        
        # Add basic recommendations
        report += """## 💡 Basic Recommendations
- Review validation issues listed above
- Ensure test environment is properly configured
- Verify input data structure and code path validity
- Check language-specific test framework setup
"""
        
        # Add failure details if available
        if failed_tests > 0:
            report += f"""
## ❌ Test Failures Summary
{failed_tests} out of {total_tests} tests failed.

### Possible Causes:
- Code compilation issues
- Missing dependencies or test setup
- Logic errors in generated scenarios
- Environment configuration problems
"""
        
        # Add test output if available
        test_output = test_results.get("test_output", "")
        if test_output:
            truncated_output = test_output[:1000] + "..." if len(test_output) > 1000 else test_output
            report += f"""
## 📋 Test Output (Truncated)
```
{truncated_output}
```
"""
        
        report += f"""
## 🔧 Technical Details
- **Code Path:** `{code_path}`
- **Report Type:** Fallback Report
- **Timestamp:** {datetime.now().isoformat()}
- **Validation Issues:** {len(validation_issues)}

---
*Fallback report generated due to analysis limitations*
"""
        
        return report

    def _save_test_results(self, code_path: str, results: Dict[str, Any]) -> None:
        """Save test results to both JSON and Markdown files for later analysis"""
        try:
            import json
            
            # Save JSON results
            results_file = os.path.join(code_path, "test_results.json")
            serializable_results = self._make_json_serializable(results)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            
            self.log(f"💾 Test results saved to: {results_file}")
            
            # Save Markdown report
            self._save_markdown_report(code_path, results)
            
        except Exception as e:
            self.log(f"⚠️ Failed to save test results: {str(e)}")

    def _save_markdown_report(self, code_path: str, results: Dict[str, Any]) -> None:
        """Save test results as a comprehensive Markdown report"""
        try:
            # Generate comprehensive Markdown report
            comprehensive_report = results.get("comprehensive_report", "")
            
            # If no comprehensive report, generate one from available data
            if not comprehensive_report:
                test_results = results.get("test_results", {})
                test_analysis = results.get("test_analysis", {})
                test_discovery = results.get("test_discovery", {})
                
                comprehensive_report = self._generate_markdown_report(
                    test_results, test_analysis, test_discovery, code_path
                )
            
            # Save to Markdown file
            markdown_file = os.path.join(code_path, "test_report.md")
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(comprehensive_report)
            
            self.log(f"📄 Markdown report saved to: {markdown_file}")
            
            # Also save a simplified version for UI display
            self._save_ui_markdown_report(code_path, results)
            
        except Exception as e:
            self.log(f"⚠️ Failed to save Markdown report: {str(e)}")

    def _save_ui_markdown_report(self, code_path: str, results: Dict[str, Any]) -> None:
        """Save a UI-optimized Markdown report for Streamlit display"""
        try:
            test_results = results.get("test_results", {})
            test_analysis = results.get("test_analysis", {})
            test_discovery = results.get("test_discovery", {})
            validation_issues = results.get("validation_issues", [])
            
            # Generate UI-optimized report
            ui_report = self._generate_ui_markdown_report(
                test_results, test_analysis, test_discovery, validation_issues
            )
            
            # Save to UI-specific Markdown file
            ui_markdown_file = os.path.join(code_path, "test_report_ui.md")
            with open(ui_markdown_file, 'w', encoding='utf-8') as f:
                f.write(ui_report)
            
            self.log(f"🎨 UI Markdown report saved to: {ui_markdown_file}")
            
        except Exception as e:
            self.log(f"⚠️ Failed to save UI Markdown report: {str(e)}")

    def _generate_markdown_report(self, test_results: Dict[str, Any], test_analysis: Dict[str, Any], 
                                test_discovery: Dict[str, Any], code_path: str) -> str:
        """Generate a comprehensive Markdown report from test data"""
        success_rate = test_results.get("success_rate", 0)
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        failed_tests = test_results.get("failed_tests", 0)
        execution_time = test_results.get("execution_time", 0)
        frameworks = test_discovery.get("test_frameworks", ["Unknown"])
        
        # Determine status
        if total_tests == 0:
            status_emoji = "⚠️"
            status_text = "No Tests Found"
        elif success_rate >= 80:
            status_emoji = "✅"
            status_text = "Excellent"
        elif success_rate >= 50:
            status_emoji = "⚠️"
            status_text = "Needs Attention"
        else:
            status_emoji = "❌"
            status_text = "Critical Issues"
        
        report = f"""# 🧪 Test Execution Report

## {status_emoji} Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Status** | {status_emoji} {status_text} |
| **Success Rate** | {success_rate:.1f}% |
| **Total Tests** | {total_tests} |
| **Execution Time** | {execution_time:.2f}s |
| **Test Frameworks** | {', '.join(frameworks)} |

## 📊 Test Statistics

### Results Breakdown
- ✅ **Passed Tests:** {passed_tests}
- ❌ **Failed Tests:** {failed_tests}
- 📁 **Test Files:** {test_discovery.get('test_files_count', 0)}
- ⏱️ **Average Time per Test:** {(execution_time/total_tests):.2f}s (if tests > 0)

### Quality Score: {test_analysis.get('test_quality_score', 0):.1f}/1.0

## 🔍 Analysis Results
"""
        
        # Add LLM analysis if available
        llm_analysis = test_analysis.get("llm_analysis", "")
        if llm_analysis:
            report += f"""
### 🤖 AI Analysis
{llm_analysis}

"""
        
        # Add key insights
        insights = test_analysis.get("key_insights", [])
        if insights:
            report += "### 💡 Key Insights\n"
            for insight in insights:
                report += f"- {insight}\n"
            report += "\n"
        
        # Add recommendations
        recommendations = test_analysis.get("recommendations", [])
        if recommendations:
            report += "### 📋 Recommendations\n"
            for rec in recommendations:
                report += f"- {rec}\n"
            report += "\n"
        
        # Add failure details if there are failures
        if failed_tests > 0:
            report += f"""## ❌ Failure Analysis

**Total Failures:** {failed_tests}

### Failed Test Details
"""
            detailed_results = test_results.get("detailed_results", [])
            failed_test_details = [test for test in detailed_results if test.get("status") == "failed"]
            
            for i, test in enumerate(failed_test_details[:10], 1):  # Show first 10 failures
                test_name = test.get('name', f'Test {i}')
                error = test.get('error', 'No error details available')
                duration = test.get('duration', 'Unknown')
                
                report += f"""
#### {i}. {test_name}
- **Duration:** {duration}
- **Error:**
```
{error[:500]}{'...' if len(error) > 500 else ''}
```

"""
            
            if len(failed_test_details) > 10:
                report += f"*... and {len(failed_test_details) - 10} more failures*\n\n"
        
        # Add technical details
        report += f"""## � Technical Details

- **Code Path:** `{code_path}`
- **Test Files Discovered:** {test_discovery.get('test_files_count', 0)}
- **Test Frameworks:** {', '.join(frameworks)}
- **Analysis Timestamp:** {test_analysis.get('analysis_timestamp', 'Unknown')}
- **Analysis Model:** {test_analysis.get('analysis_model', 'Unknown')}

---

*Report generated by Test Runner Agent - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report

    def _generate_ui_markdown_report(self, test_results: Dict[str, Any], test_analysis: Dict[str, Any], 
                                   test_discovery: Dict[str, Any], validation_issues: List[str]) -> str:
        """Generate a UI-optimized Markdown report for Streamlit display"""
        success_rate = test_results.get("success_rate", 0)
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        failed_tests = test_results.get("failed_tests", 0)
        execution_time = test_results.get("execution_time", 0)
        quality_score_raw = test_analysis.get('test_quality_score', 0)

        # Determine quality score scale (heuristic: values > 1 are already 0-100 scale)
        if quality_score_raw <= 1:
            quality_score_display = quality_score_raw * 100
        else:
            quality_score_display = quality_score_raw

        # Derive status label
        if total_tests == 0:
            status_label = "No Tests Found"
            status_emoji = "⚠️"
        elif success_rate >= 80:
            status_label = "Excellent"
            status_emoji = "✅"
        elif success_rate >= 50:
            status_label = "Needs Attention"
            status_emoji = "⚠️"
        else:
            status_label = "Critical Issues"
            status_emoji = "❌"

        # Start report
        report = ["## 🧪 Test Execution Summary", "", "### 📊 Quick Stats", f"- **Success Rate:** {success_rate:.1f}%", f"- **Tests:** {passed_tests}✅ / {failed_tests}❌ (Total: {total_tests})", f"- **Duration:** {execution_time:.2f}s", f"- **Quality Score:** {quality_score_display:.1f} / 100", "", f"### {status_emoji} Status: {status_label}"]

        # Build key points synthesizing real test data + curated insights (avoid misleading scenario bullets)
        raw_insights: List[str] = test_analysis.get("key_insights", [])
        curated_insights: List[str] = []

        # Always include an explicit pass/fail summary as first bullet when tests exist
        if total_tests > 0:
            curated_insights.append(f"{passed_tests} test(s) passed, {failed_tests} failed.")

        # Filter out placeholder or misleading lines
        for ins in raw_insights:
            if not ins or ins.strip() in {"---"}:
                continue
            lowered = ins.lower()
            # Exclude scenario coverage claims when we DO have test results (to avoid confusion)
            if ("scenario success rate" in lowered or "scenario coverage" in lowered) and total_tests > 0:
                continue
            curated_insights.append(ins.replace("- ", "").replace("• ", ""))
            if len(curated_insights) >= 3:  # limit size
                break

        if curated_insights:
            report.append("")
            report.append("### 💡 Key Points")
            for ci in curated_insights:
                report.append(f"- {ci}")

        # Recommendations (filter out those that are duplicates of insights)
        recs_raw = test_analysis.get("recommendations", [])
        cleaned_recs = []
        seen_text = {ci.lower() for ci in curated_insights}
        for rec in recs_raw:
            if not rec:
                continue
            txt = rec.replace("- ", "").replace("• ", "").strip()
            if txt.lower() in seen_text:
                continue
            cleaned_recs.append(txt)
            if len(cleaned_recs) >= 3:
                break

        if cleaned_recs:
            report.append("")
            report.append("### 📋 Top Actions")
            for cr in cleaned_recs:
                report.append(f"- {cr}")

        # Validation issues (environment/config problems)
        if validation_issues:
            report.append("")
            report.append("### ⚠️ Issues Detected")
            for issue in validation_issues[:3]:
                report.append(f"- {issue}")

        # Failure extraction & analysis
        if failed_tests > 0:
            report.append("")
            report.append("### ❌ Failures Summary")
            report.append(f"**{failed_tests} tests failed**.")

            # Gather detailed results if available
            detailed_results = test_results.get("detailed_results", [])
            failed_detail_objs = [t for t in detailed_results if t.get("status") == "failed"]

            # If no structured details, attempt to parse names from raw output
            if not failed_detail_objs:
                raw_output = test_results.get("output") or test_results.get("framework_output", "")
                parsed_names = []
                if raw_output:
                    for line in raw_output.splitlines():
                        line_stripped = line.strip()
                        if line_stripped.startswith("Failed "):
                            # Format: Failed TestName [time s]
                            name_part = line_stripped[len("Failed "):]
                            name_part = name_part.split(" [", 1)[0].strip()
                            if name_part and name_part not in parsed_names:
                                parsed_names.append(name_part)
                failed_detail_objs = [{"name": n, "error": None} for n in parsed_names]

            # Detect common root cause
            raw_all_text = (test_results.get("output") or "") + "\n" + (test_results.get("framework_output") or "")
            common_root = None
            if "actively refused" in raw_all_text.lower():
                common_root = "Connection refused to configured endpoint (likely Cosmos DB emulator/service not running or wrong port)."

            if failed_detail_objs:
                report.append("")
                report.append("**Failed Tests:**")
                for t in failed_detail_objs[:10]:  # limit output
                    report.append(f"- {t.get('name', 'Unknown Test')}")
                if len(failed_detail_objs) > 10:
                    report.append(f"- ...and {len(failed_detail_objs) - 10} more")

            if common_root:
                report.append("")
                report.append("**Probable Root Cause:** " + common_root)
                report.append("**Suggested Immediate Fix:** Ensure the Cosmos DB Emulator/service is running, correct endpoint/port configured, then rerun tests. Add a pre-test health check to fail fast if unreachable.")

        # Final footer
        report.append("")
        report.append("---")
        report.append(f"*Generated: {datetime.now().strftime('%H:%M:%S')}*")

        return "\n".join(report)

    def _make_json_serializable(self, obj):
        """Convert objects to JSON serializable format"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return obj

