from typing import Any


class ModelValidationError(Exception):
    type_structure: dict[str, Any]
    validation_errors: list[object]

    def __init__(self, type_structure, validation_errors):
        super().__init__(self)
        self.type_structure = type_structure
        self.validation_errors = validation_errors
