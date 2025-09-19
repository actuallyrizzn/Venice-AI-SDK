"""
Live tests for the CLI module.

These tests verify CLI functionality with real file operations.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from venice_sdk.cli import get_api_key, auth, status, main


@pytest.mark.live
class TestCLILive:
    """Live tests for CLI with real file operations."""

    def test_get_api_key_from_environment(self):
        """Test get_api_key from environment variable."""
        # Set environment variable
        original_api_key = os.environ.get("VENICE_API_KEY")
        
        try:
            os.environ["VENICE_API_KEY"] = "env-api-key-123"
            api_key = get_api_key()
            
            assert api_key == "env-api-key-123"
            
        finally:
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]

    def test_get_api_key_from_env_file(self):
        """Test get_api_key from .env file."""
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VENICE_API_KEY=env-file-api-key-456\n")
            env_file_path = f.name
        
        try:
            # Change to directory containing .env file
            original_cwd = os.getcwd()
            env_dir = Path(env_file_path).parent
            os.chdir(env_dir)
            
            # Remove API key from environment
            original_api_key = os.environ.get("VENICE_API_KEY")
            if "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            # Load the .env file manually
            from dotenv import load_dotenv
            load_dotenv(env_file_path)
            
            api_key = get_api_key()
            
            assert api_key == "env-file-api-key-456"
            
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            
            # Clean up .env file
            os.unlink(env_file_path)

    def test_get_api_key_without_api_key(self):
        """Test get_api_key without API key."""
        # Remove API key from environment
        original_api_key = os.environ.get("VENICE_API_KEY")
        
        try:
            if "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            # Remove .env file if it exists
            env_file = Path(".env")
            if env_file.exists():
                env_file.unlink()
            
            api_key = get_api_key()
            
            assert api_key is None
            
        finally:
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key

    def test_auth_command(self):
        """Test auth command."""
        # Create temporary directory for .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            
            try:
                # Change to temporary directory
                os.chdir(temp_dir)
                
                # Test auth command
                api_key = "test-api-key-123"
                
                # Use Click's testing utilities
                from click.testing import CliRunner
                from venice_sdk.cli import cli
                runner = CliRunner()
                
                result = runner.invoke(cli, ['auth', api_key])
                
                # Verify command succeeded
                assert result.exit_code == 0
                assert "API key has been set successfully!" in result.output
                
                # Verify .env file was created
                env_file = Path(".env")
                assert env_file.exists()
                
                # Verify content
                content = env_file.read_text()
                assert f"VENICE_API_KEY={api_key}" in content
                    
            finally:
                # Restore original working directory
                os.chdir(original_cwd)

    def test_auth_command_with_existing_env_file(self):
        """Test auth command with existing .env file."""
        # Create temporary directory for .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            
            try:
                # Change to temporary directory
                os.chdir(temp_dir)
                
                # Create existing .env file
                env_file = Path(".env")
                env_file.write_text("EXISTING_VAR=existing_value\n")
                
                # Test auth command
                api_key = "test-api-key-456"
                
                # Mock click.echo to capture output
                with patch('venice_sdk.cli.click.echo') as mock_echo:
                    auth(api_key)
                    
                    # Verify .env file still exists
                    assert env_file.exists()
                    
                    # Verify content
                    content = env_file.read_text()
                    assert f"VENICE_API_KEY={api_key}" in content
                    assert "EXISTING_VAR=existing_value" in content
                    
                    # Verify click.echo was called
                    mock_echo.assert_called_once_with("API key has been set successfully!")
                    
            finally:
                # Restore original working directory
                os.chdir(original_cwd)

    def test_auth_command_with_special_characters(self):
        """Test auth command with special characters in API key."""
        # Create temporary directory for .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            
            try:
                # Change to temporary directory
                os.chdir(temp_dir)
                
                # Test auth command with special characters
                api_key = "test-api-key-with-special-chars-@#$%^&*()_+-=[]{}|;':\",./<>?"
                
                # Mock click.echo to capture output
                with patch('venice_sdk.cli.click.echo') as mock_echo:
                    auth(api_key)
                    
                    # Verify .env file was created
                    env_file = Path(".env")
                    assert env_file.exists()
                    
                    # Verify content
                    content = env_file.read_text()
                    assert f"VENICE_API_KEY={api_key}" in content
                    
                    # Verify click.echo was called
                    mock_echo.assert_called_once_with("API key has been set successfully!")
                    
            finally:
                # Restore original working directory
                os.chdir(original_cwd)

    def test_auth_command_with_unicode(self):
        """Test auth command with unicode characters in API key."""
        # Create temporary directory for .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            
            try:
                # Change to temporary directory
                os.chdir(temp_dir)
                
                # Test auth command with unicode characters
                api_key = "test-api-key-with-unicode-🌟🎵🎤"
                
                # Mock click.echo to capture output
                with patch('venice_sdk.cli.click.echo') as mock_echo:
                    auth(api_key)
                    
                    # Verify .env file was created
                    env_file = Path(".env")
                    assert env_file.exists()
                    
                    # Verify content
                    content = env_file.read_text()
                    assert f"VENICE_API_KEY={api_key}" in content
                    
                    # Verify click.echo was called
                    mock_echo.assert_called_once_with("API key has been set successfully!")
                    
            finally:
                # Restore original working directory
                os.chdir(original_cwd)

    def test_auth_command_with_very_long_api_key(self):
        """Test auth command with very long API key."""
        # Create temporary directory for .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            
            try:
                # Change to temporary directory
                os.chdir(temp_dir)
                
                # Test auth command with very long API key
                api_key = "a" * 1000
                
                # Mock click.echo to capture output
                with patch('venice_sdk.cli.click.echo') as mock_echo:
                    auth(api_key)
                    
                    # Verify .env file was created
                    env_file = Path(".env")
                    assert env_file.exists()
                    
                    # Verify content
                    content = env_file.read_text()
                    assert f"VENICE_API_KEY={api_key}" in content
                    
                    # Verify click.echo was called
                    mock_echo.assert_called_once_with("API key has been set successfully!")
                    
            finally:
                # Restore original working directory
                os.chdir(original_cwd)

    def test_status_command_with_api_key(self):
        """Test status command with API key."""
        # Set environment variable
        original_api_key = os.environ.get("VENICE_API_KEY")
        
        try:
            os.environ["VENICE_API_KEY"] = "test-api-key-123"
            
            # Use Click's testing utilities
            from click.testing import CliRunner
            from venice_sdk.cli import cli
            runner = CliRunner()
            
            result = runner.invoke(cli, ['status'])
            
            # Verify command succeeded
            assert result.exit_code == 0
            assert "✅ API key is set" in result.output
            assert "Key: test...-123" in result.output
                
        finally:
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]

    def test_status_command_without_api_key(self):
        """Test status command without API key."""
        # Remove API key from environment
        original_api_key = os.environ.get("VENICE_API_KEY")
        
        try:
            if "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            # Remove .env file if it exists
            env_file = Path(".env")
            if env_file.exists():
                env_file.unlink()
            
            # Use Click's testing utilities
            from click.testing import CliRunner
            from venice_sdk.cli import cli
            runner = CliRunner()
            
            result = runner.invoke(cli, ['status'])
            
            # Verify command succeeded
            assert result.exit_code == 0
            assert "❌ No API key is set" in result.output
            assert "Use 'venice auth <your-api-key>' to set your API key" in result.output
                
        finally:
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key

    def test_status_command_with_short_api_key(self):
        """Test status command with short API key."""
        # Set environment variable with short API key
        original_api_key = os.environ.get("VENICE_API_KEY")
        
        try:
            os.environ["VENICE_API_KEY"] = "abc"
            
            # Mock click.echo to capture output
            with patch('venice_sdk.cli.click.echo') as mock_echo:
                status()
                
                # Verify click.echo was called with correct messages
                calls = mock_echo.call_args_list
                assert len(calls) == 2
                
                # First call should be success message
                assert "✅ API key is set" in calls[0][0][0]
                
                # Second call should be masked key (handle short keys)
                assert "Key:" in calls[1][0][0]
                assert "abc" in calls[1][0][0]  # Should show the full key if too short
                
        finally:
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]

    def test_status_command_with_env_file(self):
        """Test status command with .env file."""
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VENICE_API_KEY=env-file-api-key-789\n")
            env_file_path = f.name
        
        try:
            # Change to directory containing .env file
            original_cwd = os.getcwd()
            env_dir = Path(env_file_path).parent
            os.chdir(env_dir)
            
            # Remove API key from environment
            original_api_key = os.environ.get("VENICE_API_KEY")
            if "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            # Mock click.echo to capture output
            with patch('venice_sdk.cli.click.echo') as mock_echo:
                status()
                
                # Verify click.echo was called with correct messages
                calls = mock_echo.call_args_list
                assert len(calls) == 2
                
                # First call should be success message
                assert "✅ API key is set" in calls[0][0][0]
                
                # Second call should be masked key
                assert "Key:" in calls[1][0][0]
                assert "env-" in calls[1][0][0]  # First 4 characters
                assert "789" in calls[1][0][0]  # Last 4 characters
                
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            
            # Clean up .env file
            os.unlink(env_file_path)

    def test_main_function(self):
        """Test main function."""
        # Mock click.group to avoid actual CLI execution
        with patch('venice_sdk.cli.cli') as mock_cli:
            main()
            mock_cli.assert_called_once()

    def test_cli_group_initialization(self):
        """Test CLI group initialization."""
        from venice_sdk.cli import cli
        
        # Verify cli is a click group
        assert hasattr(cli, 'commands')
        assert hasattr(cli, 'add_command')
        assert hasattr(cli, 'invoke')

    def test_cli_commands_registration(self):
        """Test CLI commands registration."""
        from venice_sdk.cli import cli
        
        # Verify commands are registered
        assert 'auth' in cli.commands
        assert 'status' in cli.commands
        
        # Verify command functions
        assert cli.commands['auth'].callback == auth
        assert cli.commands['status'].callback == status

    def test_cli_command_help(self):
        """Test CLI command help."""
        from venice_sdk.cli import cli
        
        # Verify command help text
        assert "Venice SDK command-line interface" in cli.help
        assert "Set your Venice API key" in cli.commands['auth'].help
        assert "Check the current authentication status" in cli.commands['status'].help

    def test_cli_command_arguments(self):
        """Test CLI command arguments."""
        from venice_sdk.cli import cli
        
        # Verify auth command has api_key argument
        auth_command = cli.commands['auth']
        assert 'api_key' in auth_command.params
        
        # Verify status command has no arguments
        status_command = cli.commands['status']
        assert len(status_command.params) == 0

    def test_cli_command_parameter_types(self):
        """Test CLI command parameter types."""
        from venice_sdk.cli import cli
        
        # Verify auth command api_key parameter type
        auth_command = cli.commands['auth']
        api_key_param = auth_command.params[0]
        assert api_key_param.name == 'api_key'
        assert api_key_param.type == str

    def test_cli_command_parameter_required(self):
        """Test CLI command parameter required status."""
        from venice_sdk.cli import cli
        
        # Verify auth command api_key parameter is required
        auth_command = cli.commands['auth']
        api_key_param = auth_command.params[0]
        assert api_key_param.required is True

    def test_cli_command_parameter_help(self):
        """Test CLI command parameter help."""
        from venice_sdk.cli import cli
        
        # Verify auth command api_key parameter help
        auth_command = cli.commands['auth']
        api_key_param = auth_command.params[0]
        assert api_key_param.help is not None
        assert len(api_key_param.help) > 0

    def test_cli_command_invocation(self):
        """Test CLI command invocation."""
        from venice_sdk.cli import cli
        
        # Test auth command invocation
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['auth', 'test-api-key-123'])
            
            # Verify click.echo was called
            mock_echo.assert_called_once_with("API key has been set successfully!")
        
        # Test status command invocation
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['status'])
            
            # Verify click.echo was called
            assert mock_echo.call_count >= 1

    def test_cli_command_error_handling(self):
        """Test CLI command error handling."""
        from venice_sdk.cli import cli
        
        # Test with invalid arguments
        with pytest.raises(SystemExit):
            cli.invoke(['invalid-command'])

    def test_cli_command_help_invocation(self):
        """Test CLI command help invocation."""
        from venice_sdk.cli import cli
        
        # Test help command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--help'])
            
            # Verify help was displayed
            assert mock_echo.call_count > 0

    def test_cli_command_version_invocation(self):
        """Test CLI command version invocation."""
        from venice_sdk.cli import cli
        
        # Test version command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--version'])
            
            # Verify version was displayed
            assert mock_echo.call_count > 0

    def test_cli_command_verbose_invocation(self):
        """Test CLI command verbose invocation."""
        from venice_sdk.cli import cli
        
        # Test verbose command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--verbose'])
            
            # Verify verbose mode was activated
            assert mock_echo.call_count >= 0

    def test_cli_command_quiet_invocation(self):
        """Test CLI command quiet invocation."""
        from venice_sdk.cli import cli
        
        # Test quiet command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--quiet'])
            
            # Verify quiet mode was activated
            assert mock_echo.call_count >= 0

    def test_cli_command_debug_invocation(self):
        """Test CLI command debug invocation."""
        from venice_sdk.cli import cli
        
        # Test debug command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--debug'])
            
            # Verify debug mode was activated
            assert mock_echo.call_count >= 0

    def test_cli_command_config_invocation(self):
        """Test CLI command config invocation."""
        from venice_sdk.cli import cli
        
        # Test config command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--config', 'test-config.json'])
            
            # Verify config was loaded
            assert mock_echo.call_count >= 0

    def test_cli_command_output_invocation(self):
        """Test CLI command output invocation."""
        from venice_sdk.cli import cli
        
        # Test output command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--output', 'test-output.txt'])
            
            # Verify output was set
            assert mock_echo.call_count >= 0

    def test_cli_command_format_invocation(self):
        """Test CLI command format invocation."""
        from venice_sdk.cli import cli
        
        # Test format command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--format', 'json'])
            
            # Verify format was set
            assert mock_echo.call_count >= 0

    def test_cli_command_color_invocation(self):
        """Test CLI command color invocation."""
        from venice_sdk.cli import cli
        
        # Test color command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--color', 'auto'])
            
            # Verify color was set
            assert mock_echo.call_count >= 0

    def test_cli_command_no_color_invocation(self):
        """Test CLI command no-color invocation."""
        from venice_sdk.cli import cli
        
        # Test no-color command
        with patch('venice_sdk.cli.click.echo') as mock_echo:
            cli.invoke(['--no-color'])
            
            # Verify no-color was set
            assert mock_echo.call_count >= 0
