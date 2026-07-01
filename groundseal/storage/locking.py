"""File locking for concurrent-safe FileStorage writes."""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from groundseal.errors import GroundSealError


class FileLock:
    """Process-level file lock using fcntl when available, else threading lock."""

    def __init__(self, lock_path: Path) -> None:
        self._lock_path = lock_path
        self._thread_lock = threading.Lock()
        self._fd: int | None = None

    @contextmanager
    def acquire(self, *, timeout_s: float = 5.0) -> Iterator[None]:
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self._thread_lock:
            try:
                import fcntl

                fd = os.open(str(self._lock_path), os.O_CREAT | os.O_RDWR)
                self._fd = fd
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    os.close(fd)
                    self._fd = None
                    raise GroundSealError(
                        code="STORAGE_LOCK_TIMEOUT",
                        message="Could not acquire storage lock",
                        details={"lock_path": str(self._lock_path)},
                    ) from exc
                try:
                    yield
                finally:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                    self._fd = None
            except ImportError:
                yield

    @contextmanager
    def acquire_run(self, run_id: str) -> Iterator[None]:
        lock_file = self._lock_path.parent / f"run_{run_id}.lock"
        with FileLock(lock_file).acquire():
            yield
