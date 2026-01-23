from typing import Dict, Any, Optional
from src.core.models.enums import UserIntent


class IntentAnalyzer:
    
    ANALYSIS_PROMPT = """Analyze the user's message and extract:
1. Intent (greeting, browsing, requesting_recommendation, comparing_products, asking_question, ready_to_buy, objection, unknown)
2. Mentioned product categories or types
3. Budget if mentioned
4. Key requirements or preferences

Respond in this exact format:
Intent: [intent]
Categories: [comma-separated list or "none"]
Budget: [amount or "not mentioned"]
Requirements: [comma-separated list or "none"]"""
    
    def analyze(self, user_message: str, llm_response: str) -> Dict[str, Any]:
        try:
            return self._parse_intent_analysis(llm_response)
        except Exception:
            return self._get_default_intent()
    
    def _parse_intent_analysis(self, response: str) -> Dict[str, Any]:
        lines = response.strip().split('\n')
        result = self._get_default_intent()
        
        for line in lines:
            if ':' not in line:
                continue
            
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == "intent":
                intent_value = value.lower().replace(" ", "_")
                try:
                    result["intent"] = UserIntent(intent_value)
                except ValueError:
                    result["intent"] = UserIntent.UNKNOWN
            
            elif key == "categories" and value.lower() != "none":
                result["categories"] = [cat.strip() for cat in value.split(',')]
            
            elif key == "budget" and value.lower() != "not mentioned":
                result["budget"] = self._parse_budget(value)
            
            elif key == "requirements" and value.lower() != "none":
                result["requirements"] = [req.strip() for req in value.split(',')]
        
        return result
    
    def _parse_budget(self, budget_str: str) -> Optional[float]:
        try:
            cleaned = budget_str.replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except ValueError:
            return None
    
    def _get_default_intent(self) -> Dict[str, Any]:
        return {
            "intent": UserIntent.UNKNOWN,
            "categories": [],
            "budget": None,
            "requirements": []
        }
    
    def get_analysis_prompt(self) -> str:
        return self.ANALYSIS_PROMPT


def get_intent_analyzer() -> IntentAnalyzer:
    return IntentAnalyzer()
