"""
Test Reporter Tool

Executes tests and generates comprehensive test reports with analysis and recommendations.
"""

import os
import subprocess
import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import glob


class TestReporter:
    """Tool for running tests and generating comprehensive test reports"""
    
    def __init__(self):
        self.test_commands = {
            'csharp': {
                'command': ['dotnet', 'test', '--logger', 'trx', '--logger', 'console;verbosity=detailed'],
                'result_patterns': ['TestResults/*.trx'],
                'coverage_command': ['dotnet', 'test', '--collect:"XPlat Code Coverage"'],
                'test_discovery': ['**/*Tests.cs', '**/*Test.cs', '**/Test*.cs']
            },
            'java': {
                'command': ['mvn', 'test'],
                'result_patterns': ['target/surefire-reports/*.xml'],
                'coverage_command': ['mvn', 'test', 'jacoco:report'],
                'test_discovery': ['**/src/test/**/*Test.java', '**/src/test/**/*Tests.java']
            },
            'python': {
                'command': ['pytest', '--junitxml=pytest-results.xml', '--verbose', '--tb=short'],
                'result_patterns': ['pytest-results.xml', 'test-results.xml'],
                'coverage_command': ['pytest', '--cov=.', '--cov-report=xml', '--cov-report=html'],
                'test_discovery': ['**/test_*.py', '**/*_test.py', '**/tests.py']
            },
            'javascript': {
                'command': ['npm', 'test'],
                'result_patterns': ['test-results.xml', 'junit.xml'],
                'coverage_command': ['npm', 'run', 'test:coverage'],
                'test_discovery': ['**/*.test.js', '**/*.spec.js', '**/test/**/*.js']
            },
            'go': {
                'command': ['go', 'test', '-v', '-json', './...'],
                'result_patterns': ['test-results.json'],
                'coverage_command': ['go', 'test', '-cover', '-coverprofile=coverage.out', './...'],
                'test_discovery': ['**/*_test.go']
            },
            'rust': {
                'command': ['cargo', 'test', '--', '--format', 'json'],
                'result_patterns': ['test-results.json'],
                'coverage_command': ['cargo', 'tarpaulin', '--out', 'xml'],
                'test_discovery': ['**/src/**/*test*.rs', '**/tests/**/*.rs']
            }
        }
    
    def discover_tests(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Discover test files in the project"""
        result = {
            'language': language,
            'project_dir': project_dir,
            'test_files': [],
            'test_count_estimate': 0,
            'test_categories': {
                'unit_tests': [],
                'integration_tests': [],
                'functional_tests': [],
                'other_tests': []
            }
        }
        
        try:
            test_config = self.test_commands.get(language.lower())
            if not test_config:
                return result
            
            discovery_patterns = test_config.get('test_discovery', [])
            
            for pattern in discovery_patterns:
                # Use glob to find test files
                test_files = glob.glob(os.path.join(project_dir, pattern), recursive=True)
                result['test_files'].extend(test_files)
            
            # Remove duplicates
            result['test_files'] = list(set(result['test_files']))
            
            # Analyze test files and categorize
            for test_file in result['test_files']:
                category = self._categorize_test_file(test_file, language)
                result['test_categories'][category].append(test_file)
                
                # Estimate test count by analyzing file content
                test_count = self._estimate_test_count(test_file, language)
                result['test_count_estimate'] += test_count
            
        except Exception as e:
            result['error'] = f"Test discovery failed: {str(e)}"
        
        return result
    
    def run_tests(self, project_dir: str, language: str, include_coverage: bool = True) -> Dict[str, Any]:
        """Run tests and generate comprehensive report"""
        result = {
            'success': False,
            'language': language,
            'project_dir': project_dir,
            'timestamp': datetime.now().isoformat(),
            'test_discovery': {},
            'test_execution': {},
            'test_results': {},
            'coverage_results': {},
            'summary': {},
            'recommendations': []
        }
        
        try:
            # Step 1: Discover tests
            result['test_discovery'] = self.discover_tests(project_dir, language)
            
            if not result['test_discovery']['test_files']:
                result['recommendations'].append({
                    'type': 'no_tests_found',
                    'severity': 'high',
                    'message': f"No test files found for {language} project",
                    'suggestion': f"Create test files following {language} testing conventions"
                })
                result['success'] = True  # Not a failure if no tests exist
                return result
            
            # Step 2: Execute tests
            result['test_execution'] = self._execute_tests(project_dir, language)
            
            # Step 3: Parse test results
            result['test_results'] = self._parse_test_results(project_dir, language, result['test_execution'])
            
            # Step 4: Run coverage analysis if requested
            if include_coverage:
                result['coverage_results'] = self._run_coverage_analysis(project_dir, language)
            
            # Step 5: Generate summary and recommendations
            result['summary'] = self._generate_test_summary(result)
            result['recommendations'].extend(self._generate_recommendations(result))
            
            # Mark as successful if tests ran (even if some failed)
            result['success'] = result['test_execution'].get('executed', False)
            
        except Exception as e:
            result['error'] = f"Test execution failed: {str(e)}"
        
        return result
    
    def _categorize_test_file(self, file_path: str, language: str) -> str:
        """Categorize test file based on name and content"""
        file_name = os.path.basename(file_path).lower()
        
        if 'integration' in file_name:
            return 'integration_tests'
        elif 'functional' in file_name or 'e2e' in file_name:
            return 'functional_tests'
        elif 'unit' in file_name or 'test' in file_name:
            return 'unit_tests'
        else:
            return 'other_tests'
    
    def _estimate_test_count(self, file_path: str, language: str) -> int:
        """Estimate number of tests in a file by analyzing content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            test_patterns = {
                'csharp': [r'\[Test\]', r'\[TestMethod\]', r'\[Fact\]', r'\[Theory\]'],
                'java': [r'@Test', r'@ParameterizedTest'],
                'python': [r'def test_\w+', r'class Test\w+'],
                'javascript': [r'it\s*\(', r'test\s*\(', r'describe\s*\('],
                'go': [r'func Test\w+'],
                'rust': [r'#\[test\]']
            }
            
            patterns = test_patterns.get(language.lower(), [])
            total_count = 0
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_count += len(matches)
            
            return max(total_count, 1)  # At least 1 if file exists
            
        except Exception:
            return 1  # Default estimate
    
    def _execute_tests(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Execute test command and capture results"""
        execution_result = {
            'executed': False,
            'command': [],
            'output': '',
            'error_output': '',
            'return_code': -1,
            'execution_time': 0,
            'test_files_found': []
        }
        
        try:
            test_config = self.test_commands.get(language.lower())
            if not test_config:
                execution_result['error'] = f"No test configuration for language: {language}"
                return execution_result
            
            test_cmd = test_config['command']
            execution_result['command'] = test_cmd
            
            # Record start time
            start_time = datetime.now()
            
            # Execute test command
            process = subprocess.run(
                test_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for tests
            )
            
            # Record execution time
            end_time = datetime.now()
            execution_result['execution_time'] = (end_time - start_time).total_seconds()
            
            execution_result['output'] = process.stdout
            execution_result['error_output'] = process.stderr
            execution_result['return_code'] = process.returncode
            execution_result['executed'] = True
            
        except subprocess.TimeoutExpired:
            execution_result['error'] = "Test execution timed out after 10 minutes"
        except FileNotFoundError:
            execution_result['error'] = f"Test tool not found: {test_cmd[0] if test_cmd else 'unknown'}"
        except Exception as e:
            execution_result['error'] = f"Test execution failed: {str(e)}"
        
        return execution_result
    
    def _parse_test_results(self, project_dir: str, language: str, execution_result: Dict) -> Dict[str, Any]:
        """Parse test results from output files and console output"""
        results = {
            'parsed_successfully': False,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'error_tests': 0,
            'test_details': [],
            'failed_test_details': [],
            'execution_time': execution_result.get('execution_time', 0)
        }
        
        try:
            test_config = self.test_commands.get(language.lower())
            if not test_config:
                return results
            
            # Try to parse from result files first
            result_patterns = test_config.get('result_patterns', [])
            parsed_from_file = False
            
            for pattern in result_patterns:
                result_files = glob.glob(os.path.join(project_dir, pattern))
                for result_file in result_files:
                    if self._parse_result_file(result_file, language, results):
                        parsed_from_file = True
                        break
                
                if parsed_from_file:
                    break
            
            # If no result files found, parse from console output
            if not parsed_from_file:
                self._parse_console_output(execution_result.get('output', ''), 
                                         execution_result.get('error_output', ''), 
                                         language, results)
            
            results['parsed_successfully'] = True
            
        except Exception as e:
            results['parse_error'] = str(e)
        
        return results
    
    def _parse_result_file(self, result_file: str, language: str, results: Dict) -> bool:
        """Parse test results from XML or JSON result files"""
        try:
            if result_file.endswith('.xml'):
                return self._parse_xml_results(result_file, results)
            elif result_file.endswith('.json'):
                return self._parse_json_results(result_file, language, results)
        except Exception as e:
            results['file_parse_error'] = f"Could not parse {result_file}: {str(e)}"
        
        return False
    
    def _parse_xml_results(self, xml_file: str, results: Dict) -> bool:
        """Parse XML test result files (JUnit format)"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Handle different XML formats
            if root.tag == 'testsuites' or root.tag == 'testsuite':
                testsuites = root.findall('.//testsuite') if root.tag == 'testsuites' else [root]
                
                for testsuite in testsuites:
                    tests = int(testsuite.get('tests', 0))
                    failures = int(testsuite.get('failures', 0))
                    errors = int(testsuite.get('errors', 0))
                    skipped = int(testsuite.get('skipped', 0))
                    
                    results['total_tests'] += tests
                    results['failed_tests'] += failures
                    results['error_tests'] += errors
                    results['skipped_tests'] += skipped
                    results['passed_tests'] += (tests - failures - errors - skipped)
                    
                    # Extract failed test details
                    for testcase in testsuite.findall('testcase'):
                        test_name = testcase.get('name', 'Unknown')
                        class_name = testcase.get('classname', '')
                        
                        failure = testcase.find('failure')
                        error = testcase.find('error')
                        
                        if failure is not None:
                            results['failed_test_details'].append({
                                'name': test_name,
                                'class': class_name,
                                'type': 'failure',
                                'message': failure.get('message', ''),
                                'details': failure.text or ''
                            })
                        elif error is not None:
                            results['failed_test_details'].append({
                                'name': test_name,
                                'class': class_name,
                                'type': 'error',
                                'message': error.get('message', ''),
                                'details': error.text or ''
                            })
                
                return True
                
        except Exception as e:
            results['xml_parse_error'] = str(e)
        
        return False
    
    def _parse_json_results(self, json_file: str, language: str, results: Dict) -> bool:
        """Parse JSON test result files"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if language.lower() == 'go':
                return self._parse_go_json_results(data, results)
            elif language.lower() == 'rust':
                return self._parse_rust_json_results(data, results)
            
        except Exception as e:
            results['json_parse_error'] = str(e)
        
        return False
    
    def _parse_go_json_results(self, data: Any, results: Dict) -> bool:
        """Parse Go test JSON output"""
        try:
            if isinstance(data, list):
                test_events = data
            else:
                return False
            
            test_results = {}
            
            for event in test_events:
                if event.get('Test'):
                    test_name = event['Test']
                    action = event.get('Action')
                    
                    if action == 'pass':
                        test_results[test_name] = 'passed'
                    elif action == 'fail':
                        test_results[test_name] = 'failed'
                    elif action == 'skip':
                        test_results[test_name] = 'skipped'
            
            results['total_tests'] = len(test_results)
            results['passed_tests'] = sum(1 for status in test_results.values() if status == 'passed')
            results['failed_tests'] = sum(1 for status in test_results.values() if status == 'failed')
            results['skipped_tests'] = sum(1 for status in test_results.values() if status == 'skipped')
            
            return True
            
        except Exception:
            return False
    
    def _parse_rust_json_results(self, data: Any, results: Dict) -> bool:
        """Parse Rust test JSON output"""
        # Rust test output parsing would go here
        # This is a placeholder - implement based on actual Rust test JSON format
        return False
    
    def _parse_console_output(self, stdout: str, stderr: str, language: str, results: Dict) -> None:
        """Parse test results from console output when result files aren't available"""
        combined_output = stdout + "\n" + stderr
        
        # Language-specific console output parsing
        if language.lower() == 'python':
            self._parse_pytest_output(combined_output, results)
        elif language.lower() == 'javascript':
            self._parse_jest_output(combined_output, results)
        elif language.lower() == 'csharp':
            self._parse_dotnet_output(combined_output, results)
        elif language.lower() == 'java':
            self._parse_maven_output(combined_output, results)
        elif language.lower() == 'go':
            self._parse_go_output(combined_output, results)
        elif language.lower() == 'rust':
            self._parse_cargo_output(combined_output, results)
    
    def _parse_pytest_output(self, output: str, results: Dict) -> None:
        """Parse pytest console output"""
        # Look for test session summary
        summary_match = re.search(r'=+ (.+?) =+$', output, re.MULTILINE)
        if summary_match:
            summary = summary_match.group(1)
            
            # Extract counts
            passed_match = re.search(r'(\d+) passed', summary)
            failed_match = re.search(r'(\d+) failed', summary)
            skipped_match = re.search(r'(\d+) skipped', summary)
            error_match = re.search(r'(\d+) error', summary)
            
            if passed_match:
                results['passed_tests'] = int(passed_match.group(1))
            if failed_match:
                results['failed_tests'] = int(failed_match.group(1))
            if skipped_match:
                results['skipped_tests'] = int(skipped_match.group(1))
            if error_match:
                results['error_tests'] = int(error_match.group(1))
            
            results['total_tests'] = (results['passed_tests'] + results['failed_tests'] + 
                                    results['skipped_tests'] + results['error_tests'])
    
    def _parse_jest_output(self, output: str, results: Dict) -> None:
        """Parse Jest console output"""
        # Look for test summary
        summary_lines = output.split('\n')
        for line in summary_lines:
            if 'Tests:' in line:
                # Parse Jest summary line
                passed_match = re.search(r'(\d+) passed', line)
                failed_match = re.search(r'(\d+) failed', line)
                skipped_match = re.search(r'(\d+) skipped', line)
                
                if passed_match:
                    results['passed_tests'] = int(passed_match.group(1))
                if failed_match:
                    results['failed_tests'] = int(failed_match.group(1))
                if skipped_match:
                    results['skipped_tests'] = int(skipped_match.group(1))
                
                results['total_tests'] = (results['passed_tests'] + results['failed_tests'] + 
                                        results['skipped_tests'])
                break
    
    def _parse_dotnet_output(self, output: str, results: Dict) -> None:
        """Parse dotnet test console output"""
        # Look for test run summary
        lines = output.split('\n')
        for line in lines:
            if 'Test Run Successful' in line or 'Test Run Failed' in line:
                # Extract test counts from previous lines
                for prev_line in lines:
                    if 'Total tests:' in prev_line:
                        total_match = re.search(r'Total tests: (\d+)', prev_line)
                        passed_match = re.search(r'Passed: (\d+)', prev_line)
                        failed_match = re.search(r'Failed: (\d+)', prev_line)
                        skipped_match = re.search(r'Skipped: (\d+)', prev_line)
                        
                        if total_match:
                            results['total_tests'] = int(total_match.group(1))
                        if passed_match:
                            results['passed_tests'] = int(passed_match.group(1))
                        if failed_match:
                            results['failed_tests'] = int(failed_match.group(1))
                        if skipped_match:
                            results['skipped_tests'] = int(skipped_match.group(1))
                        break
                break
    
    def _parse_maven_output(self, output: str, results: Dict) -> None:
        """Parse Maven test console output"""
        # Look for test summary
        summary_match = re.search(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', output)
        if summary_match:
            total, failures, errors, skipped = map(int, summary_match.groups())
            results['total_tests'] = total
            results['failed_tests'] = failures
            results['error_tests'] = errors
            results['skipped_tests'] = skipped
            results['passed_tests'] = total - failures - errors - skipped
    
    def _parse_go_output(self, output: str, results: Dict) -> None:
        """Parse Go test console output"""
        # Count PASS/FAIL lines
        pass_count = len(re.findall(r'PASS', output))
        fail_count = len(re.findall(r'FAIL', output))
        
        results['passed_tests'] = pass_count
        results['failed_tests'] = fail_count
        results['total_tests'] = pass_count + fail_count
    
    def _parse_cargo_output(self, output: str, results: Dict) -> None:
        """Parse Cargo test console output"""
        # Look for test result summary
        summary_match = re.search(r'test result: (\w+)\. (\d+) passed; (\d+) failed', output)
        if summary_match:
            status, passed, failed = summary_match.groups()
            results['passed_tests'] = int(passed)
            results['failed_tests'] = int(failed)
            results['total_tests'] = int(passed) + int(failed)
    
    def _run_coverage_analysis(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Run code coverage analysis"""
        coverage_result = {
            'executed': False,
            'coverage_percentage': 0.0,
            'covered_lines': 0,
            'total_lines': 0,
            'uncovered_files': [],
            'coverage_details': {}
        }
        
        try:
            test_config = self.test_commands.get(language.lower())
            if not test_config or 'coverage_command' not in test_config:
                coverage_result['error'] = f"Coverage analysis not configured for {language}"
                return coverage_result
            
            coverage_cmd = test_config['coverage_command']
            
            process = subprocess.run(
                coverage_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            coverage_result['executed'] = True
            coverage_result['output'] = process.stdout
            coverage_result['error_output'] = process.stderr
            
            # Parse coverage results (implementation depends on coverage tool format)
            # This is a simplified version - real implementation would parse specific formats
            
        except Exception as e:
            coverage_result['error'] = f"Coverage analysis failed: {str(e)}"
        
        return coverage_result
    
    def _generate_test_summary(self, test_result: Dict) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        test_results = test_result.get('test_results', {})
        discovery = test_result.get('test_discovery', {})
        execution = test_result.get('test_execution', {})
        
        total_tests = test_results.get('total_tests', 0)
        passed_tests = test_results.get('passed_tests', 0)
        failed_tests = test_results.get('failed_tests', 0)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'test_discovery_summary': {
                'test_files_found': len(discovery.get('test_files', [])),
                'estimated_test_count': discovery.get('test_count_estimate', 0),
                'test_categories': discovery.get('test_categories', {})
            },
            'test_execution_summary': {
                'executed_successfully': execution.get('executed', False),
                'execution_time_seconds': execution.get('execution_time', 0),
                'return_code': execution.get('return_code', -1)
            },
            'test_results_summary': {
                'total_tests_run': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'skipped_tests': test_results.get('skipped_tests', 0),
                'error_tests': test_results.get('error_tests', 0),
                'success_rate_percentage': round(success_rate, 2),
                'all_tests_passed': failed_tests == 0 and test_results.get('error_tests', 0) == 0
            },
            'overall_status': 'PASSED' if failed_tests == 0 and test_results.get('error_tests', 0) == 0 else 'FAILED'
        }
    
    def _generate_recommendations(self, test_result: Dict) -> List[Dict[str, Any]]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        test_results = test_result.get('test_results', {})
        summary = test_result.get('summary', {}).get('test_results_summary', {})
        
        # Test coverage recommendations
        success_rate = summary.get('success_rate_percentage', 0)
        if success_rate < 70:
            recommendations.append({
                'type': 'low_test_success_rate',
                'severity': 'high',
                'message': f"Test success rate is {success_rate}% - below recommended 90%",
                'suggestion': "Review and fix failing tests, improve test quality"
            })
        elif success_rate < 90:
            recommendations.append({
                'type': 'moderate_test_success_rate',
                'severity': 'medium',
                'message': f"Test success rate is {success_rate}% - could be improved",
                'suggestion': "Aim for 90%+ test success rate for production readiness"
            })
        
        # Test count recommendations
        total_tests = summary.get('total_tests_run', 0)
        if total_tests == 0:
            recommendations.append({
                'type': 'no_tests_executed',
                'severity': 'critical',
                'message': "No tests were executed",
                'suggestion': "Add test cases to ensure code quality and functionality"
            })
        elif total_tests < 10:
            recommendations.append({
                'type': 'low_test_count',
                'severity': 'medium',
                'message': f"Only {total_tests} tests found - may need more comprehensive testing",
                'suggestion': "Consider adding more test cases for better coverage"
            })
        
        # Failed test recommendations
        failed_tests = test_results.get('failed_test_details', [])
        if failed_tests:
            recommendations.append({
                'type': 'tests_failing',
                'severity': 'high',
                'message': f"{len(failed_tests)} test(s) are failing",
                'suggestion': "Review and fix failing tests before deployment",
                'failed_tests': [test['name'] for test in failed_tests[:5]]  # First 5 failed tests
            })
        
        return recommendations
    
    def generate_html_report(self, test_result: Dict, output_path: str) -> str:
        """Generate HTML test report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {test_result.get('language', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
        .recommendations {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; }}
        .critical {{ border-left: 5px solid red; }}
        .high {{ border-left: 5px solid orange; }}
        .medium {{ border-left: 5px solid yellow; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Report</h1>
        <p><strong>Language:</strong> {test_result.get('language', 'Unknown')}</p>
        <p><strong>Project Directory:</strong> {test_result.get('project_dir', 'Unknown')}</p>
        <p><strong>Generated:</strong> {test_result.get('timestamp', 'Unknown')}</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        {self._generate_html_summary(test_result)}
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        {self._generate_html_recommendations(test_result)}
    </div>
    
    <div>
        <h2>Detailed Results</h2>
        {self._generate_html_details(test_result)}
    </div>
</body>
</html>
        """
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return output_path
        except Exception as e:
            return f"Failed to generate HTML report: {str(e)}"
    
    def _generate_html_summary(self, test_result: Dict) -> str:
        """Generate HTML summary section"""
        summary = test_result.get('summary', {}).get('test_results_summary', {})
        
        return f"""
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Tests</td><td>{summary.get('total_tests_run', 0)}</td></tr>
            <tr><td class="passed">Passed Tests</td><td>{summary.get('passed_tests', 0)}</td></tr>
            <tr><td class="failed">Failed Tests</td><td>{summary.get('failed_tests', 0)}</td></tr>
            <tr><td class="skipped">Skipped Tests</td><td>{summary.get('skipped_tests', 0)}</td></tr>
            <tr><td>Success Rate</td><td>{summary.get('success_rate_percentage', 0)}%</td></tr>
            <tr><td>Overall Status</td><td class="{'passed' if summary.get('all_tests_passed') else 'failed'}">{summary.get('all_tests_passed', False) and 'PASSED' or 'FAILED'}</td></tr>
        </table>
        """
    
    def _generate_html_recommendations(self, test_result: Dict) -> str:
        """Generate HTML recommendations section"""
        recommendations = test_result.get('recommendations', [])
        
        if not recommendations:
            return "<p>No specific recommendations - test results look good!</p>"
        
        html = "<ul>"
        for rec in recommendations:
            severity_class = rec.get('severity', 'medium')
            html += f'<li class="{severity_class}"><strong>{rec.get("type", "").replace("_", " ").title()}:</strong> {rec.get("message", "")} - {rec.get("suggestion", "")}</li>'
        html += "</ul>"
        
        return html
    
    def _generate_html_details(self, test_result: Dict) -> str:
        """Generate HTML detailed results section"""
        failed_tests = test_result.get('test_results', {}).get('failed_test_details', [])
        
        if not failed_tests:
            return "<p>No test failures to report.</p>"
        
        html = "<h3>Failed Tests</h3><table><tr><th>Test Name</th><th>Type</th><th>Message</th></tr>"
        for test in failed_tests:
            html += f"<tr><td>{test.get('name', 'Unknown')}</td><td>{test.get('type', 'Unknown')}</td><td>{test.get('message', '')}</td></tr>"
        html += "</table>"
        
        return html
