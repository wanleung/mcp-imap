"""Health check service for DB connectivity and IMAP pool status.

Provides a unified health check that verifies:
- Database connectivity via a lightweight query
- IMAP connection pool availability

The service is designed to be dependency-injection friendly, accepting
a database session factory and an IMAP pool reference so it can be
easily tested and configured.
"""

import logging
from typing import Any, Callable, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)


class HealthService:
    """Service responsible for checking system health.

    Checks database connectivity and IMAP connection pool availability,
    returning a structured :class:`HealthResponse`.

    Attributes:
        session_factory: Callable that returns a new async DB session.
        imap_pool: Reference to the IMAP connection pool object.
    """

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        imap_pool: Optional[Any] = None,
    ) -> None:
        """Initialise the health service.

        Args:
            session_factory: A callable returning an ``AsyncSession``
                used to verify database connectivity.
            imap_pool: An object representing the IMAP connection pool.
                Expected to expose an ``is_available`` property or method,
                or be ``None`` if IMAP is not configured.
        """
        self._session_factory = session_factory
        self._imap_pool = imap_pool

    async def check_db(self) -> str:
        """Check database connectivity by executing a lightweight query.

        Returns:
            ``"connected"`` if the database responds successfully,
            ``"disconnected"`` otherwise.
        """
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
            return "connected"
        except Exception as exc:
            logger.error("Database health check failed: %s", exc)
            return "disconnected"

    async def check_imap_pool(self) -> str:
        """Check whether the IMAP connection pool is available.

        The pool object is expected to expose either an ``is_available``
        property / attribute or an ``is_available()`` method.  If the pool
        is ``None`` (IMAP not configured) the check returns ``"unavailable"``.

        Returns:
            ``"available"`` if the pool reports readiness,
            ``"unavailable"`` otherwise.
        """
        if self._imap_pool is None:
            return "unavailable"

        try:
            # Support both property-style and method-style interfaces
            if callable(getattr(self._imap_pool, "is_available", None)):
                available = self._imap_pool.is_available()
            else:
                available = getattr(self._imap_pool, "is_available", False)

            return "available" if available else "unavailable"
        except Exception as exc:
            logger.error("IMAP pool health check failed: %s", exc)
            return "unavailable"

    async def check(self) -> HealthResponse:
        """Run all health checks and return an aggregated response.

        The overall ``status`` is ``"healthy"`` only when **both** the
        database and the IMAP pool report positive status.

        Returns:
            A :class:`HealthResponse` with individual component statuses
            and an aggregated top-level status.
        """
        db_status = await self.check_db()
        imap_status = await self.check_imap_pool()

        overall = "healthy" if (db_status == "connected" and imap_status == "available") else "unhealthy"

        return HealthResponse(
            status=overall,
            db=db_status,
            imap_pool=imap_status,
        )
