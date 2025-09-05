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
from tools.language_best_practices_manager import LanguageBestPracticesManager
from tools.prompt_loader.prompty_loader import PromptyLoader
from patterns.language_config import LanguageConfig
from integrations.azure_openai.client import get_agent_azure_openai_client


class TestRunner(BaseAgent):
    """
    Agent responsible for running tests and generating comprehensive reports
    """
    
    def __init__(self, llm=None):
        llm_instance = llm or get_agent_azure_openai_client("test_runner")
        super().__init__("Test Runner", llm_instance)
        self.language_best_practices_manager = LanguageBestPracticesManager()
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
            
            # Handle different input types (similar to CodeGenerator)
            if isinstance(input_data, dict):
                parsed_data = input_data
            elif isinstance(input_data, str):
                try:
                    parsed_data = json.loads(input_data)
                except json.JSONDecodeError:
                    # If it's not JSON, create a minimal structure for testing
                    self.log("⚠️ Input is not JSON, treating as raw output from CodeGenerator")
                    # Extract information from the string if possible
                    parsed_data = {
                        "language": "python",  # Default to python as fallback
                        "product_name": "Unknown",
                        "code_path": "",
                        "scenario_results": {},
                        "raw_output": input_data  # Store the raw input for potential parsing
                    }
            else:
                raise ValueError("Input data must be either a dictionary or string")
            
            # Extract input parameters with safe defaults
            project_files = parsed_data.get("project_files", {})
            language = parsed_data.get("language", "").lower()
            product_name = parsed_data.get("product_name", "Unknown")
            code_path = parsed_data.get("code_path", "")
            scenario_results = parsed_data.get("scenario_results", {})
            
            # Validate inputs
            if not code_path or not os.path.exists(code_path):
                raise ValueError(f"Invalid code path: {code_path}")
                
            if language not in self.test_executors:
                raise ValueError(f"Unsupported language: {language}")
            
            self.log(f"📋 Test execution details:")
            self.log(f"  - Language: {language.upper()}")
            self.log(f"  - Product: {product_name}")
            self.log(f"  - Code Path: {code_path}")
            self.log(f"  - Scenarios: {len(scenario_results.get('successful', []))} successful, {len(scenario_results.get('failed', []))} failed")
            
            # Step 1: Discover and analyze test structure
            test_discovery = self._discover_tests(code_path, language)
            self.log(f"🔍 Discovered {test_discovery['total_tests']} tests in {test_discovery['test_files_count']} files")
            
            # Step 2: Execute tests
            test_results = self._execute_tests(code_path, language, test_discovery)
            
            # Step 3: Analyze results with LLM
            test_analysis = self._analyze_test_results_with_llm(
                test_results, test_discovery, language, product_name, scenario_results
            )
            
            # Step 4: Generate comprehensive report
            comprehensive_report = self._generate_comprehensive_report(
                test_results, test_analysis, test_discovery, language, product_name, code_path
            )
            
            # Step 5: Save results
            self._save_test_results(code_path, {
                "test_results": test_results,
                "test_analysis": test_analysis,
                "comprehensive_report": comprehensive_report,
                "test_discovery": test_discovery
            })
            
            # Determine overall status
            overall_status = "success" if test_results.get("success", False) else "failure"
            
            return {
                "agent": self.name,
                "input": input_data,
                "output": {
                    "test_results": test_results,
                    "test_analysis": test_analysis,
                    "comprehensive_report": comprehensive_report,
                    "test_discovery": test_discovery
                },
                "status": overall_status,
                "test_execution_path": code_path,
                "language": language,
                "product_name": product_name,
                "execution_summary": {
                    "total_tests": test_results.get("total_tests", 0),
                    "passed_tests": test_results.get("passed_tests", 0),
                    "failed_tests": test_results.get("failed_tests", 0),
                    "success_rate": test_results.get("success_rate", 0.0),
                    "execution_time": test_results.get("execution_time", 0.0)
                }
            }
            
        except Exception as e:
            error_msg = f"Test Runner Agent failed: {str(e)}"
            self.log(f"❌ {error_msg}")
            
            return {
                "agent": self.name,
                "input": input_data,
                "output": {},
                "status": "error",
                "error": error_msg,
                "execution_summary": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "success_rate": 0.0,
                    "execution_time": 0.0
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
            
            # Prepare prompt variables
            failed_tests_summary = self._summarize_failed_tests(test_results.get("detailed_results", []))
            test_coverage_analysis = self._analyze_test_coverage(test_discovery, scenario_results)
            
            prompt_vars = {
                "language": language.upper(),
                "product_name": product_name,
                "total_tests": test_results.get("total_tests", 0),
                "passed_tests": test_results.get("passed_tests", 0),
                "failed_tests": test_results.get("failed_tests", 0),
                "success_rate": test_results.get("success_rate", 0),
                "execution_time": test_results.get("execution_time", 0),
                "test_frameworks": ', '.join(test_discovery.get("test_frameworks", ["unknown"])),
                "failed_tests_summary": failed_tests_summary,
                "test_coverage_analysis": test_coverage_analysis,
                "test_output": test_results.get("output", "")[:2000],  # Limit output size
                "scenario_count": len(scenario_results.get("successful", [])),
                "overall_success": test_results.get("success", False)
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

