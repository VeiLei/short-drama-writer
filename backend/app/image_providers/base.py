from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ImageResult:
    image_id: str
    image_url: str
    file_path: Optional[str] = None
    dimensions: str = ""
    aspect_ratio: str = ""
    api_response: dict = None

    def __post_init__(self):
        if self.api_response is None:
            self.api_response = {}


class BaseImageProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, aspect_ratio: str = "1:1",
                       reference_images: Optional[List[str]] = None) -> ImageResult:
        """Generate a single image from a text prompt."""

    @abstractmethod
    async def refine(self, image_id: str, instruction: str) -> ImageResult:
        """Refine an existing image based on natural language instruction."""
