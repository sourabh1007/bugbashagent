"""
Code Runner Tool

Provides capabilities to run generated applications and tests with real-time monitoring,
debugging support, and performance analysis.
"""

import os
import subprocess
import threading
import time
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    peak_memory_mb: float
    cpu_usage_percent: float
    process_id: Optional[int] = None
    timeout_occurred: bool = False
    error_message: Optional[str] = None


class ProcessMonitor:
    """Monitors running processes for resource usage"""
    
    def __init__(self, pid: int):
        self.pid = pid
        self.peak_memory = 0.0
        self.cpu_readings = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start monitoring process resources"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring and return statistics"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        avg_cpu = sum(self.cpu_readings) / len(self.cpu_readings) if self.cpu_readings else 0.0
        return {
            'peak_memory_mb': self.peak_memory,
            'average_cpu_percent': avg_cpu,
            'cpu_readings_count': len(self.cpu_readings)
        }
    
    def _monitor_loop(self):
        """Monitor loop running in separate thread"""
        try:
            process = psutil.Process(self.pid)
            while self.monitoring:
                try:
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
                    self.peak_memory = max(self.peak_memory, memory_mb)
                    
                    cpu_percent = process.cpu_percent()
                    self.cpu_readings.append(cpu_percent)
                    
                    time.sleep(0.1)  # Monitor every 100ms
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
        except Exception:
            pass  # Process monitoring is best effort


