from typing import Dict, Any
import json
import os
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent


class DocumentAnalyzer(BaseAgent):
    """
    Enhanced Document Analyzer Agent with Unlimited Scenario Generation & Duplicate Prevention
    
    🎯 PURPOSE:
    -----------
    Analyzes documents and extracts structured information including comprehensive, unlimited scenarios
    with clear intentions, purposes, and expected outcomes. This agent transforms unstructured 
    document content into extensive, actionable development scenarios without quantity limits.
    
    ✨ KEY ENHANCEMENTS:
    -------------------
    ✅ Unlimited Scenario Generation - Generates 15-25+ scenarios to comprehensively cover ALL functionality
    ✅ Duplicate Prevention - Advanced detection and removal of duplicate scenarios
    ✅ Detailed Scenario Structure - Each scenario includes name, description, purpose, category, priority, and expected outcome
    ✅ Clear Intentions - Every scenario explains WHY it exists and what it validates
    ✅ Comprehensive Coverage - Multiple scenarios per category (basic/advanced/integration/error_handling/performance)
    ✅ Uniqueness Validation - Ensures each scenario tests different aspects or conditions
    ✅ Smart Duplicate Resolution - Keeps the most detailed version when duplicates are found
    ✅ Enhanced Logging - Provides detailed analysis summaries and duplicate detection reports
    
    🔄 DUPLICATE DETECTION:
    ----------------------
    - Analyzes scenario names and descriptions for similarity
    - Removes exact duplicates automatically
    - Preserves the most detailed version when duplicates are found
    - Reports duplicate detection statistics in logs
    - Ensures final scenario list contains only unique test cases
    
    📊 OUTPUT FORMAT:
    ----------------
    Generates structured JSON with:
    - Language and version detection
    - Product identification
    - Comprehensive scenario list (15-25+ unique scenarios)
    - Project setup information
    - Analysis summary with scenario statistics and duplicate reports
    
    🎯 SCENARIO EXAMPLE:
    -------------------
    {
        "name": "User Authentication with Valid Credentials",
        "description": "Verify user login with correct credentials and token generation",
        "purpose": "Ensures the authentication system works and establishes secure sessions",
        "category": "basic",
        "priority": "high", 
        "expectedOutcome": "User receives auth token and accesses dashboard"
    }
    """
    
    def __init__(self, llm: Any):
        super().__init__("Document Analyzer", llm)
        self.prompt_template = PromptTemplate(
            input_variables=["document_content"],
            template="""
            You are a document analyzer agent. Your task is to analyze the provided document content and extract key information in a specific JSON format.
            
            Document Content:
            {document_content}
            
            Based on the document content, extract and determine:
            1. Programming language mentioned or most suitable for the project
            2. Product name or main technology/framework discussed
            3. Version information - Look for specific version numbers, release versions, or version identifiers in the document. If no specific version is mentioned, analyze the content to determine the most likely current version being discussed (e.g., if .NET 8 features are mentioned, use "8.0", if Python 3.11 syntax is shown, use "3.11", etc.)
            4. List of detailed scenarios with clear intentions and explanations
            5. Project setup information including installation steps, dependencies, and configuration
            
            For the scenarios, create comprehensive and meaningful test scenarios that:
            - Have clear, descriptive names that explain what is being tested
            - Include detailed descriptions of the scenario's purpose and expected behavior
            - Cover different aspects of functionality (basic operations, edge cases, error handling, integration)
            - Explain WHY each scenario is important for the application
            - Provide enough detail for implementation without being overly technical
            
            You must respond with ONLY a valid JSON object in this exact format:
            {{
                "language": "<programming_language>",
                "productName": "<product_or_technology_name>",
                "version": "<specific_version_number_or_identifier>",
                "scenarioList": [
                    {{
                        "name": "<clear_scenario_name>",
                        "description": "<detailed_description_of_what_this_scenario_does>",
                        "purpose": "<why_this_scenario_is_important_and_what_it_validates>",
                        "category": "<category: basic|advanced|integration|error_handling|performance>",
                        "priority": "<priority: high|medium|low>",
                        "expectedOutcome": "<what_should_happen_when_this_scenario_is_executed>"
                    }}
                ],
                "projectsetupInfo": {{
                    "installation": "<installation_steps>",
                    "dependencies": ["<dependency1>", "<dependency2>"],
                    "configuration": "<configuration_details>",
                    "gettingStarted": "<how_to_get_started>"
                }}
            }}
            
            SCENARIO GUIDELINES:
            - Create as many scenarios as needed to comprehensively cover ALL functionality and use cases
            - Generate 15-25 scenarios or more if the document contains extensive functionality
            - Include multiple scenarios for each category: basic, advanced, integration, error_handling, performance
            - Each scenario should be unique and implementable as actual code
            - Focus on real-world usage patterns and business value
            - Avoid generic "test this feature" descriptions - be specific about what and why
            - Ensure NO duplicate scenarios - each must test different aspects or conditions
            - Cover edge cases, boundary conditions, and various user workflows
            - Include both positive and negative test scenarios
            
            EXAMPLE SCENARIO STRUCTURE:
            {{
                "name": "User Authentication with Valid Credentials",
                "description": "Verify that a user can successfully log in to the system using correct username and password, and receives appropriate access tokens and session data",
                "purpose": "Ensures the core authentication mechanism works correctly and users can access protected resources. This validates the security foundation of the application",
                "category": "basic",
                "priority": "high",
                "expectedOutcome": "User receives authentication token, session is established, user is redirected to dashboard with appropriate permissions"
            }}
            
            IMPORTANT: For the version field, be specific:
            - If specific version numbers are mentioned (e.g., "Python 3.11", ".NET 8.0", "Node.js 18.x"), use those exact versions
            - If framework features suggest a specific version (e.g., async/await in Python suggests 3.7+, top-level programs in C# suggest .NET 6+), infer and specify that version
            - If modern syntax or recent features are shown, specify a recent stable version rather than "latest"
            - Only use "latest" if absolutely no version clues can be determined from the content
            
            Make sure the JSON is valid and complete. Do not include any other text or explanations.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Analyze the document content and generate unlimited unique scenarios with duplicate detection"""
        self.log("Starting document analysis with unlimited scenario generation and duplicate prevention")
        
        try:
            # Get the analysis result from the LLM
            self.log("Sending document content to LLM for comprehensive scenario generation...")
            analysis_result = self.chain.invoke({"document_content": input_data})
            
            # Try to parse the JSON response
            try:
                parsed_result = json.loads(analysis_result["text"].strip())
                self.log("Successfully parsed LLM response as JSON")
            except json.JSONDecodeError as e:
                # If JSON parsing fails, log the error and re-raise
                self.log(f"Failed to parse JSON from LLM response: {str(e)}")
                self.log(f"Raw LLM response: {analysis_result['text']}")
                raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
            
            # Store original count before validation
            original_count = len(parsed_result.get("scenarioList", []))
            self.log(f"📊 Initial scenario count from LLM: {original_count}")
            
            # Validate the structure and content (includes duplicate removal)
            self._validate_analysis_result(parsed_result)
            
            # Get final count after duplicate removal
            final_count = len(parsed_result.get("scenarioList", []))
            duplicate_count = original_count - final_count
            
            if duplicate_count > 0:
                self.log(f"🔍 Duplicate Detection Summary: Removed {duplicate_count} duplicates from {original_count} scenarios")
            else:
                self.log("✅ No duplicates detected - all scenarios are unique")
            
            # Log the analysis summary
            self._log_analysis_summary(parsed_result)
            
            # Generate temporary JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "workflow_outputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            json_filename = f"{output_dir}/document_analysis_{timestamp}.json"
            
            # Write the structured output to a JSON file
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(parsed_result, f, indent=2, ensure_ascii=False)
            
            output = {
                "agent": self.name,
                "input": input_data,
                "output": parsed_result,
                "json_file": json_filename,
                "status": "success",
                "original_scenario_count": original_count,
                "final_scenario_count": final_count,
                "duplicates_removed": duplicate_count,
                "analysis_summary": self._create_analysis_summary(parsed_result)
            }
            
            self.log(f"Document analysis completed successfully. JSON file created: {json_filename}")
            self.log(f"Generated {final_count} unique scenarios (removed {duplicate_count} duplicates)")
            return output
            
        except Exception as e:
            self.log(f"Error during document analysis: {str(e)}")
            return {
                "agent": self.name,
                "input": input_data,
                "output": None,
                "status": "error",
                "error": str(e)
            }
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> None:
        """Validate the structure and content of the analysis result"""
        required_fields = ["language", "productName", "version", "scenarioList", "projectsetupInfo"]
        
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate scenarios have the required structure
        scenarios = result.get("scenarioList", [])
        if not isinstance(scenarios, list) or len(scenarios) == 0:
            raise ValueError("scenarioList must be a non-empty list")
        
        # Check for duplicate scenarios
        scenario_signatures = set()
        duplicate_count = 0
        
        scenario_required_fields = ["name", "description", "purpose", "category", "priority", "expectedOutcome"]
        for i, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                raise ValueError(f"Scenario {i+1} must be a dictionary")
            
            for field in scenario_required_fields:
                if field not in scenario:
                    raise ValueError(f"Scenario {i+1} missing required field: {field}")
            
            # Create a signature for duplicate detection
            # Use name and key parts of description for uniqueness check
            name = scenario.get("name", "").lower().strip()
            description_key = scenario.get("description", "").lower()[:100].strip()  # First 100 chars
            signature = f"{name}|{description_key}"
            
            if signature in scenario_signatures:
                duplicate_count += 1
                self.log(f"⚠️  Potential duplicate detected: {scenario.get('name', 'Unnamed')}")
            else:
                scenario_signatures.add(signature)
        
        if duplicate_count > 0:
            self.log(f"🔍 Duplicate Detection: Found {duplicate_count} potential duplicates")
            # Remove duplicates from the result
            result["scenarioList"] = self._remove_duplicate_scenarios(scenarios)
            self.log(f"✅ Removed duplicates. Final scenario count: {len(result['scenarioList'])}")
        
        self.log("✅ Analysis result validation passed")
    
    def _remove_duplicate_scenarios(self, scenarios: list) -> list:
        """Remove duplicate scenarios while preserving the most detailed ones"""
        seen_signatures = {}
        unique_scenarios = []
        
        for scenario in scenarios:
            # Create signature for duplicate detection
            name = scenario.get("name", "").lower().strip()
            description_key = scenario.get("description", "").lower()[:100].strip()
            signature = f"{name}|{description_key}"
            
            if signature not in seen_signatures:
                seen_signatures[signature] = True
                unique_scenarios.append(scenario)
            else:
                # If we find a duplicate, keep the one with more detailed description
                existing_index = None
                for i, existing in enumerate(unique_scenarios):
                    existing_name = existing.get("name", "").lower().strip()
                    existing_desc_key = existing.get("description", "").lower()[:100].strip()
                    existing_sig = f"{existing_name}|{existing_desc_key}"
                    
                    if existing_sig == signature:
                        existing_index = i
                        break
                
                if existing_index is not None:
                    # Compare detail levels and keep the more comprehensive one
                    existing_detail_score = len(unique_scenarios[existing_index].get("description", ""))
                    current_detail_score = len(scenario.get("description", ""))
                    
                    if current_detail_score > existing_detail_score:
                        unique_scenarios[existing_index] = scenario
                        self.log(f"🔄 Replaced less detailed duplicate: {scenario.get('name', 'Unnamed')}")
        
        return unique_scenarios
    
    def _log_analysis_summary(self, result: Dict[str, Any]) -> None:
        """Log a summary of the analysis results"""
        self.log("📊 Analysis Summary:")
        self.log(f"  - Language: {result.get('language', 'Unknown')}")
        self.log(f"  - Product: {result.get('productName', 'Unknown')}")
        self.log(f"  - Version: {result.get('version', 'Unknown')}")
        
        scenarios = result.get("scenarioList", [])
        self.log(f"  - Final Unique Scenarios: {len(scenarios)}")
        
        # Count scenarios by category and priority
        categories = {}
        priorities = {}
        for scenario in scenarios:
            cat = scenario.get("category", "unknown")
            pri = scenario.get("priority", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            priorities[pri] = priorities.get(pri, 0) + 1
        
        self.log(f"  - Categories Distribution: {dict(categories)}")
        self.log(f"  - Priorities Distribution: {dict(priorities)}")
        
        # Check for comprehensive coverage
        total_scenarios = len(scenarios)
        if total_scenarios >= 15:
            self.log("✅ Comprehensive scenario coverage achieved (15+ scenarios)")
        elif total_scenarios >= 10:
            self.log("⚠️  Good scenario coverage (10-14 scenarios)")
        else:
            self.log("❌ Limited scenario coverage (<10 scenarios) - may need more analysis")
        
        # Log scenario names with categories
        self.log("📝 Generated Unique Scenarios:")
        for i, scenario in enumerate(scenarios, 1):
            category_emoji = self._get_category_emoji(scenario.get('category', 'unknown'))
            priority_emoji = self._get_priority_emoji(scenario.get('priority', 'unknown'))
            self.log(f"  {i:2d}. {scenario.get('name', 'Unnamed')} {category_emoji}{priority_emoji}")
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for scenario category"""
        category_emojis = {
            'basic': '🟢',
            'advanced': '🔵', 
            'integration': '🟣',
            'error_handling': '🔴',
            'performance': '🟡',
            'unknown': '⚪'
        }
        return category_emojis.get(category.lower(), '⚪')
    
    def _get_priority_emoji(self, priority: str) -> str:
        """Get emoji for scenario priority"""
        priority_emojis = {
            'high': '🔥',
            'medium': '⭐',
            'low': '💫',
            'unknown': '❓'
        }
        return priority_emojis.get(priority.lower(), '❓')
    
    def _create_analysis_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured summary of the analysis for downstream agents"""
        scenarios = result.get("scenarioList", [])
        
        summary = {
            "language": result.get("language"),
            "product_name": result.get("productName"),
            "version": result.get("version"),
            "total_unique_scenarios": len(scenarios),
            "scenario_categories": {},
            "scenario_priorities": {},
            "high_priority_scenarios": [],
            "key_dependencies": result.get("projectsetupInfo", {}).get("dependencies", []),
            "coverage_assessment": self._assess_scenario_coverage(scenarios)
        }
        
        # Analyze scenarios
        for scenario in scenarios:
            # Count categories
            category = scenario.get("category", "unknown")
            summary["scenario_categories"][category] = summary["scenario_categories"].get(category, 0) + 1
            
            # Count priorities
            priority = scenario.get("priority", "unknown")
            summary["scenario_priorities"][priority] = summary["scenario_priorities"].get(priority, 0) + 1
            
            # Collect high priority scenarios
            if priority == "high":
                summary["high_priority_scenarios"].append({
                    "name": scenario.get("name"),
                    "category": category
                })
        
        return summary
    
    def _assess_scenario_coverage(self, scenarios: list) -> Dict[str, Any]:
        """Assess the coverage quality of generated scenarios"""
        total = len(scenarios)
        categories = set()
        priorities = set()
        
        for scenario in scenarios:
            categories.add(scenario.get("category", "unknown"))
            priorities.add(scenario.get("priority", "unknown"))
        
        assessment = {
            "total_scenarios": total,
            "unique_categories": len(categories),
            "unique_priorities": len(priorities),
            "coverage_level": "comprehensive" if total >= 15 else "moderate" if total >= 10 else "basic",
            "categories_covered": list(categories),
            "priorities_covered": list(priorities)
        }
        
        # Assess completeness
        expected_categories = {"basic", "advanced", "integration", "error_handling", "performance"}
        missing_categories = expected_categories - categories
        if missing_categories:
            assessment["missing_categories"] = list(missing_categories)
        
        return assessment
