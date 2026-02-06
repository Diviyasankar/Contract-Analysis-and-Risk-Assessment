"""
Legal Analyzer Module
LLM integration for intelligent contract analysis using OpenAI GPT-4
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from .prompts import PromptTemplates


@dataclass
class AnalysisResult:
    """Result from LLM analysis"""
    success: bool
    content: str
    tokens_used: int = 0
    model: str = ""
    error: str = ""


class LegalAnalyzer:
    """
    LLM-powered legal analysis using OpenAI GPT-4
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the Legal Analyzer
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
        self.system_prompt = PromptTemplates.SYSTEM_PROMPT
    
    def is_available(self) -> bool:
        """Check if LLM is available and configured"""
        return OPENAI_AVAILABLE and self.client is not None and bool(self.api_key)
    
    def _call_llm(self, prompt: str, max_tokens: int = 2000) -> AnalysisResult:
        """
        Make a call to the LLM
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AnalysisResult with response or error
        """
        if not self.is_available():
            return AnalysisResult(
                success=False,
                content="",
                error="LLM not available. Please configure OPENAI_API_KEY."
            )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more consistent legal analysis
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            
            return AnalysisResult(
                success=True,
                content=content,
                tokens_used=tokens,
                model=self.model
            )
            
        except Exception as e:
            return AnalysisResult(
                success=False,
                content="",
                error=str(e)
            )
    
    def summarize_contract(self, contract_text: str) -> AnalysisResult:
        """
        Generate a comprehensive contract summary
        
        Args:
            contract_text: Full contract text
            
        Returns:
            AnalysisResult with summary
        """
        prompt = PromptTemplates.get_summary_prompt(contract_text)
        return self._call_llm(prompt, max_tokens=1500)
    
    def explain_clause(self, clause_text: str, clause_type: str = "General") -> AnalysisResult:
        """
        Explain a contract clause in simple language
        
        Args:
            clause_text: The clause text
            clause_type: Type of clause (e.g., "Indemnification", "Termination")
            
        Returns:
            AnalysisResult with explanation
        """
        prompt = PromptTemplates.get_clause_explanation_prompt(clause_text, clause_type)
        return self._call_llm(prompt, max_tokens=800)
    
    def analyze_risk(self, clause_text: str, clause_type: str = "General",
                     risk_indicators: List[str] = None) -> AnalysisResult:
        """
        Analyze a clause for risks
        
        Args:
            clause_text: The clause text
            clause_type: Type of clause
            risk_indicators: Pre-identified risk indicators
            
        Returns:
            AnalysisResult with risk analysis
        """
        prompt = PromptTemplates.get_risk_analysis_prompt(
            clause_text, clause_type, risk_indicators
        )
        return self._call_llm(prompt, max_tokens=1000)
    
    def suggest_renegotiation(self, clause_text: str, clause_type: str = "General",
                               issues: List[str] = None) -> AnalysisResult:
        """
        Suggest renegotiation options for an unfavorable clause
        
        Args:
            clause_text: The clause text
            clause_type: Type of clause
            issues: List of identified issues
            
        Returns:
            AnalysisResult with suggestions
        """
        prompt = PromptTemplates.get_renegotiation_prompt(clause_text, clause_type, issues)
        return self._call_llm(prompt, max_tokens=1200)
    
    def translate_hindi(self, hindi_text: str) -> AnalysisResult:
        """
        Translate Hindi contract text to English
        
        Args:
            hindi_text: Hindi text to translate
            
        Returns:
            AnalysisResult with translation
        """
        prompt = PromptTemplates.get_hindi_translation_prompt(hindi_text)
        return self._call_llm(prompt, max_tokens=2000)
    
    def check_compliance(self, contract_text: str, contract_type: str = "General") -> AnalysisResult:
        """
        Check contract for compliance with Indian laws
        
        Args:
            contract_text: Full contract text
            contract_type: Type of contract
            
        Returns:
            AnalysisResult with compliance analysis
        """
        prompt = PromptTemplates.get_compliance_prompt(contract_text, contract_type)
        return self._call_llm(prompt, max_tokens=1500)
    
    def full_analysis(self, contract_text: str, contract_type: str = "Unknown",
                      parties: List[str] = None, key_terms: List[str] = None) -> AnalysisResult:
        """
        Perform comprehensive contract analysis
        
        Args:
            contract_text: Full contract text
            contract_type: Type of contract
            parties: Extracted party names
            key_terms: Extracted key terms
            
        Returns:
            AnalysisResult with complete analysis
        """
        prompt = PromptTemplates.get_full_analysis_prompt(
            contract_text, contract_type, parties, key_terms
        )
        return self._call_llm(prompt, max_tokens=3000)
    
    def batch_explain_clauses(self, clauses: List[Dict[str, str]]) -> List[AnalysisResult]:
        """
        Explain multiple clauses (with rate limiting consideration)
        
        Args:
            clauses: List of {"text": "", "type": ""} dicts
            
        Returns:
            List of AnalysisResults
        """
        results = []
        for clause in clauses[:10]:  # Limit to 10 clauses
            result = self.explain_clause(
                clause.get("text", ""),
                clause.get("type", "General")
            )
            results.append(result)
        return results
    
    def get_quick_assessment(self, contract_text: str) -> Dict[str, Any]:
        """
        Get a quick high-level assessment without detailed LLM analysis
        
        This uses heuristics for speed when LLM is not available
        
        Args:
            contract_text: Full contract text
            
        Returns:
            Dictionary with quick assessment
        """
        text_lower = contract_text.lower()
        
        # Quick heuristic assessment
        assessment = {
            "word_count": len(contract_text.split()),
            "complexity": "Low",
            "key_topics": [],
            "quick_flags": []
        }
        
        # Estimate complexity
        if assessment["word_count"] > 5000:
            assessment["complexity"] = "High"
        elif assessment["word_count"] > 2000:
            assessment["complexity"] = "Medium"
        
        # Identify key topics
        topics = {
            "payment": ["payment", "fee", "salary", "compensation", "amount"],
            "termination": ["termination", "terminate", "cancel"],
            "confidentiality": ["confidential", "nda", "non-disclosure"],
            "liability": ["liability", "indemnify", "damages"],
            "ip": ["intellectual property", "copyright", "patent"],
            "non-compete": ["non-compete", "compete", "competitive"]
        }
        
        for topic, keywords in topics.items():
            if any(kw in text_lower for kw in keywords):
                assessment["key_topics"].append(topic)
        
        # Quick flags
        if "unlimited liability" in text_lower:
            assessment["quick_flags"].append("Unlimited liability mentioned")
        if "sole discretion" in text_lower:
            assessment["quick_flags"].append("Broad discretionary powers")
        if "waive" in text_lower or "waiver" in text_lower:
            assessment["quick_flags"].append("Waiver clauses present")
        
        return assessment


