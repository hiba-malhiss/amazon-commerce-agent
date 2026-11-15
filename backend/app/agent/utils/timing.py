import time


def elapsed_ms(started: float) -> int:
    """Milliseconds since `started` (a time.perf_counter() value)."""
    return round((time.perf_counter() - started) * 1000)
