from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    @abstractmethod
    async def fetch(self, identifier: str) -> dict[str, Any]:
        ...
