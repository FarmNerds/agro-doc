from paddleocr import PaddleOCR
from ocr.abstract_hw_reader import HandwritingReader, ReadText
import logging
from pathlib import Path

logger = logging.getLogger("paddle")


class PaddleHandwritingReader(HandwritingReader):
    def __init__(self):
        self.client = PaddleOCR(
            text_detection_model_name="PP-OCRv5_server_det",
            text_recognition_model_name="en_PP-OCRv5_mobile_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device="cpu",  # while slow, GPU isn't exposed in devcontainer TODO
        )

    def read_text(self, path: str) -> ReadText:
        """Run OCR and return extracted text in ReadText format."""
        self.results = self.client.predict(input=path)

        extracted_text: list[str] = []
        confidence_scores: list[float] = []
        bounding_boxes: list[tuple[float, float, float, float]] = []

        if self.results:
            for res_obj in self.results:
                if isinstance(res_obj, dict) and 'rec_texts' in res_obj:
                    extracted_text.extend(res_obj['rec_texts'])

                    # Extract confidence scores
                    if 'rec_scores' in res_obj:
                        confidence_scores.extend(res_obj['rec_scores'])

                    # Extract bounding boxes (convert from [x1, y1, x2, y2] format)
                    if 'rec_boxes' in res_obj:
                        for box in res_obj['rec_boxes']:
                            # box format: [x1, y1, x2, y2]
                            bounding_boxes.append((float(box[0]), float(
                                box[1]), float(box[2]), float(box[3])))

        return ReadText(
            text=extracted_text,
            confidence=confidence_scores,
            bounding_boxes=bounding_boxes if bounding_boxes else None
        )


if __name__ == "__main__":
    reader = PaddleHandwritingReader()
    read_text_result: ReadText = reader.read_text(
        path="flaskr/static/uploads/images/pow_whiteboard.jpg")

    print("Extracted text lines:")
    for i, line in enumerate(read_text_result.text):
        confidence = read_text_result.confidence[i] if i < len(
            read_text_result.confidence) else "N/A"
        bbox = read_text_result.bounding_boxes[i] if read_text_result.bounding_boxes and i < len(
            read_text_result.bounding_boxes) else "N/A"
        print(f"{i}: {line} (confidence: {confidence:.3f}, bbox: {bbox})")

    # Save visualization outputs
    for res in reader.results:
        res.print()
        output_dir = Path(__file__).parent / ".output"
        output_dir.mkdir(parents=True, exist_ok=True)
        res.save_to_img(str(output_dir))
        res.save_to_json(str(output_dir))
