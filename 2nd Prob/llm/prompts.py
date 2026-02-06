"""
Prompt Templates for LLM Integration
Structured prompts for various legal analysis tasks
"""

from typing import Dict, List


class PromptTemplates:
    """
    Collection of prompt templates for legal document analysis
    """
    
    # System prompt for legal analysis
    SYSTEM_PROMPT = """You are an expert legal advisor specializing in Indian contract law and commercial agreements. Your role is to:

1. Analyze contracts for small and medium businesses (SMEs) in India
2. Explain complex legal terms in simple, everyday business language
3. Identify potential risks and unfavorable clauses
4. Suggest practical alternatives and negotiation strategies
5. Reference relevant Indian laws when applicable

Important guidelines:
- Always be balanced and objective in your analysis
- Highlight both risks AND benefits where applicable
- Use simple language that a non-lawyer business owner can understand
- When suggesting changes, be practical and consider business realities
- Reference Indian laws (Contract Act, Companies Act, etc.) when relevant

DO NOT provide definitive legal advice. Always recommend consulting a qualified lawyer for important decisions."""

    # Contract summary prompt
    CONTRACT_SUMMARY = """Analyze the following contract and provide a comprehensive summary:

CONTRACT TEXT:
{contract_text}

Please provide:

1. **Contract Overview**
   - Type of contract
   - Parties involved
   - Main purpose/objective

2. **Key Terms**
   - Duration/term
   - Financial terms (amounts, payment schedule)
   - Key obligations of each party

3. **Important Dates**
   - Effective date
   - Expiry/renewal dates
   - Key milestones

4. **Notable Provisions**
   - Termination conditions
   - Confidentiality requirements
   - Dispute resolution mechanism

5. **Quick Assessment**
   - Overall complexity (Low/Medium/High)
   - Recommended action items

Keep the summary clear, concise, and in plain business language."""

    # Clause explanation prompt
    CLAUSE_EXPLANATION = """Explain the following contract clause in simple, everyday language:

CLAUSE TEXT:
{clause_text}

CLAUSE TYPE: {clause_type}

Please provide:

1. **Plain Language Explanation**
   - What does this clause actually mean?
   - Write as if explaining to someone with no legal background

2. **Practical Implications**
   - How does this affect the parties in practice?
   - Real-world examples of how this might apply

3. **Key Points to Note**
   - Most important aspects to remember
   - Any hidden implications

4. **Common Questions**
   - What business owners typically ask about such clauses
   - Brief answers to those questions

Keep the explanation under 300 words and use bullet points for clarity."""

    # Risk analysis prompt
    RISK_ANALYSIS = """Analyze the following clause for potential risks:

CLAUSE TEXT:
{clause_text}

CLAUSE TYPE: {clause_type}
CURRENT RISK INDICATORS: {risk_indicators}

Please provide:

1. **Risk Assessment**
   - Risk Level: [Low/Medium/High/Critical]
   - Risk Score: [1-10]

2. **Identified Risks**
   - List each specific risk
   - Explain why it's a concern
   - Who bears the risk (which party)

3. **Potential Consequences**
   - Worst-case scenarios
   - Financial implications
   - Operational impact

4. **Indian Law Context**
   - Relevant Indian laws or regulations
   - Whether the clause is enforceable
   - Any statutory protections available

5. **Business Impact**
   - How this affects day-to-day operations
   - Long-term implications

Be specific and practical in your analysis."""

    # Renegotiation suggestions prompt
    RENEGOTIATION_SUGGESTIONS = """Suggest improvements for the following unfavorable clause:

ORIGINAL CLAUSE:
{clause_text}

CLAUSE TYPE: {clause_type}
IDENTIFIED ISSUES: {issues}

Please provide:

1. **Issues Summary**
   - What makes this clause unfavorable
   - Which party it favors and why

2. **Suggested Revisions**
   - Option 1: Minor modification (easier to negotiate)
   - Option 2: Balanced alternative (fair to both parties)
   - Option 3: Favorable revision (ideal for your client)

3. **Sample Language**
   - Provide actual revised clause text for Option 2

4. **Negotiation Tips**
   - How to approach this discussion
   - Common counterarguments and responses
   - What to prioritize vs. what to concede

5. **Industry Standards**
   - What's typical in similar contracts
   - Reasonable expectations

Make suggestions practical and likely to be accepted in negotiation."""

    # Hindi to English translation prompt
    HINDI_TRANSLATION = """Translate the following Hindi contract text to English, maintaining legal accuracy:

HINDI TEXT:
{hindi_text}

Please provide:

1. **English Translation**
   - Accurate translation preserving legal meaning
   - Maintain formal contract language style

2. **Key Legal Terms**
   - List important Hindi legal terms found
   - Their English equivalents
   - Brief explanation of each

3. **Cultural/Legal Context**
   - Any terms specific to Indian legal system
   - Regional variations if any

4. **Translation Notes**
   - Any ambiguities in the original text
   - Multiple possible interpretations

Ensure the translation is suitable for legal review."""

    # Compliance check prompt
    COMPLIANCE_CHECK = """Check the following contract for compliance with Indian laws:

CONTRACT TEXT:
{contract_text}

CONTRACT TYPE: {contract_type}

Please analyze compliance with:

1. **Indian Contract Act, 1872**
   - Valid offer and acceptance
   - Consideration
   - Free consent (no coercion, fraud, misrepresentation)
   - Lawful object and consideration
   - Any void or voidable clauses

2. **Specific Industry Regulations** (if applicable)
   - Labor laws (if employment)
   - Consumer protection (if applicable)
   - IT Act (for technology contracts)
   - FEMA (for foreign exchange aspects)

3. **Stamp Duty Requirements**
   - Whether stamping is required
   - Applicable state and amount (general guidance)

4. **Registration Requirements**
   - Whether registration is needed
   - Relevant authority

5. **Compliance Issues Found**
   - List any non-compliant clauses
   - Recommended corrections

6. **Recommendations**
   - Priority actions for compliance
   - Suggested legal consultations

Note: This is general guidance. Specific legal advice requires consultation with a licensed advocate."""

    # Full contract analysis prompt
    FULL_ANALYSIS = """Perform a comprehensive analysis of this contract:

CONTRACT TEXT:
{contract_text}

CONTRACT TYPE: {contract_type}
EXTRACTED PARTIES: {parties}
EXTRACTED KEY TERMS: {key_terms}

Please provide a structured analysis:

## 1. Executive Summary (2-3 sentences)

## 2. Contract Classification
- Primary type and sub-type
- Confidence in classification

## 3. Parties Analysis
- Who are the parties
- Their roles and obligations
- Power balance assessment

## 4. Key Commercial Terms
- Financial terms
- Duration and renewal
- Performance metrics

## 5. Risk Assessment
| Area | Risk Level | Key Concern |
|------|------------|-------------|
(List top 5-7 risk areas)

## 6. Favorable vs Unfavorable Analysis
### Favorable Clauses
- List with brief explanation

### Unfavorable Clauses
- List with brief explanation and suggested action

## 7. Missing Important Clauses
- What should be there but isn't

## 8. Action Items
- Immediate: (before signing)
- Short-term: (within first month)
- Ongoing: (throughout contract term)

## 9. Negotiation Priority
High Priority (must address):
Medium Priority (should address):
Low Priority (nice to have):

## 10. Overall Recommendation
- Proceed / Proceed with caution / Renegotiate / Do not sign
- Key reasons for recommendation

Keep language accessible to business owners without legal background."""

    @classmethod
    def get_summary_prompt(cls, contract_text: str) -> str:
        """Get formatted summary prompt"""
        return cls.CONTRACT_SUMMARY.format(contract_text=contract_text[:15000])
    
    @classmethod
    def get_clause_explanation_prompt(cls, clause_text: str, clause_type: str = "General") -> str:
        """Get formatted clause explanation prompt"""
        return cls.CLAUSE_EXPLANATION.format(
            clause_text=clause_text[:3000],
            clause_type=clause_type
        )
    
    @classmethod
    def get_risk_analysis_prompt(cls, clause_text: str, clause_type: str = "General", 
                                  risk_indicators: List[str] = None) -> str:
        """Get formatted risk analysis prompt"""
        indicators = ", ".join(risk_indicators) if risk_indicators else "None identified"
        return cls.RISK_ANALYSIS.format(
            clause_text=clause_text[:3000],
            clause_type=clause_type,
            risk_indicators=indicators
        )
    
    @classmethod
    def get_renegotiation_prompt(cls, clause_text: str, clause_type: str = "General",
                                  issues: List[str] = None) -> str:
        """Get formatted renegotiation suggestions prompt"""
        issues_text = "\n- ".join(issues) if issues else "General unfavorable terms"
        return cls.RENEGOTIATION_SUGGESTIONS.format(
            clause_text=clause_text[:3000],
            clause_type=clause_type,
            issues=issues_text
        )
    
    @classmethod
    def get_hindi_translation_prompt(cls, hindi_text: str) -> str:
        """Get formatted Hindi translation prompt"""
        return cls.HINDI_TRANSLATION.format(hindi_text=hindi_text[:5000])
    
    @classmethod
    def get_compliance_prompt(cls, contract_text: str, contract_type: str = "General") -> str:
        """Get formatted compliance check prompt"""
        return cls.COMPLIANCE_CHECK.format(
            contract_text=contract_text[:15000],
            contract_type=contract_type
        )
    
    @classmethod
    def get_full_analysis_prompt(cls, contract_text: str, contract_type: str = "Unknown",
                                  parties: List[str] = None, key_terms: List[str] = None) -> str:
        """Get formatted full analysis prompt"""
        return cls.FULL_ANALYSIS.format(
            contract_text=contract_text[:20000],
            contract_type=contract_type,
            parties=", ".join(parties) if parties else "Not extracted",
            key_terms=", ".join(key_terms) if key_terms else "Not extracted"
        )


# Quick test
if __name__ == "__main__":
    print("Prompt Templates Module")
    print("=" * 50)
    print("\nAvailable prompts:")
    print("- SYSTEM_PROMPT")
    print("- CONTRACT_SUMMARY")
    print("- CLAUSE_EXPLANATION")
    print("- RISK_ANALYSIS")
    print("- RENEGOTIATION_SUGGESTIONS")
    print("- HINDI_TRANSLATION")
    print("- COMPLIANCE_CHECK")
    print("- FULL_ANALYSIS")
    
    # Test prompt generation
    test_clause = "The Employee shall not engage in any competing business for 5 years after termination."
    prompt = PromptTemplates.get_clause_explanation_prompt(test_clause, "Non-Compete")
    print(f"\nSample generated prompt length: {len(prompt)} characters")
