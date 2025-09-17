from sqlalchemy import ColumnElement, TIMESTAMP
from sqlalchemy.ext.compiler import compiles

_DEFAULT_UTC_NOW_PER_DIALECT = "CURRENT_TIMESTAMP"  # fallback (may not be UTC)
_UTC_NOW_PER_DIALECT = {
    "mariadb": "UTC_TIMESTAMP()",
    "mssql": "SYSUTCDATETIME()",
    "mysql": "UTC_TIMESTAMP()",
    "oracle": "SYS_EXTRACT_UTC(SYSTIMESTAMP)",
    "postgresql": "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')",
    "sqlite": "(datetime('now'))",
    "sqlserver": "SYSUTCDATETIME()",
}


class SDUTCNow(ColumnElement):
    """
    A custom SQLAlchemy expression that renders a UTC timestamp based on the dialect.
    """

    type = TIMESTAMP()


@compiles(SDUTCNow)
def _compile_sd_utcnow(element, compiler, **kw):
    """
    This function is called by SQLAlchemy's compiler to render the UTCNow expression.
    """
    dialect_name = compiler.dialect.name
    expression = _UTC_NOW_PER_DIALECT.get(dialect_name, _DEFAULT_UTC_NOW_PER_DIALECT)
    return expression
