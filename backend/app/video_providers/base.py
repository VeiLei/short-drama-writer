from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class VideoResult:
    video_id: str
    video_url: str = ""
    file_path: Optional[str] = None
    duration: int = 0
    dimensions: str = ""
    aspect_ratio: str = "16:9"
    api_response: dict = field(default_factory=dict)


class BaseVideoProvider(ABC):

    @abstractmethod
    async def create_task(
        self, prompt: str, reference_images: Optional[List[str]] = None,
        ratio: str = "16:9", duration: int = 10, **kwargs
    ) -> str:
        """Create a video generation task, return task_id."""

    @abstractmethod
    async def get_task_status(self, task_id: str) -> VideoResult:
        """Poll task status."""

    @abstractmethod
    async def generate(
        self, prompt: str, reference_images: Optional[List[str]] = None,
        ratio: str = "16:9", duration: int = 10, **kwargs
    ) -> VideoResult:
        """Create task and poll until completion."""
