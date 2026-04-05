from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class SlidingWindowRateLimiter:
    max_requests: int
    window_seconds: int = 60
    _events: deque[datetime] = field(default_factory=deque)

    def allow(self, now: datetime | None = None) -> bool:
        current_time = now or datetime.now(timezone.utc)
        self._trim(current_time)
        if len(self._events) >= self.max_requests:
            return False
        self._events.append(current_time)
        return True

    def remaining(self, now: datetime | None = None) -> int:
        current_time = now or datetime.now(timezone.utc)
        self._trim(current_time)
        return max(self.max_requests - len(self._events), 0)

    def reset_in_seconds(self, now: datetime | None = None) -> int:
        current_time = now or datetime.now(timezone.utc)
        self._trim(current_time)
        if not self._events:
            return 0
        oldest = self._events[0]
        reset_at = oldest + timedelta(seconds=self.window_seconds)
        return max(int((reset_at - current_time).total_seconds()), 0)

    def _trim(self, now: datetime) -> None:
        cutoff = now - timedelta(seconds=self.window_seconds)
        while self._events and self._events[0] <= cutoff:
            self._events.popleft()
