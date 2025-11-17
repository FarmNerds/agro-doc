"""
Wrapper around Google Cloud Vision's API

Requires google cloud vision and google cloud SDK
"""
from google.cloud import vision
from handwriting_reader import HandwritingReader
import os


class GoogleCloudVisionHR(HandwritingReader):

    def read_text(self, path):
        """Detects document features in an image."""

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".creds/farmdocs-7e1092c19709.json"
        client = vision.ImageAnnotatorClient()
        with open(path, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        words = ""  # in string format
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                print(f"\nBlock confidence: {block.confidence}\n")
                for paragraph in block.paragraphs:
                    print("Paragraph confidence: {}".format(
                        paragraph.confidence))
                    for word in paragraph.words:
                        word_text = "".join(
                            [symbol.text for symbol in word.symbols])
                        print(
                            "Word text: {} (confidence: {})".format(
                                word_text, word.confidence
                            )
                        )
                        words += word_text + " "
                        for symbol in word.symbols:
                            print(
                                "\tSymbol: {} (confidence: {})".format(
                                    symbol.text, symbol.confidence
                                )
                            )
        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message)
            )
        return words
