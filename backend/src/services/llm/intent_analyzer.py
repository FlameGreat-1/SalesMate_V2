from typing import Dict, Any, Optional, List
from src.core.models.enums import UserIntent


class IntentAnalyzer:
    
    ANALYSIS_PROMPT = """Analyze the customer message and conversation context. Extract:

1. Intent: greeting, browsing, requesting_recommendation, comparing_products, asking_question, ready_to_buy, objection, or unknown
2. Products: Full product names being discussed (use conversation history for pronouns like "it", "that one")
3. Categories: Product categories mentioned
4. Budget: Price or budget mentioned
5. Requirements: Specific features requested

Format:
Intent: [value]
Products: [comma-separated names or "none"]
Categories: [comma-separated or "none"]
Budget: [amount or "none"]
Requirements: [comma-separated or "none"]"""
    
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
                intent_value = value.lower().replace(" ", "_").replace("-", "_")
                try:
                    result["intent"] = UserIntent(intent_value)
                except ValueError:
                    result["intent"] = UserIntent.UNKNOWN
            
            elif key == "products" and value.lower() not in ["none", "n/a", ""]:
                products = []
                for prod in value.split(','):
                    prod_name = prod.strip()
                    if prod_name and prod_name.lower() not in ["none", "n/a"]:
                        products.append(prod_name)
                result["products"] = products
            
            elif key == "categories" and value.lower() not in ["none", "n/a", ""]:
                result["categories"] = [
                    cat.strip() for cat in value.split(',') 
                    if cat.strip() and cat.strip().lower() not in ["none", "n/a"]
                ]
            
            elif key == "budget" and value.lower() not in ["none", "not mentioned", "n/a", ""]:
                result["budget"] = self._parse_budget(value)
            
            elif key == "requirements" and value.lower() not in ["none", "n/a", ""]:
                result["requirements"] = [
                    req.strip() for req in value.split(',') 
                    if req.strip() and req.strip().lower() not in ["none", "n/a"]
                ]
        
        return result
    
    def _parse_budget(self, budget_str: str) -> Optional[float]:
        try:
            cleaned = budget_str.replace('$', '').replace(',', '').replace('USD', '').strip()
            if '-' in cleaned:
                parts = cleaned.split('-')
                cleaned = parts[-1].strip()
            for prefix in ['under ', 'up to ', 'around ', 'about ']:
                if cleaned.lower().startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
            return float(cleaned)
        except ValueError:
            return None
    
    def _get_default_intent(self) -> Dict[str, Any]:
        return {
            "intent": UserIntent.UNKNOWN,
            "products": [],
            "categories": [],
            "budget": None,
            "requirements": []
        }
    
    def get_analysis_prompt(self) -> str:
        return self.ANALYSIS_PROMPT
    
    def build_analysis_prompt_with_context(
        self, 
        conversation_history: List[Dict[str, str]], 
        current_message: str
    ) -> str:
        prompt_parts = [self.ANALYSIS_PROMPT]
        
        if conversation_history:
            prompt_parts.append("\n--- HISTORY ---")
            for msg in conversation_history[-6:]:
                role = msg.get("role", "unknown").capitalize()
                content = msg.get("content", "")
                if len(content) > 300:
                    content = content[:300] + "..."
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("--- END ---\n")
        
        prompt_parts.append(f"Customer: {current_message}")
        
        return "\n".join(prompt_parts)


def get_intent_analyzer() -> IntentAnalyzer:
    return IntentAnalyzer()
