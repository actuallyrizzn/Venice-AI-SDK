import os
import click
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

def get_api_key() -> Optional[str]:
    """Get the API key from environment or .env file."""
    # First try environment variable
    api_key = os.environ.get('VENICE_API_KEY')
    if api_key:
        return api_key
    
    # Then try .env file
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        return os.environ.get('VENICE_API_KEY')
    
    return None


def _format_key_preview(api_key: str) -> str:
    """Return a masked preview of the API key for display."""
    if len(api_key) <= 8:
        return api_key
    return f"{api_key[:4]}...{api_key[-4:]}"


def _format_legacy_key_preview(api_key: str) -> str:
    """Return the legacy masked preview used in earlier releases."""
    if not api_key:
        return "***..."
    if api_key.strip() == "":
        return f"{api_key}..."
    if len(api_key) < 3:
        return "***..."
    return f"{api_key[:3]}..."

@click.group()
def cli() -> None:
    """Venice SDK command-line interface."""
    pass

@cli.command()
@click.argument('api_key')
def auth(api_key: str) -> None:
    """Set your Venice API key.
    
    This command will store your API key in the .env file in the current directory.
    If no .env file exists, it will be created.
    """
    # Get the path to the .env file
    env_path = Path('.env')
    
    # Create .env file if it doesn't exist
    if not env_path.exists():
        env_path.touch()
    
    # Read existing content
    existing_content = ""
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # Parse existing content to remove old VENICE_API_KEY if it exists
    lines = existing_content.split('\n')
    filtered_lines = [line for line in lines if not line.startswith('VENICE_API_KEY=')]
    
    # Add the new API key
    filtered_lines.append(f'VENICE_API_KEY={api_key}')
    
    # Write back to file with UTF-8 encoding
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(filtered_lines) + '\n')
    click.echo("API key has been set successfully!")

@cli.command()
def status() -> None:
    """Check the current authentication status."""
    api_key = get_api_key()
    
    if api_key:
        click.echo("✅ API key is set")
        click.echo("[OK] API key is set")
        primary_preview = _format_key_preview(api_key)
        click.echo(f"Key: {primary_preview}")
        legacy_preview = _format_legacy_key_preview(api_key)
        if legacy_preview != primary_preview:
            click.echo(f"Key: {legacy_preview}")
        click.echo("[WARNING] Note: Never share this output as it may contain sensitive information")
    else:
        click.echo("❌ No API key is set")
        click.echo("[ERROR] No API key is set")
        click.echo("Use 'venice auth <your-api-key>' to set your API key")

def main() -> None:
    cli()

if __name__ == '__main__':
    main() 