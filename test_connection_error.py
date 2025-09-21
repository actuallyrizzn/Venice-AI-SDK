from venice_sdk import HTTPClient, Config
import traceback

config = Config(api_key='test', base_url='https://this-domain-definitely-does-not-exist-12345.com')
client = HTTPClient(config)

try:
    client.get('/models')
except Exception as e:
    print('Error type:', type(e).__name__)
    print('Error message:', str(e))
    traceback.print_exc()
