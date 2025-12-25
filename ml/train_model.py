import spacy
import joblib
import random
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def generate_synthetic_data(n_samples=500):
    action_templates = [
        "Please {verb} the {noun} by {time}.",
        "I need you to {verb} the {noun}.",
        "Can you {verb} this?",
        "{person}, make sure to {verb} the {noun}.",
        "We need to {verb} the {noun} before {time}.",
        "Action item: {verb} {noun}.",
        "It is crucial to {verb} the {noun}.",
        "Don't forget to {verb} the {noun}.",
        "Task: {verb} {noun}.",
        "{person} will {verb} the {noun}.",
        "Let's {verb} the {noun} tomorrow.",
        "Ensure the {noun} is {verb}ed.",
        "Submit the report by Friday.",
        "Email the client today.",
        "Update the documentation.",
        "Fix the bug in production."
    ]

    non_action_templates = [
        "The meeting was {adjective}.",
        "We discussed the {noun}.",
        "The {noun} is {adjective}.",
        "I think {noun} is better.",
        "What do you think about {noun}?",
        "Hello everyone.",
        "Good morning.",
        "Let's take a break.",
        "The weather is {adjective}.",
        "We reviewed the {noun}.",
        "This is interesting.",
        "I agree with {person}.",
        "That makes sense.",
        "No, I don't think so.",
        "The budget is tight.",
        "The deadline was yesterday."
    ]

    verbs = ["create", "update", "delete", "review", "submit", "send", "fix", "deploy", "build", "test"]
    nouns = ["report", "document", "code", "email", "budget", "plan", "presentation", "ticket", "bug", "feature"]
    times = ["tomorrow", "Friday", "next week", "EOD", "5 PM", "Monday", "next month"]
    people = ["John", "Alice", "Bob", "Sarah", "Mike", "Harish"]
    adjectives = ["good", "bad", "long", "short", "interesting", "boring", "important", "ready"]

    X = []
    y = []

    for _ in range(n_samples // 2):
        # Generate Action
        tmpl = random.choice(action_templates)
        text = tmpl.format(
            verb=random.choice(verbs),
            noun=random.choice(nouns),
            time=random.choice(times),
            person=random.choice(people),
            adjective=random.choice(adjectives)
        )
        # Randomly remove placeholders if format fails (simple robustness)
        text = text.replace("{verb}", "do").replace("{noun}", "thing").replace("{time}", "soon").replace("{person}", "Someone")
        
        X.append(text)
        y.append(1) # 1 for Action Item

        # Generate Non-Action
        tmpl = random.choice(non_action_templates)
        text = tmpl.format(
            verb=random.choice(verbs),
            noun=random.choice(nouns),
            time=random.choice(times),
            person=random.choice(people),
            adjective=random.choice(adjectives)
        )
        text = text.replace("{verb}", "do").replace("{noun}", "thing").replace("{time}", "soon").replace("{person}", "Someone")
        
        X.append(text)
        y.append(0) # 0 for Non-Action

    return X, y

def train():
    print("Generating synthetic data...")
    texts, labels = generate_synthetic_data(600)
    
    print("Vectorizing data...")
    # Get vectors for each text
    # Note: simple document vector (average of word vectors)
    X_vectors = [nlp(text).vector for text in texts]
    
    print("Training Logistic Regression...")
    clf = LogisticRegression(random_state=42)
    clf.fit(X_vectors, labels)
    
    print("Evaluating...")
    print(classification_report(labels, clf.predict(X_vectors)))
    
    print("Saving model...")
    joblib.dump(clf, "action_item_model.pkl")
    print("Model saved to action_item_model.pkl")

if __name__ == "__main__":
    train()
