import requests
import json
import time

def test_api():
    url = "http://localhost:5000/extract"
    data = {"text": "Bob, please complete the analysis by Tuesday. The weather is great. Alice to schedule the meeting."}
    
    print("Sending request...")
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start if running immediately after
    # time.sleep(2) 
    test_api()
