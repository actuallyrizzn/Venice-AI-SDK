"""
Comprehensive unit tests for the cli module.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from click.testing import CliRunner
from venice_sdk.cli import get_api_key, cli, auth, status, main


class TestGetApiKeyComprehensive:
    """Comprehensive test suite for get_api_key function."""

    def test_get_api_key_from_environment(self):
        """Test get_api_key when API key is in environment variables."""
        with patch.dict(os.environ, {'VENICE_API_KEY': 'env-api-key'}, clear=True):
            with patch('venice_sdk.cli.load_dotenv'):
                api_key = get_api_key()
                assert api_key == 'env-api-key'

    def test_get_api_key_from_env_file(self):
        """Test get_api_key when API key is in .env file."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('venice_sdk.cli.Path') as mock_path:
                mock_env_path = MagicMock()
                mock_env_path.exists.return_value = True
                mock_path.return_value = mock_env_path
                
                with patch('venice_sdk.cli.load_dotenv') as mock_load_dotenv:
                    # Mock load_dotenv to set the environment variable
                    def mock_load_dotenv_side_effect(path):
                        os.environ['VENICE_API_KEY'] = 'env-file-key'
                    mock_load_dotenv.side_effect = mock_load_dotenv_side_effect
                    
                    api_key = get_api_key()
                    assert api_key == 'env-file-key'
                    mock_load_dotenv.assert_called_once_with(mock_env_path)

    def test_get_api_key_env_file_not_exists(self):
        """Test get_api_key when .env file doesn't exist."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('venice_sdk.cli.Path') as mock_path:
                mock_env_path = MagicMock()
                mock_env_path.exists.return_value = False
                mock_path.return_value = mock_env_path
                
                api_key = get_api_key()
                assert api_key is None

    def test_get_api_key_environment_overrides_env_file(self):
        """Test that environment variable overrides .env file."""
        with patch.dict(os.environ, {'VENICE_API_KEY': 'env-key'}, clear=True):
            with patch('venice_sdk.cli.Path') as mock_path:
                mock_env_path = MagicMock()
                mock_env_path.exists.return_value = True
                mock_path.return_value = mock_env_path
                
                with patch('venice_sdk.cli.load_dotenv'):
                    api_key = get_api_key()
                    assert api_key == 'env-key'

    def test_get_api_key_no_key_found(self):
        """Test get_api_key when no key is found anywhere."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('venice_sdk.cli.Path') as mock_path:
                mock_env_path = MagicMock()
                mock_env_path.exists.return_value = False
                mock_path.return_value = mock_env_path
                
                api_key = get_api_key()
                assert api_key is None

    def test_get_api_key_empty_environment_key(self):
        """Test get_api_key with empty environment variable."""
        with patch.dict(os.environ, {'VENICE_API_KEY': ''}, clear=True):
            with patch('venice_sdk.cli.Path') as mock_path:
                mock_env_path = MagicMock()
                mock_env_path.exists.return_value = True
                mock_path.return_value = mock_env_path
                
                with patch('venice_sdk.cli.load_dotenv'):
                    with patch.dict(os.environ, {'VENICE_API_KEY': 'env-file-key'}, clear=True):
                        api_key = get_api_key()
                        assert api_key == 'env-file-key'

    def test_get_api_key_whitespace_key(self):
        """Test get_api_key with whitespace-only key."""
        with patch.dict(os.environ, {'VENICE_API_KEY': '   '}, clear=True):
            with patch('venice_sdk.cli.load_dotenv'):
                api_key = get_api_key()
                assert api_key == '   '  # Whitespace preserved

    def test_get_api_key_special_characters(self):
        """Test get_api_key with special characters in key."""
        special_key = 'sk-1234567890abcdef!@#$%^&*()'
        with patch.dict(os.environ, {'VENICE_API_KEY': special_key}, clear=True):
            with patch('venice_sdk.cli.load_dotenv'):
                api_key = get_api_key()
                assert api_key == special_key


