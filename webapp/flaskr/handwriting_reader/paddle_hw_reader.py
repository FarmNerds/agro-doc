from paddleocr import PaddleOCR
from handwriting_reader import HandwritingReader


class PaddleHandwritingReader(HandwritingReader):
    def __init__(self):
        self.ocr = PaddleOCR(
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device="cpu",
        )

    def read_text(self, path: str) -> list:
        results = self.ocr.predict(
            input=path
        )

        return results


if __name__ == "__main__":
    reader = PaddleHandwritingReader()
    results = reader.read_text(
        path="flaskr/static/uploads/images/pow_whiteboard.jpg")

    for res in results:
        res.print()
        res.save_to_img("flaskr/handwriting_reader/.output")
        res.save_to_json("flaskr/handwriting_reader/.output")
