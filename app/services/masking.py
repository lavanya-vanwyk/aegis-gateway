from typing import Dict, Any
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PrivacyMaskingService:
    def __init__(self):
        """
        Initializes the Presidio Analyzer and Anonymizer engines.
        The heavy spaCy language models are loaded into memory here once.
        """
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def mask_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the input text for default PII entities and replaces them 
        with standardized tokens.
            
        Returns: A dictionary containing the anonymized text and 
                 the count of entities that were masked.
        """
        if not text.strip():
            return {"anonymized_text": text, "entities_masked_count": 0}

        analysis_results = self.analyzer.analyze(text=text, language="en")

        anonymized_result = self.anonymizer.anonymize(
            text=text, 
            analyzer_results=analysis_results
        )

        return {
            "anonymized_text": anonymized_result.text,
            "entities_masked_count": len(analysis_results)
        }