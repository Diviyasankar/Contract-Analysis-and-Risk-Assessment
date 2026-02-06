"""
NLP Pipeline Module
Handles tokenization, NER, and linguistic analysis using spaCy and NLTK
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Try to import spaCy
try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Try to import NLTK
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


@dataclass
class Entity:
    """Represents a named entity extracted from text"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class Clause:
    """Represents a contract clause"""
    id: str
    text: str
    clause_type: str
    entities: List[Entity]
    obligations: List[str]
    rights: List[str]
    prohibitions: List[str]


class NLPPipeline:
    """
    NLP processing pipeline for contract analysis
    """
    
    # Legal entity patterns
    LEGAL_PATTERNS = {
        "party": [
            r'(?:hereinafter|hereafter)?\s*(?:referred to as|called)\s*["\']?([A-Za-z\s]+)["\']?',
            r'(?:Party|PARTY)\s*(?:A|B|1|2|One|Two|First|Second)[:\s]+([A-Za-z\s\.]+)',
            r'(?:between|BETWEEN)\s+([A-Za-z\s\.]+)\s+(?:and|AND)',
        ],
        "date": [
            r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b',
            r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4})\b',
            r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
        ],
        "amount": [
            r'(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)',
            r'(?:\$|USD)\s*([\d,]+(?:\.\d{2})?)',
            r'([\d,]+(?:\.\d{2})?)\s*(?:Rupees|rupees|dollars|Dollars)',
        ],
        "duration": [
            r'(\d+)\s*(?:years?|months?|days?|weeks?)',
            r'(?:period of|term of)\s+(\d+)\s*(?:years?|months?|days?)',
        ],
        "jurisdiction": [
            r'(?:courts? of|jurisdiction of|governed by.*laws? of)\s+([A-Za-z\s]+)',
            r'(?:subject to.*jurisdiction.*of)\s+([A-Za-z\s]+)',
        ]
    }
    
    # Obligation/Right/Prohibition indicators
    OBLIGATION_KEYWORDS = [
        "shall", "must", "will", "agrees to", "undertakes to", "obligated to",
        "required to", "is responsible for", "covenant to"
    ]
    
    RIGHT_KEYWORDS = [
        "may", "can", "is entitled to", "has the right to", "reserves the right",
        "at its option", "at its discretion", "permitted to"
    ]
    
    PROHIBITION_KEYWORDS = [
        "shall not", "must not", "may not", "cannot", "will not", "prohibited from",
        "restricted from", "is not allowed to", "is forbidden to"
    ]
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize NLP pipeline
        
        Args:
            use_spacy: Whether to use spaCy (recommended) or fall back to NLTK
        """
        self.nlp = None
        self.use_spacy = use_spacy
        
        if use_spacy and SPACY_AVAILABLE:
            try:
                # Try to load the English model
                self.nlp = spacy.load("en_core_web_sm")
                print("spaCy model loaded successfully")
            except OSError:
                print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
                self.use_spacy = False
        
        if not self.use_spacy and NLTK_AVAILABLE:
            # Download required NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger', quiet=True)
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text through the NLP pipeline
        
        Returns:
            Dictionary with entities, clauses, and analysis results
        """
        result = {
            "entities": [],
            "sentences": [],
            "clauses": [],
            "parties": [],
            "dates": [],
            "amounts": [],
            "obligations": [],
            "rights": [],
            "prohibitions": []
        }
        
        # Extract sentences
        result["sentences"] = self._extract_sentences(text)
        
        # Extract named entities
        result["entities"] = self._extract_entities(text)
        
        # Extract legal-specific entities using patterns
        result["parties"] = self._extract_parties(text)
        result["dates"] = self._extract_dates(text)
        result["amounts"] = self._extract_amounts(text)
        
        # Classify sentence intent (obligation/right/prohibition)
        for sentence in result["sentences"]:
            classification = self._classify_sentence_intent(sentence)
            if classification["type"] == "obligation":
                result["obligations"].append(sentence)
            elif classification["type"] == "right":
                result["rights"].append(sentence)
            elif classification["type"] == "prohibition":
                result["prohibitions"].append(sentence)
        
        return result
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        if self.use_spacy and self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        elif NLTK_AVAILABLE:
            return sent_tokenize(text)
        else:
            # Simple fallback
            return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities using spaCy"""
        entities = []
        
        if self.use_spacy and self.nlp:
            doc = self.nlp(text[:100000])  # Limit for performance
            for ent in doc.ents:
                entities.append(Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char
                ))
        
        return entities
    
    def _extract_parties(self, text: str) -> List[str]:
        """Extract party names from contract"""
        parties = set()
        
        for pattern in self.LEGAL_PATTERNS["party"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                cleaned = match.strip().strip('"\'')
                if len(cleaned) > 2 and len(cleaned) < 100:
                    parties.add(cleaned)
        
        # Also extract from spaCy ORG entities
        if self.use_spacy and self.nlp:
            doc = self.nlp(text[:50000])
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PERSON"]:
                    parties.add(ent.text)
        
        return list(parties)[:10]  # Limit to top 10
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from contract"""
        dates = []
        
        for pattern in self.LEGAL_PATTERNS["date"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))[:20]  # Limit and dedupe
    
    def _extract_amounts(self, text: str) -> List[Dict[str, str]]:
        """Extract monetary amounts from contract"""
        amounts = []
        
        for pattern in self.LEGAL_PATTERNS["amount"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amounts.append({
                    "value": match.group(1) if match.groups() else match.group(),
                    "context": text[max(0, match.start()-50):match.end()+50]
                })
        
        return amounts[:30]  # Limit
    
    def _classify_sentence_intent(self, sentence: str) -> Dict[str, Any]:
        """
        Classify sentence as obligation, right, or prohibition
        
        Returns:
            Dictionary with type and confidence
        """
        sentence_lower = sentence.lower()
        
        # Check prohibitions first (they often contain obligation words)
        for keyword in self.PROHIBITION_KEYWORDS:
            if keyword in sentence_lower:
                return {"type": "prohibition", "confidence": 0.9, "keyword": keyword}
        
        # Check obligations
        for keyword in self.OBLIGATION_KEYWORDS:
            if keyword in sentence_lower:
                return {"type": "obligation", "confidence": 0.85, "keyword": keyword}
        
        # Check rights
        for keyword in self.RIGHT_KEYWORDS:
            if keyword in sentence_lower:
                return {"type": "right", "confidence": 0.85, "keyword": keyword}
        
        return {"type": "neutral", "confidence": 0.5, "keyword": None}
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract and parse individual clauses from contract
        
        Returns:
            List of clause dictionaries
        """
        clauses = []
        
        # Pattern for clause headers
        clause_pattern = r'(?:^|\n)\s*(\d+(?:\.\d+)*)\s*[\.:\)]\s*([^\n]+)'
        
        matches = list(re.finditer(clause_pattern, text))
        
        for i, match in enumerate(matches):
            clause_num = match.group(1)
            clause_title = match.group(2).strip()
            
            # Get clause content (until next clause or end)
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            
            # Analyze the clause
            clause_analysis = self.process(content)
            
            clauses.append({
                "number": clause_num,
                "title": clause_title,
                "content": content[:1000],  # Limit content length
                "entities": clause_analysis["entities"][:5],
                "obligations": clause_analysis["obligations"][:3],
                "rights": clause_analysis["rights"][:3],
                "prohibitions": clause_analysis["prohibitions"][:3]
            })
        
        return clauses
    
    def get_key_terms(self, text: str, top_n: int = 20) -> List[str]:
        """
        Extract key legal terms from the document
        
        Returns:
            List of important terms
        """
        # Legal keywords to look for
        legal_terms = [
            "indemnify", "liability", "termination", "confidential", "proprietary",
            "arbitration", "jurisdiction", "warranty", "breach", "damages",
            "force majeure", "assignment", "notice", "amendment", "waiver",
            "governing law", "intellectual property", "non-compete", "non-disclosure",
            "severability", "entire agreement", "counterparts"
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in legal_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms


# Quick test
if __name__ == "__main__":
    pipeline = NLPPipeline()
    print(f"NLP Pipeline initialized. spaCy available: {SPACY_AVAILABLE}, NLTK available: {NLTK_AVAILABLE}")
    
    test_text = """
    This Agreement is entered into between ABC Company (hereinafter referred to as "Employer")
    and John Doe (hereinafter referred to as "Employee") on January 15, 2024.
    
    The Employee shall perform their duties diligently and may not engage in competing business.
    The Employer will pay Rs. 50,000 per month as salary.
    """
    
    result = pipeline.process(test_text)
    print(f"\nParties found: {result['parties']}")
    print(f"Dates found: {result['dates']}")
    print(f"Amounts found: {result['amounts']}")
    print(f"Obligations: {len(result['obligations'])}")
    print(f"Prohibitions: {len(result['prohibitions'])}")
