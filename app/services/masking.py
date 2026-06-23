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

