"""Base provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GenerateResult:
    task_id: str
    status: str  # pending | processing | done | failed
    file_url: str | None = None
    file_path: str | None = None
    error: str | None = None


class ImageProvider(ABC):
    @abstractmethod
    async def generate_image(self, prompt: dict) -> GenerateResult:
        ...

    @abstractmethod
    async def get_status(self, task_id: str) -> GenerateResult:
        ...


class VideoProvider(ABC):
    @abstractmethod
    async def generate_video(self, prompt: dict) -> GenerateResult:
        ...

    @abstractmethod
    async def get_status(self, task_id: str) -> GenerateResult:
        ...
