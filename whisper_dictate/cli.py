"""Command-line interface for whisper-dictate."""

import asyncio
import logging
import sys
from typing import Optional

import click

from whisper_dictate.config import load_config, DatabaseConfig
from whisper_dictate.dictation import DictationService
from whisper_dictate.database import get_database
from whisper_dictate.cli_helpers import with_database


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
        service = DictationService(config)
        ctx.obj["service"] = service

        # Register cleanup to close service after any command
        ctx.call_on_close(service.close_sync)
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
    import json
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig

    db = None
    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)
        asyncio.run(db.initialize())

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
    finally:
        if db:
            asyncio.run(db.close())


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
    import json
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig

    db = None
    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)
        asyncio.run(db.initialize())

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
    finally:
        if db:
            asyncio.run(db.close())


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

    db = None
    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)
        asyncio.run(db.initialize())

        # Get retention days from config if not provided
        if days is None:
            retention_days = db_config.log_retention_days
        else:
            retention_days = days

        deleted = asyncio.run(db.cleanup_old_logs(retention_days))

        click.echo(f"Cleaned up {deleted} log entries older than {retention_days} days")

    except Exception as e:
        click.echo(f"Error cleaning up logs: {e}", err=True)
        sys.exit(1)
    finally:
        if db:
            asyncio.run(db.close())


# ============ History Command Group ============


@click.group()
def history() -> None:
    """Query and manage transcription history stored in the database.

    This command group provides functionality to view, search,
    and delete past transcriptions.
    """
    pass


@history.command("list")
@click.option(
    "--limit", type=int, default=20, help="Maximum number of transcriptions to display"
)
@click.option("--date", help="Filter by date (YYYY-MM-DD format)")
def list_history(limit: int, date: Optional[str]) -> None:
    """List recent transcriptions with pagination.

    Examples:
        whisper-dictate history list
        whisper-dictate history list --limit 10
        whisper-dictate history list --date 2024-03-15
    """
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig

    db = None
    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)
        asyncio.run(db.initialize())

        transcriptions = asyncio.run(db.list_transcriptions(limit=limit, date=date))

        if not transcriptions:
            click.echo("No transcriptions found.")
            return

        click.echo(
            f"Recent Transcriptions (showing {len(transcriptions)} of {len(transcriptions)}):\n"
        )
        click.echo(f"{'ID':<5} {'Date':<20} {'Duration':<10} {'Preview':<50}")
        click.echo("-" * 90)

        for t in transcriptions:
            # Format timestamp
            timestamp = t.get("timestamp", "N/A")
            date_str = timestamp.split()[0] if timestamp != "N/A" else "N/A"
            time_str = (
                timestamp.split()[1][:8]
                if " " in timestamp and len(timestamp.split()) > 1
                else ""
            )

            # Format duration
            duration = t.get("duration")
            duration_str = f"{duration:.1f}s" if duration else "N/A"

            # Truncate text for preview
            text = t.get("text", "")
            preview = text[:47] + "..." if len(text) > 50 else text

            click.echo(
                f"{t['id']:<5} {date_str} {time_str:<10} {duration_str:<10} {preview:<50}"
            )

    except Exception as e:
        click.echo(f"Error listing transcriptions: {e}", err=True)
        sys.exit(1)
    finally:
        if db:
            asyncio.run(db.close())


