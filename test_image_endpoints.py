from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

# Test different image endpoint variations
endpoints = [
    # Test different image endpoint paths
    '/api/v1/image/styles',
    '/api/v1/images/styles', 
    '/api/v1/image/generate',
    '/api/v1/images/generations',
    '/api/v1/image/edit',
    '/api/v1/images/edits',
    '/api/v1/image/upscale',
    '/api/v1/images/upscales',
]

print("Testing image endpoint variations:")
print("=" * 50)

for ep in endpoints:
    try:
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
