"""Command-line interface for whisper-dictate."""

import logging
import sys
from typing import Optional

import click

from whisper_dictate.config import load_config
from whisper_dictate.dictation import DictationService


def setup_logging(level: str) -> None:
    """WHY THIS EXISTS: Logging needs to be configured consistently
    across the application for debugging and monitoring.
    
    RESPONSIBILITY: Configure logging with specified level and format.
    BOUNDARIES:
    - DOES: Set up logging configuration with file output
    - DOES NOT: Handle log rotation or file management
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    from pathlib import Path
    
    # Create log directory
    log_dir = Path.home() / '.local' / 'share' / 'whisper-dictate'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'whisper-dictate.log'
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


@click.group()
@click.option("--log-level", default="INFO", help="Logging level")
@click.pass_context
def cli(ctx: click.Context, log_level: str) -> None:
    """WHY THIS EXISTS: Users need a command-line interface to interact
    with the dictation service without writing code.
    
    RESPONSIBILITY: Provide command-line interface for dictation operations.
    BOUNDARIES:
    - DOES: Handle command-line arguments and user interaction
    - DOES NOT: Implement core dictation logic
    
    Args:
        ctx: Click context
        log_level: Logging level
    """
    setup_logging(log_level)
    ctx.ensure_object(dict)
    
    try:
        config = load_config()
        ctx.obj["config"] = config
        ctx.obj["service"] = DictationService(config)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--duration", type=float, help="Recording duration in seconds")
@click.pass_context
def dictate(ctx: click.Context, duration: Optional[float]) -> None:
    """WHY THIS EXISTS: Users need a simple command to start dictation.
    
    RESPONSIBILITY: Execute dictation workflow from command line.
    BOUNDARIES:
    - DOES: Handle user interaction and display results
    - DOES NOT: Implement core dictation logic
    
    Args:
        ctx: Click context
        duration: Recording duration in seconds
    """
    service = ctx.obj["service"]
    
    try:
        click.echo("🎤 Recording... (Press Ctrl+C to stop early)")
        
        result = service.dictate(duration)
        
        if result:
            click.echo(f"✅ Transcription: {result.text}")
            if result.language:
                click.echo(f"🌐 Language: {result.language}")
        else:
            click.echo("❌ Dictation failed", err=True)
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo("\n⏹️  Recording stopped by user")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """WHY THIS EXISTS: Users need diagnostic information to troubleshoot
    configuration issues.
    
    RESPONSIBILITY: Display system diagnostic information.
    BOUNDARIES:
    - DOES: Display system information
    - DOES NOT: Perform system modifications
    
    Args:
        ctx: Click context
    """
    service = ctx.obj["service"]
    info = service.get_system_info()
    
    click.echo("🔍 System Information:")
    click.echo("=" * 40)
    
    click.echo("\n🎤 Audio Devices:")
    for device in info["audio_devices"]:
        click.echo(f"  • {device}")
    
    click.echo("\n📋 Clipboard Tools:")
    for tool in info["clipboard_tools"]:
        click.echo(f"  • {tool}")
    click.echo("\n⚙️  Configuration:")
    for key, value in info["config"].items():
        click.echo(f"  • {key}: {value}")

    click.echo("\n📊 Logging:")
    from pathlib import Path
    log_file = Path.home() / '.local' / 'share' / 'whisper-dictate' / 'whisper-dictate.log'
    click.echo(f"  • Log file: {log_file}")
    click.echo(f"  • View logs: tail -f {log_file}")



if __name__ == "__main__":
    cli()