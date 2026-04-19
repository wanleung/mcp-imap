"""Async per-account lock manager to prevent concurrent syncs.

This module provides an AccountLockManager that maintains a dictionary
of asyncio.Lock instances keyed by account_id. This ensures that only
one sync operation can run at a time for any given account, while
allowing different accounts to sync concurrently.
"""

import asyncio
from typing import Dict


class AccountLockManager:
    """Manages per-account asyncio locks to prevent concurrent syncs.

    Each account_id maps to its own asyncio.Lock. When a sync operation
    begins for an account, it acquires that account's lock. If another
    sync is already in progress for the same account, the second caller
    will block (or can be configured to fail immediately).

    Usage:
        lock_manager = AccountLockManager()
        lock = await lock_manager.get_lock("user@example.com")
        async with lock:
            # perform sync operation
            ...
    """

    def __init__(self) -> None:
        """Initialize the lock manager with an empty lock dictionary."""
        self._locks: Dict[str, asyncio.Lock] = {}
        self._creation_lock = asyncio.Lock()

    async def get_lock(self, account_id: str) -> asyncio.Lock:
        """Get or create the asyncio.Lock for the given account_id.

        If no lock exists for the account_id, a new asyncio.Lock is
        created and stored. Subsequent calls with the same account_id
        return the same lock instance.

        Args:
            account_id: The unique identifier for the account whose
                lock is being requested.

        Returns:
            The asyncio.Lock instance associated with the given account_id.
        """
        async with self._creation_lock:
            lock = self._locks.get(account_id)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[account_id] = lock
            return lock

    def is_locked(self, account_id: str) -> bool:
        """Check whether the lock for a given account is currently held.

        Args:
            account_id: The unique identifier for the account to check.

        Returns:
            True if the lock is currently acquired (sync in progress),
            False if the lock is free or does not exist yet.
        """
        lock = self._locks.get(account_id)
        if lock is None:
            return False
        return lock.locked()

    async def remove_lock(self, account_id: str) -> None:
        """Remove the lock entry for a given account.

        This is useful for cleanup when an account is deleted or
        deactivated, preventing unbounded growth of the _locks dict.

        Args:
            account_id: The unique identifier for the account whose
                lock entry should be removed.

        Raises:
            RuntimeError: If the lock exists and is currently acquired.
        """
        async with self._creation_lock:
            lock = self._locks.get(account_id)
            if lock is None:
                return
            if lock.locked():
                raise RuntimeError(
                    f"Cannot remove lock for account '{account_id}' while it is in use."
                )
            self._locks.pop(account_id, None)

    @property
    def active_locks(self) -> int:
        """Return the number of accounts currently holding a lock.

        Returns:
            Count of locks that are currently in the locked state.
        """
        return sum(1 for lock in self._locks.values() if lock.locked())

    @property
    def total_accounts(self) -> int:
        """Return the total number of accounts with lock entries.

        Returns:
            Count of all account lock entries, whether locked or not.
        """
        return len(self._locks)
