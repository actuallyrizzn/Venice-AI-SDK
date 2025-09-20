from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

# Test POST endpoints for image generation
endpoints = [
    # Test different image generation endpoint paths
    ('/api/v1/image/generate', {"model": "stable-diffusion-3.5", "prompt": "test"}),
    ('/api/v1/images/generations', {"model": "stable-diffusion-3.5", "prompt": "test"}),
]

print("Testing image POST endpoint variations:")
print("=" * 50)

for ep, data in endpoints:
    try:
        response = requests.post(f"https://api.venice.ai{ep}",
                               headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                               json=data)
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
