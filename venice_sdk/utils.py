"""
Utility functions for the Venice SDK.
"""

from typing import List, Optional, Union
import tiktoken


def count_tokens(
    text: str, 
    encoder: Optional[str] = None,
    model: Optional[str] = None
) -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to count tokens for
        encoder: Specific encoder to use (e.g., "cl100k_base", "p50k_base")
        model: Model name to auto-detect encoder
        
    Returns:
        Number of tokens in the text
    """
    if encoder is None:
        if model is not None:
            encoder = _get_encoder_for_model(model)
        else:
            encoder = "cl100k_base"  # Default fallback
    
    try:
        encoder_obj = tiktoken.get_encoding(encoder)
        return len(encoder_obj.encode(text))
    except KeyError:
        # Fallback to default encoder if invalid encoder specified
        encoder_obj = tiktoken.get_encoding("cl100k_base")
        return len(encoder_obj.encode(text))


def _get_encoder_for_model(model: str) -> str:
    """
    Get the appropriate encoder for a given model.
    
    Args:
        model: Model name to get encoder for
        
    Returns:
        Encoder name for the model
    """
    if model is None:
        return "cl100k_base"
    
    model_lower = model.lower()
    
    # OpenAI GPT models
    if "gpt-4" in model_lower or "gpt-3.5" in model_lower:
        return "cl100k_base"
    elif "text-davinci" in model_lower:
        return "p50k_base"
    elif "text-curie" in model_lower or "text-babbage" in model_lower or "text-ada" in model_lower:
        return "r50k_base"
    
    # Default fallback for Venice models and unknown models
    return "cl100k_base"


def validate_stop_sequences(stop: Optional[Union[str, List[str]]] = None) -> Optional[List[str]]:
    """
    Validate and normalize stop sequences.
    
    Args:
        stop: Stop sequence(s) to validate. Can be a string or list of strings.
        
    Returns:
        List of stop sequences or None
        
    Raises:
        ValueError: If stop sequences are invalid
    """
    if stop is None:
        return None
        
    if isinstance(stop, str):
        return [stop]
        
    if isinstance(stop, list):
        if not all(isinstance(s, str) for s in stop):
            raise ValueError("All stop sequences must be strings")
        return stop
        
    raise ValueError("Stop sequences must be a string or list of strings")


def format_messages(messages: List[dict]) -> List[dict]:
    """
    Validate and format chat messages.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Validated and formatted messages
        
    Raises:
        ValueError: If messages are invalid
    """
    if not messages:
        raise ValueError("Messages list cannot be empty")
        
    valid_roles = {"system", "user", "assistant", "function"}
    
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Each message must be a dictionary")
            
        if "role" not in message or "content" not in message:
            raise ValueError("Each message must have 'role' and 'content' keys")
            
        if message["role"] not in valid_roles:
            raise ValueError(f"Invalid message role. Must be one of: {valid_roles}")
    
    return messages


def format_tools(tools: List[dict]) -> List[dict]:
    """
    Validate and format tool definitions.
    
    Args:
        tools: List of tool dictionaries
        
    Returns:
        Validated and formatted tools
        
    Raises:
        ValueError: If tools are invalid
    """
    if not tools:
        raise ValueError("Tools list cannot be empty")
        
    for tool in tools:
        if not isinstance(tool, dict):
            raise ValueError("Each tool must be a dictionary")
            
        if "type" not in tool or tool["type"] != "function":
            raise ValueError("Each tool must have type 'function'")
            
        if "function" not in tool:
            raise ValueError("Each tool must have a 'function' definition")
            
        function = tool["function"]
        if not isinstance(function, dict):
            raise ValueError("Function definition must be a dictionary")
            
        required_keys = {"name", "description", "parameters"}
        missing_keys = required_keys - set(function.keys())
        if missing_keys:
            raise ValueError(f"Function definition missing required keys: {missing_keys}")
            
        if not isinstance(function["parameters"], dict):
            raise ValueError("Function parameters must be a dictionary")
    
    return tools 