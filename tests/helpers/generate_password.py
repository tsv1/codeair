import random
import string

__all__ = ["generate_password"]


def generate_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
