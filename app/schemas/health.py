"""Pydantic schemas for health check responses."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response model for the health check endpoint.

    Attributes:
        status: Overall health status - "healthy" or "unhealthy".
        db: Database connectivity status - "connected" or "disconnected".
        imap_pool: IMAP connection pool status - "available" or "unavailable".
    """

    status: str
    db: str
    imap_pool: str