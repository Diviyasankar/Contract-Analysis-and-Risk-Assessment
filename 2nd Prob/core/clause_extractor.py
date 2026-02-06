"""
Clause Extractor Module
Extracts and categorizes contract clauses with detailed analysis
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ExtractedClause:
    """Represents an extracted contract clause with analysis"""
    clause_id: str
    title: str
    content: str
    category: str
    risk_indicators: List[str] = field(default_factory=list)
    key_terms: List[str] = field(default_factory=list)
    amounts: List[str] = field(default_factory=list)
    dates: List[str] = field(default_factory=list)


class ClauseExtractor:
    """
    Extracts and categorizes clauses from contract documents
    """
    
    # Clause category patterns
    CLAUSE_CATEGORIES = {
        "payment": [
            "payment", "compensation", "salary", "fee", "price", "cost",
            "invoice", "billing", "remuneration"
        ],
        "termination": [
            "termination", "terminate", "cancel", "cancellation", "exit",
            "end of agreement", "expiry", "expire"
        ],
        "confidentiality": [
            "confidential", "confidentiality", "non-disclosure", "nda",
            "proprietary", "trade secret", "sensitive information"
        ],
        "liability": [
            "liability", "liable", "indemnify", "indemnification", "indemnity",
            "hold harmless", "defend", "damages"
        ],
        "intellectual_property": [
            "intellectual property", "ip", "patent", "copyright", "trademark",
            "invention", "work product", "proprietary rights"
        ],
        "non_compete": [
            "non-compete", "non compete", "compete", "competition",
            "competitive activity", "restraint of trade"
        ],
        "arbitration": [
            "arbitration", "dispute", "resolution", "mediation", "arbitrator"
        ],
        "jurisdiction": [
            "jurisdiction", "governing law", "venue", "court", "applicable law"
        ],
        "warranty": [
            "warranty", "warranties", "represent", "representation",
            "guarantee", "assurance"
        ],
        "force_majeure": [
            "force majeure", "act of god", "unforeseen", "beyond control",
            "natural disaster", "pandemic"
        ],
        "renewal": [
            "renewal", "renew", "auto-renew", "automatic renewal", "extension",
            "extend", "evergreen"
        ],
        "notice": [
            "notice", "notification", "notify", "inform", "written notice"
        ],
        "assignment": [
            "assignment", "assign", "transfer", "delegate", "succession"
        ],
        "amendment": [
            "amendment", "amend", "modify", "modification", "change"
        ],
        "definitions": [
            "definition", "defined", "means", "shall mean", "interpretation"
        ],
        "scope": [
            "scope", "services", "deliverables", "obligations", "responsibilities",
            "work", "duties"
        ]
    }
    
    # High-risk patterns
    HIGH_RISK_PATTERNS = {
        "unlimited_liability": [
            r"unlimited\s+liability",
            r"full\s+liability",
            r"liable\s+for\s+all\s+damages"
        ],
        "unilateral_termination": [
            r"(?:party\s+[ab12]|employer|company)\s+may\s+terminate\s+(?:at\s+any\s+time|without\s+cause|immediately)",
            r"sole\s+discretion.*terminat"
        ],
        "excessive_penalty": [
            r"penalty\s+of\s+(?:rs\.?|inr|₹)\s*[\d,]+",
            r"liquidated\s+damages.*(?:rs\.?|inr|₹)\s*[\d,]+"
        ],
        "broad_non_compete": [
            r"(?:worldwide|global|unlimited)\s+(?:non-compete|restriction)",
            r"non-compete.*(?:\d+\s+years|\d+\s+year\s+period)"
        ],
        "ip_assignment": [
            r"assign.*all.*(?:intellectual\s+property|ip|rights)",
            r"work.*for.*hire",
            r"transfer.*ownership.*(?:ip|intellectual)"
        ],
        "auto_renewal": [
            r"auto(?:matic)?(?:ally)?\s+renew",
            r"evergreen.*clause"
        ],
        "one_sided_indemnity": [
            r"(?:employee|contractor|vendor)\s+shall\s+indemnify",
            r"indemnify.*(?:company|employer).*all.*claims"
        ]
    }
    
    def __init__(self):
        self.clauses: List[ExtractedClause] = []
    
    def extract_clauses(self, text: str) -> List[ExtractedClause]:
        """
        Extract all clauses from contract text
        
        Args:
            text: Full contract text
            
        Returns:
            List of ExtractedClause objects
        """
        self.clauses = []
        
        # Multiple patterns for clause detection
        clause_patterns = [
            # Numbered clauses: 1., 1.1, 1.1.1, etc.
            r'(?:^|\n)\s*(\d+(?:\.\d+)*)\s*[\.:\)]\s*([A-Z][^\n]{0,100})',
            # Article/Section/Clause headers
            r'(?:^|\n)\s*(?:ARTICLE|Article|SECTION|Section|CLAUSE|Clause)\s*(\d+(?:\.\d+)?)[\.:\s]+([^\n]+)',
            # Roman numeral sections
            r'(?:^|\n)\s*([IVXLC]+)\s*[\.:\)]\s*([^\n]+)',
            # Lettered subsections: (a), (b), etc.
            r'(?:^|\n)\s*\(([a-z])\)\s*([^\n]+)',
        ]
        
        all_matches = []
        
        for pattern in clause_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
            for match in matches:
                all_matches.append({
                    "id": match.group(1),
                    "title": match.group(2).strip() if len(match.groups()) > 1 else "",
                    "start": match.start(),
                    "end": match.end()
                })
        
        # Sort by position
        all_matches.sort(key=lambda x: x["start"])
        
        # Extract content for each clause
        for i, match in enumerate(all_matches):
            start = match["end"]
            end = all_matches[i + 1]["start"] if i + 1 < len(all_matches) else len(text)
            content = text[start:end].strip()
            
            # Skip if content is too short
            if len(content) < 20:
                continue
            
            # Categorize the clause
            category = self._categorize_clause(match["title"], content)
            
            # Extract risk indicators
            risk_indicators = self._find_risk_indicators(content)
            
            # Extract key terms
            key_terms = self._extract_key_terms(content)
            
            # Extract amounts
            amounts = self._extract_amounts(content)
            
            # Extract dates
            dates = self._extract_dates(content)
            
            clause = ExtractedClause(
                clause_id=str(match["id"]),
                title=match["title"][:200],
                content=content[:2000],  # Limit content size
                category=category,
                risk_indicators=risk_indicators,
                key_terms=key_terms,
                amounts=amounts,
                dates=dates
            )
            
            self.clauses.append(clause)
        
        return self.clauses
    
    def _categorize_clause(self, title: str, content: str) -> str:
        """Determine the category of a clause based on title and content"""
        combined_text = (title + " " + content).lower()
        
        category_scores = {}
        
        for category, keywords in self.CLAUSE_CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "general"
    
    def _find_risk_indicators(self, content: str) -> List[str]:
        """Find high-risk patterns in clause content"""
        risk_indicators = []
        content_lower = content.lower()
        
        for risk_type, patterns in self.HIGH_RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    risk_indicators.append(risk_type)
                    break
        
        return list(set(risk_indicators))
    
    def _extract_key_terms(self, content: str) -> List[str]:
        """Extract important legal terms from clause"""
        legal_terms = [
            "shall", "must", "may", "will", "agrees", "warrants", "represents",
            "indemnify", "terminate", "liable", "confidential", "proprietary",
            "exclusive", "non-exclusive", "irrevocable", "perpetual"
        ]
        
        found_terms = []
        content_lower = content.lower()
        
        for term in legal_terms:
            if term in content_lower:
                found_terms.append(term)
        
        return found_terms[:10]
    
    def _extract_amounts(self, content: str) -> List[str]:
        """Extract monetary amounts from clause"""
        patterns = [
            r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?',
            r'\$\s*[\d,]+(?:\.\d{2})?',
            r'[\d,]+\s*(?:rupees|dollars|lakhs?|crores?)'
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            amounts.extend(matches)
        
        return amounts[:5]
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from clause"""
        patterns = [
            r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
            r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        
        return dates[:5]
    
    def extract_data_dimensions(self, text: str) -> Dict[str, Any]:
        """
        Extract all required data dimensions from the contract
        
        Returns:
            Dictionary with all extracted dimensions
        """
        dimensions = {
            "parties": [],
            "financial_amounts": [],
            "obligations": [],
            "liabilities": [],
            "deliverables": [],
            "timeline": [],
            "duration": None,
            "termination_conditions": [],
            "jurisdiction": None,
            "governing_law": None,
            "ip_rights": [],
            "confidentiality_terms": [],
            "nda_terms": []
        }
        
        # Extract parties
        party_patterns = [
            r'(?:between|BETWEEN)\s+(.+?)\s+(?:and|AND)\s+(.+?)(?:\.|,|\n)',
            r'(?:Party\s*[AB12])[:\s]+(.+?)(?:\n|,|\.)',
            r'(?:hereinafter.*(?:called|referred).*["\'](.+?)["\'])'
        ]
        
        for pattern in party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    dimensions["parties"].extend([m.strip() for m in match if m.strip()])
                else:
                    dimensions["parties"].append(match.strip())
        
        dimensions["parties"] = list(set(dimensions["parties"]))[:10]
        
        # Extract financial amounts
        amount_pattern = r'(?:Rs\.?|INR|₹|\$)\s*([\d,]+(?:\.\d{2})?)'
        dimensions["financial_amounts"] = re.findall(amount_pattern, text)[:20]
        
        # Extract duration
        duration_pattern = r'(?:term|period|duration)\s+(?:of\s+)?(\d+)\s+(years?|months?|days?)'
        duration_match = re.search(duration_pattern, text, re.IGNORECASE)
        if duration_match:
            dimensions["duration"] = f"{duration_match.group(1)} {duration_match.group(2)}"
        
        # Extract jurisdiction/governing law
        jurisdiction_pattern = r'(?:governed by|subject to|jurisdiction of)\s+(?:the\s+)?(?:laws?\s+of\s+)?([A-Za-z\s,]+)(?:\.|\n|$)'
        jurisdiction_match = re.search(jurisdiction_pattern, text, re.IGNORECASE)
        if jurisdiction_match:
            dimensions["jurisdiction"] = jurisdiction_match.group(1).strip()
            dimensions["governing_law"] = jurisdiction_match.group(1).strip()
        
        # Extract termination conditions
        termination_section = self._extract_section(text, ["termination", "terminate"])
        if termination_section:
            conditions = re.findall(r'(?:may\s+terminate|terminate.*(?:if|upon|when))(.+?)(?:\.|;|$)', 
                                    termination_section, re.IGNORECASE)
            dimensions["termination_conditions"] = [c.strip()[:200] for c in conditions[:5]]
        
        # Extract IP rights mentions
        ip_pattern = r'(?:intellectual\s+property|patent|copyright|trademark|invention)(.{0,200})'
        ip_matches = re.findall(ip_pattern, text, re.IGNORECASE)
        dimensions["ip_rights"] = [match.strip()[:200] for match in ip_matches[:5]]
        
        # Extract confidentiality terms
        conf_section = self._extract_section(text, ["confidential", "non-disclosure", "nda"])
        if conf_section:
            dimensions["confidentiality_terms"] = [conf_section[:500]]
        
        return dimensions
    
    def _extract_section(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extract a section of text containing specific keywords"""
        for keyword in keywords:
            pattern = rf'(?:^|\n)\s*(?:\d+(?:\.\d+)*\.?\s*)?[^\n]*{keyword}[^\n]*\n(.+?)(?=(?:^|\n)\s*\d+(?:\.\d+)*\.\s*[A-Z]|\Z)'
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                return match.group(0)[:1000]
        return None
    
    def get_clause_summary(self) -> Dict[str, int]:
        """Get summary of extracted clauses by category"""
        summary = {}
        for clause in self.clauses:
            category = clause.category
            summary[category] = summary.get(category, 0) + 1
        return summary


# Quick test
if __name__ == "__main__":
    extractor = ClauseExtractor()
    
    test_text = """
    1. DEFINITIONS
    In this Agreement, the following terms shall have the meanings set forth below.
    
    2. SCOPE OF SERVICES
    The Contractor shall provide software development services as described in Schedule A.
    
    3. PAYMENT TERMS
    3.1 The Client shall pay Rs. 5,00,000 upon signing this agreement.
    3.2 Subsequent payments of Rs. 2,50,000 shall be made monthly.
    
    4. CONFIDENTIALITY
    All information shared between parties shall be kept strictly confidential.
    The receiving party shall not disclose any proprietary information.
    
    5. TERMINATION
    Either party may terminate this agreement with 30 days written notice.
    The Company may terminate immediately for cause.
    
    6. JURISDICTION
    This agreement shall be governed by the laws of Karnataka, India.
    """
    
    clauses = extractor.extract_clauses(test_text)
    print(f"Extracted {len(clauses)} clauses:")
    for clause in clauses:
        print(f"  - {clause.clause_id}: {clause.title} [{clause.category}]")
        if clause.risk_indicators:
            print(f"    Risk: {clause.risk_indicators}")
