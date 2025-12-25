import requests
import json

API_URL = "http://localhost:5000"

def test_reset():
    # 1. Add some data
    print("Adding data...")
    try:
        requests.post(f"{API_URL}/process_text", json={"text": "Harish to fix the bug by tomorrow."})
    except Exception as e:
        print(f"Failed to add data: {e}")
        return

    # 2. Check status
    print("Checking status (should have data)...")
    res = requests.get(f"{API_URL}/status").json()
    print(f"Action Items: {len(res['action_items'])}")
    
    if len(res['action_items']) == 0:
        print("WARNING: Data was not added!")

    # 3. Call Reset
    print("Calling Reset...")
    requests.post(f"{API_URL}/reset")

    # 4. Check status again
    print("Checking status (should be empty)...")
    res = requests.get(f"{API_URL}/status").json()
    print(f"Action Items: {len(res['action_items'])}")
    
    if len(res['action_items']) == 0:
        print("SUCCESS: Reset works correctly on backend.")
    else:
        print("FAILURE: Reset did not clear data.")

if __name__ == "__main__":
    test_reset()
