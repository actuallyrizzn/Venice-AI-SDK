from venice_sdk import VeniceClient

client = VeniceClient()
models = client.models.list()
print('Available models:')
for m in models[:10]:
    print(f'- {m["id"]}')
