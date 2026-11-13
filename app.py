"""Login and registration demo: a small Tkinter desktop app."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path

from user_store import LoginError, RegistrationError, UserStore

USERS_FILE = Path(__file__).resolve().parent / "users.json"


class AccountApp:
    """The main window with its Login and Register dialogs."""

    def __init__(self, store: UserStore):
        self.store = store
        self.root = tk.Tk()
        self.root.geometry("300x250")
        self.root.title("Account Login")

        tk.Label(
            self.root, text="Select Your Choice", bg="blue", fg="white",
            width="300", height="2", font=("Calibri", 13),
        ).pack()
        tk.Label(self.root, text="").pack()
        tk.Button(
            self.root, text="Login", height="2", width="30", command=self.open_login
        ).pack()
        tk.Label(self.root, text="").pack()
        tk.Button(
            self.root, text="Register", height="2", width="30", command=self.open_register
        ).pack()

    def _open_form(self, title: str, heading: str, button_text: str, on_submit):
        """Build a dialog with username and password fields and a status line."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x250")

        tk.Label(dialog, text=heading).pack()
        tk.Label(dialog, text="").pack()
        tk.Label(dialog, text="Username * ").pack()
        username = tk.Entry(dialog)
        username.pack()
        tk.Label(dialog, text="Password * ").pack()
        password = tk.Entry(dialog, show="*")
        password.pack()
        tk.Label(dialog, text="").pack()
        status = tk.Label(dialog, text="", font=("Calibri", 11), wraplength=280)

        def submit(_event=None):
            ok, message = on_submit(username.get(), password.get())
            status.config(text=message, fg="green" if ok else "red")
            password.delete(0, tk.END)
            if ok:
                username.delete(0, tk.END)

        button = tk.Button(dialog, text=button_text, width=10, height=1, command=submit)
        button.pack()
        status.pack(pady=5)
        dialog.bind("<Return>", submit)
        username.focus_set()

        # Exposed so a test can drive the dialog.
        dialog.username, dialog.password = username, password
        dialog.submit_button, dialog.status = button, status
        return dialog

    def open_register(self):
        return self._open_form(
            "Register", "Please enter details below", "Register", self._register
        )

    def open_login(self):
        return self._open_form(
            "Login", "Please enter details below to login", "Login", self._login
        )

    def _register(self, username: str, password: str) -> tuple[bool, str]:
        try:
            self.store.register(username, password)
        except RegistrationError as problem:
            return False, str(problem)
        return True, "Registration Success"

    def _login(self, username: str, password: str) -> tuple[bool, str]:
        try:
            self.store.verify(username, password)
        except LoginError as problem:
            return False, str(problem)
        return True, "Login Success"

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    AccountApp(UserStore(USERS_FILE)).run()


if __name__ == "__main__":
    main()
