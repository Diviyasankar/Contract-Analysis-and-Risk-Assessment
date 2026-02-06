"""
Risk Assessor Module
Comprehensive risk scoring and analysis for contract clauses
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskFinding:
    """Represents a single risk finding in the contract"""
    clause_id: str
    risk_type: str
    risk_level: RiskLevel
    score: float  # 1-10
    description: str
    original_text: str
    suggestion: str = ""
    indian_law_reference: str = ""


@dataclass
class RiskReport:
    """Complete risk assessment report for a contract"""
    overall_score: float
    overall_level: RiskLevel
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    findings: List[RiskFinding] = field(default_factory=list)
    summary: str = ""


class RiskAssessor:
    """
    Comprehensive risk assessment engine for contracts
    """
    
    # Risk scoring weights
    RISK_WEIGHTS = {
        "unlimited_liability": 9,
        "one_sided_indemnity": 8,
        "unilateral_termination": 8,
        "ip_full_transfer": 8,
        "broad_non_compete": 7,
        "excessive_penalty": 7,
        "auto_renewal_hidden": 6,
        "unfavorable_jurisdiction": 6,
        "vague_termination": 5,
        "missing_liability_cap": 5,
        "missing_notice_period": 4,
        "ambiguous_deliverables": 4,
        "missing_dispute_resolution": 4,
        "unclear_payment_terms": 3,
        "missing_confidentiality": 3
    }
    
    # Risk detection patterns
    RISK_PATTERNS = {
        "unlimited_liability": {
            "patterns": [
                r"unlimited\s+liability",
                r"liable\s+for\s+all\s+(?:damages|losses|claims)",
                r"full\s+liability\s+for",
                r"no\s+limitation\s+(?:on|of)\s+liability"
            ],
            "description": "Unlimited liability exposure",
            "suggestion": "Negotiate a liability cap (typically 12 months of fees or specific amount)",
            "indian_law": "Indian Contract Act, Section 73-74 allows for reasonable limitation"
        },
        "one_sided_indemnity": {
            "patterns": [
                r"(?:vendor|contractor|employee|consultant)\s+shall\s+(?:fully\s+)?indemnify",
                r"indemnify\s+(?:and\s+hold\s+harmless\s+)?(?:the\s+)?(?:company|employer|client)",
                r"defend\s+(?:and\s+)?indemnify.*(?:all|any)\s+claims"
            ],
            "description": "One-sided indemnification favoring the other party",
            "suggestion": "Request mutual indemnification or limit indemnity scope",
            "indian_law": "Should be mutual per fair contract principles"
        },
        "unilateral_termination": {
            "patterns": [
                r"(?:company|employer|client)\s+may\s+terminate\s+(?:at\s+any\s+time|without\s+cause|immediately|forthwith)",
                r"terminate\s+(?:this\s+agreement\s+)?at\s+(?:its?\s+)?sole\s+discretion",
                r"reserved?\s+(?:the\s+)?right\s+to\s+terminate\s+without"
            ],
            "description": "Only one party can terminate without cause",
            "suggestion": "Ensure mutual termination rights with reasonable notice period",
            "indian_law": "Indian Contract Act requires reasonable opportunity to cure"
        },
        "ip_full_transfer": {
            "patterns": [
                r"assign(?:s|ed)?\s+all\s+(?:right|title|interest).*(?:intellectual\s+property|ip|work\s+product)",
                r"work(?:s)?\s+(?:made\s+)?for\s+hire",
                r"(?:all|any)\s+(?:inventions?|creations?|developments?).*(?:belong|vest|transfer).*(?:company|employer)",
                r"irrevocable.*(?:license|assignment|transfer).*(?:ip|intellectual)"
            ],
            "description": "Complete transfer of intellectual property rights",
            "suggestion": "Negotiate to retain rights to pre-existing IP and general knowledge",
            "indian_law": "Copyright Act, 1957 - Assignment should be in writing and specific"
        },
        "broad_non_compete": {
            "patterns": [
                r"(?:shall\s+)?not\s+(?:directly\s+or\s+indirectly\s+)?(?:engage|work|compete).*(?:worldwide|global|any\s+(?:market|territory))",
                r"non-compete.*(?:[2-9]|[1-9]\d+)\s+years",
                r"restrain(?:ed|t)?\s+from\s+(?:engaging|working|competing).*(?:perpetual|indefinite)"
            ],
            "description": "Overly broad non-compete restrictions",
            "suggestion": "Limit geographic scope and duration (6-12 months is typical in India)",
            "indian_law": "Section 27 of Indian Contract Act - Restraint of trade is void unless reasonable"
        },
        "excessive_penalty": {
            "patterns": [
                r"(?:penalty|liquidated\s+damages)\s+(?:of|equal\s+to)\s+(?:rs\.?|inr|₹)\s*(?:[5-9]\d{5,}|[1-9]\d{6,})",
                r"forfeit.*(?:entire|full|all).*(?:amount|fee|payment)",
                r"penalty.*(?:double|triple|twice|thrice)"
            ],
            "description": "Potentially excessive penalty clauses",
            "suggestion": "Negotiate reasonable and proportionate penalties",
            "indian_law": "Section 74 of Indian Contract Act - Only reasonable compensation is recoverable"
        },
        "auto_renewal_hidden": {
            "patterns": [
                r"(?:automatically|auto)\s+renew(?:ed|s)?",
                r"shall\s+(?:continue|renew)\s+(?:for|unless).*(?:notice|terminated)",
                r"evergreen\s+(?:clause|term|provision)"
            ],
            "description": "Automatic renewal clause that may lock you in",
            "suggestion": "Add clear opt-out mechanism with reasonable notice period",
            "indian_law": "Consumer Protection Act, 2019 requires clear disclosure"
        },
        "unfavorable_jurisdiction": {
            "patterns": [
                r"(?:exclusive\s+)?jurisdiction\s+(?:of|in)\s+(?:courts?\s+(?:of|in)\s+)?(?:london|new\s+york|singapore|hong\s+kong|us|uk|england)",
                r"governed\s+by.*(?:laws?\s+of\s+)?(?:england|new\s+york|singapore|delaware)"
            ],
            "description": "Foreign jurisdiction may be costly and inconvenient",
            "suggestion": "Negotiate for local Indian jurisdiction (preferably your state)",
            "indian_law": "Indian courts should have jurisdiction for domestic parties"
        },
        "vague_termination": {
            "patterns": [
                r"terminate.*(?:any\s+reason|no\s+reason|whatsoever)",
                r"(?:at\s+will|without\s+cause).*terminat"
            ],
            "description": "Vague termination grounds without proper process",
            "suggestion": "Define specific grounds for termination and cure periods",
            "indian_law": "Industrial Disputes Act requires proper process for employment termination"
        },
        "missing_liability_cap": {
            "patterns": [
                r"(?:no|without)\s+(?:limitation|cap|ceiling)\s+(?:on|of)\s+(?:liability|damages)"
            ],
            "description": "No cap on liability exposure",
            "suggestion": "Include liability cap (e.g., total fees paid in last 12 months)",
            "indian_law": "Parties can contractually limit liability under Indian Contract Act"
        }
    }
    
    # Indian law compliance checks
    INDIAN_LAW_COMPLIANCE = {
        "stamp_duty": "Contract may require stamp duty as per Indian Stamp Act",
        "registration": "Lease agreements over 11 months require registration",
        "tds_applicability": "Check TDS applicability under Income Tax Act",
        "gst_compliance": "Verify GST obligations for services",
        "fema_compliance": "Foreign payments may require FEMA compliance",
        "it_act_compliance": "Electronic contracts must comply with IT Act 2000"
    }
    
    def __init__(self):
        self.findings: List[RiskFinding] = []
        self.overall_score = 0.0
    
    def assess_contract(self, text: str, clauses: List[Dict] = None) -> RiskReport:
        """
        Perform comprehensive risk assessment on the contract
        
        Args:
            text: Full contract text
            clauses: Optional list of pre-extracted clauses
            
        Returns:
            RiskReport with all findings
        """
        self.findings = []
        
        # Analyze full text for risk patterns
        self._analyze_text_risks(text)
        
        # Analyze individual clauses if provided
        if clauses:
            for clause in clauses:
                self._analyze_clause_risks(clause)
        
        # Check for missing important clauses
        self._check_missing_protections(text)
        
        # Calculate overall score
        report = self._calculate_overall_score()
        
        return report
    
    def _analyze_text_risks(self, text: str):
        """Analyze full text for risk patterns"""
        text_lower = text.lower()
        
        for risk_type, risk_info in self.RISK_PATTERNS.items():
            for pattern in risk_info["patterns"]:
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                for match in matches:
                    # Get surrounding context (100 chars before and after)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]
                    
                    # Create finding
                    score = self.RISK_WEIGHTS.get(risk_type, 5)
                    level = self._score_to_level(score)
                    
                    finding = RiskFinding(
                        clause_id="general",
                        risk_type=risk_type.replace("_", " ").title(),
                        risk_level=level,
                        score=score,
                        description=risk_info["description"],
                        original_text=context.strip(),
                        suggestion=risk_info["suggestion"],
                        indian_law_reference=risk_info.get("indian_law", "")
                    )
                    
                    # Avoid duplicate findings for same risk type
                    if not any(f.risk_type == finding.risk_type and f.original_text == finding.original_text 
                               for f in self.findings):
                        self.findings.append(finding)
    
    def _analyze_clause_risks(self, clause: Dict):
        """Analyze a specific clause for risks"""
        content = clause.get("content", "")
        clause_id = clause.get("clause_id", clause.get("number", "unknown"))
        
        # Check for risk indicators already extracted
        risk_indicators = clause.get("risk_indicators", [])
        
        for indicator in risk_indicators:
            if indicator in self.RISK_WEIGHTS:
                score = self.RISK_WEIGHTS[indicator]
                risk_info = self.RISK_PATTERNS.get(indicator, {})
                
                finding = RiskFinding(
                    clause_id=str(clause_id),
                    risk_type=indicator.replace("_", " ").title(),
                    risk_level=self._score_to_level(score),
                    score=score,
                    description=risk_info.get("description", indicator),
                    original_text=content[:200],
                    suggestion=risk_info.get("suggestion", ""),
                    indian_law_reference=risk_info.get("indian_law", "")
                )
                
                if not any(f.clause_id == finding.clause_id and f.risk_type == finding.risk_type 
                           for f in self.findings):
                    self.findings.append(finding)
    
    def _check_missing_protections(self, text: str):
        """Check for missing important protective clauses"""
        text_lower = text.lower()
        
        missing_checks = {
            "liability_cap": {
                "check": ["limitation of liability", "liability cap", "liability shall not exceed", "maximum liability"],
                "description": "Missing liability limitation clause",
                "suggestion": "Add a clause capping total liability exposure",
                "score": 5
            },
            "dispute_resolution": {
                "check": ["arbitration", "dispute resolution", "mediation", "conciliation"],
                "description": "Missing dispute resolution mechanism",
                "suggestion": "Include arbitration clause as per Arbitration and Conciliation Act, 1996",
                "score": 4
            },
            "notice_period": {
                "check": ["notice period", "days notice", "written notice", "prior notice"],
                "description": "Missing or unclear notice period requirements",
                "suggestion": "Specify clear notice periods for termination and other actions",
                "score": 4
            },
            "force_majeure": {
                "check": ["force majeure", "act of god", "unforeseen circumstances"],
                "description": "Missing force majeure clause",
                "suggestion": "Add force majeure clause to protect against unforeseen events",
                "score": 3
            },
            "confidentiality": {
                "check": ["confidential", "non-disclosure", "proprietary information", "trade secret"],
                "description": "Missing confidentiality provisions",
                "suggestion": "Include mutual confidentiality obligations",
                "score": 3
            }
        }
        
        for check_type, check_info in missing_checks.items():
            found = any(keyword in text_lower for keyword in check_info["check"])
            
            if not found:
                finding = RiskFinding(
                    clause_id="missing",
                    risk_type=f"Missing {check_type.replace('_', ' ').title()}",
                    risk_level=self._score_to_level(check_info["score"]),
                    score=check_info["score"],
                    description=check_info["description"],
                    original_text="[Not found in contract]",
                    suggestion=check_info["suggestion"],
                    indian_law_reference=""
                )
                self.findings.append(finding)
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level"""
        if score >= 8:
            return RiskLevel.CRITICAL
        elif score >= 6:
            return RiskLevel.HIGH
        elif score >= 4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_overall_score(self) -> RiskReport:
        """Calculate overall risk score and generate report"""
        if not self.findings:
            return RiskReport(
                overall_score=2.0,
                overall_level=RiskLevel.LOW,
                high_risk_count=0,
                medium_risk_count=0,
                low_risk_count=0,
                findings=[],
                summary="No significant risks found. Contract appears well-balanced."
            )
        
        # Count by level
        critical_count = sum(1 for f in self.findings if f.risk_level == RiskLevel.CRITICAL)
        high_count = sum(1 for f in self.findings if f.risk_level == RiskLevel.HIGH)
        medium_count = sum(1 for f in self.findings if f.risk_level == RiskLevel.MEDIUM)
        low_count = sum(1 for f in self.findings if f.risk_level == RiskLevel.LOW)
        
        # Calculate weighted average score
        total_score = sum(f.score for f in self.findings)
        avg_score = total_score / len(self.findings)
        
        # Adjust for severity
        if critical_count > 0:
            avg_score = min(10, avg_score + critical_count * 0.5)
        if high_count > 2:
            avg_score = min(10, avg_score + 0.5)
        
        overall_level = self._score_to_level(avg_score)
        
        # Generate summary
        summary_parts = []
        if critical_count > 0:
            summary_parts.append(f"{critical_count} critical risk(s) require immediate attention")
        if high_count > 0:
            summary_parts.append(f"{high_count} high-risk clause(s) should be renegotiated")
        if medium_count > 0:
            summary_parts.append(f"{medium_count} medium-risk item(s) to review")
        
        summary = ". ".join(summary_parts) if summary_parts else "Contract has acceptable risk levels."
        
        return RiskReport(
            overall_score=round(avg_score, 1),
            overall_level=overall_level,
            high_risk_count=critical_count + high_count,
            medium_risk_count=medium_count,
            low_risk_count=low_count,
            findings=sorted(self.findings, key=lambda x: x.score, reverse=True),
            summary=summary
        )
    
    def get_clause_risk_score(self, clause_content: str) -> Tuple[float, RiskLevel, List[str]]:
        """
        Quick risk assessment for a single clause
        
        Returns:
            Tuple of (score, level, risk_types found)
        """
        findings = []
        content_lower = clause_content.lower()
        
        for risk_type, risk_info in self.RISK_PATTERNS.items():
            for pattern in risk_info["patterns"]:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    findings.append(risk_type)
                    break
        
        if not findings:
            return (2.0, RiskLevel.LOW, [])
        
        max_score = max(self.RISK_WEIGHTS.get(f, 5) for f in findings)
        return (max_score, self._score_to_level(max_score), findings)


