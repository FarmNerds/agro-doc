from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
from enum import Enum


class OCRType(Enum):
    """
    Enum for the type of OCR to use.
    """

    GOOGLE_CLOUD_VISION = "google_cloud_vision"  # No longer in use as of 12-15-2025
    PADDLE = "paddle"


@dataclass
class ReadText:
    """
    Wrapper for the text, confidence, and bounding boxes output returned by the
    OCR API call.

    Note: not all OCR APIs return bounding boxes, so this field is optional.
    """

    text: List[str]
    confidence: List[float]
    bounding_boxes: List[tuple[float, float, float, float]] | None

    def __len__(self) -> int:
        return len(self.text)


class HandwritingReader(ABC):
    """
    Abstract base class for handwriting readers.

    Implementations should override read_text() to return a ReadText object.
    """

    @abstractmethod
    def read_text(self, path: str) -> ReadText:
        """
        Uses OCR to extract text from an image file at the specified path.

        Args:
            path: a string representing the path to the image file.

        Returns:
            A ReadText object containing the extracted text, confidence scores,
            and bounding boxes.
        """
        pass
