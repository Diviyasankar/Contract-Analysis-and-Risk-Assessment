"""
Contract Classifier Module
Classifies contracts into different types based on content analysis
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Result of contract classification"""
    contract_type: str
    confidence: float
    sub_type: str = ""
    key_indicators: List[str] = None
    
    def __post_init__(self):
        if self.key_indicators is None:
            self.key_indicators = []


class ContractClassifier:
    """
    Classifies contracts into predefined categories based on content analysis
    """
    
    # Contract type patterns and keywords
    CONTRACT_PATTERNS = {
        "Employment Agreement": {
            "keywords": [
                "employment", "employee", "employer", "salary", "compensation",
                "working hours", "leave", "provident fund", "gratuity", "probation",
                "termination of employment", "notice period", "designation", "job duties",
                "reporting", "workplace", "office hours"
            ],
            "patterns": [
                r"employment\s+agreement",
                r"contract\s+of\s+employment",
                r"letter\s+of\s+appointment",
                r"offer\s+letter",
                r"service\s+agreement.*employee"
            ],
            "sub_types": ["Full-time", "Part-time", "Fixed-term", "Probationary", "Executive"]
        },
        "Vendor Contract": {
            "keywords": [
                "vendor", "supplier", "purchase", "supply", "goods", "materials",
                "delivery", "invoice", "procurement", "quality", "specifications",
                "order", "consignment", "warranty on goods"
            ],
            "patterns": [
                r"vendor\s+agreement",
                r"supply\s+agreement",
                r"purchase\s+agreement",
                r"procurement\s+contract",
                r"supplier\s+contract"
            ],
            "sub_types": ["Supply Agreement", "Purchase Order", "Framework Agreement"]
        },
        "Lease Agreement": {
            "keywords": [
                "lease", "lessor", "lessee", "rent", "rental", "premises", "property",
                "tenant", "landlord", "security deposit", "maintenance", "occupancy",
                "possession", "eviction", "sub-lease", "monthly rent"
            ],
            "patterns": [
                r"lease\s+(?:agreement|deed)",
                r"rental\s+agreement",
                r"tenancy\s+agreement",
                r"leave\s+and\s+license",
                r"property\s+lease"
            ],
            "sub_types": ["Residential", "Commercial", "Industrial", "Leave and License"]
        },
        "Partnership Deed": {
            "keywords": [
                "partnership", "partner", "partners", "profit sharing", "capital contribution",
                "partnership firm", "mutual consent", "dissolution", "goodwill",
                "partner's share", "draw", "partnership act"
            ],
            "patterns": [
                r"partnership\s+deed",
                r"partnership\s+agreement",
                r"articles\s+of\s+partnership",
                r"(?:general|limited)\s+partnership"
            ],
            "sub_types": ["General Partnership", "Limited Partnership", "LLP"]
        },
        "Service Contract": {
            "keywords": [
                "services", "service provider", "client", "deliverables", "scope of work",
                "milestones", "project", "consultancy", "professional services",
                "statement of work", "sow", "service level", "sla"
            ],
            "patterns": [
                r"service\s+agreement",
                r"consulting\s+agreement",
                r"professional\s+services\s+agreement",
                r"master\s+service\s+agreement",
                r"statement\s+of\s+work"
            ],
            "sub_types": ["Consulting", "IT Services", "Professional Services", "Maintenance"]
        },
        "Non-Disclosure Agreement": {
            "keywords": [
                "confidential", "non-disclosure", "nda", "proprietary", "trade secret",
                "confidential information", "receiving party", "disclosing party",
                "sensitive information", "protect"
            ],
            "patterns": [
                r"non-disclosure\s+agreement",
                r"confidentiality\s+agreement",
                r"\bnda\b",
                r"mutual\s+(?:non-disclosure|confidentiality)"
            ],
            "sub_types": ["Mutual NDA", "One-way NDA", "Employee NDA"]
        },
        "Licensing Agreement": {
            "keywords": [
                "license", "licensor", "licensee", "royalty", "intellectual property",
                "trademark", "patent", "copyright", "sublicense", "territory",
                "exclusive", "non-exclusive", "usage rights"
            ],
            "patterns": [
                r"licens(?:e|ing)\s+agreement",
                r"software\s+license",
                r"trademark\s+license",
                r"patent\s+license",
                r"end\s+user\s+license"
            ],
            "sub_types": ["Software License", "IP License", "Franchise", "Technology License"]
        },
        "Sales Agreement": {
            "keywords": [
                "sale", "seller", "buyer", "purchaser", "purchase price", "goods",
                "transfer of ownership", "title", "delivery", "payment terms",
                "bill of sale", "consideration"
            ],
            "patterns": [
                r"sale\s+agreement",
                r"sale\s+deed",
                r"agreement\s+(?:for|of)\s+sale",
                r"purchase\s+and\s+sale"
            ],
            "sub_types": ["Asset Sale", "Share Sale", "Real Estate Sale", "Business Sale"]
        },
        "Loan Agreement": {
            "keywords": [
                "loan", "lender", "borrower", "principal", "interest", "repayment",
                "emi", "collateral", "security", "default", "disbursement",
                "promissory note", "mortgage"
            ],
            "patterns": [
                r"loan\s+agreement",
                r"credit\s+agreement",
                r"facility\s+agreement",
                r"promissory\s+note"
            ],
            "sub_types": ["Personal Loan", "Business Loan", "Mortgage", "Line of Credit"]
        },
        "Franchise Agreement": {
            "keywords": [
                "franchise", "franchisee", "franchisor", "brand", "trademark usage",
                "franchise fee", "royalty", "territory", "operational standards",
                "training", "marketing fund"
            ],
            "patterns": [
                r"franchise\s+agreement",
                r"franchising\s+agreement",
                r"master\s+franchise"
            ],
            "sub_types": ["Unit Franchise", "Master Franchise", "Area Development"]
        }
    }
    
    def __init__(self):
        self.result: ClassificationResult = None
    
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify the contract type based on content analysis
        
        Args:
            text: Full contract text
            
        Returns:
            ClassificationResult with type, confidence, and indicators
        """
        text_lower = text.lower()
        scores: Dict[str, Dict] = {}
        
        # Score each contract type
        for contract_type, type_info in self.CONTRACT_PATTERNS.items():
            score = 0
            matched_keywords = []
            
            # Check keywords
            for keyword in type_info["keywords"]:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    score += min(count, 5)  # Cap contribution per keyword
                    matched_keywords.append(keyword)
            
            # Check patterns (higher weight)
            for pattern in type_info["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 10
                    matched_keywords.append(f"[pattern: {pattern[:30]}...]")
            
            if score > 0:
                scores[contract_type] = {
                    "score": score,
                    "keywords": matched_keywords[:10]
                }
        
        if not scores:
            self.result = ClassificationResult(
                contract_type="Unknown",
                confidence=0.0,
                sub_type="",
                key_indicators=[]
            )
            return self.result
        
        # Find best match
        best_type = max(scores.keys(), key=lambda x: scores[x]["score"])
        best_score = scores[best_type]["score"]
        
        # Normalize confidence (0-1 scale)
        max_possible = len(self.CONTRACT_PATTERNS[best_type]["keywords"]) * 5 + \
                       len(self.CONTRACT_PATTERNS[best_type]["patterns"]) * 10
        confidence = min(1.0, best_score / (max_possible * 0.3))  # 30% of max is high confidence
        
        # Determine sub-type
        sub_type = self._determine_sub_type(text_lower, best_type)
        
        self.result = ClassificationResult(
            contract_type=best_type,
            confidence=round(confidence, 2),
            sub_type=sub_type,
            key_indicators=scores[best_type]["keywords"]
        )
        
        return self.result
    
    def _determine_sub_type(self, text_lower: str, contract_type: str) -> str:
        """Determine the sub-type of the contract"""
        type_info = self.CONTRACT_PATTERNS.get(contract_type, {})
        sub_types = type_info.get("sub_types", [])
        
        for sub_type in sub_types:
            if sub_type.lower() in text_lower:
                return sub_type
        
        # Special logic for certain types
        if contract_type == "Employment Agreement":
            if "probation" in text_lower:
                return "Probationary"
            elif "fixed term" in text_lower or "fixed-term" in text_lower:
                return "Fixed-term"
            elif "executive" in text_lower or "managing director" in text_lower:
                return "Executive"
            else:
                return "Full-time"
        
        elif contract_type == "Lease Agreement":
            if "residential" in text_lower or "house" in text_lower or "apartment" in text_lower:
                return "Residential"
            elif "commercial" in text_lower or "office" in text_lower or "shop" in text_lower:
                return "Commercial"
            elif "leave and license" in text_lower:
                return "Leave and License"
            else:
                return "Commercial"
        
        elif contract_type == "Non-Disclosure Agreement":
            if "mutual" in text_lower:
                return "Mutual NDA"
            else:
                return "One-way NDA"
        
        return sub_types[0] if sub_types else ""
    
    def get_classification_summary(self) -> str:
        """Get human-readable classification summary"""
        if not self.result:
            return "No classification performed yet."
        
        confidence_label = "High" if self.result.confidence >= 0.7 else \
                          "Medium" if self.result.confidence >= 0.4 else "Low"
        
        summary = f"Contract Type: {self.result.contract_type}"
        if self.result.sub_type:
            summary += f" ({self.result.sub_type})"
        summary += f"\nConfidence: {self.result.confidence:.0%} ({confidence_label})"
        
        if self.result.key_indicators:
            summary += f"\nKey Indicators: {', '.join(self.result.key_indicators[:5])}"
        
        return summary
    
    def get_all_scores(self, text: str) -> List[Tuple[str, float]]:
        """
        Get classification scores for all contract types
        
        Returns:
            List of (contract_type, score) tuples, sorted by score
        """
        text_lower = text.lower()
        scores = []
        
        for contract_type, type_info in self.CONTRACT_PATTERNS.items():
            score = 0
            
            for keyword in type_info["keywords"]:
                if keyword.lower() in text_lower:
                    score += 1
            
            for pattern in type_info["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 5
            
            if score > 0:
                scores.append((contract_type, score))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)


# Quick test
if __name__ == "__main__":
    classifier = ContractClassifier()
    
    test_contracts = {
        "employment": """
        EMPLOYMENT AGREEMENT
        This Employment Agreement is made between ABC Corporation (Employer) and 
        John Doe (Employee). The Employee shall work as Software Engineer with 
        a monthly salary of Rs. 80,000. The probation period shall be 6 months.
        Working hours: 9 AM to 6 PM. Annual leave: 24 days.
        """,
        
        "nda": """
        NON-DISCLOSURE AGREEMENT
        This Mutual Non-Disclosure Agreement is entered between Party A and Party B.
        Both parties agree to protect confidential information shared during discussions.
        Trade secrets and proprietary information shall remain confidential for 5 years.
        """,
        
        "service": """
        MASTER SERVICE AGREEMENT
        This Service Agreement is between XYZ Consulting (Service Provider) and 
        Client Corp (Client). The scope of work includes software development services.
        Deliverables as per Statement of Work attached. Service levels as per SLA.
        """
    }
    
    for name, text in test_contracts.items():
        result = classifier.classify(text)
        print(f"\n{'='*50}")
        print(f"Test: {name.upper()}")
        print(f"{'='*50}")
        print(classifier.get_classification_summary())
