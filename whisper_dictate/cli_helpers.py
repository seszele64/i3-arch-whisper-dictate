"""Helper functions and decorators for CLI commands."""

import asyncio
import click
from whisper_dictate.database import get_database
from whisper_dictate.config import DatabaseConfig


def with_database(f):
    """Decorator that handles database initialization and cleanup.

    This decorator ensures that:
    1. Database is initialized before the command runs
    2. Database connection is properly closed after the command completes
    3. Cleanup happens even if an exception occurs

    Usage:
        @cli.command()
        @with_database
        @click.pass_context
        def my_command(ctx, ...):
            db = ctx.obj['db']
            # use db - already initialized
            results = asyncio.run(db.query(...))
    """

    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        db = None
        try:
            db_config = DatabaseConfig()
            db = get_database(db_config)
            asyncio.run(db.initialize())
            ctx.obj["db"] = db
            return ctx.invoke(f, ctx, *args, **kwargs)
        except Exception:
            # Re-raise to let Click handle error display
            raise
        finally:
            if db:
                asyncio.run(db.close())

    # Preserve function metadata
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper
