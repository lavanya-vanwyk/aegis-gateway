import uuid
from rich import print

from typing import Dict, Any
from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
    RecognizerRegistry,
)

from presidio_anonymizer import AnonymizerEngine
from app.services.storage import TokenVaultService


class PrivacyMaskingService:
    def __init__(self):
        """
        Initializes the Presidio Analyzer and Anonymizer engines.
        The heavy spaCy language models are loaded into memory here once.

        """

        # Custom lowering of US recognizer scores as Presidio defaults to them over the custom ZA recognizers

        us_recognizers = [
            "UsSsnRecognizer",
            "PhoneRecognizer",
            "UsBankRecognizer",
            "UsLicenseRecognizer",
            "MedicalLicenseRecognizer",
            "UsPassportRecognizer",
            "NhsRecognizer",
            "UsItinRecognizer",
            "PhoneRecognizer",
        ]

        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()

        for recognizer in registry.get_recognizers(language="en", all_fields=True):
            if recognizer.name in us_recognizers:
                if hasattr(recognizer, "patterns") and recognizer.patterns:
                    for pattern in recognizer.patterns:
                        pattern.score = 0.05

        self.analyzer = AnalyzerEngine(registry=registry)
        self.south_african_pii_recognizer()
        self.vault = TokenVaultService()

    def south_african_pii_recognizer(self):
        """
        Method that adds custom regex rules for South African PII using
        strict non-capturing groups to prevent overlapping entity counts.
        """

        sa_patterns = [
            PatternRecognizer(
                supported_entity="ZA_ID_NUMBER",
                patterns=[
                    Pattern(
                        name="ZA_ID_NUMBER",
                        # Non-capturing groups (?:) guarantee only 1 entity is counted.
                        # Strictly enforces YY MM DD format + 4 digits + 08/18 + 1 digit.
                        regex=r"\b(?:\d{2})(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])(?:[\s]?\d{4})(?:[\s]?[01]8(?:[\s]?)\d)\b",
                        score=0.99,
                    )
                ],
            ),
            PatternRecognizer(
                supported_entity="ZA_PHONE_NUMBER",
                patterns=[
                    Pattern(
                        name="ZA_PHONE_NUMBER",
                        # Strictly expects 9 digits after the prefix, ignoring spaces/hyphens.
                        regex=r"(?<!\d)(?:\+27|27|0)(?:[\s\-]?\d){9}\b",
                        score=0.99,
                    )
                ],
            ),
            PatternRecognizer(
                supported_entity="ZA_PASSPORT_NUM",
                patterns=[
                    Pattern(
                        name="ZA_PASSPORT_NUM", regex=r"\b[ADMTadmt]\d{8}\b", score=0.99
                    )
                ],
            ),
            PatternRecognizer(
                supported_entity="ZA_VEHICLE_REG",
                patterns=[
                    Pattern(
                        name="ZA_VEHICLE_REG",
                        regex=r"\b(?:[B-DF-HJ-NP-TV-Z]{2}\s?\d{2}\s?[B-DF-HJ-NP-TV-Z]{2}(?:\s?GP)?|[A-Z]{3}\s?\d{3}\s?(?:EC|FS|L|MP|NC|NW|WP)|[A-Z]{1,3}\s?\d{1,6}(?:\s?ZN)?|[A-Z]{2}\s?\d{2}\s?[A-Z]{2}\s?ZN)\b",
                        score=0.99,
                    )
                ],
            ),
            PatternRecognizer(
                supported_entity="ZA_UIF_NUM",
                patterns=[Pattern(name="ZA_UIF_NUM", regex=r"\bU\d{9}\b", score=0.99)],
            ),
            PatternRecognizer(
                supported_entity="ZA_TAX_NUMBER",
                patterns=[
                    Pattern(name="ZA_TAX_NUMBER", regex=r"\b[0-39]\d{9}\b", score=0.99)
                ],
            ),
        ]

        for pattern in sa_patterns:
            self.analyzer.registry.add_recognizer(pattern)

    async def mask_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the input text for default PII entities and replaces them
        with standardized tokens.

        Returns: A dictionary containing the anonymized text and
                 the count of entities that were masked.
        """
        allowed_entities = [
            "PERSON",
            "EMAIL_ADDRESS",
            "URL",
            "IP_ADDRESS",
            "ZA_ID_NUMBER",
            "ZA_PHONE_NUMBER",
            "ZA_PASSPORT_NUM",
            "ZA_UIF_NUM",
            "ZA_TAX_NUMBER",
        ]

        if not text.strip():
            return {"anonymized_text": text, "entities_masked_count": 0}

        analysis_results = self.analyzer.analyze(
            text=text, language="en", entities=allowed_entities
        )

        sorted_results = sorted(analysis_results, key=lambda x: x.start, reverse=True)

        anonymized_text = text

        for match in sorted_results:
            original_value = text[match.start : match.end]

            # generate a unique token for each
            unique_id = uuid.uuid4().hex[:6]
            token_id = f"<{match.entity_type}_{unique_id}>"

            await self.vault.store_mapping(
                token_id=token_id, original_text=original_value
            )

            anonymized_text = (
                anonymized_text[: match.start] + token_id + anonymized_text[match.end :]
            )

        return {
            "anonymized_text": anonymized_text,
            "entities_masked_count": len(sorted_results),
        }
