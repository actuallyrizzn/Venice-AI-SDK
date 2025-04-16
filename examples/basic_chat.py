"""
Basic example of using the Venice SDK for chat completions.
"""

from dotenv import load_dotenv

from venice_sdk import VeniceClient, ChatAPI


def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the client
    client = VeniceClient()
    
    # Create a chat API instance
    chat = ChatAPI(client)
    
    # Send a message
    response = chat.complete(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about AI."}
        ],
        model="llama-3.3-70b"
    )
    
    # Print the response
    print(response.choices[0].message.content)
    
    # Example with streaming
    print("\nStreaming example:")
    for chunk in chat.complete(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Count from 1 to 5."}
        ],
        model="llama-3.3-70b",
        stream=True
    ):
        print(chunk.choices[0].message.content, end="", flush=True)
    print()


if __name__ == "__main__":
    main() 