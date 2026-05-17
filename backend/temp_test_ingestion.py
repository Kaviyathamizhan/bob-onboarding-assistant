import httpx
import sys

URLS_TO_TEST = [
    # Small repo
    "https://github.com/Kaviyathamizhan/bob-onboarding-assistant",
    # Medium repo
    "https://github.com/expressjs/express",
    # Large repo (should cap at 100 files)
    "https://github.com/pallets/flask"
]

API_ENDPOINT = "http://localhost:8000/api/analyze"

def test_ingestion():
    with httpx.Client(timeout=60.0) as client:
        for url in URLS_TO_TEST:
            print(f"\n--- Testing Repo: {url} ---")
            try:
                response = client.post(API_ENDPOINT, json={"repo_url": url})
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"SUCCESS: {response.status_code}")
                    print(f"Parsed Name: {data.get('repo_name')}")
                    print(f"Files Processed: {data.get('file_count')} (Max 100)")
                    print(f"Tech Stack detected: {len(data.get('tech_stack', []))} items")
                    print(f"Modules detected: {len(data.get('modules', []))} items")
                else:
                    print(f"FAILED: {response.status_code}")
                    print(response.text)
                    
            except Exception as e:
                print(f"ERROR connecting to API: {e}")

if __name__ == "__main__":
    test_ingestion()
