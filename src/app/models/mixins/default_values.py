from sqlalchemy.inspection import inspect

from app.exceptions.model_validation_error import ModelValidationError


class DefaultValuesMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        mapper = inspect(self.__class__)
        for column in mapper.columns:
            if getattr(self, column.name) is None and column.default is not None:
                default = column.default.arg
                value = default() if callable(default) else default
                setattr(self, column.name, value)
        self.validate_model_instance()

    def validate_model_instance(self):
        mapper = inspect(self.__class__)
        structure = {}
        errors = []
        for column in mapper.columns:
            structure[column.name] = {
                "type": f"{column.type}",
                "nullable": column.nullable,
                "default": None if column.default is None else f"{column.default}"
            }
            if not column.nullable and not column.autoincrement and column.default is None and column.server_default is None:
                if getattr(self, column.name) is None:
                    errors.append({
                        "field": column.name,
                        "expected_type": str(column.type)
                    })
        if len(errors) > 0:
            raise ModelValidationError(structure, errors)
