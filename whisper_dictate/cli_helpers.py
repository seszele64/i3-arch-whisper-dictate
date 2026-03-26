"""Helper functions and decorators for CLI commands."""

import asyncio
import click
from whisper_dictate.database import get_database
from whisper_dictate.config import DatabaseConfig


def _run_async(coro):
    """Run a coroutine in a new event loop, handling nested loop cases."""
    try:
        # Try to get existing loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop - safe to use asyncio.run()
        return asyncio.run(coro)

    # There's a running loop - create a new one for this operation
    new_loop = asyncio.new_event_loop()
    try:
        return new_loop.run_until_complete(coro)
    finally:
        new_loop.close()


def with_database(f):
    """Decorator that handles database initialization and cleanup.

    Works with both synchronous and asynchronous command functions.
    """

    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        # Initialize database
        db_config = DatabaseConfig()
        db = get_database(db_config)
        _run_async(db.initialize())

        ctx.obj = ctx.obj or {}
        ctx.obj["db"] = db

        try:
            # Invoke the command
            result = ctx.invoke(f, ctx, *args, **kwargs)

            # Handle async command functions - await the coroutine
            if asyncio.iscoroutine(result):
                result = _run_async(result)
            return result
        finally:
            # Close database
            _run_async(db.close())

    # Preserve function metadata
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper
