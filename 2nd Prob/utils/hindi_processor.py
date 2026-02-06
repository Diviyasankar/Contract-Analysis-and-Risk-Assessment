"""
Hindi Processor Module
Handles Hindi language detection, translation, and normalization
"""

import re
from typing import Tuple, Optional


class HindiProcessor:
    """
    Processes Hindi text in contracts for analysis
    """
    
    # Common Hindi legal terms with English equivalents
    HINDI_LEGAL_TERMS = {
        "अनुबंध": "contract/agreement",
        "करार": "agreement",
        "पक्षकार": "party",
        "प्रथम पक्ष": "first party",
        "द्वितीय पक्ष": "second party",
        "साक्षी": "witness",
        "गवाह": "witness",
        "शर्तें": "terms and conditions",
        "नियम": "rules/terms",
        "दायित्व": "liability/obligation",
        "जिम्मेदारी": "responsibility",
        "क्षतिपूर्ति": "indemnity/compensation",
        "हर्जाना": "damages",
        "समाप्ति": "termination",
        "रद्द": "cancellation",
        "नवीनीकरण": "renewal",
        "अवधि": "duration/term",
        "भुगतान": "payment",
        "राशि": "amount",
        "रुपये": "rupees",
        "वेतन": "salary",
        "मजदूरी": "wages",
        "गोपनीयता": "confidentiality",
        "गुप्त": "secret/confidential",
        "विवाद": "dispute",
        "मध्यस्थता": "arbitration",
        "न्यायालय": "court",
        "क्षेत्राधिकार": "jurisdiction",
        "कानून": "law",
        "अधिनियम": "act/statute",
        "धारा": "section",
        "उपधारा": "sub-section",
        "अनुसूची": "schedule",
        "परिशिष्ट": "appendix",
        "हस्ताक्षर": "signature",
        "मुहर": "seal/stamp",
        "तारीख": "date",
        "दिनांक": "date",
        "प्रभावी": "effective",
        "बाध्यकारी": "binding",
        "वैध": "valid",
        "अमान्य": "invalid/void",
        "स्वामित्व": "ownership",
        "अधिकार": "rights",
        "हस्तांतरण": "transfer",
        "लाइसेंस": "license",
        "पट्टा": "lease",
        "किराया": "rent",
        "जमानत": "security/guarantee",
        "प्रतिभूति": "security",
        "बंधक": "mortgage",
        "ऋण": "loan",
        "ब्याज": "interest",
        "मूलधन": "principal",
        "चूक": "default",
        "उल्लंघन": "breach/violation",
        "बल मज़ूर": "force majeure",
        "अप्रत्याशित": "unforeseen"
    }
    
    # Hindi numerals
    HINDI_NUMERALS = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    
    def __init__(self):
        self.translator = None
        self._init_translator()
    
    def _init_translator(self):
        """Initialize translator (googletrans as fallback)"""
        try:
            from googletrans import Translator
            self.translator = Translator()
        except ImportError:
            self.translator = None
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect if text is primarily Hindi or English
        
        Returns:
            Tuple of (language_code, confidence)
            language_code: 'hi' for Hindi, 'en' for English, 'mixed' for bilingual
        """
        if not text:
            return ("en", 1.0)
        
        # Count Devanagari characters
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        hindi_chars = len(hindi_pattern.findall(text))
        
        # Count ASCII letters
        english_pattern = re.compile(r'[a-zA-Z]')
        english_chars = len(english_pattern.findall(text))
        
        total = hindi_chars + english_chars
        if total == 0:
            return ("en", 0.5)
        
        hindi_ratio = hindi_chars / total
        
        if hindi_ratio > 0.7:
            return ("hi", hindi_ratio)
        elif hindi_ratio > 0.2:
            return ("mixed", 0.5)
        else:
            return ("en", 1 - hindi_ratio)
    
    def is_hindi(self, text: str) -> bool:
        """Check if text contains significant Hindi content"""
        lang, conf = self.detect_language(text)
        return lang in ["hi", "mixed"]
    
    def normalize_numerals(self, text: str) -> str:
        """Convert Hindi numerals to Arabic numerals"""
        for hindi, arabic in self.HINDI_NUMERALS.items():
            text = text.replace(hindi, arabic)
        return text
    
    def extract_hindi_terms(self, text: str) -> dict:
        """
        Extract recognized Hindi legal terms and their meanings
        
        Returns:
            Dictionary of found terms and their English meanings
        """
        found_terms = {}
        
        for hindi_term, english_meaning in self.HINDI_LEGAL_TERMS.items():
            if hindi_term in text:
                found_terms[hindi_term] = english_meaning
        
        return found_terms
    
    def translate_to_english(self, text: str) -> Tuple[str, bool]:
        """
        Translate Hindi text to English
        
        Returns:
            Tuple of (translated_text, success)
        """
        if not text.strip():
            return ("", True)
        
        # Check if translation is needed
        lang, _ = self.detect_language(text)
        if lang == "en":
            return (text, True)
        
        # Normalize numerals first
        text = self.normalize_numerals(text)
        
        # Try Google Translate
        if self.translator:
            try:
                result = self.translator.translate(text, src='hi', dest='en')
                return (result.text, True)
            except Exception as e:
                print(f"Translation error: {e}")
        
        # Fallback: Return original with term annotations
        terms = self.extract_hindi_terms(text)
        if terms:
            annotations = "\n\n[Hindi Terms Found:\n"
            for hindi, english in terms.items():
                annotations += f"  - {hindi}: {english}\n"
            annotations += "]"
            return (text + annotations, False)
        
        return (text, False)
    
    def prepare_for_nlp(self, text: str) -> str:
        """
        Prepare Hindi/mixed text for NLP processing
        
        This normalizes the text for better processing by:
        1. Converting Hindi numerals
        2. Translating if possible
        3. Preserving structure
        
        Returns:
            Normalized text suitable for NLP
        """
        # Normalize numerals
        text = self.normalize_numerals(text)
        
        # Check language
        lang, conf = self.detect_language(text)
        
        if lang == "en":
            return text
        
        # For mixed text, try to translate Hindi portions
        if lang in ["hi", "mixed"]:
            translated, success = self.translate_to_english(text)
            if success:
                return translated
        
        return text
    
    def get_bilingual_summary(self, text: str) -> dict:
        """
        Get summary information about bilingual content
        
        Returns:
            Dictionary with language analysis
        """
        lang, conf = self.detect_language(text)
        terms = self.extract_hindi_terms(text)
        
        # Count words in each script
        hindi_words = len(re.findall(r'[\u0900-\u097F]+', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        return {
            "primary_language": lang,
            "confidence": conf,
            "hindi_word_count": hindi_words,
            "english_word_count": english_words,
            "total_words": hindi_words + english_words,
            "hindi_legal_terms_found": len(terms),
            "legal_terms": terms
        }


# Quick test
if __name__ == "__main__":
    processor = HindiProcessor()
    
    print("Hindi Processor Module")
    print("=" * 50)
    
    # Test with Hindi text
    hindi_text = "यह अनुबंध प्रथम पक्ष और द्वितीय पक्ष के बीच है। भुगतान राशि ₹५०,००० है।"
    
    print(f"\nTest text: {hindi_text}")
    
    lang, conf = processor.detect_language(hindi_text)
    print(f"Language: {lang} (confidence: {conf:.2f})")
    
    terms = processor.extract_hindi_terms(hindi_text)
    print(f"Legal terms found: {len(terms)}")
    for hindi, english in terms.items():
        print(f"  - {hindi}: {english}")
    
    normalized = processor.normalize_numerals(hindi_text)
    print(f"\nNormalized: {normalized}")
