from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add root project path to import from backend module
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from backend.llm_agent import LLMAgent

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Global State
llm_agent = LLMAgent()
transcript_log = [] # List of strings (manual entries)
action_items = []   # List of dicts
important_notes = [] # List of strings

@app.route('/process_text', methods=['POST'])
def process_text():
    global transcript_log, action_items, important_notes
    
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"status": "No text provided"}), 400
        
    # Log the input
    transcript_log.append(text)
    
    # Process with LLM
    result = llm_agent.process_segment(text)
    
    new_items_count = 0
    new_notes_count = 0
    
    if result:
        # Handle Action Items
        new_items = result.get("action_items", [])
        if new_items:
            # Add 'done' status to new items
            for item in new_items:
                item['done'] = False
            
            print(f"New Action Items: {new_items}")
            action_items.extend(new_items)
            new_items_count = len(new_items)
            
        # Handle Important Notes
        new_notes = result.get("important_notes", [])
        if new_notes:
            print(f"New Notes: {new_notes}")
            important_notes.extend(new_notes)
            new_notes_count = len(new_notes)
        
    return jsonify({
        "status": "Processed",
        "new_items_count": new_items_count,
        "new_notes_count": new_notes_count
    })

@app.route('/toggle_task', methods=['POST'])
def toggle_task():
    global action_items
    data = request.json
    index = data.get('index')
    
    if index is not None and 0 <= index < len(action_items):
        action_items[index]['done'] = not action_items[index].get('done', False)
        return jsonify({"status": "Toggled", "new_state": action_items[index]['done']})
    
    return jsonify({"status": "Invalid index"}), 400

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "transcript": transcript_log,
        "action_items": action_items,
        "important_notes": important_notes
    })

@app.route('/reset', methods=['POST'])
def reset():
    global transcript_log, action_items, important_notes
    transcript_log = []
    action_items = []
    important_notes = []
    # Optionally reset LLM context too
    llm_agent.context = "" 
    return jsonify({"status": "Reset complete"})

@app.route('/save_session', methods=['POST'])
def save_session():
    global transcript_log, action_items, important_notes
    data = request.json
    title = data.get('title', '').strip()
    
    if not title:
        return jsonify({"status": "Title required"}), 400
    
    # Create saved_sessions directory if it doesn't exist
    sessions_dir = os.path.join(current_dir, 'saved_sessions')
    os.makedirs(sessions_dir, exist_ok=True)
    
    # Sanitize filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_title}.json"
    filepath = os.path.join(sessions_dir, filename)
    
    # Save session data
    import json
    import time
    
    session_data = {
        "title": title,
        "transcript": transcript_log,
        "action_items": action_items,
        "important_notes": important_notes,
        "timestamp": time.time()  # Current timestamp
    }
    
    with open(filepath, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    return jsonify({"status": "Session saved", "title": title})

@app.route('/list_sessions', methods=['GET'])
def list_sessions():
    sessions_dir = os.path.join(current_dir, 'saved_sessions')
    
    if not os.path.exists(sessions_dir):
        return jsonify({"sessions": []})
    
    import json
    sessions = []
    for filename in os.listdir(sessions_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(sessions_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        "title": data.get("title", filename[:-5]),
                        "filename": filename,
                        "item_count": len(data.get("action_items", [])),
                        "note_count": len(data.get("important_notes", []))
                    })
            except:
                pass
    
    return jsonify({"sessions": sessions})

@app.route('/load_session', methods=['POST'])
def load_session():
    global transcript_log, action_items, important_notes
    data = request.json
    filename = data.get('filename', '')
    
    if not filename:
        return jsonify({"status": "Filename required"}), 400
    
    sessions_dir = os.path.join(current_dir, 'saved_sessions')
    filepath = os.path.join(sessions_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({"status": "Session not found"}), 404
    
    import json
    try:
        with open(filepath, 'r') as f:
            session_data = json.load(f)
        
        transcript_log = session_data.get("transcript", [])
        action_items = session_data.get("action_items", [])
        important_notes = session_data.get("important_notes", [])
        
        return jsonify({"status": "Session loaded", "title": session_data.get("title")})
    except Exception as e:
        return jsonify({"status": "Error loading session", "error": str(e)}), 500

@app.route('/delete_session', methods=['DELETE'])
def delete_session():
    data = request.json
    filename = data.get('filename', '')
    
    if not filename:
        return jsonify({"status": "Filename required"}), 400
    
    sessions_dir = os.path.join(current_dir, 'saved_sessions')
    filepath = os.path.join(sessions_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({"status": "Session not found"}), 404
    
    try:
        os.remove(filepath)
        return jsonify({"status": "Session deleted"})
    except Exception as e:
        return jsonify({"status": "Error deleting session", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

