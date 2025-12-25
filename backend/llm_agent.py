import ollama
import json
import re

class LLMAgent:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.context = "" 
        
    def process_segment(self, new_text):
        """
        Appends new text to context and asks LLM to extract action items AND important notes.
        """
        if not new_text or len(new_text) < 5:
            return None

        self.context += f" {new_text}"
        
        prompt = f"""
        You are an advanced Executive Assistant AI. Your PRIMARY GOAL is to ensure NO action items are missed. You must be thorough and exhaustive.

        Current Transcript Segment:
        "{new_text}"
        
        Context so far:
        "{self.context[-4000:]}"
        
        INSTRUCTIONS:
        1. ANALYZE the conversation for ANY task, assignment, or future commitment.
        2. BE AGGRESSIVE in extraction. If someone says "I will do X", "We need to Y", "Let's Z", or "Can you...", these are ALL action items.
        3. SPLIT multifaceted requested into individual items. "John, please write the report and fix the bug" = 2 separate action items.
        4. EXTRACT two types of information:
           A. "action_items": Lists of concrete tasks.
           B. "important_notes": Strategic context or decisions.
        
        3. OUTPUT FORMAT (JSON ONLY):
        {{
            "action_items": [
                {{
                    "task": "Specific actionable task description",
                    "owner": "Name or Unassigned",
                    "deadline": "Date or No Deadline",
                    "priority": "High/Medium/Low"
                }}
            ],
            "important_notes": ["Note 1", "Note 2"]
        }}
        
        4. CRITICAL RULES:
           - IGNORE past tense ("I completed the report").
           - CAPTURE future tense or imperative ("I will complete the report", "Complete the report").
           - If a name is mentioned near a task, assume they are the owner.
           - If multiple tasks are mentioned, Create separate entries for each.
        """
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            content = response['message']['content']
            
            # Parsing logic
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    data = json.loads(json_str)
                    return data
                except:
                    pass
            
            # Fallback
            try:
                data = json.loads(content)
                return data
            except:
                return {"action_items": [], "important_notes": []}
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return {"action_items": [], "important_notes": []}