@history.command("show")
@click.argument("transcript_id", type=int)
@click.option("--audio", is_flag=True, help="Show audio file path")
def show_history(transcript_id: int, audio: bool) -> None:
    """Show full details of a transcription by ID.

    Examples:
        whisper-dictate history show 42
        whisper-dictate history show 42 --audio
    """
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig
    from whisper_dictate.audio_storage import get_audio_storage

    db = None
    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)
        asyncio.run(db.initialize())

        transcription = asyncio.run(db.get_transcription_with_recording(transcript_id))

        if not transcription:
            click.echo(
                f"Error: Transcription with ID {transcript_id} not found.", err=True
            )
            sys.exit(1)

        click.echo("=" * 60)
        click.echo(f"Transcription #{transcription['id']}")
        click.echo("=" * 60)

        # Timestamp
        timestamp = transcription.get("timestamp", "N/A")
        click.echo(f"\n📅 Date: {timestamp}")

        # Duration
        duration = transcription.get("duration")
        if duration:
            click.echo(f"⏱️  Duration: {duration:.1f} seconds")

        # Language
        language = transcription.get("language")
        if language:
            click.echo(f"🌐 Language: {language}")

        # Model
        model = transcription.get("model_used", "N/A")
        click.echo(f"🤖 Model: {model}")

        # Confidence
        confidence = transcription.get("confidence")
        if confidence:
            click.echo(f"📊 Confidence: {confidence:.1%}")

        # Audio file path
        if audio:
            audio_storage = get_audio_storage(db_config)
            audio_path = audio_storage.get_audio_path(transcription["file_path"])
            click.echo(f"\n🎵 Audio File: {audio_path}")

        # Full transcript text
        click.echo("\n" + "-" * 60)
        click.echo("📝 Transcript:")
        click.echo("-" * 60)
        click.echo(transcription.get("text", ""))

    except Exception as e:
        click.echo(f"Error showing transcription: {e}", err=True)
        sys.exit(1)
    finally:
        if db:
            asyncio.run(db.close())


@history.command("search")
@click.argument("query")
@click.option(
    "--limit", type=int, default=20, help="Maximum number of results to display"
)
def search_history(query: str, limit: int) -> None:
    """Search transcriptions by text (case-insensitive).

    Examples:
        whisper-dictate history search "meeting"
        whisper-dictate history search "project" --limit 50
    """
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig

    db = None
    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)
        asyncio.run(db.initialize())

        results = asyncio.run(db.search_transcripts(query, limit=limit))

        if not results:
            click.echo(f"No transcriptions found matching: '{query}'")
            return

        click.echo(f"Found {len(results)} transcription(s) matching: '{query}'\n")
        click.echo(f"{'ID':<5} {'Date':<20} {'Match Preview':<55}")
        click.echo("-" * 85)

        for t in results:
            # Format timestamp
            timestamp = t.get("timestamp", "N/A")
            date_str = timestamp.split()[0] if timestamp != "N/A" else "N/A"
            time_str = (
                timestamp.split()[1][:8]
                if " " in timestamp and len(timestamp.split()) > 1
                else ""
            )

            # Highlight matching text
            text = t.get("text", "")
            # Find position of query (case-insensitive)
            lower_text = text.lower()
            lower_query = query.lower()
            pos = lower_text.find(lower_query)

            if pos >= 0:
                # Get context around the match
                start = max(0, pos - 20)
                end = min(len(text), pos + len(query) + 20)
                preview = (
                    ("..." if start > 0 else "")
                    + text[start:end]
                    + ("..." if end < len(text) else "")
                )
            else:
                preview = text[:52] + "..." if len(text) > 55 else text

            click.echo(f"{t['id']:<5} {date_str} {time_str:<10} {preview:<55}")

    except Exception as e:
        click.echo(f"Error searching transcriptions: {e}", err=True)
        sys.exit(1)
    finally:
        if db:
            asyncio.run(db.close())


