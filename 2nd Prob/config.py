"""
Configuration file for Contract Analysis & Risk Assessment Bot
GUVI HCL Hackathon 2026
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = "gpt-4-turbo-preview"  # or "gpt-4" or "gpt-3.5-turbo"

# File Upload Settings
ALLOWED_EXTENSIONS = ["pdf", "docx", "doc", "txt"]
MAX_FILE_SIZE_MB = 10

# Risk Thresholds
RISK_LEVELS = {
    "LOW": (1, 3),
    "MEDIUM": (4, 6),
    "HIGH": (7, 10)
}

# High-Risk Clause Keywords
HIGH_RISK_KEYWORDS = {
    "penalty": ["penalty", "liquidated damages", "fine", "forfeit"],
    "indemnity": ["indemnify", "indemnification", "hold harmless", "defend"],
    "termination": ["terminate", "termination", "cancel", "rescind"],
    "non_compete": ["non-compete", "non compete", "restraint of trade", "compete"],
    "ip_transfer": ["intellectual property", "IP rights", "patent", "copyright", "trademark", "assign all rights"],
    "auto_renewal": ["auto-renew", "automatic renewal", "auto renewal", "evergreen"],
    "arbitration": ["arbitration", "arbitrator", "dispute resolution"],
    "jurisdiction": ["jurisdiction", "governing law", "venue"],
    "liability": ["unlimited liability", "liability cap", "limitation of liability"],
    "confidentiality": ["confidential", "NDA", "non-disclosure", "trade secret"]
}

# Contract Types
CONTRACT_TYPES = [
    "Employment Agreement",
    "Vendor Contract",
    "Lease Agreement",
    "Partnership Deed",
    "Service Contract",
    "Non-Disclosure Agreement",
    "Consulting Agreement",
    "Licensing Agreement",
    "Other"
]

# Indian Law Compliance Keywords
INDIAN_LAW_KEYWORDS = [
    "Indian Contract Act",
    "Arbitration and Conciliation Act",
    "Information Technology Act",
    "Companies Act",
    "SEBI",
    "RBI",
    "GST",
    "Income Tax Act"
]

# Data Extraction Fields
EXTRACTION_FIELDS = [
    "parties",
    "financial_amounts",
    "obligations",
    "liabilities",
    "deliverables",
    "timeline",
    "duration",
    "termination_conditions",
    "jurisdiction",
    "governing_law",
    "ip_rights",
    "confidentiality",
    "nda_terms"
]

# UI Configuration
APP_TITLE = "📄 Contract Analysis & Risk Assessment Bot"
APP_SUBTITLE = "GenAI-powered Legal Assistant for Indian SMEs"
PAGE_ICON = "📄"

# Paths
UPLOAD_DIR = "data/uploads"
EXPORT_DIR = "data/exports"
AUDIT_LOG_DIR = "logs/audit"
