"""Custom exception hierarchy for MCP Email Service domain errors."""

from typing import Optional


class MCPEmailError(Exception):
    """Base exception for MCP email service."""

    def __init__(self, message: str = "", detail: Optional[str] = None) -> None:
        self.message = message
        self.detail = detail
        super().__init__(message)

    def __str__(self) -> str:
        if self.detail:
            return f"{self.message} — {self.detail}"
        return self.message


class AccountNotFoundError(MCPEmailError):
    """Raised when account_id not found."""

    def __init__(self, account_id: str, detail: Optional[str] = None) -> None:
        self.account_id = account_id
        message = f"Account not found: {account_id}"
        super().__init__(message=message, detail=detail)


class SyncInProgressError(MCPEmailError):
    """Raised when sync already in progress for account."""

    def __init__(self, account_id: str, detail: Optional[str] = None) -> None:
        self.account_id = account_id
        message = f"Sync already in progress for account: {account_id}"
        super().__init__(message=message, detail=detail)


class IMAPConnectionError(MCPEmailError):
    """Raised when IMAP connection fails."""

    def __init__(
        self,
        message: str = "IMAP connection failed",
        host: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        self.host = host
        super().__init__(message=message, detail=detail)


class CredentialValidationError(MCPEmailError):
    """Raised when IMAP credentials are invalid."""

    def __init__(
        self,
        message: str = "Invalid IMAP credentials",
        account_id: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        self.account_id = account_id
        super().__init__(message=message, detail=detail)
