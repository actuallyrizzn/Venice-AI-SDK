from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

# Test all documented endpoints to see which ones work
endpoints = [
    # Core AI Services
    '/api/v1/models',
    '/api/v1/chat/completions',
    '/api/v1/embeddings/generate',
    '/api/v1/models/traits',
    '/api/v1/models/compatibility_mapping',
    
    # Image Processing
    '/api/v1/image/generate',
    '/api/v1/image/edit', 
    '/api/v1/image/upscale',
    '/api/v1/image/styles',
    
    # Audio Services
    '/api/v1/audio/speech',
    
    # Character Management
    '/api/v1/characters',
    
    # Account Management (some work, some don't)
    '/api/v1/api_keys',
    '/api/v1/api_keys/rate_limits',
    '/api/v1/api_keys/rate_limits/log',
    '/api/v1/billing/usage',
    '/api/v1/api_keys/generate_web3_key'
]

print("Testing all documented endpoints:")
print("=" * 50)

for ep in endpoints:
    try:
        if ep == '/api/v1/chat/completions':
            # POST request for chat completions
            response = requests.post(f"https://api.venice.ai{ep}", 
                                   headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                                   json={"model": "llama-3.3-70b", "messages": [{"role": "user", "content": "test"}]})
        elif ep == '/api/v1/embeddings/generate':
            # POST request for embeddings
            response = requests.post(f"https://api.venice.ai{ep}",
                                   headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                                   json={"model": "text-embedding-bge-m3", "input": "test"})
        elif ep == '/api/v1/api_keys/generate_web3_key':
            # POST request for web3 key generation
            response = requests.post(f"https://api.venice.ai{ep}",
                                   headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                                   json={"name": "test", "description": "test"})
        else:
            # GET request for most endpoints
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
            print(f"⚠️  {ep}: {status} - {response.text[:50]}")
            
    except Exception as e:
        print(f"💥 {ep}: ERROR - {str(e)[:50]}")

print("\n" + "=" * 50)
print("Summary:")
print("✅ = Working endpoints")
print("🔒 = Authentication required (admin key needed)")
print("🚫 = Forbidden (insufficient permissions)")
print("❌ = Not found (endpoint doesn't exist)")
print("⚠️  = Other status codes")
print("💥 = Request failed with exception")
