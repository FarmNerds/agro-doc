"""
Definition for abstract HandwritingReader class
"""
from ocr.abstract_hw_reader import HandwritingReader, OCRType


class HandwritingReaderFactory:
    """
    Factory class to create the appropriate HandwritingReader based on OCRType.
    """

    @staticmethod
    def create(ocr_type: OCRType = OCRType.PADDLE) -> HandwritingReader:
        """
        Creates and returns the appropriate HandwritingReader implementation.

        Args:
            ocr_type: an OCRType enum value specifying the type of OCR to use.

        Returns:
            An instance of the appropriate HandwritingReader subclass.
        """
        if ocr_type == OCRType.GOOGLE_CLOUD_VISION:
            from ocr.gcp_hw_reader import GoogleCloudVisionHR
            return GoogleCloudVisionHR()
        elif ocr_type == OCRType.PADDLE:
            from ocr.paddle_hw_reader import PaddleHandwritingReader
            return PaddleHandwritingReader()
        else:
            raise ValueError(f"Unsupported OCR type: {ocr_type}")


if __name__ == "__main__":
    # Example usage
    ocr_type = OCRType.PADDLE
    reader = HandwritingReaderFactory.create(ocr_type)
    text_data = reader.read_text(
        "flaskr/static/uploads/images/pow_whiteboard.jpg")
    print(text_data.text)
