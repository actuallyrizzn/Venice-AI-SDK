import os
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner
from venice_sdk.cli import cli

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