from time import time

__all__ = ["generate_monotonic_id"]

def generate_monotonic_id() -> int:
    return int(time() * 1000)
