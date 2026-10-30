"""Domain errors. The API layer turns these into JSON error responses."""


class DomainError(Exception):
    status_code = 400

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class NotFoundError(DomainError):
    status_code = 404


class ValidationFailedError(DomainError):
    status_code = 422


class ConflictError(DomainError):
    status_code = 409