@history.command("delete")
@click.argument("transcript_id", type=int)
@click.option("--yes", "confirm_yes", is_flag=True, help="Skip confirmation prompt")
def delete_history(transcript_id: int, confirm_yes: bool) -> None:
    """Delete a transcription and its associated audio file.

    Examples:
        whisper-dictate history delete 42
        whisper-dictate history delete 42 --yes
    """
    from whisper_dictate.database import get_database
    from whisper_dictate.config import DatabaseConfig
    from whisper_dictate.audio_storage import get_audio_storage

    db = None
    try:
        db_config = DatabaseConfig()
        db = get_database(db_config)
        asyncio.run(db.initialize())

        # First get the transcription to verify it exists and get audio path
        transcription = asyncio.run(db.get_transcription_with_recording(transcript_id))

        if not transcription:
            click.echo(
                f"Error: Transcription with ID {transcript_id} not found.", err=True
            )
            sys.exit(1)

        # Show info about what will be deleted
        timestamp = transcription.get("timestamp", "N/A")
        text_preview = transcription.get("text", "")[:50]
        text_preview = (
            text_preview + "..."
            if len(transcription.get("text", "")) > 50
            else text_preview
        )

        click.echo(f"About to delete transcription #{transcript_id}:")
        click.echo(f"  Date: {timestamp}")
        click.echo(f"  Preview: {text_preview}")

        # Confirm deletion
        if not confirm_yes:
            if not click.confirm(
                "\nAre you sure you want to delete this transcription?"
            ):
                click.echo("Deletion cancelled.")
                return

        # Delete the recording (cascades to transcript due to foreign key)
        audio_path = None
        if transcription.get("file_path"):
            audio_storage = get_audio_storage(db_config)
            audio_path = audio_storage.get_audio_path(transcription["file_path"])

        recording_id = transcription.get("recording_id")
        deleted = asyncio.run(db.delete_recording(recording_id))

        if deleted:
            # Also delete the audio file if it exists
            if audio_path and audio_path.exists():
                audio_path.unlink()
                click.echo(f"Deleted audio file: {audio_path}")

            click.echo(f"✅ Deleted transcription #{transcript_id}")
        else:
            click.echo(
                f"Error: Failed to delete transcription #{transcript_id}", err=True
            )
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error deleting transcription: {e}", err=True)
        sys.exit(1)
    finally:
        if db:
            asyncio.run(db.close())


# Register subcommands with the main cli group
cli.add_command(logs)
cli.add_command(history)


# ============ Migration Command ============


@cli.command()
@click.option(
    "--force", is_flag=True, help="Force re-migration even if already completed"
)
@click.option("--status", is_flag=True, help="Check migration status only")
def migrate(force: bool, status: bool) -> None:
    """Migrate legacy state files to database.

    This command migrates legacy state files to the database:
    - ~/.whisper-dictate-state (recording state marker)
    - ~/.whisper-dictate-pid (recording process PID)

    Original files are backed up before migration.

    Examples:
        whisper-dictate migrate
        whisper-dictate migrate --force
        whisper-dictate migrate --status
    """
    import asyncio

    from whisper_dictate.migration import (
        MigrationError,
        check_migration_status,
        run_migration,
    )

    try:
        if status:
            # Just check and display status
            result = asyncio.run(check_migration_status())

            click.echo("Migration Status:")
            click.echo("=" * 40)

            legacy = result["legacy_files"]
            click.echo(
                f"Legacy state file:  {'Found' if legacy['state_file'] else 'Not found'}"
            )
            click.echo(
                f"Legacy PID file:   {'Found' if legacy['pid_file'] else 'Not found'}"
            )
            click.echo(
                f"Legacy audio file: {'Found' if legacy['audio_file'] else 'Not found'}"
            )

            click.echo(f"\nMigration completed: {result['migration_completed']}")
            click.echo(f"Migration needed:   {result['migration_needed']}")

            if result["migration_needed"]:
                click.echo("\nRun 'whisper-dictate migrate' to perform migration.")
            return

        # Run migration
        click.echo("Starting migration...")

        result = asyncio.run(run_migration(force=force))

        if result.get("skipped"):
            click.echo(f"⚠️  {result['message']}")
            return

        if result["success"]:
            click.echo("✅ Migration completed successfully")
            click.echo("\nMigrated files:")
            for name, exists in result["migrated_files"].items():
                if exists:
                    click.echo(f"  • {name}")

            if result.get("backup_path"):
                click.echo(f"\nBackup saved to: {result['backup_path']}")
        else:
            click.echo("❌ Migration failed", err=True)
            sys.exit(1)

    except MigrationError as e:
        click.echo(f"❌ Migration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
