# Advisory Service Back-End

## Getting Started
1. Create an account (can be free) in Hugging Face: https://huggingface.co/
1. Create an access token: Click on profile icon (top-right corner) and "Access Tokens" from the menu.
1. Create file `src/secrets.json` with the following contents:
   ```json
   {
       "huggingface-access-token": "...Copy your HuggingFace access token (point x) here..."
   }
   ```
1. Configure database connection string and Hugging Face models in file `src/config.json`.
1. Create database objects with Alembic (Unix-based shell):
   ```shell
   src/${env}-db.sh upgrade
   ```
   *Note: env can be `dev` or `prod`*

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
