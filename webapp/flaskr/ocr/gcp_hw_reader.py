"""
Wrapper around Google Cloud Vision's API

Requires google cloud vision and google cloud SDK
"""

from google.cloud import vision
from abstract_hw_reader import HandwritingReader, ReadText
import logging
import os

logger = logging.getLogger("gcp")


class GoogleCloudVisionHR(HandwritingReader):
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            ".creds/farmdocs-7e1092c19709.json"
        )
        self.client = vision.ImageAnnotatorClient()

    def read_text(self, path: str) -> ReadText:
        """
        Detects document features in an image using Google Cloud Vision API.

        Args:
            path: Path to the image file.

        Returns:
            ReadText object containing extracted text, confidence scores, and bounding boxes.
        """
        with open(path, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = self.client.document_text_detection(image=image)

        text_list = []
        confidence_list = []
        bounding_boxes = []

        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                logger.debug(f"Block confidence: {block.confidence}")
                for paragraph in block.paragraphs:
                    logger.debug(
                        f"Paragraph confidence: {paragraph.confidence}")
                    for word in paragraph.words:
                        word_text = "".join(
                            [symbol.text for symbol in word.symbols])
                        logger.debug(
                            f"Word text: {word_text} (confidence: {word.confidence})")

                        text_list.append(word_text)
                        confidence_list.append(word.confidence)

                        # Extract bounding box vertices
                        vertices = word.bounding_box.vertices
                        if vertices:
                            # Store as (x_min, y_min, x_max, y_max)
                            x_coords = [v.x for v in vertices]
                            y_coords = [v.y for v in vertices]
                            bbox = (
                                min(x_coords),
                                min(y_coords),
                                max(x_coords),
                                max(y_coords),
                            )
                            bounding_boxes.append(bbox)

                        for symbol in word.symbols:
                            logger.debug(
                                f"\tSymbol: {symbol.text} (confidence: {symbol.confidence})")

        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message
                )
            )

        return ReadText(
            text=text_list,
            confidence=confidence_list,
            bounding_boxes=bounding_boxes if bounding_boxes else None,
        )


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    reader = GoogleCloudVisionHR()
    read_text_result = reader.read_text(
        "flaskr/static/uploads/images/pow_whiteboard.jpg")

    logger.info("------ HASN'T BEEN TESTED YET ------")
    # As of 12-15-2025, this code has not been tested as we're switching to
    # PaddleOCR for the meantime, and GCP SDK has been removed from the env.
