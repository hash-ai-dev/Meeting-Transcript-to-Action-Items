import spacy
import joblib
import os

class ActionExtractor:
    def __init__(self, model_path="action_item_model.pkl"):
        # Load spaCy 
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
             from spacy.cli import download
             download("en_core_web_sm")
             self.nlp = spacy.load("en_core_web_sm")
            
        # Load Model
        # If model doesn't exist, we might need to train it or warn
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            # Fallback for dev: try to find it in the same dir or raise
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(curr_dir, model_path)
            if os.path.exists(full_path):
                self.model = joblib.load(full_path)
            else:
                 raise FileNotFoundError(f"Model not found at {model_path} or {full_path}. Run train_model.py first.")

    def extract_action_items(self, transcript):
        doc = self.nlp(transcript)
        action_items = []

        for sent in doc.sents:
            # Classification
            if self.is_action_item(sent):
                item = self.parse_details(sent)
                action_items.append(item)
        
        return action_items

    def is_action_item(self, sent):
        # Smart rule: check for Question marks? Usually questions are not action items unless rhetorical
        # text = sent.text.strip()
        # if text.endswith("?"): return False
        
        # ML Prediction
        vector = sent.vector.reshape(1, -1)
        prediction = self.model.predict(vector)[0]
        return prediction == 1

    def parse_details(self, sent):
        owner = "Unassigned"
        deadline = None
        
        # Extract Deadline (DATE entities)
        dates = [ent.text for ent in sent.ents if ent.label_ == "DATE"]
        if dates:
            deadline = dates[0] # Take the first date found for now

        # Extract Owner (Subject of the sentence or specific PERSON dependency)
        # Heuristic: If there is a PERSON entity in nsubj, it's likely the owner
        
        for token in sent:
            if token.dep_ == "nsubj" and token.ent_type_ == "PERSON":
                owner = token.text
                break
            # Fallback: check for proper noun in nsubj
            elif token.dep_ == "nsubj" and token.pos_ == "PROPN":
                owner = token.text
        
        # If no nsubj owner found, maybe it's imperative (root verb implied "You") -> "Unassigned" or check for "assign to X"
        
        return {
            "text": sent.text.strip(),
            "owner": owner,
            "deadline": deadline or "No Deadline"
        }

if __name__ == "__main__":
    # Test
    extractor = ActionExtractor("ml/action_item_model.pkl") # Adjust path for local run
    text = "John, please submit the report by Friday. The weather is nice. Sarah needs to fix the bug."
    print(extractor.extract_action_items(text))
