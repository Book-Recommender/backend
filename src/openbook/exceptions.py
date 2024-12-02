from fastapi import HTTPException


class UnauthenticatedError(HTTPException):
    """Raised when the user is not authenticated and attempting to access endpoints requiring authentication."""

    def __init__(self) -> None:
        super().__init__(status_code=401, detail="You are not authenticated.")
