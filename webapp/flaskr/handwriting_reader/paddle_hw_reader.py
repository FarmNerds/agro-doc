from paddleocr import PaddleOCR
from handwriting_reader import HandwritingReader
import logging
from typing import Any, Dict

logger = logging.getLogger('paddle')


class PaddleHandwritingReader(HandwritingReader):
    def __init__(self):
        self.ocr = PaddleOCR(
            text_detection_model_name="PP-OCRv5_server_det",
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device="cpu",
        )

    def read_text(self, path: str) -> list:
        self.results = self.ocr.predict(input=path)

        return self.results

    def get_text_output(self) -> list[str]:
        # return [res["text"] for res in self.results]
        extracted_text: list[str] = []
        if not self.results:
            print("No results to process.")
            return []

        # --- INSPECTION CODE ---
        # Get the first result object for inspection
        first_res = self.results[0]
        print(f"Type of result object: {type(first_res)}")
        print(f"Attributes available: {dir(first_res)}")
        # If it has a __dict__ attribute (most custom objects do), print that too:
        try:
            print(f"Object internal dictionary: {first_res.__dict__}")
        except AttributeError:
            print("Object does not have a __dict__ attribute.")
        # ---------------------

        for res_obj in self.results:
            # Based on the dynamic inspection above, you should find the correct attribute name
            # Replace text with the correct attribute name found in the print output (e.g., 'text', 'content', 'ocr_text')
            try:
                text = res_obj.text
                extracted_text.append(text)
            except AttributeError:
                print("Could not find the correct attribute name.")
                break
        return extracted_text


if __name__ == "__main__":
    reader = PaddleHandwritingReader()
    results = reader.read_text(
        path="flaskr/static/uploads/images/pow_whiteboard.jpg")
    texts: list[str] = reader.get_text_output()
    for res in results:
        res.print()
        res.save_to_img("flaskr/handwriting_reader/.output")
        res.save_to_json("flaskr/handwriting_reader/.output")

    for text in texts:
        print(text)
