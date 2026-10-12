"""Tiny helpers to protect a post with a PIN (so only the owner can delete it)."""
import hashlib
import hmac
import secrets


def _digest(pin: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), 100_000).hex()


def hash_pin(pin: str) -> str:
    salt = secrets.token_hex(8)
    return f"{salt}${_digest(pin, salt)}"


def verify_pin(pin: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    return hmac.compare_digest(_digest(pin, salt), digest)
