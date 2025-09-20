from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

# Test more potential admin endpoints
endpoints = [
    '/api/v1/admin/api_keys',
    '/api/v1/admin/account',
    '/api/v1/admin/billing',
    '/api/v1/admin/usage',
    '/api/v1/admin/rate_limits',
    '/api/v1/me',
    '/api/v1/user',
    '/api/v1/profile',
    '/api/v1/settings',
    '/api/v1/dashboard'
]

for ep in endpoints:
    response = requests.get(f"https://api.venice.ai{ep}", headers={"Authorization": f"Bearer {api_key}"})
    print(f"{ep}: {response.status_code} - {response.text[:100]}")