# Fallback analyzer when LLM is not available
class FallbackAnalyzer:
    """
    Fallback analyzer using rule-based methods when LLM is unavailable
    """
    
    @staticmethod
    def generate_summary(contract_text: str, metadata: Dict = None) -> str:
        """Generate a basic summary using extracted metadata"""
        summary_parts = ["## Contract Summary\n"]
        
        if metadata:
            if metadata.get("contract_type"):
                summary_parts.append(f"**Type:** {metadata['contract_type']}\n")
            if metadata.get("parties"):
                summary_parts.append(f"**Parties:** {', '.join(metadata['parties'][:5])}\n")
            if metadata.get("word_count"):
                summary_parts.append(f"**Length:** {metadata['word_count']} words\n")
        
        # Extract first paragraph as overview
        paragraphs = contract_text.split('\n\n')
        if paragraphs:
            summary_parts.append(f"\n**Overview:**\n{paragraphs[0][:500]}...\n")
        
        return "\n".join(summary_parts)
    
    @staticmethod
    def generate_clause_explanation(clause_text: str, clause_type: str) -> str:
        """Generate basic clause explanation"""
        explanations = {
            "indemnity": "This clause requires one party to compensate the other for losses or damages. It transfers risk from one party to another.",
            "termination": "This clause specifies when and how the contract can be ended by either party.",
            "confidentiality": "This clause protects sensitive information from being shared with third parties.",
            "non_compete": "This clause restricts a party from engaging in competing business activities.",
            "liability": "This clause defines the extent of financial responsibility for damages or losses.",
            "payment": "This clause outlines the payment terms, amounts, and schedules.",
            "jurisdiction": "This clause determines which court or legal system will handle disputes."
        }
        
        # Find matching explanation
        for key, explanation in explanations.items():
            if key in clause_type.lower():
                return f"**{clause_type}**\n\n{explanation}\n\n**Original text:**\n{clause_text[:300]}..."
        
        return f"**{clause_type}**\n\n{clause_text[:500]}..."


# Quick test
if __name__ == "__main__":
    analyzer = LegalAnalyzer()
    
    print("Legal Analyzer Module")
    print("=" * 50)
    print(f"OpenAI available: {OPENAI_AVAILABLE}")
    print(f"LLM configured: {analyzer.is_available()}")
    
    if not analyzer.is_available():
        print("\nUsing fallback analyzer...")
        fallback = FallbackAnalyzer()
        
        test_clause = "The Employee shall indemnify and hold harmless the Company from any claims."
        explanation = fallback.generate_clause_explanation(test_clause, "Indemnity Clause")
        print(f"\nFallback explanation:\n{explanation}")
