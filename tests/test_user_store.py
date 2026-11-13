import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from user_store import LoginError, RegistrationError, UserStore  # noqa: E402


class UserStoreTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "users.json"
        # Few iterations keep the tests fast; the app uses the real default.
        self.store = UserStore(self.path, iterations=1_000)

    def test_a_registered_user_can_sign_in(self):
        self.store.register("asha", "s3cret-pass")

        self.store.verify("asha", "s3cret-pass")

    def test_a_wrong_password_is_rejected(self):
        self.store.register("asha", "s3cret-pass")

        with self.assertRaisesRegex(LoginError, "Invalid Password"):
            self.store.verify("asha", "wrong-pass")

    def test_an_unknown_user_is_rejected(self):
        with self.assertRaisesRegex(LoginError, "User Not Found"):
            self.store.verify("nobody", "s3cret-pass")

    def test_the_password_is_never_written_to_disk(self):
        self.store.register("asha", "s3cret-pass")

        self.assertNotIn("s3cret-pass", self.path.read_text())

    def test_two_users_with_the_same_password_get_different_hashes(self):
        self.store.register("asha", "s3cret-pass")
        self.store.register("ravi", "s3cret-pass")

        users = json.loads(self.path.read_text())
        self.assertNotEqual(users["asha"]["hash"], users["ravi"]["hash"])

    def test_a_username_cannot_be_registered_twice(self):
        self.store.register("asha", "s3cret-pass")

        with self.assertRaisesRegex(RegistrationError, "already taken"):
            self.store.register("asha", "another-pass")
        self.store.verify("asha", "s3cret-pass")

    def test_a_blank_username_or_short_password_is_rejected(self):
        with self.assertRaisesRegex(RegistrationError, "Enter a username"):
            self.store.register("   ", "s3cret-pass")
        with self.assertRaisesRegex(RegistrationError, "at least 6 characters"):
            self.store.register("asha", "abc")
        self.assertFalse(self.path.exists())

    def test_a_username_that_looks_like_a_path_creates_no_other_file(self):
        self.store.register("../escape", "s3cret-pass")

        self.assertEqual([p.name for p in self.folder.iterdir()], ["users.json"])
        self.assertFalse((self.folder.parent / "escape").exists())

    def test_accounts_survive_a_new_store_on_the_same_file(self):
        self.store.register("asha", "s3cret-pass")

        UserStore(self.path).verify("asha", "s3cret-pass")


if __name__ == "__main__":
    unittest.main()
