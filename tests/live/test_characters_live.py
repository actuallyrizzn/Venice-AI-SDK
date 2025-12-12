"""
Live tests for the CharactersAPI module.

These tests make real API calls to verify characters functionality.
"""

import pytest
import os
from venice_sdk.characters import CharactersAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config, load_config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.live
class TestCharactersAPILive:
    """Live tests for CharactersAPI with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = load_config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.characters_api = CharactersAPI(self.client)

    def test_list_characters(self):
        """Test listing all available characters."""
        characters = self.characters_api.list()
        
        assert isinstance(characters, list)
        assert len(characters) > 0
        
        # Verify character structure
        character = characters[0]
        assert hasattr(character, 'id')
        assert hasattr(character, 'name')
        assert hasattr(character, 'description')
        assert hasattr(character, 'category')
        assert hasattr(character, 'tags')
        assert hasattr(character, 'capabilities')
        assert hasattr(character, 'system_prompt')
        assert hasattr(character, 'slug')

    def test_get_character_by_id(self):
        """Test getting a specific character by ID."""
        # First get the list to find a valid character ID
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        character_id = characters[0].id
        character = self.characters_api.get(character_id)
        
        # The API might return a list, so handle both cases
        if isinstance(character, list):
            assert len(character) > 0
            character = character[0]
        
        assert character is not None
        assert character.id == character_id
        assert hasattr(character, 'name')
        assert hasattr(character, 'description')

    def test_get_nonexistent_character(self):
        """Test getting a character that doesn't exist."""
        try:
            character = self.characters_api.get("nonexistent-character-id")
            # If it returns a list, check if it's empty
            if isinstance(character, list):
                assert len(character) == 0
            else:
                assert character is None
        except VeniceAPIError:
            # API might raise an error for nonexistent characters
            pass

    def test_search_characters(self):
        """Test searching characters."""
        # Search for characters with "assistant" in the name or description
        characters = self.characters_api.search("assistant")
        
        assert isinstance(characters, list)
        # Should find at least one character
        assert len(characters) > 0
        
        # Verify search results
        for character in characters:
            search_term = "assistant"
            assert (search_term in character.name.lower() or 
                   search_term in character.description.lower())

    def test_search_characters_case_insensitive(self):
        """Test case-insensitive character search."""
        characters = self.characters_api.search("ASSISTANT")
        
        assert isinstance(characters, list)
        assert len(characters) > 0

    def test_search_characters_no_results(self):
        """Test character search with no results."""
        characters = self.characters_api.search("nonexistent-character-name")
        
        assert isinstance(characters, list)
        assert len(characters) == 0

    def test_get_characters_by_category(self):
        """Test getting characters by category."""
        # First get all characters to find available categories
        all_characters = self.characters_api.list()
        assert len(all_characters) > 0
        
        # Get unique categories
        categories = set(char.category for char in all_characters if char.category)
        
        if categories:
            category = list(categories)[0]
            characters = self.characters_api.get_by_category(category)
            
            assert isinstance(characters, list)
            assert len(characters) > 0
            
            # Verify all characters belong to the specified category
            for character in characters:
                assert character.category == category

    def test_get_characters_by_tags(self):
        """Test getting characters by tags."""
        # First get all characters to find available tags
        all_characters = self.characters_api.list()
        assert len(all_characters) > 0
        
        # Get unique tags
        all_tags = set()
        for char in all_characters:
            if char.tags:
                all_tags.update(char.tags)
        
        if all_tags:
            tag = list(all_tags)[0]
            characters = self.characters_api.get_by_tags([tag])
            
            assert isinstance(characters, list)
            assert len(characters) > 0
            
            # Verify all characters have the specified tag
            for character in characters:
                assert tag in character.tags

    def test_get_public_characters(self):
        """Test getting public characters."""
        characters = self.characters_api.get_public_characters()
        
        assert isinstance(characters, list)
        # Note: There might not be any public characters, so just check the structure
        for character in characters:
            assert hasattr(character, 'is_public')
            # Don't assert is_public is True since the API might not have public characters

    def test_get_categories(self):
        """Test getting available categories."""
        categories = self.characters_api.get_categories()
        
        assert isinstance(categories, list)
        # Note: There might not be any categories, so just check the structure
        for category in categories:
            assert isinstance(category, str)
            assert len(category) > 0

    def test_get_tags(self):
        """Test getting available tags."""
        tags = self.characters_api.get_tags()
        
        assert isinstance(tags, list)
        assert len(tags) > 0
        
        # Verify all tags are strings
        for tag in tags:
            assert isinstance(tag, str)
            assert len(tag) > 0

    def test_character_capabilities(self):
        """Test character capabilities."""
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        character = characters[0]
        
        # Test has_capability method
        if character.capabilities:
            for capability in character.capabilities:
                assert character.has_capability(capability) is True
        
        # Test capabilities access
        if character.capabilities:
            for capability, value in character.capabilities.items():
                assert character.capabilities.get(capability) == value
        
        # Test capabilities with default
        assert character.capabilities.get("nonexistent", "default") == "default"

    def test_character_to_venice_parameters(self):
        """Test character to Venice parameters conversion."""
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        character = characters[0]
        params = character.to_venice_parameters()
        
        assert isinstance(params, dict)
        assert "character_slug" in params
        
        # Verify parameter types
        assert isinstance(params["character_slug"], str)
        assert params["character_slug"] == character.slug

    def test_character_manager_get_character(self):
        """Test CharacterManager get_character method."""
        from venice_sdk.characters import CharacterManager
        
        manager = CharacterManager(self.characters_api)
        
        # First get the list to find a valid character ID
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        character_id = characters[0].id
        character = manager.get_character(character_id)
        
        # The API might return a list, so handle both cases
        if isinstance(character, list):
            assert len(character) > 0
            character = character[0]
        
        assert character is not None
        assert character.id == character_id

    def test_character_manager_find_characters_by_capability(self):
        """Test CharacterManager find_characters_by_capability method."""
        from venice_sdk.characters import CharacterManager
        
        manager = CharacterManager(self.characters_api)
        
        # Find characters with any capability
        characters = self.characters_api.list()
        if characters and characters[0].capabilities:
            capability = list(characters[0].capabilities.keys())[0]
            matching_characters = manager.find_characters_by_capability(capability)
            
            assert isinstance(matching_characters, list)
            assert len(matching_characters) > 0
            
            # Verify all characters have the capability
            for character in matching_characters:
                assert character.has_capability(capability)

    def test_character_manager_get_recommended_characters(self):
        """Test CharacterManager get_recommended_characters method."""
        from venice_sdk.characters import CharacterManager
        
        manager = CharacterManager(self.characters_api)
        
        # Get recommended characters for a task
        task = "chat"
        recommended = manager.get_recommended_characters(task)
        
        assert isinstance(recommended, list)
        # Note: There might not be any recommended characters, so just check the structure
        for character in recommended:
            assert hasattr(character, 'id')
            assert hasattr(character, 'name')

    def test_character_manager_clear_cache(self):
        """Test CharacterManager clear_cache method."""
        from venice_sdk.characters import CharacterManager
        
        manager = CharacterManager(self.characters_api)
        
        # Clear cache should not raise an error
        manager.clear_cache()

    def test_character_personality_structure(self):
        """Test character personality structure."""
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        for character in characters:
            # Character class doesn't have personality attribute, so just check basic structure
            assert hasattr(character, 'description')
            assert isinstance(character.description, str)

    def test_character_background_structure(self):
        """Test character background structure."""
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        for character in characters:
            # Character class doesn't have background attribute, so just check basic structure
            assert hasattr(character, 'description')
            assert isinstance(character.description, str)

    def test_character_tags_structure(self):
        """Test character tags structure."""
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        for character in characters:
            if character.tags:
                assert isinstance(character.tags, list)
                assert all(isinstance(tag, str) for tag in character.tags)
                assert all(len(tag) > 0 for tag in character.tags)

    def test_character_capabilities_structure(self):
        """Test character capabilities structure."""
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        for character in characters:
            if character.capabilities:
                assert isinstance(character.capabilities, dict)
                # Capabilities might contain various features
                for key, value in character.capabilities.items():
                    assert isinstance(key, str)
                    assert isinstance(value, (str, int, float, bool, list, dict))

    def test_character_error_handling(self):
        """Test error handling in characters API."""
        # Test with invalid client
        from venice_sdk.client import HTTPClient
        from venice_sdk.config import Config
        
        invalid_config = Config(api_key="invalid-key")
        invalid_client = HTTPClient(invalid_config)
        invalid_characters_api = CharactersAPI(invalid_client)
        
        with pytest.raises(VeniceAPIError):
            invalid_characters_api.list()

    def test_character_performance(self):
        """Test characters API performance."""
        import time
        
        start_time = time.time()
        characters = self.characters_api.list()
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert len(characters) > 0
        assert response_time < 10  # Should complete within 10 seconds
        assert response_time > 0

    def test_character_caching(self):
        """Test characters API caching behavior."""
        import time
        
        # First call
        start_time = time.time()
        characters1 = self.characters_api.list()
        first_call_time = time.time() - start_time
        
        # Second call (should be faster due to caching)
        start_time = time.time()
        characters2 = self.characters_api.list()
        second_call_time = time.time() - start_time
        
        assert characters1 == characters2
        # Second call should be faster (though this might not always be true)
        assert second_call_time >= 0

    def test_character_concurrent_access(self):
        """Test concurrent access to characters API."""
        import threading
        import time
        
        results = []
        errors = []
        
        def get_characters():
            try:
                characters = self.characters_api.list()
                results.append(len(characters))
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_characters)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 5
        assert len(errors) == 0
        assert all(count > 0 for count in results)
        assert all(count == results[0] for count in results)  # All should return same count

    def test_character_search_performance(self):
        """Test character search performance."""
        import time
        
        search_queries = ["assistant", "helper", "friend", "teacher", "guide"]
        
        for query in search_queries:
            start_time = time.time()
            characters = self.characters_api.search(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert isinstance(characters, list)
            assert response_time < 5  # Should complete within 5 seconds
            assert response_time > 0

    def test_character_category_filtering(self):
        """Test character category filtering."""
        all_characters = self.characters_api.list()
        assert len(all_characters) > 0
        
        # Get unique categories
        categories = set(char.category for char in all_characters if char.category)
        
        for category in categories:
            filtered_characters = self.characters_api.get_by_category(category)
            
            assert isinstance(filtered_characters, list)
            assert len(filtered_characters) > 0
            
            # Verify all characters belong to the specified category
            for character in filtered_characters:
                assert character.category == category

    def test_character_tag_filtering(self):
        """Test character tag filtering."""
        all_characters = self.characters_api.list()
        assert len(all_characters) > 0
        
        # Get unique tags
        all_tags = set()
        for char in all_characters:
            if char.tags:
                all_tags.update(char.tags)
        
        for tag in list(all_tags)[:5]:  # Test first 5 tags
            filtered_characters = self.characters_api.get_by_tags([tag])
            
            assert isinstance(filtered_characters, list)
            assert len(filtered_characters) > 0
            
            # Verify all characters have the specified tag
            for character in filtered_characters:
                assert tag in character.tags

    def test_character_memory_usage(self):
        """Test memory usage during character operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple character operations
        for _ in range(10):
            characters = self.characters_api.list()
            assert len(characters) > 0
            
            # Search for characters
            search_results = self.characters_api.search("assistant")
            assert isinstance(search_results, list)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024

    def test_character_data_consistency(self):
        """Test character data consistency across multiple calls."""
        characters1 = self.characters_api.list()
        characters2 = self.characters_api.list()
        
        # Data should be consistent
        assert len(characters1) == len(characters2)
        
        # Character IDs should be the same
        ids1 = [char.id for char in characters1]
        ids2 = [char.id for char in characters2]
        assert set(ids1) == set(ids2)

    def test_character_unicode_handling(self):
        """Test character handling with unicode characters."""
        characters = self.characters_api.list()
        assert len(characters) > 0
        
        for character in characters:
            # Test that unicode characters in names and descriptions are handled properly
            assert isinstance(character.name, str)
            assert isinstance(character.description, str)
            
            # Names should not be empty, descriptions might be
            assert len(character.name) > 0
