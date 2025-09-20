from venice_sdk import VeniceClient
import requests

client = VeniceClient()
api_key = client.http_client.config.api_key

endpoints = ['/api/v1/account', '/api/v1/billing', '/api/v1/usage', '/api/v1/rate_limits', '/api/v1/api_keys']

for ep in endpoints:
    response = requests.get(f"https://api.venice.ai{ep}", headers={"Authorization": f"Bearer {api_key}"})
    print(f"{ep}: {response.status_code} - {response.text[:100]}")
