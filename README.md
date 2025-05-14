# Digital Therapeutix

A secure Flask-based authentication system for doctors, featuring email verification, license validation, password reset, and session management.

## Features

- Doctor signup with license and institution details
- Email verification for new accounts
- Manual license approval by admin
- Secure login/logout with session and JWT support
- Password reset via email
- CSRF protection on all forms
- Environment-based configuration

## Project Structure

```
digital_therapeutix/
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   │   └── user.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── forms.py
│   └── templates/
│       └── auth/
│           ├── login.html
│           ├── signup.html
│           ├── forgot_password.html
│           └── reset_password.html
├── config.py
├── .env
├── .gitignore
├── requirements.txt
└── run.py
```

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/digital_therapeutix.git
cd digital_therapeutix
```

### 2. Create and activate a virtual environment

```sh
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

### 4. Set up your `.env` file

Create a `.env` file in the project root with the following content:

```
SECRET_KEY=your-very-secret-key
DATABASE_URL=sqlite:///dev.db
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

> **Note:** Never commit your `.env` file to version control.

### 5. Run the application

```sh
python run.py
```

Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

## Database Initialization

The database tables are created automatically when you run the app for the first time.

## Security Notes

- All forms are CSRF-protected.
- Passwords are securely hashed.
- Email and license verification are required for login.
- Sensitive configuration is loaded from environment variables.

## License

Digital Therapeutix License

---

**Developed with ❤️ by Nightowl Tech Solutions Pvt. Ltd.**
