# Advisory Service Back-End

## Getting Started
1. Create an account (can be free) in Hugging Face: https://huggingface.co/
2. Create an access token: Click on profile icon (top-right corner) and "Access Tokens" from the menu.
3. Create virtual environment:
   ```shell
   python -m venv .venv
   # Then activate this virtual environment
   # On Linux/macOS: source .venv/bin/activate
   # On Windows (Command Prompt): .venv\Scripts\activate.bat
   # On Windows (PowerShell): .venv\Scripts\Activate.ps1
   pip install -r requirements.txt # some configurations may need `--trusted_host files.pythonhosted.org`
   ```
4. Create file `src/secrets.json` with the following contents:
   ```json
   {
       "huggingface-access-token": "...Copy your HuggingFace access token (point x) here..."
   }
   ```
5. *(TODO - Future)* Configure database connection string and Hugging Face models in file `src/config.json`.
6. Create database objects with Alembic (Unix-based shell):
   ```shell
   src/${env}-db.sh upgrade
   ```
   *Note: env can be `dev` or `prod`*

---

## Run Server
```shell
# Move to src directory
cd src
# Export FLASK_* variables (note, in PowerShell use `set`):
export FLASK_APP=app/__init__.py
export FLASK_ENV=development # or production
# Run server instance
flask run
```

---

## Tests
Tests are located in directory `tests`. They've been written and expected to be run using pytest.

### Running tests
```shell
cd tests
pytest
```

---

## Maintenance
**IMPORTANT: When building the list of requirements in PowerShell, please use the following line:**
```shell
pip freeze | Out-File -Encoding UTF8 requirements.txt
```
Simply redirecting the output to the file results in a `requirements.txt` file in UTF-16LE encoding,
making it binary to most Git implementations.

### Upgrading all dependencies
```shell
pip-review --auto
```
And remember to re-freeze dependencies--as explained above--afterwards.

---

## TODO: REMOVE THIS

[
    "https://msrc.microsoft.com/blog/tags/azure/feed",
    "https://msrc.microsoft.com/blog/categories/microsoft-threat-hunting/feed",
    "https://msrc.microsoft.com/blog/tags/security-advisory/feed",
    "https://msrc.microsoft.com/blog/categories/security-research-defense/feed",
    "https://msrc.microsoft.com/blog/tags/windows-insider-preview/feed",
    "https://msrc.microsoft.com/blog/tags/windows-update/feed"
]
