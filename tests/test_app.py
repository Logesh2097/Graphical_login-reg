import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from user_store import UserStore  # noqa: E402


def display_available():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        return False
    return sys.platform == "win32" or bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(display_available(), "needs Tkinter and a display")
class AccountAppTests(unittest.TestCase):
    def setUp(self):
        from app import AccountApp

        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        store = UserStore(Path(folder.name) / "users.json", iterations=1_000)
        self.app = AccountApp(store)
        self.addCleanup(self.app.root.destroy)

    def submit(self, dialog, username, password):
        dialog.username.insert(0, username)
        dialog.password.insert(0, password)
        dialog.submit_button.invoke()
        return dialog.status.cget("text")

    def test_registering_then_signing_in_succeeds(self):
        self.assertEqual(
            self.submit(self.app.open_register(), "asha", "s3cret-pass"), "Registration Success"
        )
        self.assertEqual(self.submit(self.app.open_login(), "asha", "s3cret-pass"), "Login Success")

    def test_a_wrong_password_shows_invalid_password(self):
        self.submit(self.app.open_register(), "asha", "s3cret-pass")

        message = self.submit(self.app.open_login(), "asha", "nope-nope")

        self.assertEqual(message, "Invalid Password")

    def test_an_unknown_user_shows_user_not_found(self):
        self.assertEqual(self.submit(self.app.open_login(), "nobody", "whatever"), "User Not Found")

    def test_the_password_box_is_cleared_after_every_attempt(self):
        dialog = self.app.open_login()
        self.submit(dialog, "nobody", "whatever")

        self.assertEqual(dialog.password.get(), "")


if __name__ == "__main__":
    unittest.main()
