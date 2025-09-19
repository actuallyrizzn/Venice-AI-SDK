"""
Comprehensive unit tests for the characters module.
"""

import pytest
from unittest.mock import patch, MagicMock
from venice_sdk.characters import (
    Character, CharactersAPI, CharacterManager,
    get_character, list_characters, search_characters
)
from venice_sdk.errors import VeniceAPIError, CharacterNotFoundError


class TestCharacterComprehensive:
    """Comprehensive test suite for Character class."""

    def test_character_initialization(self):
        """Test Character initialization with all parameters."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities={"function_calling": True, "web_search": False},
            category="assistant",
            tags=["helpful", "test"],
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            is_public=True,
            creator="user123"
        )
        
        assert character.id == "char-123"
        assert character.name == "Test Character"
        assert character.slug == "test-character"
        assert character.description == "A test character"
        assert character.system_prompt == "You are a helpful test character."
        assert character.capabilities == {"function_calling": True, "web_search": False}
        assert character.category == "assistant"
        assert character.tags == ["helpful", "test"]
        assert character.created_at == "2023-01-01T00:00:00Z"
        assert character.updated_at == "2023-01-02T00:00:00Z"
        assert character.is_public is True
        assert character.creator == "user123"

    def test_character_initialization_with_defaults(self):
        """Test Character initialization with default values."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities={}
        )
        
        assert character.id == "char-123"
        assert character.name == "Test Character"
        assert character.slug == "test-character"
        assert character.description == "A test character"
        assert character.system_prompt == "You are a helpful test character."
        assert character.capabilities == {}
        assert character.category is None
        assert character.tags is None
        assert character.created_at is None
        assert character.updated_at is None
        assert character.is_public is False
        assert character.creator is None

    def test_to_venice_parameters(self):
        """Test to_venice_parameters method."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities={}
        )
        
        params = character.to_venice_parameters()
        
        assert params == {"character_slug": "test-character"}

    def test_get_capabilities_with_dict(self):
        """Test get_capabilities method with dict capabilities."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities={"function_calling": True, "web_search": False, "streaming": True}
        )
        
        capabilities = character.get_capabilities()
        
        assert set(capabilities) == {"function_calling", "web_search", "streaming"}

    def test_get_capabilities_with_non_dict(self):
        """Test get_capabilities method with non-dict capabilities."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities="not_a_dict"
        )
        
        capabilities = character.get_capabilities()
        
        assert capabilities == []

    def test_has_capability_true(self):
        """Test has_capability method returning True."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities={"function_calling": True, "web_search": False}
        )
        
        assert character.has_capability("function_calling") is True
        assert character.has_capability("web_search") is True

    def test_has_capability_false(self):
        """Test has_capability method returning False."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities={"function_calling": True}
        )
        
        assert character.has_capability("web_search") is False
        assert character.has_capability("nonexistent") is False

    def test_has_capability_with_non_dict(self):
        """Test has_capability method with non-dict capabilities."""
        character = Character(
            id="char-123",
            name="Test Character",
            slug="test-character",
            description="A test character",
            system_prompt="You are a helpful test character.",
            capabilities="not_a_dict"
        )
        
        assert character.has_capability("function_calling") is False

    def test_character_equality(self):
        """Test Character equality comparison."""
        char1 = Character("char-123", "Test Character", "test-character", "desc", "prompt", {})
        char2 = Character("char-123", "Test Character", "test-character", "desc", "prompt", {})
        char3 = Character("char-456", "Test Character", "test-character", "desc", "prompt", {})
        
        assert char1 == char2
        assert char1 != char3

    def test_character_string_representation(self):
        """Test Character string representation."""
        character = Character("char-123", "Test Character", "test-character", "desc", "prompt", {})
        char_str = str(character)
        
        assert "Character" in char_str
        assert "char-123" in char_str


class TestCharactersAPIComprehensive:
    """Comprehensive test suite for CharactersAPI class."""

    def test_characters_api_initialization(self, mock_client):
        """Test CharactersAPI initialization."""
        api = CharactersAPI(mock_client)
        assert api.client == mock_client

    def test_list_success(self, mock_client):
        """Test successful character listing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Character 1",
                    "slug": "character-1",
                    "description": "First character",
                    "system_prompt": "You are character 1",
                    "capabilities": {"function_calling": True},
                    "category": "assistant",
                    "tags": ["helpful"],
                    "is_public": True
                },
                {
                    "id": "char-2",
                    "name": "Character 2",
                    "slug": "character-2",
                    "description": "Second character",
                    "system_prompt": "You are character 2",
                    "capabilities": {"web_search": True},
                    "is_public": False
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.list()
        
        assert len(characters) == 2
        assert all(isinstance(char, Character) for char in characters)
        assert characters[0].id == "char-1"
        assert characters[0].name == "Character 1"
        assert characters[0].is_public is True
        assert characters[1].id == "char-2"
        assert characters[1].is_public is False

    def test_list_with_filters(self, mock_client):
        """Test character listing with filters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.list(
            category="assistant",
            tags=["helpful", "test"],
            is_public=True,
            limit=10,
            offset=5,
            custom_param="value"
        )
        
        mock_client.get.assert_called_once_with("/characters", params={
            "category": "assistant",
            "tags": "helpful,test",
            "is_public": True,
            "limit": 10,
            "offset": 5,
            "custom_param": "value"
        })

    def test_list_invalid_response(self, mock_client):
        """Test character listing with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        
        with pytest.raises(CharacterNotFoundError, match="Invalid response format from characters API"):
            api.list()

    def test_get_success(self, mock_client):
        """Test successful character retrieval by slug."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "char-123",
                "name": "Test Character",
                "slug": "test-character",
                "description": "A test character",
                "system_prompt": "You are a test character",
                "capabilities": {"function_calling": True},
                "is_public": True
            }
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        character = api.get("test-character")
        
        assert character is not None
        assert isinstance(character, Character)
        assert character.id == "char-123"
        assert character.slug == "test-character"

    def test_get_not_found(self, mock_client):
        """Test character retrieval when character not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": None}
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        character = api.get("nonexistent-character")
        
        assert character is None

    def test_get_with_404_error(self, mock_client):
        """Test character retrieval with 404 error."""
        mock_client.get.side_effect = VeniceAPIError("Character not found", status_code=404)
        
        api = CharactersAPI(mock_client)
        character = api.get("nonexistent-character")
        
        assert character is None

    def test_get_with_other_error(self, mock_client):
        """Test character retrieval with other API error."""
        mock_client.get.side_effect = VeniceAPIError("Server error", status_code=500)
        
        api = CharactersAPI(mock_client)
        
        with pytest.raises(VeniceAPIError, match="Server error"):
            api.get("test-character")

    def test_search_success(self, mock_client):
        """Test successful character search."""
        # Mock list response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Helpful Assistant",
                    "slug": "helpful-assistant",
                    "description": "A helpful AI assistant",
                    "system_prompt": "You are a helpful assistant",
                    "capabilities": {},
                    "category": "assistant"
                },
                {
                    "id": "char-2",
                    "name": "Creative Writer",
                    "slug": "creative-writer",
                    "description": "A creative writing assistant",
                    "system_prompt": "You are a creative writer",
                    "capabilities": {},
                    "category": "creative"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.search("helpful")
        
        assert len(characters) == 1
        assert characters[0].name == "Helpful Assistant"

    def test_search_with_filters(self, mock_client):
        """Test character search with filters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.search("test", category="assistant", tags=["helpful"])
        
        mock_client.get.assert_called_once_with("/characters", params={
            "category": "assistant",
            "tags": "helpful"
        })

    def test_search_case_insensitive(self, mock_client):
        """Test character search case insensitive."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Helpful Assistant",
                    "slug": "helpful-assistant",
                    "description": "A helpful AI assistant",
                    "system_prompt": "You are a helpful assistant",
                    "capabilities": {},
                    "category": "assistant"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.search("HELPFUL")
        
        assert len(characters) == 1
        assert characters[0].name == "Helpful Assistant"

    def test_search_in_description(self, mock_client):
        """Test character search in description."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Test Character",
                    "slug": "test-character",
                    "description": "This is a helpful assistant",
                    "system_prompt": "You are a test character",
                    "capabilities": {},
                    "category": "assistant"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.search("helpful")
        
        assert len(characters) == 1
        assert characters[0].name == "Test Character"

    def test_search_in_system_prompt(self, mock_client):
        """Test character search in system prompt."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Test Character",
                    "slug": "test-character",
                    "description": "A test character",
                    "system_prompt": "You are a helpful assistant",
                    "capabilities": {},
                    "category": "assistant"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.search("helpful")
        
        assert len(characters) == 1
        assert characters[0].name == "Test Character"

    def test_get_by_category(self, mock_client):
        """Test getting characters by category."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.get_by_category("assistant")
        
        mock_client.get.assert_called_once_with("/characters", params={"category": "assistant"})

    def test_get_by_tags(self, mock_client):
        """Test getting characters by tags."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.get_by_tags(["helpful", "test"])
        
        mock_client.get.assert_called_once_with("/characters", params={"tags": "helpful,test"})

    def test_get_public_characters(self, mock_client):
        """Test getting public characters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        characters = api.get_public_characters()
        
        mock_client.get.assert_called_once_with("/characters", params={"is_public": True})

    def test_get_categories(self, mock_client):
        """Test getting character categories."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"category": "assistant"},
                {"category": "creative"},
                {"category": "assistant"},  # Duplicate
                {"category": "technical"},
                {"category": None}  # None category
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        categories = api.get_categories()
        
        assert categories == ["assistant", "creative", "technical"]

    def test_get_tags(self, mock_client):
        """Test getting character tags."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"tags": ["helpful", "test"]},
                {"tags": ["creative", "art"]},
                {"tags": ["helpful", "assistant"]},  # Overlapping tags
                {"tags": None}  # None tags
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = CharactersAPI(mock_client)
        tags = api.get_tags()
        
        assert set(tags) == {"helpful", "test", "creative", "art", "assistant"}

    def test_parse_character(self, mock_client):
        """Test character parsing from API response."""
        api = CharactersAPI(mock_client)
        
        data = {
            "id": "char-123",
            "name": "Test Character",
            "slug": "test-character",
            "description": "A test character",
            "system_prompt": "You are a test character",
            "capabilities": {"function_calling": True},
            "category": "assistant",
            "tags": ["helpful", "test"],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
            "is_public": True,
            "creator": "user123"
        }
        
        character = api._parse_character(data)
        
        assert isinstance(character, Character)
        assert character.id == "char-123"
        assert character.name == "Test Character"
        assert character.slug == "test-character"
        assert character.description == "A test character"
        assert character.system_prompt == "You are a test character"
        assert character.capabilities == {"function_calling": True}
        assert character.category == "assistant"
        assert character.tags == ["helpful", "test"]
        assert character.created_at == "2023-01-01T00:00:00Z"
        assert character.updated_at == "2023-01-02T00:00:00Z"
        assert character.is_public is True
        assert character.creator == "user123"

    def test_parse_character_with_defaults(self, mock_client):
        """Test character parsing with default values."""
        api = CharactersAPI(mock_client)
        
        data = {
            "id": "char-123",
            "name": "Test Character",
            "slug": "test-character",
            "description": "A test character",
            "system_prompt": "You are a test character",
            "capabilities": {}
        }
        
        character = api._parse_character(data)
        
        assert character.id == "char-123"
        assert character.name == "Test Character"
        assert character.slug == "test-character"
        assert character.description == "A test character"
        assert character.system_prompt == "You are a test character"
        assert character.capabilities == {}
        assert character.category is None
        assert character.tags is None
        assert character.created_at is None
        assert character.updated_at is None
        assert character.is_public is False
        assert character.creator is None


class TestCharacterManagerComprehensive:
    """Comprehensive test suite for CharacterManager class."""

    def test_character_manager_initialization(self, mock_client):
        """Test CharacterManager initialization."""
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        assert manager.characters_api == characters_api
        assert manager._character_cache == {}

    def test_get_character_by_slug_with_cache(self, mock_client):
        """Test getting character by slug with caching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "char-123",
                "name": "Test Character",
                "slug": "test-character",
                "description": "A test character",
                "system_prompt": "You are a test character",
                "capabilities": {}
            }
        }
        mock_client.get.return_value = mock_response
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        # First call - should cache the result
        character1 = manager.get_character("test-character")
        assert character1 is not None
        assert character1.slug == "test-character"
        
        # Second call - should use cache
        character2 = manager.get_character("test-character")
        assert character2 == character1
        assert "test-character" in manager._character_cache

    def test_get_character_by_slug_without_cache(self, mock_client):
        """Test getting character by slug without caching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "char-123",
                "name": "Test Character",
                "slug": "test-character",
                "description": "A test character",
                "system_prompt": "You are a test character",
                "capabilities": {}
            }
        }
        mock_client.get.return_value = mock_response
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        character = manager.get_character("test-character", use_cache=False)
        assert character is not None
        assert character.slug == "test-character"
        assert "test-character" not in manager._character_cache

    def test_get_character_by_name_fallback(self, mock_client):
        """Test getting character by name when slug fails."""
        # First call (by slug) returns None
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {"data": None}
        
        # Second call (search by name) returns results
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {
            "data": [
                {
                    "id": "char-123",
                    "name": "Test Character",
                    "slug": "test-character",
                    "description": "A test character",
                    "system_prompt": "You are a test character",
                    "capabilities": {}
                }
            ]
        }
        
        mock_client.get.side_effect = [mock_response1, mock_response2]
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        character = manager.get_character("Test Character")
        assert character is not None
        assert character.name == "Test Character"

    def test_get_character_not_found(self, mock_client):
        """Test getting character that doesn't exist."""
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {"data": None}
        
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {"data": []}
        
        mock_client.get.side_effect = [mock_response1, mock_response2]
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        character = manager.get_character("nonexistent")
        assert character is None

    def test_find_characters_by_capability(self, mock_client):
        """Test finding characters by capability."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Character 1",
                    "slug": "character-1",
                    "description": "First character",
                    "system_prompt": "You are character 1",
                    "capabilities": {"function_calling": True, "web_search": False}
                },
                {
                    "id": "char-2",
                    "name": "Character 2",
                    "slug": "character-2",
                    "description": "Second character",
                    "system_prompt": "You are character 2",
                    "capabilities": {"web_search": True, "streaming": True}
                },
                {
                    "id": "char-3",
                    "name": "Character 3",
                    "slug": "character-3",
                    "description": "Third character",
                    "system_prompt": "You are character 3",
                    "capabilities": {"function_calling": False}
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        # Find characters with function_calling capability
        characters = manager.find_characters_by_capability("function_calling")
        assert len(characters) == 1
        assert characters[0].id == "char-1"
        
        # Find characters with web_search capability
        characters = manager.find_characters_by_capability("web_search")
        assert len(characters) == 1
        assert characters[0].id == "char-2"

    def test_get_recommended_characters_creative(self, mock_client):
        """Test getting recommended characters for creative context."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Creative Writer",
                    "slug": "creative-writer",
                    "description": "A creative writing assistant",
                    "system_prompt": "You are a creative writer",
                    "capabilities": {"creative": True}
                },
                {
                    "id": "char-2",
                    "name": "Technical Assistant",
                    "slug": "technical-assistant",
                    "description": "A technical assistant",
                    "system_prompt": "You are a technical assistant",
                    "capabilities": {"technical": True}
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        characters = manager.get_recommended_characters("I need help with creative writing and art")
        assert len(characters) == 1
        assert characters[0].id == "char-1"

    def test_get_recommended_characters_technical(self, mock_client):
        """Test getting recommended characters for technical context."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Creative Writer",
                    "slug": "creative-writer",
                    "description": "A creative writing assistant",
                    "system_prompt": "You are a creative writer",
                    "capabilities": {"creative": True}
                },
                {
                    "id": "char-2",
                    "name": "Technical Assistant",
                    "slug": "technical-assistant",
                    "description": "A technical assistant",
                    "system_prompt": "You are a technical assistant",
                    "capabilities": {"technical": True}
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        characters = manager.get_recommended_characters("I need help with programming and code")
        assert len(characters) == 1
        assert characters[0].id == "char-2"

    def test_get_recommended_characters_multiple_matches(self, mock_client):
        """Test getting recommended characters with multiple matches."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Creative Writer",
                    "slug": "creative-writer",
                    "description": "A creative writing assistant",
                    "system_prompt": "You are a creative writer",
                    "capabilities": {"creative": True}
                },
                {
                    "id": "char-2",
                    "name": "Art Assistant",
                    "slug": "art-assistant",
                    "description": "An art creation assistant",
                    "system_prompt": "You are an art assistant",
                    "capabilities": {"creative": True}
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        characters = manager.get_recommended_characters("I need help with creative writing and art")
        assert len(characters) == 2
        character_ids = [char.id for char in characters]
        assert "char-1" in character_ids
        assert "char-2" in character_ids

    def test_get_recommended_characters_no_matches(self, mock_client):
        """Test getting recommended characters with no matches."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Technical Assistant",
                    "slug": "technical-assistant",
                    "description": "A technical assistant",
                    "system_prompt": "You are a technical assistant",
                    "capabilities": {"technical": True}
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        characters = manager.get_recommended_characters("I need help with something unrelated")
        assert len(characters) == 0

    def test_clear_cache(self, mock_client):
        """Test clearing the character cache."""
        characters_api = CharactersAPI(mock_client)
        manager = CharacterManager(characters_api)
        
        # Add something to cache
        manager._character_cache["test"] = "cached_value"
        assert "test" in manager._character_cache
        
        # Clear cache
        manager.clear_cache()
        assert manager._character_cache == {}


class TestConvenienceFunctionsComprehensive:
    """Comprehensive test suite for convenience functions."""

    def test_get_character_with_client(self, mock_client):
        """Test get_character with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "char-123",
                "name": "Test Character",
                "slug": "test-character",
                "description": "A test character",
                "system_prompt": "You are a test character",
                "capabilities": {}
            }
        }
        mock_client.get.return_value = mock_response
        
        character = get_character("test-character", client=mock_client)
        
        assert character is not None
        assert isinstance(character, Character)
        assert character.slug == "test-character"

    def test_get_character_without_client(self):
        """Test get_character without provided client."""
        with patch('venice_sdk.characters.load_config') as mock_load_config:
            with patch('venice_sdk.characters.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": {
                        "id": "char-123",
                        "name": "Test Character",
                        "slug": "test-character",
                        "description": "A test character",
                        "system_prompt": "You are a test character",
                        "capabilities": {}
                    }
                }
                mock_client.get.return_value = mock_response
                
                character = get_character("test-character")
                
                assert character is not None
                assert character.slug == "test-character"

    def test_list_characters_with_client(self, mock_client):
        """Test list_characters with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Character 1",
                    "slug": "character-1",
                    "description": "First character",
                    "system_prompt": "You are character 1",
                    "capabilities": {}
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        characters = list_characters(client=mock_client, category="assistant")
        
        assert len(characters) == 1
        assert isinstance(characters[0], Character)
        assert characters[0].id == "char-1"

    def test_search_characters_with_client(self, mock_client):
        """Test search_characters with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "char-1",
                    "name": "Helpful Assistant",
                    "slug": "helpful-assistant",
                    "description": "A helpful assistant",
                    "system_prompt": "You are a helpful assistant",
                    "capabilities": {}
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        characters = search_characters("helpful", client=mock_client)
        
        assert len(characters) == 1
        assert characters[0].name == "Helpful Assistant"

    def test_search_characters_without_client(self):
        """Test search_characters without provided client."""
        with patch('venice_sdk.characters.load_config') as mock_load_config:
            with patch('venice_sdk.characters.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": [
                        {
                            "id": "char-1",
                            "name": "Helpful Assistant",
                            "slug": "helpful-assistant",
                            "description": "A helpful assistant",
                            "system_prompt": "You are a helpful assistant",
                            "capabilities": {}
                        }
                    ]
                }
                mock_client.get.return_value = mock_response
                
                characters = search_characters("helpful")
                
                assert len(characters) == 1
                assert characters[0].name == "Helpful Assistant"
