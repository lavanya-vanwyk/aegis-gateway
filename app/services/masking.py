from typing import Dict, Any
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine

class PrivacyMaskingService:
    def __init__(self):
        """
        Initializes the Presidio Analyzer and Anonymizer engines.
        The heavy spaCy language models are loaded into memory here once.

        US_BANK_NUMBER trips the ZA_ID check, and is removed for the 
        purposes of this masker
        """
        

        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def south_african_pii_recognizer(self):
        """
        Method that adds custom regex rules for South African PII like ID numbers,
        passport numbers, South African mobile numbers, vehicle registrations, and SARS UIF
        numbers

        """
        sa_patterns = [
            PatternRecognizer(
                supported_entity="ZA_ID_NUMBER",
                patterns=[Pattern(name="ZA_ID_NUMBER",regex=r"(([0-9]{2})(0|1)([0-9])([0-3])([0-9]))([ ]?)(([0-9]{4})([ ]?)([0-1][8]([ ]?)[0-9]))",score=0.99)]
                ),
            PatternRecognizer(
                supported_entity="ZA_PHONE_NUMBER",
                patterns=[Pattern(name="ZA_PHONE_NUMBER", regex=r"^(\+27|0)[6-8][1-5|8-9][0-9]{7}$", score=0.99)]
            ),
            PatternRecognizer(
                supported_entity="ZA_PASSPORT_NUM",
                patterns=[Pattern(name="ZA_PASSPORT_NUM", regex=r"^[ADMTadmt]\d{8}$", score=0.99)]
            ),
            
            PatternRecognizer(
                supported_entity="ZA_VEHICLE_REG",
                patterns=[Pattern(name="ZA_VEHICLE_REG", regex=r"^(?:[B-DF-HJ-NP-TV-Z]{2}\s?\d{2}\s?[B-DF-HJ-NP-TV-Z]{2}(?:\s?GP)?|[A-Z]{3}\s?\d{3}\s?(?:EC|FS|L|MP|NC|NW|WP)|[A-Z]{1,3}\s?\d{1,6}(?:\s?ZN)?|[A-Z]{2}\s?\d{2}\s?[A-Z]{2}\s?ZN|[A-Z0-9]{1,7}\s?(?:GP|EC|FS|L|MP|NC|NW|WP|ZN))$", score=0.99)]
            ),
            PatternRecognizer(
                supported_entity="ZA_UIF_NUM",
                patterns=[Pattern(name="ZA_UIF_NUM", regex=r"^U\d{9}$", score=0.99)]
            )
            ]
        for pattern in sa_patterns:
            self.analyzer.registry.add_recognizer(pattern)

    def mask_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the input text for default PII entities and replaces them 
        with standardized tokens.
            
        Returns: A dictionary containing the anonymized text and 
                 the count of entities that were masked.
        """
        allowed_entities = [
        "PERSON", "EMAIL_ADDRESS", "URL", "IP_ADDRESS",
        "ZA_ID_NUMBER", "ZA_PHONE_NUMBER", "ZA_PASSPORT_NUM", "ZA_UIF_NUM"
        ]

        
        if not text.strip():
            return {"anonymized_text": text, "entities_masked_count": 0}

        analysis_results = self.analyzer.analyze(
        text=text, 
        language="en",
        entities=allowed_entities 
        )

        anonymized_result = self.anonymizer.anonymize(
            text=text, 
            analyzer_results=analysis_results
        )

        return {
            "anonymized_text": anonymized_result.text,
            "entities_masked_count": len(analysis_results)
        }
    
    