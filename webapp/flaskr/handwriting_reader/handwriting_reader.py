"""
Definition for abstract HandwritingReader class
"""
from abc import ABC, abstractmethod


class HandwritingReader(ABC):
    @abstractmethod
    def read_text(self, path):
        """Reads text from image"""
