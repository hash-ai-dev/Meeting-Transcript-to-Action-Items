import requests
import json

def test_process():
    url = "http://localhost:5000/process_text"
    payload = {
        "text": "Harish needs to deploy the application by Friday. The server must be updated."
    }
    
    print(f"Sending payload: {payload}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("SUCCESS: Endpoint works.")
        else:
            print("FAILURE: Endpoint returned error.")
            
    except Exception as e:
        print(f"FAILURE: Connection error: {e}")

if __name__ == "__main__":
    test_process()
