#!/usr/bin/env python3
"""
Test different models for embeddings functionality.
"""

import os
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config

def test_embeddings_models():
    """Test different models for embeddings."""
    api_key = os.getenv('VENICE_API_KEY')
    if not api_key:
        print('No API key found')
        return
    
    config = Config(api_key=api_key)
    client = HTTPClient(config)
    
    # Try embeddings with different models
    models_to_try = ['text-embedding-3-small', 'qwen3-4b', 'venice-uncensored', 'llama-3.2-3b']
    
    for model in models_to_try:
        try:
            response = client.post('embeddings', data={
                'input': 'test text for embedding',
                'model': model
            })
            print(f'Model {model}: Status {response.status_code}')
            if response.status_code == 200:
                result = response.json()
                print(f'  Success! Response keys: {list(result.keys())}')
                if 'data' in result and result['data']:
                    embedding_data = result['data'][0]
                    if 'embedding' in embedding_data:
                        print(f'  First embedding length: {len(embedding_data["embedding"])}')
            else:
                print(f'  Error: {response.text}')
        except Exception as e:
            print(f'Model {model}: Exception - {e}')

if __name__ == "__main__":
    test_embeddings_models()
