# Contract Analysis & Risk Assessment Bot

## 📄 Overview

A sophisticated GenAI-powered legal assistant that helps small and medium business owners understand complex contracts, identify potential legal risks, and receive actionable advice in plain language.

**Built for GUVI HCL Hackathon 2026**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### Core Legal NLP Tasks
- ✅ Contract Type Classification (Employment, Vendor, Lease, Partnership, Service, etc.)
- ✅ Clause & Sub-Clause Extraction
- ✅ Named Entity Recognition (Parties, Dates, Jurisdiction, Liabilities, Amounts)
- ✅ Obligation vs. Right vs. Prohibition Identification
- ✅ Risk & Compliance Detection
- ✅ Ambiguity Detection & Flagging
- ✅ Clause Similarity Matching to Standard Templates

### Risk Assessment Capabilities
- ✅ Clause-level Risk Scores (Low / Medium / High / Critical)
- ✅ Contract-level Composite Risk Score
- ✅ Identification of High-Risk Clauses:
  - Penalty Clauses
  - Indemnity Clauses
  - Unilateral Termination
  - Arbitration & Jurisdiction Terms
  - Auto-Renewal & Lock-in Periods
  - Non-compete & IP Transfer Clauses

### User-Facing Outputs
- ✅ Simplified Contract Summary
- ✅ Clause-by-clause Plain-language Explanation
- ✅ Unfavorable Clause Highlighting
- ✅ Suggested Renegotiation Alternatives
- ✅ Standardized SME-friendly Contract Templates
- ✅ PDF Export for Legal Review

### Multilingual Support
- ✅ English + Hindi Contract Parsing
- ✅ Hindi → English Internal Normalization
- ✅ Output Summaries in Simple Business English

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **LLM** | GPT-4 (OpenAI) |
| **NLP** | Python with spaCy and NLTK |
| **UI** | Streamlit |
| **Storage** | Local file & JSON-based audit logs |
| **PDF Processing** | PyPDF2, pdfplumber |
| **Document Processing** | python-docx |
| **PDF Export** | fpdf2 |

## 📁 Project Structure

```
contract-analysis-bot/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── README.md                   # This file
│
├── core/
│   ├── __init__.py
│   ├── document_loader.py      # PDF, DOCX, TXT extraction
│   ├── nlp_pipeline.py         # spaCy/NLTK processing
│   ├── clause_extractor.py     # Clause identification
│   ├── risk_assessor.py        # Risk scoring engine
│   └── contract_classifier.py  # Contract type detection
│
├── llm/
│   ├── __init__.py
│   ├── prompts.py              # Prompt templates
│   └── legal_analyzer.py       # LLM integration
│
├── ui/
│   ├── __init__.py
│   ├── components.py           # Streamlit UI components
│   └── pdf_exporter.py         # PDF generation
│
├── utils/
│   ├── __init__.py
│   ├── hindi_processor.py      # Hindi language handling
│   └── audit_logger.py         # JSON audit logs
│
├── data/
│   ├── uploads/                # Uploaded contracts
│   └── exports/                # Generated PDFs
│
└── logs/
    └── audit/                  # Audit trail JSON files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "d:\Rohith\Guvi\2nd Prob"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # OR
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up environment variables:**
   ```bash
   # Create .env file
   copy .env.example .env
   # Edit .env and add your OpenAI API key
   ```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload a Contract
- Click "Upload Contract" or drag-and-drop a PDF, DOCX, or TXT file
- Supported formats: `.pdf`, `.docx`, `.doc`, `.txt`

### 2. Configure Settings (Sidebar)
- **OpenAI API Key**: Required for AI-powered analysis
- **Enable AI Analysis**: Toggle GPT-4 integration
- **Hindi Support**: Enable Hindi language detection
- **Risk Threshold**: Set minimum score for risk alerts

### 3. Review Analysis
- **Summary Tab**: Contract type, parties, key metrics
- **Risk Assessment Tab**: Overall score, risk findings, suggestions
- **Clauses Tab**: Detailed clause-by-clause breakdown
- **AI Analysis Tab**: GPT-4 powered explanations
- **Export Tab**: Download PDF report

## 🔒 Security & Confidentiality

- All processing happens locally (except LLM calls)
- No contract data is stored on external servers
- Audit logs track all activities
- API calls only send necessary text for analysis

## ⚠️ Disclaimer

This tool is designed for informational purposes only and does not constitute legal advice. The analysis provided is AI-generated and should be reviewed by a qualified legal professional before making any decisions based on the results.

## 📄 Sample Contracts for Testing

The `samples/` folder contains example contracts for testing:
- `sample_employment_agreement.txt` - Employment contract
- `sample_vendor_contract.txt` - Vendor agreement
- `sample_nda.txt` - Non-disclosure agreement

## 🤝 Contributing

This project was built for the GUVI HCL Hackathon 2026.

## 📜 License

MIT License - See LICENSE file for details.

## 👨‍💻 Author

Built with ❤️ for Indian SMEs

---

**GUVI HCL Hackathon 2026 - Contract Analysis & Risk Assessment Bot**
