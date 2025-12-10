import os
from pathlib import Path
from unittest.mock import patch, mock_open
from click.testing import CliRunner
from venice_sdk.cli import cli, get_global_config_path

def test_auth_command(tmp_path):
    """Test the auth command."""
    runner = CliRunner()
    
    # Change to a temporary directory
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # Run the auth command
        result = runner.invoke(cli, ['auth', 'test-api-key'])
        
        # Check that the command succeeded
        assert result.exit_code == 0
        assert "API key has been set successfully!" in result.output
        
        # Check that the .env file was created
        env_path = Path('.env')
        assert env_path.exists()
        
        # Check that the API key was set correctly
        with open(env_path) as f:
            content = f.read()
            assert 'VENICE_API_KEY=test-api-key' in content


def test_auth_command_global(tmp_path):
    """Test the auth command with --global flag."""
    runner = CliRunner()
    
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['auth', 'test-api-key', '--global'])
        
        assert result.exit_code == 0
        assert "API key has been set successfully!" in result.output
        assert "global configuration" in result.output.lower()
        
        # Check that the global config file was created
        global_env_path = get_global_config_path()
        assert global_env_path.exists()
        
        # Check that the API key was set correctly
        with open(global_env_path) as f:
            content = f.read()
            assert 'VENICE_API_KEY=test-api-key' in content


def test_configure_command(tmp_path):
    """Test the configure command."""
    runner = CliRunner()
    
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['configure', '--base-url', 'https://api.example.com'])
        
        assert result.exit_code == 0
        assert "Base URL has been set" in result.output
        assert "https://api.example.com" in result.output
        
        # Check that the .env file was created
        env_path = Path('.env')
        assert env_path.exists()
        
        # Check that the base URL was set correctly
        with open(env_path) as f:
            content = f.read()
            assert 'VENICE_BASE_URL=https://api.example.com' in content


def test_configure_command_global(tmp_path):
    """Test the configure command with --global flag."""
    runner = CliRunner()
    
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['configure', '--base-url', 'https://api.example.com', '--global'])
        
        assert result.exit_code == 0
        assert "Base URL has been set" in result.output
        
        # Check that the global config file was created
        global_env_path = get_global_config_path()
        assert global_env_path.exists()
        
        # Check that the base URL was set correctly
        with open(global_env_path) as f:
            content = f.read()
            assert 'VENICE_BASE_URL=https://api.example.com' in content


def test_configure_command_warns_http(tmp_path):
    """Test that configure command warns about HTTP URLs."""
    runner = CliRunner()
    
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['configure', '--base-url', 'http://api.example.com'])
        
        assert result.exit_code == 0
        assert "WARNING" in result.output
        assert "HTTP" in result.output or "insecure" in result.output.lower()


def test_config_command(tmp_path):
    """Test the config command."""
    runner = CliRunner()
    
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # First set an API key
        runner.invoke(cli, ['auth', 'test-api-key'])
        
        # Then check config
        result = runner.invoke(cli, ['config'])
        
        assert result.exit_code == 0
        assert "Current Configuration" in result.output
        assert "API Key" in result.output
        assert "Base URL" in result.output


def test_config_command_shows_priority(tmp_path):
    """Test that config command shows configuration priority."""
    runner = CliRunner()
    
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # Set local config
        runner.invoke(cli, ['auth', 'local-key'])
        runner.invoke(cli, ['configure', '--base-url', 'https://local.example.com'])
        
        # Set global config
        runner.invoke(cli, ['auth', 'global-key', '--global'])
        runner.invoke(cli, ['configure', '--base-url', 'https://global.example.com', '--global'])
        
        # Check config shows both
        result = runner.invoke(cli, ['config'])
        
        assert result.exit_code == 0
        assert "Local" in result.output
        assert "Global" in result.output
        assert "Priority" in result.output


def test_config_command_with_env_vars(tmp_path):
    """Test that config command shows environment variables take priority."""
    runner = CliRunner()
    
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # Set local config
        runner.invoke(cli, ['auth', 'local-key'])
        
        # Check config with environment variable
        with patch.dict(os.environ, {'VENICE_API_KEY': 'env-key'}):
            result = runner.invoke(cli, ['config'])
            
            assert result.exit_code == 0
            assert "Environment" in result.output
            assert "env-key" in result.output or "env..." in result.output

def test_status_command_with_key():
    """Test the status command when an API key is set."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {'VENICE_API_KEY': 'test-api-key'}):
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "✅ API key is set" in result.output
        assert "Key: test...-key" in result.output

@patch.dict(os.environ, {}, clear=True)
def test_status_command_without_key(tmp_path, monkeypatch):
    """Test the status command when no API key is set."""
    runner = CliRunner()
    
    # Use a temporary directory to ensure no .env file exists
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Ensure no environment variables are set
        monkeypatch.delenv('VENICE_API_KEY', raising=False)
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "❌ No API key is set" in result.output
        assert "Use 'venice auth <your-api-key>' to set your API key" in result.output 