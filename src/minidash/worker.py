"""Background task that releases due scheduled orders on a fixed interval (see ADR-001)."""

import asyncio
import logging
from collections.abc import Callable

log = logging.getLogger(__name__)


async def run_release_loop(
    release_once: Callable[[], object], interval_seconds: float, stop: asyncio.Event
) -> None:
    """Every `interval_seconds`, run `release_once()` in a worker thread, until `stop` is set.

    A failing pass is logged and the loop carries on, so one bad tick never stops releases
    or takes the API down with it.
    """
    while True:
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_seconds)
            return  # stop was set
        except TimeoutError:
            pass
        try:
            await asyncio.to_thread(release_once)
        except Exception:
            log.exception("Release pass failed; retrying next interval")
