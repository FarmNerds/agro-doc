import logging
from dataclasses import dataclass
from ocr.abstract_hw_reader import ReadText

logger = logging.getLogger("ocr_post_processing")


@dataclass
class ProcessedOCR:
    """
    Post-processed OCR output with filtering and cleaning applied.

    Attributes:
        high_confidence: Lines above confidence threshold (likely correct)
        low_confidence: Lines below threshold (need LLM correction)
        filtered_out: Lines filtered out completely (too low confidence)
        original: Original unprocessed ReadText object
    """
    high_confidence: ReadText
    low_confidence: ReadText
    filtered_out: ReadText
    original: ReadText


class OCRPostProcessor:
    """
    Post-processes raw OCR output before LLM correction.

    Handles:
    - Filtering by confidence threshold
    - Basic text cleaning (whitespace, artifacts)
    - Grouping results by confidence level
    """

    def __init__(
        self,
        min_confidence: float = 0.3,  # Filter out below this
        high_confidence_threshold: float = 0.75,  # Above this = likely correct
    ):
        """
        Initialize post-processor with thresholds.

        Args:
            min_confidence: Minimum confidence to keep (0.0-1.0)
            high_confidence_threshold: Threshold for "high confidence" (0.0-1.0)
        """
        self.min_confidence = min_confidence
        self.high_confidence_threshold = high_confidence_threshold
        logger.info(
            f"Initialized OCR post-processor: "
            f"min={min_confidence}, high={high_confidence_threshold}"
        )

    def process(self, ocr_result: ReadText) -> ProcessedOCR:
        """
        Post-process OCR results by filtering and grouping by confidence.

        Args:
            ocr_result: Raw OCR output from reader

        Returns:
            ProcessedOCR with results grouped by confidence level
        """
        logger.debug(f"Post-processing {len(ocr_result)} OCR lines")

        high_conf_text, high_conf_scores, high_conf_boxes = [], [], []
        low_conf_text, low_conf_scores, low_conf_boxes = [], [], []
        filtered_text, filtered_scores, filtered_boxes = [], [], []

        for i, (text, conf) in enumerate(zip(ocr_result.text, ocr_result.confidence)):
            # Clean the text
            cleaned_text = self._clean_text(text)

            # Get bounding box if available
            bbox = ocr_result.bounding_boxes[i] if ocr_result.bounding_boxes else None

            # Filter by confidence
            if conf < self.min_confidence:
                logger.debug(
                    f"Filtering out low confidence [{conf:.3f}]: {cleaned_text}")
                filtered_text.append(cleaned_text)
                filtered_scores.append(conf)
                if bbox:
                    filtered_boxes.append(bbox)
            elif conf >= self.high_confidence_threshold:
                logger.debug(f"High confidence [{conf:.3f}]: {cleaned_text}")
                high_conf_text.append(cleaned_text)
                high_conf_scores.append(conf)
                if bbox:
                    high_conf_boxes.append(bbox)
            else:
                logger.debug(
                    f"Low confidence [{conf:.3f}]: {cleaned_text} (needs LLM)")
                low_conf_text.append(cleaned_text)
                low_conf_scores.append(conf)
                if bbox:
                    low_conf_boxes.append(bbox)

        logger.info(
            f"Post-processing complete: "
            f"{len(high_conf_text)} high conf, "
            f"{len(low_conf_text)} low conf, "
            f"{len(filtered_text)} filtered"
        )

        return ProcessedOCR(
            high_confidence=ReadText(
                text=high_conf_text,
                confidence=high_conf_scores,
                bounding_boxes=high_conf_boxes if high_conf_boxes else None
            ),
            low_confidence=ReadText(
                text=low_conf_text,
                confidence=low_conf_scores,
                bounding_boxes=low_conf_boxes if low_conf_boxes else None
            ),
            filtered_out=ReadText(
                text=filtered_text,
                confidence=filtered_scores,
                bounding_boxes=filtered_boxes if filtered_boxes else None
            ),
            original=ocr_result
        )

    def _clean_text(self, text: str) -> str:
        """
        Clean OCR text artifacts.

        Args:
            text: Raw OCR text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())

        # If I come across artifacts in testing, remove them
        # artifacts = []
        # for artifact in artifacts:
        #     text = text.replace(artifact, "")

        return text.strip()

    def combine_results(
        self,
        high_confidence: ReadText,
        corrected_low_confidence: ReadText
    ) -> ReadText:
        """
        Combine high-confidence (unchanged) and LLM-corrected results.

        Args:
            high_confidence: High confidence lines (already correct)
            corrected_low_confidence: LLM-corrected low confidence lines

        Returns:
            Combined ReadText with all results
        """
        combined_text = high_confidence.text + corrected_low_confidence.text
        combined_conf = high_confidence.confidence + corrected_low_confidence.confidence

        combined_boxes = None
        if high_confidence.bounding_boxes and corrected_low_confidence.bounding_boxes:
            combined_boxes = high_confidence.bounding_boxes + \
                corrected_low_confidence.bounding_boxes

        logger.debug(
            f"Combined {len(high_confidence)} high-conf + "
            f"{len(corrected_low_confidence)} corrected = "
            f"{len(combined_text)} total lines"
        )

        return ReadText(
            text=combined_text,
            confidence=combined_conf,
            bounding_boxes=combined_boxes
        )
