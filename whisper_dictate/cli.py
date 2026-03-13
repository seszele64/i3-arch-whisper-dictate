"""Command-line interface for whisper-dictate."""

import asyncio
import logging
import sys
from typing import Optional

import click

from whisper_dictate.config import load_config, DatabaseConfig
from whisper_dictate.dictation import DictationService
from whisper_dictate.database import get_database, initialize_database


def setup_logging(level: str, enable_db_logging: bool = True) -> None:
    """WHY THIS EXISTS: Logging needs to be configured consistently
    across the application for debugging and monitoring.

    RESPONSIBILITY: Configure logging with specified level, format, and handlers.
    Supports dual logging (file + database) when database is available.
    BOUNDARIES:
    - DOES: Set up logging configuration with file and optional database output
    - DOES NOT: Handle log rotation or database initialization

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        enable_db_logging: Whether to enable database logging
    """
    from pathlib import Path

    # Create log directory
    log_dir = Path.home() / ".local" / "share" / "whisper-dictate"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "whisper-dictate.log"

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
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

    # Add database logging handler if enabled
    if enable_db_logging:
        try:
            from whisper_dictate.db_logging import DatabaseLogHandler

            # Get or create database
            db_config = DatabaseConfig()
            db = get_database(db_config)

            # Initialize database synchronously for logging
            asyncio.run(db.initialize())

            # Add database handler
            db_handler = DatabaseLogHandler(database=db)
            db_handler.setLevel(getattr(logging, level.upper()))
            db_handler.setFormatter(formatter)
            root_logger.addHandler(db_handler)

            # Run log retention cleanup
            retention_days = db_config.log_retention_days
            deleted = asyncio.run(db.cleanup_old_logs(retention_days))
            if deleted > 0:
                root_logger.info(f"Cleaned up {deleted} old log entries")

        except Exception as e:
            # Database logging is optional - continue without it
            root_logger.debug(f"Database logging not available: {e}")


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

    log_file = (
        Path.home() / ".local" / "share" / "whisper-dictate" / "whisper-dictate.log"
    )
    click.echo(f"  • Log file: {log_file}")
    click.echo(f"  • View logs: tail -f {log_file}")


@click.group()
def logs() -> None:
    """Query and manage application logs stored in the database.

    This command group provides functionality to view, filter,
    and export application logs.
    """
    pass


@logs.command("list")
@click.option(
    "--level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="Filter by log level",
)
@click.option("--source", help="Filter by source module")
@click.option(
    "--from-time", help="Filter from timestamp (ISO format: YYYY-MM-DD HH:MM:SS)"
)
@click.option("--to-time", help="Filter to timestamp (ISO format: YYYY-MM-DD HH:MM:SS)")
@click.option(
    "--limit", type=int, default=100, help="Maximum number of logs to display"
)
def list_logs(
    level: Optional[str],
    source: Optional[str],
    from_time: Optional[str],
    to_time: Optional[str],
    limit: int,
) -> None:
    """List application logs with optional filters.

    Examples:
        whisper-dictate logs list
        whisper-dictate logs list --level ERROR
        whisper-dictate logs list --source whisper_dictate.audio --limit 50
        whisper-dictate logs list --from-time "2024-01-01" --to-time "2024-01-31"
    """
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig
    import json

    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)

        # Run async function
        logs = asyncio.run(
            db.query_logs(
                level=level,
                source=source,
                from_time=from_time,
                to_time=to_time,
                limit=limit,
            )
        )

        if not logs:
            click.echo("No logs found matching the specified criteria.")
            return

        # Display logs
        click.echo(f"Found {len(logs)} log entries:\n")
        for log in logs:
            timestamp = log.get("timestamp", "N/A")
            lvl = log.get("level", "N/A")
            src = log.get("source", "N/A")
            msg = log.get("message", "")

            # Color code by level
            if lvl == "ERROR":
                lvl_display = click.style(lvl, fg="red")
            elif lvl == "WARNING":
                lvl_display = click.style(lvl, fg="yellow")
            elif lvl == "INFO":
                lvl_display = click.style(lvl, fg="green")
            else:
                lvl_display = lvl

            click.echo(f"{timestamp} | {lvl_display:8} | {src:30} | {msg}")

            # Display metadata if present
            if log.get("metadata_json"):
                try:
                    metadata = json.loads(log["metadata_json"])
                    click.echo(f"       Metadata: {metadata}")
                except json.JSONDecodeError:
                    pass

    except Exception as e:
        click.echo(f"Error querying logs: {e}", err=True)
        sys.exit(1)


@logs.command("export")
@click.argument("filename")
@click.option(
    "--level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="Filter by log level",
)
@click.option("--source", help="Filter by source module")
@click.option("--from-time", help="Filter from timestamp (ISO format)")
@click.option("--to-time", help="Filter to timestamp (ISO format)")
@click.option(
    "--format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Export format",
)
def export_logs(
    filename: str,
    level: Optional[str],
    source: Optional[str],
    from_time: Optional[str],
    to_time: Optional[str],
    format: str,
) -> None:
    """Export logs to a file.

    Examples:
        whisper-dictate logs export logs.txt
        whisper-dictate logs export error_logs.json --level ERROR --format json
    """
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig
    import json

    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)

        # Get all logs (no limit for export)
        logs = asyncio.run(
            db.query_logs(
                level=level,
                source=source,
                from_time=from_time,
                to_time=to_time,
                limit=10000,  # High limit for export
            )
        )

        if not logs:
            click.echo("No logs found matching the specified criteria.")
            return

        # Write to file
        if format == "json":
            with open(filename, "w") as f:
                json.dump(logs, f, indent=2)
        else:
            with open(filename, "w") as f:
                for log in logs:
                    timestamp = log.get("timestamp", "N/A")
                    lvl = log.get("level", "N/A")
                    src = log.get("source", "N/A")
                    msg = log.get("message", "")
                    f.write(f"{timestamp} | {lvl:8} | {src:30} | {msg}\n")

        click.echo(f"Exported {len(logs)} log entries to {filename}")

    except Exception as e:
        click.echo(f"Error exporting logs: {e}", err=True)
        sys.exit(1)


@logs.command("cleanup")
@click.option(
    "--days",
    type=int,
    default=None,
    help="Delete logs older than N days (default: use configured retention)",
)
def cleanup_logs(days: Optional[int]) -> None:
    """Clean up old logs based on retention policy.

    Examples:
        whisper-dictate logs cleanup
        whisper-dictate logs cleanup --days 7
    """
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig

    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)

        retention_days = days if days is not None else db_config.log_retention_days

        deleted = asyncio.run(db.cleanup_old_logs(retention_days))

        click.echo(f"Cleaned up {deleted} log entries older than {retention_days} days")

    except Exception as e:
        click.echo(f"Error cleaning up logs: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
