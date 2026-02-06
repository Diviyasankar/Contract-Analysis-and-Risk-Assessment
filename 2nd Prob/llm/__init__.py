"""
LLM module for Contract Analysis & Risk Assessment Bot
"""

from .legal_analyzer import LegalAnalyzer
from .prompts import PromptTemplates

__all__ = ["LegalAnalyzer", "PromptTemplates"]
