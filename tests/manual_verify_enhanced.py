import requests
import json

def test_enhanced():
    url_process = "http://localhost:5000/process_text"
    url_toggle = "http://localhost:5000/toggle_task"
    
    # Needs a context that implies notes but not tasks
    payload = {
        "text": "The marketing team decided to delay the campaign. Sarah should update the website by tomorrow."
    }
    
    print(f"Sending payload: {payload['text']}")
    res = requests.post(url_process, json=payload)
    data = res.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get("new_notes_count", 0) > 0:
        print("SUCCESS: Notes detected.")
    else:
        print("WARNING: No notes detected.")
        
    if data.get("new_items_count", 0) > 0:
        print("SUCCESS: Action items detected.")
        
        # Test Toggle
        print("Testing Toggle on index 0...")
        res_t = requests.post(url_toggle, json={"index": 0})
        print(f"Toggle Response: {json.dumps(res_t.json(), indent=2)}")
    else:
        print("WARNING: No action items detected, skipping toggle test.")

if __name__ == "__main__":
    test_enhanced()
