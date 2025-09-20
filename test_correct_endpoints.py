from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

# Test the correct endpoint paths based on what's actually implemented
endpoints = [
    # Test embeddings with correct path
    ('/api/v1/embeddings', 'POST', {"model": "text-embedding-bge-m3", "input": "test"}),
    
    # Test image generation with correct path
    ('/api/v1/images/generations', 'POST', {"model": "stable-diffusion-3.5", "prompt": "test"}),
    
    # Test audio with correct path
    ('/api/v1/audio/speech', 'POST', {"model": "tts-kokoro", "input": "test", "voice": "af_alloy"}),
]

print("Testing correct endpoint paths:")
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
