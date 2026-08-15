import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from shek_common_utility.logging import get_logger

logger = get_logger(__name__)


class ModelLocks:
    """Per-model asyncio lock with anti-thrash guard.

    - Concurrent requests to the same model queue in FIFO order.
    - Concurrent requests to *different* models pass through freely, but if the
      same model was recently swapped in, we hold the lock briefly to avoid
      pathological ping-pong loading on a 4 GB VRAM GPU.
    """

    def __init__(self, *, anti_thrash_window_seconds: float = 30.0) -> None:
        self._locks: dict[str, asyncio.Lock] = {}
        self._last_used: dict[str, float] = {}
        self._anti_thrash_window = anti_thrash_window_seconds

    def _lock_for(self, model: str) -> asyncio.Lock:
        lock = self._locks.get(model)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[model] = lock
        return lock

    @asynccontextmanager
    async def acquire(self, model: str) -> AsyncIterator[None]:
        lock = self._lock_for(model)
        acquired_at = time.monotonic()
        await lock.acquire()
        try:
            wait_ms = int((time.monotonic() - acquired_at) * 1000)
            if wait_ms > 100:
                logger.info("model_lock_waited", model=model, wait_ms=wait_ms)
            self._last_used[model] = time.monotonic()
            yield
        finally:
            lock.release()

    def recently_used(self, model: str) -> bool:
        last = self._last_used.get(model)
        if last is None:
            return False
        return (time.monotonic() - last) < self._anti_thrash_window