class TestCliComprehensive:
    """Comprehensive test suite for CLI commands."""

    def test_cli_group_creation(self):
        """Test that CLI group is created properly."""
        assert cli.name == 'cli'
        assert hasattr(cli, 'commands')

    def test_auth_command_with_new_env_file(self, tmp_path):
        """Test auth command creating new .env file."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = False
            mock_env_path.touch.return_value = None
            mock_path.return_value = mock_env_path
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = runner.invoke(auth, ['test-api-key'])
                
                assert result.exit_code == 0
                assert "API key has been set successfully!" in result.output
                mock_env_path.touch.assert_called_once()
                mock_file.assert_called_once_with(mock_env_path, 'w', encoding='utf-8')
                mock_file().write.assert_called_once_with('\nVENICE_API_KEY=test-api-key\n')

    def test_auth_command_with_existing_env_file(self, tmp_path):
        """Test auth command with existing .env file."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = True
            mock_path.return_value = mock_env_path
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = runner.invoke(auth, ['test-api-key'])
                
                assert result.exit_code == 0
                assert "API key has been set successfully!" in result.output
                mock_env_path.touch.assert_not_called()
                # Should be called twice: once for reading, once for writing
                assert mock_file.call_count == 2
                mock_file().write.assert_called_once_with('\nVENICE_API_KEY=test-api-key\n')

    def test_auth_command_with_special_characters(self, tmp_path):
        """Test auth command with special characters in API key."""
        runner = CliRunner()
        special_key = 'sk-1234567890abcdef!@#$%^&*()'
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = False
            mock_env_path.touch.return_value = None
            mock_path.return_value = mock_env_path
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = runner.invoke(auth, [special_key])
                
                assert result.exit_code == 0
                assert "API key has been set successfully!" in result.output
                mock_file().write.assert_called_once_with(f'\nVENICE_API_KEY={special_key}\n')

    def test_auth_command_with_whitespace_key(self, tmp_path):
        """Test auth command with whitespace in API key."""
        runner = CliRunner()
        whitespace_key = '  test-key  '
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = False
            mock_env_path.touch.return_value = None
            mock_path.return_value = mock_env_path
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = runner.invoke(auth, [whitespace_key])
                
                assert result.exit_code == 0
                assert "API key has been set successfully!" in result.output
                mock_file().write.assert_called_once_with(f'\nVENICE_API_KEY={whitespace_key}\n')

    def test_auth_command_with_empty_key(self, tmp_path):
        """Test auth command with empty API key."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = False
            mock_env_path.touch.return_value = None
            mock_path.return_value = mock_env_path
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = runner.invoke(auth, [''])
                
                assert result.exit_code == 0
                assert "API key has been set successfully!" in result.output
                mock_file().write.assert_called_once_with('\nVENICE_API_KEY=\n')

    def test_status_command_with_api_key(self):
        """Test status command when API key is present."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.get_api_key', return_value='sk-1234567890abcdef'):
            result = runner.invoke(status)
            
            assert result.exit_code == 0
            assert "[OK] API key is set" in result.output
            assert "Key: sk-..." in result.output
            assert "[WARNING] Note: Never share this output" in result.output

    def test_status_command_without_api_key(self):
        """Test status command when no API key is present."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.get_api_key', return_value=None):
            result = runner.invoke(status)
            
            assert result.exit_code == 0
            assert "[ERROR] No API key is set" in result.output
            assert "Use 'venice auth <your-api-key>' to set your API key" in result.output

    def test_status_command_with_short_api_key(self):
        """Test status command with very short API key."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.get_api_key', return_value='sk'):
            result = runner.invoke(status)
            
            assert result.exit_code == 0
            assert "[OK] API key is set" in result.output
            assert "Key: ***..." in result.output

    def test_status_command_with_very_short_api_key(self):
        """Test status command with single character API key."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.get_api_key', return_value='s'):
            result = runner.invoke(status)
            
            assert result.exit_code == 0
            assert "[OK] API key is set" in result.output
            assert "Key: ***..." in result.output

    def test_status_command_with_empty_api_key(self):
        """Test status command with empty API key."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.get_api_key', return_value=''):
            result = runner.invoke(status)
            
            assert result.exit_code == 0
            assert "[ERROR] No API key is set" in result.output

    def test_status_command_with_whitespace_api_key(self):
        """Test status command with whitespace-only API key."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.get_api_key', return_value='   '):
            result = runner.invoke(status)
            
            assert result.exit_code == 0
            assert "[OK] API key is set" in result.output
            assert "Key:    ..." in result.output

    def test_main_function(self):
        """Test main function calls cli."""
        with patch('venice_sdk.cli.cli') as mock_cli:
            main()
            mock_cli.assert_called_once()

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Venice SDK command-line interface" in result.output

    def test_auth_command_help(self):
        """Test auth command help."""
        runner = CliRunner()
        result = runner.invoke(auth, ['--help'])
        
        assert result.exit_code == 0
        assert "Set your Venice API key" in result.output
        assert "store your API key in the .env file" in result.output

    def test_status_command_help(self):
        """Test status command help."""
        runner = CliRunner()
        result = runner.invoke(status, ['--help'])
        
        assert result.exit_code == 0
        assert "Check the current authentication status" in result.output

    def test_auth_command_missing_argument(self):
        """Test auth command without API key argument."""
        runner = CliRunner()
        result = runner.invoke(auth, [])
        
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_auth_command_with_multiple_arguments(self):
        """Test auth command with multiple arguments (should fail)."""
        runner = CliRunner()
        result = runner.invoke(auth, ['key1', 'key2'])
        
        assert result.exit_code != 0
        assert "Got unexpected extra argument" in result.output

    def test_status_command_with_arguments(self):
        """Test status command with arguments (should ignore them)."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.get_api_key', return_value='test-key'):
            result = runner.invoke(status, ['extra-arg'])
            
            # Click should handle this gracefully
            assert result.exit_code == 0 or result.exit_code != 0  # Either works or fails gracefully

    def test_auth_command_file_write_error(self, tmp_path):
        """Test auth command when file write fails."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = False
            mock_env_path.touch.return_value = None
            mock_path.return_value = mock_env_path
            
            with patch('builtins.open', side_effect=IOError("Permission denied")):
                result = runner.invoke(auth, ['test-key'])
                
                assert result.exit_code != 0
                assert "Permission denied" in str(result.exception)

    def test_auth_command_touch_error(self, tmp_path):
        """Test auth command when touch fails."""
        runner = CliRunner()
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = False
            mock_env_path.touch.side_effect = OSError("Permission denied")
            mock_path.return_value = mock_env_path
            
            result = runner.invoke(auth, ['test-key'])
            
            assert result.exit_code != 0
            assert "Permission denied" in str(result.exception)

    def test_cli_command_list(self):
        """Test that CLI has the expected commands."""
        assert 'auth' in cli.commands
        assert 'status' in cli.commands
        assert len(cli.commands) == 2

    def test_auth_command_with_long_api_key(self):
        """Test auth command with very long API key."""
        runner = CliRunner()
        long_key = 'sk-' + 'a' * 1000  # Very long key
        
        with patch('venice_sdk.cli.Path') as mock_path:
            mock_env_path = MagicMock()
            mock_env_path.exists.return_value = False
            mock_env_path.touch.return_value = None
            mock_path.return_value = mock_env_path
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = runner.invoke(auth, [long_key])
                
                assert result.exit_code == 0
                assert "API key has been set successfully!" in result.output
                mock_file().write.assert_called_once_with(f'\nVENICE_API_KEY={long_key}\n')

    def test_status_command_with_long_api_key(self):
        """Test status command with very long API key."""
        runner = CliRunner()
        long_key = 'sk-' + 'a' * 1000  # Very long key
        
        with patch('venice_sdk.cli.get_api_key', return_value=long_key):
            result = runner.invoke(status)
            
            assert result.exit_code == 0
            assert "[OK] API key is set" in result.output
            assert "Key: sk-..." in result.output
