# Alembic

## Setup
Add the following into Alembic's `env.py` when Migrations have just been initialised (no migration created yet):
```python
from app.models.mixins.soft_delete import rebuild_partial_indexes # <-- Add this import.
...
def run_migrations_online(): # <-- Then at the end of this method,
    ...
    with connectable.connect() as connection: # <-- inside the use of the connection,
        ...
        if not getattr(context.config.cmd_opts, 'autogenerate', False): # <-- add these lines.
            rebuild_partial_indexes(connection) # <-- yes, this one too.
```
