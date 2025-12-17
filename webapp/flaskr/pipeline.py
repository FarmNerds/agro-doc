from llm.phi3 import Phi3Wrapper
from ocr.handwriting_reader import HandwritingReader, HandwritingReaderFactory
from ocr.ocr_post_processing import OCRPostProcessor
from time import perf_counter


class Pipeline:
    def __init__(self, phi3_wrapper: Phi3Wrapper, handwriting_reader: HandwritingReader):
        self.phi3_wrapper = phi3_wrapper
        self.handwriting_reader = handwriting_reader
        self.post_processor = OCRPostProcessor(min_confidence=0.3,
                                               high_confidence_threshold=0.75)

    def process_image(self, image_path: str) -> str:
        # Get extracted text from the handwriting reader
        read_text_res = self.handwriting_reader.read_text(image_path)
        processed_text = self.post_processor.process(read_text_res)
        # Cleanup and context correction using Phi3
        final_text = self.phi3_wrapper.clean_ocr_output(
            processed_text)

        return final_text


if __name__ == "__main__":
    start_time = perf_counter()
    path = "flaskr/static/uploads/images/pow_whiteboard.jpg"
    pipeline = Pipeline(Phi3Wrapper(), HandwritingReaderFactory.create())

    result = pipeline.process_image(path)
    print(result)

    end_time = perf_counter()
    print(f"Processing time: {end_time - start_time:.2f} seconds")
