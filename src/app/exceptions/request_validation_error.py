class RequestValidationError(Exception):
    message: str

    def __init__(self, message):
        super().__init__(self)
        self.message = message
