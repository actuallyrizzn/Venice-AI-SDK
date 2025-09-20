"""
Venice AI SDK - Character Management Module

This module provides character/persona management capabilities using the Venice AI API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .client import HTTPClient
from .errors import VeniceAPIError, CharacterNotFoundError
from .config import load_config


@dataclass
class Character:
    """Represents an AI character/persona."""
    id: str
    name: str
    slug: str
    description: str
    system_prompt: str
    capabilities: Dict[str, Any]
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_public: bool = False
    creator: Optional[str] = None
    
    def to_venice_parameters(self) -> Dict[str, Any]:
        """Convert character to venice_parameters for chat completions."""
        return {
            "character_slug": self.slug
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of character capabilities."""
        if isinstance(self.capabilities, dict):
            return list(self.capabilities.keys())
        return []
    
    def has_capability(self, capability: str) -> bool:
        """Check if character has a specific capability."""
        if isinstance(self.capabilities, dict):
            return self.capabilities.get(capability, False)
        return False


class CharactersAPI:
    """Character management API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def list(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs
    ) -> List[Character]:
        """
        List available characters.
        
        Args:
            category: Filter by character category
            tags: Filter by character tags
            is_public: Filter by public/private status
            limit: Maximum number of characters to return
            offset: Number of characters to skip
            **kwargs: Additional parameters
            
        Returns:
            List of Character objects
        """
        params = {}
        
        if category:
            params["category"] = category
        if tags:
            params["tags"] = ",".join(tags)
        if is_public is not None:
            params["is_public"] = is_public
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        
        params.update(kwargs)
        
        response = self.client.get("/characters", params=params)
        result = response.json()
        
        if "data" not in result:
            raise CharacterNotFoundError("Invalid response format from characters API")
        
        characters = []
        for item in result["data"]:
            characters.append(self._parse_character(item))
        
        return characters
    
    def get(self, slug: str) -> Optional[Character]:
        """
        Get a specific character by slug.
        
        Args:
            slug: Character slug identifier
            
        Returns:
            Character object or None if not found
        """
        try:
            response = self.client.get(f"/characters/{slug}")
            result = response.json()
            
            if "data" in result:
                data = result["data"]
                # Handle both list and dict responses
                if isinstance(data, list):
                    if len(data) > 0:
                        return self._parse_character(data[0])
                    return None
                else:
                    return self._parse_character(data)
            return None
            
        except VeniceAPIError as e:
            if "not found" in str(e).lower() or "404" in str(e):
                return None
            raise
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> List[Character]:
        """
        Search for characters by name, description, or content.
        
        Args:
            query: Search query
            category: Filter by character category
            tags: Filter by character tags
            **kwargs: Additional parameters
            
        Returns:
            List of matching Character objects
        """
        all_characters = self.list(category=category, tags=tags, **kwargs)
        query_lower = query.lower()
        
        matching_characters = []
        for character in all_characters:
            # Search in name, description, and system prompt
            if (query_lower in character.name.lower() or
                query_lower in character.description.lower() or
                query_lower in character.system_prompt.lower()):
                matching_characters.append(character)
        
        return matching_characters
    
    def get_by_category(self, category: str) -> List[Character]:
        """
        Get all characters in a specific category.
        
        Args:
            category: Character category
            
        Returns:
            List of Character objects in the category
        """
        return self.list(category=category)
    
    def get_by_tags(self, tags: List[str]) -> List[Character]:
        """
        Get all characters with specific tags.
        
        Args:
            tags: List of tags to filter by
            
        Returns:
            List of Character objects with matching tags
        """
        return self.list(tags=tags)
    
    def get_public_characters(self) -> List[Character]:
        """
        Get all public characters.
        
        Returns:
            List of public Character objects
        """
        return self.list(is_public=True)
    
    def get_categories(self) -> List[str]:
        """
        Get list of available character categories.
        
        Returns:
            List of category names
        """
        characters = self.list()
        categories = set()
        
        for character in characters:
            if character.category:
                categories.add(character.category)
        
        return sorted(list(categories))
    
    def get_tags(self) -> List[str]:
        """
        Get list of available character tags.
        
        Returns:
            List of tag names
        """
        characters = self.list()
        tags = set()
        
        for character in characters:
            if character.tags:
                tags.update(character.tags)
        
        return sorted(list(tags))
    
    def _parse_character(self, data: Dict[str, Any]) -> Character:
        """Parse character data from API response."""
        if data is None:
            raise CharacterNotFoundError("Character not found")
        
        return Character(
            id=data.get("id", ""),
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            description=data.get("description", ""),
            system_prompt=data.get("system_prompt", ""),
            capabilities=data.get("capabilities", {}),
            category=data.get("category"),
            tags=data.get("tags"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            is_public=data.get("is_public", False),
            creator=data.get("creator")
        )


class CharacterManager:
    """High-level character management utilities."""
    
    def __init__(self, characters_api: CharactersAPI):
        self.characters_api = characters_api
        self._character_cache = {}
    
    def get_character(self, identifier: str, use_cache: bool = True) -> Optional[Character]:
        """
        Get a character by slug or name with optional caching.
        
        Args:
            identifier: Character slug or name
            use_cache: Whether to use cached results
            
        Returns:
            Character object or None if not found
        """
        if use_cache and identifier in self._character_cache:
            return self._character_cache[identifier]
        
        # Try as slug first
        character = self.characters_api.get(identifier)
        
        if not character:
            # Try searching by name
            search_results = self.characters_api.search(identifier)
            if search_results:
                character = search_results[0]  # Take first match
        
        if character and use_cache:
            self._character_cache[identifier] = character
        
        return character
    
    def find_characters_by_capability(self, capability: str) -> List[Character]:
        """
        Find characters that have a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of characters with the capability
        """
        all_characters = self.characters_api.list()
        return [
            char for char in all_characters
            if char.has_capability(capability)
        ]
    
    def get_recommended_characters(self, context: str) -> List[Character]:
        """
        Get recommended characters based on context.
        
        Args:
            context: Context description for recommendations
            
        Returns:
            List of recommended characters
        """
        # Simple keyword-based recommendation
        context_lower = context.lower()
        
        # Define capability keywords
        capability_keywords = {
            "creative": ["creative", "art", "writing", "design"],
            "technical": ["technical", "code", "programming", "engineering"],
            "business": ["business", "marketing", "sales", "strategy"],
            "educational": ["education", "teaching", "learning", "tutorial"],
            "entertainment": ["entertainment", "fun", "game", "story"],
            "support": ["support", "help", "assistant", "service"]
        }
        
        # Find matching capabilities
        matching_capabilities = []
        for capability, keywords in capability_keywords.items():
            if any(keyword in context_lower for keyword in keywords):
                matching_capabilities.append(capability)
        
        # Get characters with matching capabilities
        recommended = []
        for capability in matching_capabilities:
            chars = self.find_characters_by_capability(capability)
            recommended.extend(chars)
        
        # Remove duplicates and return
        seen = set()
        unique_recommended = []
        for char in recommended:
            if char.slug not in seen:
                seen.add(char.slug)
                unique_recommended.append(char)
        
        return unique_recommended
    
    def clear_cache(self) -> None:
        """Clear the character cache."""
        self._character_cache.clear()


# Convenience functions
def get_character(
    slug: str,
    client: Optional[HTTPClient] = None
) -> Optional[Character]:
    """Convenience function to get a character by slug."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = CharactersAPI(client)
    return api.get(slug)


def list_characters(
    client: Optional[HTTPClient] = None,
    **kwargs
) -> List[Character]:
    """Convenience function to list characters."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = CharactersAPI(client)
    return api.list(**kwargs)


def search_characters(
    query: str,
    client: Optional[HTTPClient] = None,
    **kwargs
) -> List[Character]:
    """Convenience function to search characters."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = CharactersAPI(client)
    return api.search(query, **kwargs)
