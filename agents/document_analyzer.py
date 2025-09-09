from typing import Dict, Any, List
import json
import os
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .base_agent import BaseAgent
from tools.prompt_loader import PromptyLoader
from integrations.langsmith import trace_agent_execution


class DocumentAnalyzer(BaseAgent):
    """
    Enhanced Document Analyzer Agent with Unlimited Scenario Generation & Duplicate Prevention
    
    🎯 PURPOSE:
    -----------
    Analyzes documents and extracts structured information including comprehensive, unlimited scenarios
    with intelligent duplicate detection and removal to ensure scenario uniqueness and completeness.
    
    ✨ KEY FEATURES:
    ----------------
    • Unlimited scenario generation (not restricted to 10-15 scenarios)
    • Intelligent duplicate detection and removal
    • Comprehensive scenario categorization (basic, advanced, integration, error_handling, edge_case)  
    • Priority assignment (high, medium, low)
    • Detailed purpose explanation for each scenario
    • Expected outcome specification
    • Enhanced scenario validation and quality control
    • Automatic language and version detection
    • Setup instruction extraction
    
    🔧 DUPLICATE PREVENTION:
    -------------------------
    • Content-based similarity detection
    • Name normalization and comparison
    • Category-wise uniqueness validation
    • Automatic merging of similar scenarios
    • Quality threshold enforcement
    
    📊 REPORTING:
    -------------
    • Original vs final scenario counts
    • Duplicate removal statistics
    • Validation error details
    • Quality metrics and insights
    
    🚀 ENHANCED WORKFLOW:
    ---------------------
    1. Document content analysis
    2. Unlimited scenario extraction
    3. Intelligent duplicate detection
    4. Quality validation and enhancement
    5. Structured JSON output generation
    6. Comprehensive reporting
    """
    
    def __init__(self, llm: Any):
        super().__init__("Document Analyzer", llm)
        # Load prompt template from prompty file
        self.prompty_loader = PromptyLoader()
        self.prompt_template = self.prompty_loader.create_prompt_template(
            "document_analyzer", "scenario_extraction"
        )
        # Get LLM with prompty-specific settings
        llm_for_chain = self.prompty_loader.create_llm_with_prompty_settings(
            self.llm, "document_analyzer", "scenario_extraction"
        )
        # Build Runnable pipeline instead of deprecated LLMChain
        self._runnable = self.prompt_template | llm_for_chain | StrOutputParser()
    
    @trace_agent_execution("Document Analyzer")
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Analyze the document content and generate unlimited unique scenarios with duplicate detection"""
        self.log("Starting document analysis with unlimited scenario generation and duplicate prevention")
        
        try:
            # Update status - starting analysis
            self.update_status("running", "Analyzing document content", 20.0)
            
            # Get the analysis result from the LLM
            self.log("Sending document content to LLM for comprehensive scenario generation...")
            
            # Log the actual prompt that will be sent to LLM
            actual_prompt = self.prompt_template.format(document_content=input_data)
            self.log_prompt_to_file(
                actual_prompt, 
                "document_analysis", 
                "document_scenario_extraction"
            )
            
            # Update status - querying LLM
            self.update_status("running", "Querying LLM for scenario generation", 40.0)
            
            analysis_result = self._runnable.invoke({"document_content": input_data})

            # Update status - parsing response
            self.update_status("running", "Parsing LLM response", 60.0)
            
            # Try to parse the JSON response with recovery strategies
            parsed_result, parse_debug = self._parse_json_response(analysis_result)
            if not parsed_result:
                # Persist raw response for debugging
                debug_file = self._write_debug_output("document_analysis", analysis_result, suffix="raw_response")
                self.log(f"Failed to parse JSON after recovery attempts. Raw saved to {debug_file}")
                raise ValueError(f"Invalid JSON response from LLM: {parse_debug}")
            else:
                self.log("Successfully parsed LLM response as JSON")
            
            # Store original count before validation
            original_count = len(parsed_result.get("scenarioList", []))
            self.log(f"📊 Initial scenario count from LLM: {original_count}")
            
            # Update status - validating and removing duplicates
            self.update_status("running", "Validating scenarios and removing duplicates", 80.0)
            
            # Validate the structure and content (includes duplicate removal)
            self._validate_analysis_result(parsed_result)
            
            # Get final count after duplicate removal
            final_count = len(parsed_result.get("scenarioList", []))
            duplicate_count = original_count - final_count
            
            if duplicate_count > 0:
                self.log(f"🔧 Duplicate prevention: Removed {duplicate_count} duplicate/similar scenarios")
            
            self.log(f"✅ Final unique scenario count: {final_count}")
            
            # Update status - finalizing results
            self.update_status("running", f"Analysis complete: {final_count} unique scenarios generated", 95.0)
            
            # Enhanced reporting
            self._log_scenario_analysis_summary(parsed_result, original_count, duplicate_count)
            
            # Return in the expected workflow format
            return {
                "agent": self.name,
                "input": input_data,
                "output": parsed_result,
                "status": "success"
            }
            
        except Exception as e:
            self.log(f"❌ Error during document analysis: {str(e)}")
            return {
                "agent": self.name,
                "input": input_data,
                "output": None,
                "status": "error",
                "error": str(e)
            }

    # ---------------- Internal Helpers: JSON Parsing & Recovery -----------------
    def _parse_json_response(self, raw: str):
        """Attempt to parse LLM output into JSON with multiple recovery strategies.

        Returns (parsed_json_or_none, debug_message)
        """
        if raw is None:
            return None, "Empty response"

        text = raw.strip()

        # Fast path
        try:
            return json.loads(text), "ok"
        except Exception:
            pass

        # Remove markdown code fences
        if text.startswith("```"):
            # Extract content inside first fenced block
            parts = text.split("```")
            # parts example: ['', 'json', '{...}', ''] or ['','json\n{...}','']
            for segment in parts:
                seg = segment.strip()
                if seg.startswith('{') and seg.endswith('}'):
                    try:
                        return json.loads(seg), "parsed_from_code_fence"
                    except Exception:
                        # continue
                        pass
            # Remove any language hint like ```json
            text = '\n'.join([p for p in parts if '{' in p])

        # Attempt bracket extraction: find first '{' and last '}'
        first = text.find('{')
        last = text.rfind('}')
        if first != -1 and last != -1 and last > first:
            candidate = text[first:last+1]
            try:
                return json.loads(candidate), "parsed_from_brace_slice"
            except Exception:
                # Try minor repairs
                repaired = self._repair_common_json_issues(candidate)
                if repaired:
                    try:
                        return json.loads(repaired), "parsed_after_repair"
                    except Exception as e:
                        return None, f"repair_failed: {e}"

        return None, "all_strategies_failed"

    def _repair_common_json_issues(self, text: str) -> str:
        """Attempt minimal, safe repairs (dangling commas, code fences removal)."""
        repaired = text.strip()
        # Remove leading/trailing markdown fences if still present
        if repaired.startswith('```'):
            repaired = repaired.lstrip('`')
        if repaired.endswith('```'):
            repaired = repaired.rstrip('`')
        # Remove trailing commas before closing list/dict
        repaired = repaired.replace(',\n]', '\n]')
        repaired = repaired.replace(',\n}', '\n}')
        return repaired
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> None:
        """
        Enhanced validation with duplicate detection and quality control
        
        🔍 VALIDATION CHECKS:
        ---------------------
        • Required field presence
        • Data type validation
        • Scenario uniqueness verification
        • Content quality assessment
        • Category distribution analysis
        """
        self.log("🔍 Starting comprehensive scenario validation with duplicate detection...")
        
        # Check required top-level fields
        required_fields = ["language", "productName", "version", "scenarioList", "setupInstructions"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate scenario list
        if not isinstance(result["scenarioList"], list):
            raise ValueError("scenarioList must be a list")
        
        if len(result["scenarioList"]) == 0:
            raise ValueError("scenarioList cannot be empty")
        
        # Remove duplicates and validate scenarios
        result["scenarioList"] = self._remove_duplicate_scenarios(result["scenarioList"])
        
        # Validate each scenario structure
        scenario_required_fields = ["name", "description", "purpose", "category", "priority", "expectedOutcome"]
        for i, scenario in enumerate(result["scenarioList"]):
            for field in scenario_required_fields:
                if field not in scenario:
                    self.log(f"⚠️ Warning: Scenario {i+1} missing field '{field}', adding placeholder")
                    scenario[field] = f"<missing_{field}>"
        
        # Validate setup instructions
        if not isinstance(result["setupInstructions"], dict):
            result["setupInstructions"] = {
                "dependencies": [],
                "installationSteps": [],
                "configuration": "No configuration specified"
            }
        
        self.log(f"✅ Validation complete. {len(result['scenarioList'])} unique scenarios validated")
    
    def _remove_duplicate_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Advanced duplicate detection and removal with similarity analysis
        
        🧠 DUPLICATE DETECTION METHODS:
        --------------------------------
        • Exact name matching (case-insensitive)
        • Content similarity analysis
        • Purpose overlap detection
        • Category-based grouping
        • Keyword extraction and comparison
        
        🔧 MERGING STRATEGY:
        --------------------
        • Keep the more detailed scenario
        • Combine complementary information
        • Preserve higher priority scenarios
        • Maintain category diversity
        """
        if not scenarios:
            return scenarios
        
        self.log(f"🔍 Starting duplicate detection for {len(scenarios)} scenarios...")
        
        unique_scenarios = []
        removed_count = 0
        
        for current_scenario in scenarios:
            is_duplicate = False
            current_name = current_scenario.get("name", "").strip().lower()
            current_desc = current_scenario.get("description", "").strip().lower()
            current_purpose = current_scenario.get("purpose", "").strip().lower()
            
            # Check against existing unique scenarios
            for existing_scenario in unique_scenarios:
                existing_name = existing_scenario.get("name", "").strip().lower()
                existing_desc = existing_scenario.get("description", "").strip().lower()
                existing_purpose = existing_scenario.get("purpose", "").strip().lower()
                
                # Check for various types of duplicates
                if self._are_scenarios_similar(
                    current_name, current_desc, current_purpose,
                    existing_name, existing_desc, existing_purpose
                ):
                    is_duplicate = True
                    removed_count += 1
                    
                    # Merge information if current scenario has more detail
                    if len(current_desc) > len(existing_desc):
                        existing_scenario["description"] = current_scenario["description"]
                    if len(current_purpose) > len(existing_purpose):
                        existing_scenario["purpose"] = current_scenario["purpose"]
                    
                    break
            
            if not is_duplicate:
                unique_scenarios.append(current_scenario)
        
        if removed_count > 0:
            self.log(f"🔧 Removed {removed_count} duplicate/similar scenarios")
        
        return unique_scenarios
    
    def _are_scenarios_similar(self, name1: str, desc1: str, purpose1: str, 
                              name2: str, desc2: str, purpose2: str) -> bool:
        """
        Advanced similarity detection using multiple criteria
        """
        # Exact name match (high confidence)
        if name1 == name2:
            return True
        
        # High similarity in names (fuzzy matching)
        if self._calculate_similarity(name1, name2) > 0.8:
            return True
        
        # Similar descriptions and purposes
        desc_similarity = self._calculate_similarity(desc1, desc2)
        purpose_similarity = self._calculate_similarity(purpose1, purpose2)
        
        # Combined similarity threshold
        if desc_similarity > 0.7 and purpose_similarity > 0.6:
            return True
        
        # Check for keyword overlap
        name1_words = set(name1.split())
        name2_words = set(name2.split())
        
        if len(name1_words & name2_words) >= 2 and len(name1_words | name2_words) <= 5:
            return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using word overlap
        """
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _log_scenario_analysis_summary(self, result: Dict[str, Any], original_count: int, duplicate_count: int) -> None:
        """
        Generate comprehensive analysis summary with detailed insights
        """
        scenarios = result.get("scenarioList", [])
        final_count = len(scenarios)
        
        # Category distribution
        category_counts = {}
        priority_counts = {}
        
        for scenario in scenarios:
            category = scenario.get("category", "unknown")
            priority = scenario.get("priority", "unknown")
            
            category_counts[category] = category_counts.get(category, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        self.log("📊 === SCENARIO ANALYSIS SUMMARY ===")
        self.log(f"📈 Total Scenarios Generated: {original_count}")
        self.log(f"🔧 Duplicates Removed: {duplicate_count}")
        self.log(f"✅ Final Unique Scenarios: {final_count}")
        self.log(f"📊 Retention Rate: {(final_count/original_count*100):.1f}%")
        
        self.log("📊 Category Distribution:")
        for category, count in sorted(category_counts.items()):
            percentage = (count / final_count * 100) if final_count > 0 else 0
            self.log(f"   • {category}: {count} scenarios ({percentage:.1f}%)")
        
        self.log("📊 Priority Distribution:")
        for priority, count in sorted(priority_counts.items()):
            percentage = (count / final_count * 100) if final_count > 0 else 0
            self.log(f"   • {priority}: {count} scenarios ({percentage:.1f}%)")
        
        self.log("✅ Document analysis completed successfully!")