class CodeRunner:
    """Tool for running generated code with monitoring and debugging capabilities"""
    
    def __init__(self):
        self.run_commands = {
            'csharp': {
                'console': ['dotnet', 'run'],
                'test': ['dotnet', 'test', '--verbosity', 'normal'],
                'test_with_coverage': ['dotnet', 'test', '--collect:"XPlat Code Coverage"'],
                'debug': ['dotnet', 'run', '--configuration', 'Debug'],
                'release': ['dotnet', 'run', '--configuration', 'Release']
            },
            'java': {
                'console': ['mvn', 'exec:java'],
                'test': ['mvn', 'test'],
                'test_verbose': ['mvn', 'test', '-Dtest.verbose=true'],
                'debug': ['mvn', 'exec:java', '-Dexec.args="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005"'],
                'spring_boot': ['mvn', 'spring-boot:run']
            },
            'python': {
                'console': ['python', 'main.py'],
                'module': ['python', '-m'],
                'test': ['pytest', '-v'],
                'test_coverage': ['pytest', '--cov=.', '--cov-report=html'],
                'debug': ['python', '-m', 'pdb'],
                'interactive': ['python', '-i']
            },
            'javascript': {
                'console': ['node', 'index.js'],
                'npm_start': ['npm', 'start'],
                'test': ['npm', 'test'],
                'test_watch': ['npm', 'run', 'test:watch'],
                'debug': ['node', '--inspect', 'index.js'],
                'dev': ['npm', 'run', 'dev']
            },
            'go': {
                'console': ['go', 'run', 'main.go'],
                'test': ['go', 'test', '-v', './...'],
                'test_coverage': ['go', 'test', '-coverprofile=coverage.out', './...'],
                'debug': ['dlv', 'debug'],
                'race': ['go', 'run', '-race', 'main.go']
            },
            'rust': {
                'console': ['cargo', 'run'],
                'test': ['cargo', 'test'],
                'test_verbose': ['cargo', 'test', '--', '--nocapture'],
                'debug': ['cargo', 'run', '--', '--debug'],
                'release': ['cargo', 'run', '--release'],
                'bench': ['cargo', 'bench']
            }
        }
    
    def run_application(self, project_dir: str, language: str, run_type: str = 'console', 
                       timeout: int = 30, monitor_resources: bool = True) -> ExecutionResult:
        """Run the application with monitoring"""
        start_time = time.time()
        
        # Get run command
        commands = self.run_commands.get(language.lower(), {})
        if not commands:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Unsupported language: {language}",
                execution_time=0.0,
                peak_memory_mb=0.0,
                cpu_usage_percent=0.0,
                error_message=f"Language {language} not supported for execution"
            )
        
        run_cmd = commands.get(run_type)
        if not run_cmd:
            available_types = list(commands.keys())
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Unsupported run type: {run_type}. Available: {available_types}",
                execution_time=0.0,
                peak_memory_mb=0.0,
                cpu_usage_percent=0.0,
                error_message=f"Run type {run_type} not available"
            )
        
        try:
            # Start the process
            process = subprocess.Popen(
                run_cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start monitoring if requested
            monitor = None
            if monitor_resources and process.pid:
                monitor = ProcessMonitor(process.pid)
                monitor.start_monitoring()
            
            try:
                # Wait for completion with timeout
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
                timeout_occurred = False
                
            except subprocess.TimeoutExpired:
                # Handle timeout
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -9  # SIGKILL
                timeout_occurred = True
            
            execution_time = time.time() - start_time
            
            # Get resource statistics
            peak_memory = 0.0
            avg_cpu = 0.0
            if monitor:
                stats = monitor.stop_monitoring()
                peak_memory = stats['peak_memory_mb']
                avg_cpu = stats['average_cpu_percent']
            
            return ExecutionResult(
                success=exit_code == 0 and not timeout_occurred,
                exit_code=exit_code,
                stdout=stdout or "",
                stderr=stderr or "",
                execution_time=execution_time,
                peak_memory_mb=peak_memory,
                cpu_usage_percent=avg_cpu,
                process_id=process.pid,
                timeout_occurred=timeout_occurred,
                error_message="Timeout occurred" if timeout_occurred else None
            )
            
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Command not found: {' '.join(run_cmd)}",
                execution_time=time.time() - start_time,
                peak_memory_mb=0.0,
                cpu_usage_percent=0.0,
                error_message=f"Command not found: {' '.join(run_cmd)}"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time,
                peak_memory_mb=0.0,
                cpu_usage_percent=0.0,
                error_message=str(e)
            )
    
    def run_tests_with_monitoring(self, project_dir: str, language: str, 
                                 test_type: str = 'test', timeout: int = 120) -> ExecutionResult:
        """Run tests with detailed monitoring and analysis"""
        return self.run_application(project_dir, language, test_type, timeout, monitor_resources=True)
    
    def run_performance_test(self, project_dir: str, language: str, 
                           iterations: int = 5, timeout_per_run: int = 30) -> Dict[str, Any]:
        """Run multiple iterations to gather performance statistics"""
        results = []
        
        for i in range(iterations):
            print(f"🏃 Running performance iteration {i + 1}/{iterations}...")
            result = self.run_application(
                project_dir, language, 'console', 
                timeout_per_run, monitor_resources=True
            )
            
            if result.success:
                results.append({
                    'iteration': i + 1,
                    'execution_time': result.execution_time,
                    'peak_memory_mb': result.peak_memory_mb,
                    'cpu_usage_percent': result.cpu_usage_percent
                })
            else:
                print(f"⚠️ Iteration {i + 1} failed: {result.error_message}")
        
        if not results:
            return {
                'success': False,
                'error': 'All performance test iterations failed',
                'results': []
            }
        
        # Calculate statistics
        execution_times = [r['execution_time'] for r in results]
        memory_usage = [r['peak_memory_mb'] for r in results]
        cpu_usage = [r['cpu_usage_percent'] for r in results]
        
        return {
            'success': True,
            'iterations': len(results),
            'execution_time': {
                'mean': sum(execution_times) / len(execution_times),
                'min': min(execution_times),
                'max': max(execution_times),
                'std_dev': self._calculate_std_dev(execution_times)
            },
            'memory_usage_mb': {
                'mean': sum(memory_usage) / len(memory_usage),
                'min': min(memory_usage),
                'max': max(memory_usage),
                'std_dev': self._calculate_std_dev(memory_usage)
            },
            'cpu_usage_percent': {
                'mean': sum(cpu_usage) / len(cpu_usage),
                'min': min(cpu_usage),
                'max': max(cpu_usage),
                'std_dev': self._calculate_std_dev(cpu_usage)
            },
            'detailed_results': results
        }
    
    def run_interactive_session(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Start an interactive session for debugging and exploration"""
        interactive_commands = {
            'python': ['python', '-i'],
            'javascript': ['node'],
            'go': ['go', 'run', '-i'],  # Note: Go doesn't have true interactive mode
            'rust': ['cargo', 'run', '--bin', 'interactive']  # Custom interactive binary
        }
        
        cmd = interactive_commands.get(language.lower())
        if not cmd:
            return {
                'success': False,
                'error': f'Interactive mode not supported for {language}',
                'available_languages': list(interactive_commands.keys())
            }
        
        try:
            # For interactive sessions, we don't capture output - let it run in terminal
            process = subprocess.Popen(
                cmd,
                cwd=project_dir,
                stdin=None,
                stdout=None,
                stderr=None
            )
            
            return {
                'success': True,
                'process_id': process.pid,
                'command': ' '.join(cmd),
                'message': f'Interactive {language} session started with PID {process.pid}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(cmd)
            }
    
    def get_available_run_types(self, language: str) -> List[str]:
        """Get available run types for a language"""
        commands = self.run_commands.get(language.lower(), {})
        return list(commands.keys())
    
    def check_runtime_requirements(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Check if runtime requirements are met"""
        requirements = {
            'csharp': {
                'commands': ['dotnet'],
                'files': ['*.csproj', '*.sln'],
                'env_vars': []
            },
            'java': {
                'commands': ['java', 'mvn'],
                'files': ['pom.xml', 'build.gradle'],
                'env_vars': ['JAVA_HOME']
            },
            'python': {
                'commands': ['python'],
                'files': ['requirements.txt', 'setup.py', 'main.py'],
                'env_vars': []
            },
            'javascript': {
                'commands': ['node', 'npm'],
                'files': ['package.json'],
                'env_vars': []
            },
            'go': {
                'commands': ['go'],
                'files': ['go.mod'],
                'env_vars': ['GOPATH', 'GOROOT']
            },
            'rust': {
                'commands': ['cargo', 'rustc'],
                'files': ['Cargo.toml'],
                'env_vars': []
            }
        }
        
        lang_reqs = requirements.get(language.lower(), {})
        if not lang_reqs:
            return {
                'supported': False,
                'error': f'Language {language} not supported'
            }
        
        result = {
            'supported': True,
            'language': language,
            'commands': {},
            'files': {},
            'environment': {},
            'ready_to_run': True
        }
        
        # Check commands
        for cmd in lang_reqs.get('commands', []):
            try:
                subprocess.run([cmd, '--version'], 
                             capture_output=True, timeout=5)
                result['commands'][cmd] = True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                result['commands'][cmd] = False
                result['ready_to_run'] = False
        
        # Check files
        for file_pattern in lang_reqs.get('files', []):
            found = False
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    if file_pattern.replace('*', '') in file:
                        found = True
                        break
                if found:
                    break
            result['files'][file_pattern] = found
        
        # Check environment variables
        for env_var in lang_reqs.get('env_vars', []):
            value = os.environ.get(env_var)
            result['environment'][env_var] = {
                'set': value is not None,
                'value': value if value else None
            }
            if not value and env_var in ['JAVA_HOME']:  # Critical env vars
                result['ready_to_run'] = False
        
        return result
    
    def create_execution_report(self, result: ExecutionResult, project_dir: str, 
                              language: str, run_type: str) -> str:
        """Create a detailed execution report"""
        report = f"""# Code Execution Report

## Execution Summary
- **Language**: {language}
- **Run Type**: {run_type}
- **Project Directory**: {project_dir}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Success**: {'✅ Yes' if result.success else '❌ No'}
- **Exit Code**: {result.exit_code}

## Performance Metrics
- **Execution Time**: {result.execution_time:.3f} seconds
- **Peak Memory Usage**: {result.peak_memory_mb:.2f} MB
- **Average CPU Usage**: {result.cpu_usage_percent:.1f}%
- **Process ID**: {result.process_id or 'N/A'}

## Output Analysis

### Standard Output
```
{result.stdout or 'No output'}
```

### Standard Error
```
{result.stderr or 'No errors'}
```

## Issues and Recommendations
"""
        
        if result.timeout_occurred:
            report += """
⚠️ **Timeout Occurred**
- The process exceeded the maximum allowed execution time
- Consider optimizing performance or increasing timeout limit
- Check for infinite loops or blocking operations
"""
        
        if result.exit_code != 0 and not result.timeout_occurred:
            report += f"""
❌ **Non-Zero Exit Code ({result.exit_code})**
- The application terminated with an error
- Check the error output above for details
- Verify all dependencies are installed and configured
"""
        
        if result.peak_memory_mb > 100:
            report += f"""
📊 **High Memory Usage ({result.peak_memory_mb:.1f} MB)**
- Consider memory optimization techniques
- Check for memory leaks or excessive allocations
- Monitor memory usage in production environments
"""
        
        if result.cpu_usage_percent > 80:
            report += f"""
🔥 **High CPU Usage ({result.cpu_usage_percent:.1f}%)**
- Application is CPU-intensive
- Consider algorithm optimization
- May benefit from parallel processing
"""
        
        if result.success:
            report += """
✅ **Execution Successful**
- Application completed without errors
- Performance metrics within acceptable ranges
- Ready for further testing or deployment
"""
        
        return report
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
