import os
import subprocess
import click
from pathlib import Path
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv


def get_global_config_path() -> Path:
    """Get the path to the global configuration directory."""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.getenv('APPDATA', '')) / 'venice'
    else:  # Unix-like
        config_dir = Path.home() / '.config' / 'venice'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / '.env'


def is_git_repo(path: Path) -> bool:
    """Check if the given path is in a git repository."""
    current = path.resolve()
    while current != current.parent:
        git_dir = current / '.git'
        if git_dir.exists():
            return True
        current = current.parent
    return False


def warn_about_secrets(env_path: Path) -> None:
    """Display security warnings about committing secrets."""
    if is_git_repo(env_path):
        click.echo(click.style(
            "⚠️  WARNING: You are creating a .env file in a git repository!",
            fg='yellow',
            bold=True
        ))
        click.echo(click.style(
            "   Make sure .env is in your .gitignore file to prevent committing secrets.",
            fg='yellow'
        ))
        
        # Check if .gitignore exists and contains .env
        gitignore_path = env_path.parent / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            if '.env' not in gitignore_content:
                click.echo(click.style(
                    "   Consider adding .env to your .gitignore file.",
                    fg='yellow'
                ))
        else:
            click.echo(click.style(
                "   Consider creating a .gitignore file and adding .env to it.",
                fg='yellow'
            ))


def read_config_file(env_path: Path) -> Dict[str, str]:
    """Read and parse a .env file."""
    config = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config


def write_config_file(env_path: Path, key: str, value: str) -> None:
    """Write a key-value pair to a .env file, updating if it exists."""
    config = read_config_file(env_path)
    config[key] = value
    
    # Write back to file
    lines = []
    for k, v in config.items():
        lines.append(f'{k}={v}')
    
    env_path.parent.mkdir(parents=True, exist_ok=True)
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def get_api_key() -> Optional[str]:
    """Get the API key from environment or .env file (local then global)."""
    # First try environment variable (highest priority)
    api_key = os.environ.get('VENICE_API_KEY')
    if api_key:
        return api_key
    
    # Then try local .env file
    local_env_path = Path('.env')
    if local_env_path.exists():
        load_dotenv(local_env_path)
        api_key = os.environ.get('VENICE_API_KEY')
        if api_key:
            return api_key
    
    # Finally try global .env file
    global_env_path = get_global_config_path()
    if global_env_path.exists():
        load_dotenv(global_env_path)
        api_key = os.environ.get('VENICE_API_KEY')
        if api_key:
            return api_key
    
    return None


def get_base_url() -> Optional[str]:
    """Get the base URL from environment or .env file (local then global)."""
    # First try environment variable (highest priority)
    base_url = os.environ.get('VENICE_BASE_URL')
    if base_url:
        return base_url
    
    # Then try local .env file
    local_env_path = Path('.env')
    if local_env_path.exists():
        load_dotenv(local_env_path)
        base_url = os.environ.get('VENICE_BASE_URL')
        if base_url:
            return base_url
    
    # Finally try global .env file
    global_env_path = get_global_config_path()
    if global_env_path.exists():
        load_dotenv(global_env_path)
        base_url = os.environ.get('VENICE_BASE_URL')
        if base_url:
            return base_url
    
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
@click.option('--global', 'use_global', is_flag=True, help='Store API key in global configuration')
def auth(api_key: str, use_global: bool) -> None:
    """Set your Venice API key.
    
    This command will store your API key in the .env file.
    By default, it stores in the current directory. Use --global to store globally.
    """
    if use_global:
        env_path = get_global_config_path()
        click.echo(f"Storing API key in global configuration: {env_path}")
    else:
        env_path = Path('.env')
        # Display security warning if in git repo
        warn_about_secrets(env_path)
    
    # Write the API key
    write_config_file(env_path, 'VENICE_API_KEY', api_key)
    
    click.echo(click.style("✅ API key has been set successfully!", fg='green'))
    if use_global:
        click.echo("The API key is now available globally across all projects.")

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


@cli.command()
@click.option('--base-url', 'base_url', help='Set the base URL for the Venice API')
@click.option('--global', 'use_global', is_flag=True, help='Store configuration globally')
def configure(base_url: Optional[str], use_global: bool) -> None:
    """Configure Venice SDK settings.
    
    This command allows you to set configuration options like the base URL.
    Use --global to store configuration globally.
    """
    if not base_url:
        click.echo("No configuration option specified.")
        click.echo("Use --base-url <url> to set the base URL.")
        return
    
    # Validate base URL
    if not base_url.startswith(('http://', 'https://')):
        click.echo(click.style(
            "⚠️  WARNING: Base URL should start with http:// or https://",
            fg='yellow'
        ))
    
    # Warn about HTTP (insecure)
    if base_url.startswith('http://') and not base_url.startswith('https://'):
        click.echo(click.style(
            "⚠️  WARNING: Using HTTP instead of HTTPS is insecure!",
            fg='yellow',
            bold=True
        ))
    
    if use_global:
        env_path = get_global_config_path()
        click.echo(f"Storing base URL in global configuration: {env_path}")
    else:
        env_path = Path('.env')
        warn_about_secrets(env_path)
    
    write_config_file(env_path, 'VENICE_BASE_URL', base_url)
    click.echo(click.style(f"✅ Base URL has been set to: {base_url}", fg='green'))


@cli.command()
def config() -> None:
    """Display current configuration."""
    # Get values from all sources
    env_api_key = os.environ.get('VENICE_API_KEY')
    env_base_url = os.environ.get('VENICE_BASE_URL')
    
    local_env_path = Path('.env')
    local_config = read_config_file(local_env_path) if local_env_path.exists() else {}
    
    global_env_path = get_global_config_path()
    global_config = read_config_file(global_env_path) if global_env_path.exists() else {}
    
    # Determine active values
    active_api_key = get_api_key()
    active_base_url = get_base_url() or "https://api.venice.ai/api/v1"
    
    click.echo("Current Configuration:")
    click.echo("=" * 50)
    
    # API Key
    click.echo("\nAPI Key:")
    if env_api_key:
        click.echo(f"  Environment: {_format_key_preview(env_api_key)} (active)")
    elif local_config.get('VENICE_API_KEY'):
        click.echo(f"  Local (.env): {_format_key_preview(local_config['VENICE_API_KEY'])} (active)")
    elif global_config.get('VENICE_API_KEY'):
        click.echo(f"  Global: {_format_key_preview(global_config['VENICE_API_KEY'])} (active)")
    else:
        click.echo("  Not set")
    
    # Base URL
    click.echo("\nBase URL:")
    if env_base_url:
        click.echo(f"  Environment: {env_base_url} (active)")
    elif local_config.get('VENICE_BASE_URL'):
        click.echo(f"  Local (.env): {local_config['VENICE_BASE_URL']} (active)")
    elif global_config.get('VENICE_BASE_URL'):
        click.echo(f"  Global: {global_config['VENICE_BASE_URL']} (active)")
    else:
        click.echo(f"  Default: {active_base_url} (active)")
    
    click.echo("\n" + "=" * 50)
    click.echo("Priority: Environment > Local > Global > Default")

def main() -> None:
    cli()

if __name__ == '__main__':
    main() 