# Quick test
if __name__ == "__main__":
    assessor = RiskAssessor()
    
    test_text = """
    INDEMNIFICATION
    The Contractor shall fully indemnify and hold harmless the Company, its officers, 
    directors, and employees from any and all claims, damages, losses, costs, and expenses 
    arising out of or related to the Contractor's performance under this Agreement.
    
    TERMINATION
    The Company may terminate this Agreement at any time, with or without cause, 
    by providing written notice to the Contractor. Upon termination, the Contractor 
    shall have no claim for damages.
    
    NON-COMPETE
    The Contractor agrees not to engage in any competing business activities worldwide
    for a period of 5 years following termination of this Agreement.
    
    INTELLECTUAL PROPERTY
    All work product, inventions, and intellectual property created by the Contractor
    shall belong exclusively to the Company. The Contractor hereby assigns all rights,
    title, and interest in such work product to the Company.
    
    JURISDICTION
    This Agreement shall be governed by the laws of Singapore. Any disputes shall be
    resolved in the courts of Singapore.
    """
    
    report = assessor.assess_contract(test_text)
    
    print(f"\n{'='*60}")
    print(f"RISK ASSESSMENT REPORT")
    print(f"{'='*60}")
    print(f"Overall Score: {report.overall_score}/10 ({report.overall_level.value})")
    print(f"High Risk: {report.high_risk_count} | Medium: {report.medium_risk_count} | Low: {report.low_risk_count}")
    print(f"\nSummary: {report.summary}")
    print(f"\n{'='*60}")
    print(f"FINDINGS ({len(report.findings)} total):")
    print(f"{'='*60}")
    
    for finding in report.findings[:5]:
        print(f"\n[{finding.risk_level.value}] {finding.risk_type} (Score: {finding.score})")
        print(f"  Description: {finding.description}")
        print(f"  Suggestion: {finding.suggestion}")
