from abc import ABC, abstractmethod
from datetime import date

class InstrumentHandler(ABC):
    """
    Abstract base class for all instrument handlers.
    Provides helper for determining if an update is needed.
    Subclasses must define `asset_type` string.
    """
    asset_type: str

    def __init__(self, client, meta):
        self.client = client
        self.meta   = meta
        if not hasattr(self, 'asset_type'):
            raise ValueError("Subclasses must define asset_type class attribute")

    @abstractmethod
    def download_full(self, **kwargs):
        """Download full dataset for this asset type."""
        raise NotImplementedError

    @abstractmethod
    def download_update(self, period: str, **kwargs):
        """Download incremental update for given period (day/week/month)."""
        raise NotImplementedError

    @abstractmethod
    def last_remote_update(self, full: bool=False) -> date:
        """Return date of last remote update (full if specified)."""
        raise NotImplementedError

    def needs_update(self, period: str) -> bool:
        """
        Compare remote vs local metadata to decide if an update is needed.
        """
        remote = self.last_remote_update(full=False)
        local_str = self.meta.get(self.asset_type, period)
        if local_str is None:
            return True
        local = date.fromisoformat(local_str)
        return remote > local