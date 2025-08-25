# Advisory Service Back-End

## Getting Started
1. Create an account (can be free) in Hugging Face: https://huggingface.co/
1. Create an access token: Click on profile icon (top-right corner) and "Access Tokens" from the menu.
1. Create virtual environment:
   ```shell
   python -m venv .venv
   # Then activate this virtual environment
   # On Linux/macOS: source .venv/bin/activate
   # On Windows (Command Prompt): .venv\Scripts\activate.bat
   # On Windows (PowerShell): .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
1. Create file `src/secrets.json` with the following contents:
   ```json
   {
       "huggingface-access-token": "...Copy your HuggingFace access token (point x) here..."
   }
   ```
1. *(TODO - Future)* Configure database connection string and Hugging Face models in file `src/config.json`.
1. Create database objects with Alembic (Unix-based shell):
   ```shell
   src/${env}-db.sh upgrade
   ```
   *Note: env can be `dev` or `prod`*

---

## Run Server
```shell
# Move to src directory
cd src
# Export FLASK_* variables:
export FLASK_APP=app/__init__.py
export FLASK_ENV=development # or production
# Run server instance
flask run
```

## TODO: REMOVE THIS

[
    "https://msrc.microsoft.com/blog/tags/azure/feed",
    "https://msrc.microsoft.com/blog/categories/microsoft-threat-hunting/feed",
    "https://msrc.microsoft.com/blog/tags/security-advisory/feed",
    "https://msrc.microsoft.com/blog/categories/security-research-defense/feed",
    "https://msrc.microsoft.com/blog/tags/windows-insider-preview/feed",
    "https://msrc.microsoft.com/blog/tags/windows-update/feed"
]
