"""Account storage for the login demo.

Accounts are kept in one JSON file. A password is never stored: only a
salted PBKDF2-SHA256 hash of it is.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path

MIN_PASSWORD_LENGTH = 6
PBKDF2_ITERATIONS = 600_000


class RegistrationError(ValueError):
    """The account could not be created. The message is shown to the user."""


class LoginError(ValueError):
    """Sign-in failed. The message is shown to the user."""


class UserStore:
    def __init__(self, path: str | os.PathLike[str], iterations: int = PBKDF2_ITERATIONS):
        self.path = Path(path)
        self.iterations = iterations

    def register(self, username: str, password: str) -> None:
        """Create an account, or raise ``RegistrationError``."""
        username = username.strip()
        if not username:
            raise RegistrationError("Enter a username.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise RegistrationError(
                f"The password must be at least {MIN_PASSWORD_LENGTH} characters long."
            )
        users = self._load()
        if username in users:
            raise RegistrationError("That username is already taken.")

        salt = secrets.token_bytes(16)
        users[username] = {
            "salt": salt.hex(),
            "iterations": self.iterations,
            "hash": self._hash(password, salt, self.iterations).hex(),
        }
        self._save(users)

    def verify(self, username: str, password: str) -> None:
        """Return quietly when the password is right, or raise ``LoginError``."""
        record = self._load().get(username.strip())
        if record is None:
            raise LoginError("User Not Found")
        salt = bytes.fromhex(record["salt"])
        attempt = self._hash(password, salt, record["iterations"])
        if not hmac.compare_digest(attempt, bytes.fromhex(record["hash"])):
            raise LoginError("Invalid Password")

    @staticmethod
    def _hash(password: str, salt: bytes, iterations: int) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    def _load(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        with self.path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, users: dict[str, dict]) -> None:
        # Write to a temporary file and swap it in, so a crash mid-write
        # cannot leave a half-written accounts file behind.
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(users, handle, indent=2)
        os.replace(temporary, self.path)
