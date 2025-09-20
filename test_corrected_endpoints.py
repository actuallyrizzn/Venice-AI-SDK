from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

# Test the corrected endpoint paths
endpoints = [
    # Test image edit with correct path
    ('/api/v1/images/edits', 'POST', {"model": "stable-diffusion-3.5", "image": "test", "prompt": "test"}),
    
    # Test image upscale with correct path
    ('/api/v1/images/upscales', 'POST', {"model": "upscaler", "image": "test"}),
    
    # Test image styles with correct path
    ('/api/v1/images/styles', 'GET', None),
]

print("Testing corrected endpoint paths:")
print("=" * 50)

for ep, method, data in endpoints:
    try:
        if method == 'POST':
            response = requests.post(f"https://api.venice.ai{ep}",
                                   headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                                   json=data)
        else:
            response = requests.get(f"https://api.venice.ai{ep}", headers={"Authorization": f"Bearer {api_key}"})
        
        status = response.status_code
        if status == 200:
            print(f"✅ {ep}: {status} - WORKING")
        elif status == 401:
            print(f"🔒 {ep}: {status} - AUTHENTICATION REQUIRED")
        elif status == 403:
            print(f"🚫 {ep}: {status} - FORBIDDEN")
        elif status == 404:
            print(f"❌ {ep}: {status} - NOT FOUND")
        else:
            print(f"⚠️  {ep}: {status} - {response.text[:100]}")
            
    except Exception as e:
        print(f"💥 {ep}: ERROR - {str(e)[:50]}")

print("\n" + "=" * 50)
