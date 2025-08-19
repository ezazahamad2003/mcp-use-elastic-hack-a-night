import asyncio
import itertools
import sys
from typing import Optional


class Spinner:
    """
    An asynchronous context manager to display a spinner in the console.
    """

    def __init__(self, message: str = "Thinking..."):
        self._spinner = itertools.cycle(["-", "/", "|", "\\"])
        self._message = message
        self._spinner_task: Optional[asyncio.Task] = None

    async def _spin(self):
        """Private method to run the spinner."""
        while True:
            sys.stdout.write(f"\r{self._message} {next(self._spinner)}")
            sys.stdout.flush()
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
        sys.stdout.write("\r" + " " * (len(self._message) + 2) + "\r")
        sys.stdout.flush()

    async def __aenter__(self):
        """Starts the spinner."""
        self._spinner_task = asyncio.create_task(self._spin())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Stops the spinner."""
        if self._spinner_task:
            self._spinner_task.cancel()
            try:
                await self._spinner_task
            except asyncio.CancelledError:
                pass
