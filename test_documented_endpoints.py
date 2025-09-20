from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

# Test the documented admin endpoints
endpoints = [
    '/api/v1/api_keys',
    '/api/v1/api_keys/rate_limits', 
    '/api/v1/api_keys/rate_limits/log',
    '/api/v1/billing/usage'
]

for ep in endpoints:
    response = requests.get(f"https://api.venice.ai{ep}", headers={"Authorization": f"Bearer {api_key}"})
    print(f"{ep}: {response.status_code} - {response.text[:200]}")
    print()
