# Graphical Login and Registration

[![CI](https://github.com/Logesh2097/Graphical_login-reg/actions/workflows/ci.yml/badge.svg)](https://github.com/Logesh2097/Graphical_login-reg/actions/workflows/ci.yml)

A small desktop login and registration app written in Python with Tkinter.

## Overview

The main window offers **Login** and **Register**. Registering creates an
account in a local file; logging in checks a username and password against it
and reports "Login Success", "Invalid Password" or "User Not Found". Written as
a learning project for Tkinter forms and safe password storage.

## Features

- Register and login dialogs, submitted with the button or the Enter key.
- Passwords are never stored. Each account keeps a salted PBKDF2-SHA256 hash (600,000 iterations), compared in constant time.
- All accounts live in one JSON file, so a username can never be used as a file path.
- Rejects a blank username, a password shorter than 6 characters, and a username that is already taken.
- Account storage is separate from the window, so it is tested without a display.
- No third-party dependencies.

## Architecture

| File | Responsibility |
|---|---|
| `user_store.py` | `UserStore`: create an account, verify a password, read and write the accounts file |
| `app.py` | `AccountApp`: the Tkinter windows; calls `UserStore` and shows the result |

```
app.py (Tkinter) ──▶ UserStore.register() / verify() ──▶ users.json
```

## Technology stack

Python 3.10+ and Tkinter (both in the standard library), `hashlib` PBKDF2. ruff and GitHub Actions for checks.

## Project structure

```
.
├── app.py
├── user_store.py
└── tests/
    ├── test_user_store.py
    └── test_app.py
```

## Installation and running

Tkinter ships with the python.org installers for Windows and macOS. On
Debian or Ubuntu, install it with `sudo apt install python3-tk`.

```bash
git clone https://github.com/Logesh2097/Graphical_login-reg.git
cd Graphical_login-reg
python app.py
```

Accounts are written to `users.json` beside `app.py`. The file is listed in
`.gitignore`. There are no environment variables.

## Using the store from Python

```python
from user_store import UserStore, LoginError

store = UserStore("users.json")
store.register("asha", "a-long-password")
try:
    store.verify("asha", "a-long-password")   # returns quietly on success
except LoginError as problem:
    print(problem)                             # "Invalid Password" or "User Not Found"
```

## Testing

```bash
python -m unittest discover -s tests -v
ruff check .        # pip install ruff
```

The store tests run anywhere. The four window tests need Tkinter and a
display and are skipped without them; in GitHub Actions they run under a
virtual display (`xvfb-run`).

## Limitations and future improvements

- This is a local, single-user demo: there is no session after login and no lockout after repeated failures.
- Telling "User Not Found" apart from "Invalid Password" is kept from the original design; a real system should give one message for both.
- A screen after login, and a way to change a password.
