"""
Contract Analysis & Risk Assessment Bot
Main Streamlit Application

GUVI HCL Hackathon 2026
"""

import streamlit as st
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import core modules
from core.document_loader import DocumentLoader
from core.nlp_pipeline import NLPPipeline
from core.clause_extractor import ClauseExtractor
from core.risk_assessor import RiskAssessor, RiskLevel
from core.contract_classifier import ContractClassifier

# Import LLM modules
from llm.legal_analyzer import LegalAnalyzer, FallbackAnalyzer
from llm.prompts import PromptTemplates

# Import utility modules
from utils.hindi_processor import HindiProcessor
from utils.audit_logger import AuditLogger

# Import UI modules
from ui.components import UIComponents
from ui.pdf_exporter import PDFExporter

# Page configuration
st.set_page_config(
    page_title="Contract Analysis Bot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    .risk-high { color: #e74c3c; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low { color: #27ae60; font-weight: bold; }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .clause-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'contract_text' not in st.session_state:
        st.session_state.contract_text = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'clauses' not in st.session_state:
        st.session_state.clauses = None
    if 'risk_report' not in st.session_state:
        st.session_state.risk_report = None
    if 'contract_type' not in st.session_state:
        st.session_state.contract_type = None
    if 'metadata' not in st.session_state:
        st.session_state.metadata = None
    if 'llm_analysis' not in st.session_state:
        st.session_state.llm_analysis = None
    if 'audit_logger' not in st.session_state:
        st.session_state.audit_logger = AuditLogger()


def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>📄 Contract Analysis & Risk Assessment Bot</h1>
        <p>GenAI-powered Legal Assistant for Indian SMEs | GUVI HCL Hackathon 2026</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with settings and info"""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key for GPT-4 analysis"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("API Key configured!")
        
        st.markdown("---")
        
        # Settings
        st.markdown("### Analysis Options")
        
        enable_llm = st.checkbox(
            "Enable AI Analysis",
            value=True,
            help="Use GPT-4 for detailed analysis"
        )
        
        detect_hindi = st.checkbox(
            "Hindi Support",
            value=True,
            help="Enable Hindi language detection and translation"
        )
        
        show_all_clauses = st.checkbox(
            "Show All Clauses",
            value=False,
            help="Display all extracted clauses"
        )
        
        risk_threshold = st.slider(
            "Risk Alert Threshold",
            min_value=1,
            max_value=10,
            value=5,
            help="Minimum score to highlight as risk"
        )
        
        st.markdown("---")
        
        # File format info
        st.markdown("### 📁 Supported Formats")
        st.markdown("- PDF documents (.pdf)")
        st.markdown("- Word documents (.docx)")
        st.markdown("- Plain text (.txt)")
        
        st.markdown("---")
        
        # About section
        st.markdown("### ℹ️ About")
        st.markdown("""
        This tool analyzes contracts to identify:
        - Risk clauses
        - Legal obligations
        - Compliance issues
        - Unfavorable terms
        
        **Disclaimer:** This is an AI-powered tool 
        and does not constitute legal advice.
        """)
        
        return {
            'api_key': api_key,
            'enable_llm': enable_llm,
            'detect_hindi': detect_hindi,
            'show_all_clauses': show_all_clauses,
            'risk_threshold': risk_threshold
        }


def process_document(uploaded_file, settings):
    """Process uploaded document and perform analysis"""
    
    # Initialize components
    doc_loader = DocumentLoader()
    nlp_pipeline = NLPPipeline()
    clause_extractor = ClauseExtractor()
    risk_assessor = RiskAssessor()
    classifier = ContractClassifier()
    hindi_processor = HindiProcessor()
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Load document
        status_text.text("📄 Loading document...")
        progress_bar.progress(10)
        
        file_bytes = uploaded_file.read()
        text, metadata = doc_loader.load_from_bytes(file_bytes, uploaded_file.name)
        
        if not text or len(text.strip()) < 100:
            st.error("Could not extract sufficient text from the document. Please try a different file.")
            return None
        
        st.session_state.contract_text = text
        st.session_state.metadata = metadata
        
        # Log upload
        st.session_state.audit_logger.log_document_upload(
            uploaded_file.name, 
            len(file_bytes),
            metadata.get('language', 'en')
        )
        
        # Step 2: Language detection and processing
        status_text.text("🌐 Detecting language...")
        progress_bar.progress(20)
        
        if settings['detect_hindi'] and hindi_processor.is_hindi(text):
            status_text.text("🔄 Processing Hindi content...")
            text = hindi_processor.prepare_for_nlp(text)
            metadata['original_language'] = 'hindi'
        
        # Step 3: Classify contract type
        status_text.text("📋 Classifying contract type...")
        progress_bar.progress(30)
        
        classification = classifier.classify(text)
        st.session_state.contract_type = classification
        
        # Step 4: Extract clauses
        status_text.text("📝 Extracting clauses...")
        progress_bar.progress(45)
        
        clauses = clause_extractor.extract_clauses(text)
        data_dimensions = clause_extractor.extract_data_dimensions(text)
        st.session_state.clauses = clauses
        
        # Step 5: NLP Processing
        status_text.text("🧠 Performing NLP analysis...")
        progress_bar.progress(60)
        
        nlp_results = nlp_pipeline.process(text)
        
        # Step 6: Risk Assessment
        status_text.text("⚠️ Assessing risks...")
        progress_bar.progress(75)
        
        clause_dicts = [
            {
                "clause_id": c.clause_id,
                "title": c.title,
                "content": c.content,
                "category": c.category,
                "risk_indicators": c.risk_indicators
            }
            for c in clauses
        ]
        
        risk_report = risk_assessor.assess_contract(text, clause_dicts)
        st.session_state.risk_report = risk_report
        
        # Log risk findings
        for finding in risk_report.findings[:5]:
            st.session_state.audit_logger.log_risk_finding(
                uploaded_file.name,
                finding.risk_type,
                finding.risk_level.value if hasattr(finding.risk_level, 'value') else str(finding.risk_level)
            )
        
        # Step 7: LLM Analysis (if enabled)
        llm_analysis = None
        if settings['enable_llm'] and settings.get('api_key'):
            status_text.text("🤖 Generating AI analysis...")
            progress_bar.progress(85)
            
            analyzer = LegalAnalyzer(api_key=settings['api_key'])
            
            if analyzer.is_available():
                result = analyzer.summarize_contract(text[:10000])
                if result.success:
                    llm_analysis = result.content
                    st.session_state.llm_analysis = llm_analysis
                    st.session_state.audit_logger.log_llm_call(
                        "gpt-4",
                        "contract_summary",
                        result.tokens_used,
                        True
                    )
        
        # Step 8: Compile results
        status_text.text("✅ Compiling results...")
        progress_bar.progress(95)
        
        results = {
            'text': text,
            'metadata': metadata,
            'classification': classification,
            'clauses': clauses,
            'clause_dicts': clause_dicts,
            'data_dimensions': data_dimensions,
            'nlp_results': nlp_results,
            'risk_report': risk_report,
            'llm_analysis': llm_analysis
        }
        
        st.session_state.analysis_results = results
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        return results
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        st.session_state.audit_logger.log_error("processing_error", str(e))
        return None


def render_summary_tab(results):
    """Render the contract summary tab"""
    st.header("📊 Contract Summary")
    
    # Classification
    classification = results['classification']
    metadata = results['metadata']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Contract Type", classification.contract_type)
    
    with col2:
        st.metric("Confidence", f"{classification.confidence:.0%}")
    
    with col3:
        st.metric("Word Count", f"{metadata.get('word_count', 0):,}")
    
    with col4:
        st.metric("Language", metadata.get('language', 'en').upper())
    
    # Sub-type
    if classification.sub_type:
        st.info(f"📋 Sub-type: **{classification.sub_type}**")
    
    # Key indicators
    if classification.key_indicators:
        with st.expander("🔍 Classification Indicators"):
            st.write(", ".join(classification.key_indicators[:10]))
    
    st.markdown("---")
    
    # Data dimensions
    st.subheader("📝 Extracted Information")
    
    dimensions = results['data_dimensions']
    
    tab1, tab2, tab3 = st.tabs(["Parties & Dates", "Financial Terms", "Legal Terms"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Identified Parties:**")
            parties = dimensions.get('parties', [])
            if parties:
                for party in parties[:5]:
                    st.markdown(f"- {party}")
            else:
                st.markdown("_No parties identified_")
        
        with col2:
            st.markdown("**Duration:**")
            duration = dimensions.get('duration')
            if duration:
                st.markdown(f"📅 {duration}")
            else:
                st.markdown("_Not specified_")
    
    with tab2:
        amounts = dimensions.get('financial_amounts', [])
        if amounts:
            st.markdown("**Financial Amounts Found:**")
            for amount in amounts[:10]:
                st.markdown(f"- ₹{amount}" if not amount.startswith('$') else f"- {amount}")
        else:
            st.markdown("_No financial amounts identified_")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Jurisdiction:**")
            st.write(dimensions.get('jurisdiction', 'Not specified'))
        
        with col2:
            st.markdown("**Governing Law:**")
            st.write(dimensions.get('governing_law', 'Not specified'))
        
        if dimensions.get('termination_conditions'):
            st.markdown("**Termination Conditions:**")
            for condition in dimensions['termination_conditions'][:3]:
                st.markdown(f"- {condition[:150]}...")


def render_risk_tab(results):
    """Render the risk assessment tab"""
    st.header("⚠️ Risk Assessment")
    
    risk_report = results['risk_report']
    
    # Overall score with visual
    score = risk_report.overall_score
    level = risk_report.overall_level
    level_str = level.value if hasattr(level, 'value') else str(level)
    
    # Color based on risk level
    colors = {
        'LOW': '#27ae60',
        'MEDIUM': '#f39c12',
        'HIGH': '#e74c3c',
        'CRITICAL': '#9b59b6'
    }
    color = colors.get(level_str, '#95a5a6')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="
            background: {color}15;
            border-left: 5px solid {color};
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        ">
            <h2 style="margin: 0; color: {color};">Overall Risk Score: {score}/10</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Risk Level: <strong>{level_str}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("High Risk", risk_report.high_risk_count, delta_color="inverse")
        st.metric("Medium Risk", risk_report.medium_risk_count)
        st.metric("Low Risk", risk_report.low_risk_count, delta_color="off")
    
    # Summary
    if risk_report.summary:
        st.info(f"📋 **Summary:** {risk_report.summary}")
    
    st.markdown("---")
    
    # Detailed findings
    st.subheader("🔍 Risk Findings")
    
    if not risk_report.findings:
        st.success("✅ No significant risks identified!")
    else:
        for i, finding in enumerate(risk_report.findings):
            risk_type = finding.risk_type if hasattr(finding, 'risk_type') else finding.get('risk_type', 'Unknown')
            risk_level = finding.risk_level if hasattr(finding, 'risk_level') else finding.get('risk_level', 'MEDIUM')
            if hasattr(risk_level, 'value'):
                risk_level = risk_level.value
            finding_score = finding.score if hasattr(finding, 'score') else finding.get('score', 5)
            description = finding.description if hasattr(finding, 'description') else finding.get('description', '')
            suggestion = finding.suggestion if hasattr(finding, 'suggestion') else finding.get('suggestion', '')
            indian_law = finding.indian_law_reference if hasattr(finding, 'indian_law_reference') else finding.get('indian_law_reference', '')
            
            finding_color = colors.get(risk_level, '#95a5a6')
            
            with st.expander(f"{'🔴' if risk_level in ['HIGH', 'CRITICAL'] else '🟡' if risk_level == 'MEDIUM' else '🟢'} {risk_type} ({finding_score}/10)", expanded=(i < 3)):
                st.markdown(f"**Risk Level:** <span style='color:{finding_color}'>{risk_level}</span>", unsafe_allow_html=True)
                st.markdown(f"**Description:** {description}")
                
                if suggestion:
                    st.info(f"💡 **Suggestion:** {suggestion}")
                
                if indian_law:
                    st.caption(f"📚 **Indian Law Reference:** {indian_law}")


def render_clauses_tab(results, show_all=False):
    """Render the clause analysis tab"""
    st.header("📝 Clause Analysis")
    
    clauses = results['clauses']
    
    if not clauses:
        st.warning("No clauses could be extracted from this document.")
        return
    
    st.write(f"**Total clauses extracted:** {len(clauses)}")
    
    # Category summary
    categories = {}
    for clause in clauses:
        cat = clause.category
        categories[cat] = categories.get(cat, 0) + 1
    
    with st.expander("📊 Clause Categories"):
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- **{cat.replace('_', ' ').title()}:** {count} clause(s)")
    
    st.markdown("---")
    
    # Filter options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input("🔍 Search clauses", placeholder="Enter keywords...")
    
    with col2:
        filter_category = st.selectbox(
            "Filter by category",
            ["All"] + list(set(c.category for c in clauses))
        )
    
    # Display clauses
    displayed = 0
    max_display = 20 if show_all else 10
    
    for clause in clauses:
        # Apply filters
        if filter_category != "All" and clause.category != filter_category:
            continue
        
        if search and search.lower() not in clause.content.lower() and search.lower() not in clause.title.lower():
            continue
        
        if displayed >= max_display:
            break
        
        displayed += 1
        
        # Determine styling based on risk
        has_risk = bool(clause.risk_indicators)
        border_color = '#e74c3c' if has_risk else '#667eea'
        
        with st.expander(
            f"📋 Clause {clause.clause_id}: {clause.title[:60]}{'...' if len(clause.title) > 60 else ''}", 
            expanded=False
        ):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**Category:** {clause.category.replace('_', ' ').title()}")
            
            with col2:
                if has_risk:
                    st.markdown("⚠️ **Has Risks**")
            
            st.markdown("**Content:**")
            st.text(clause.content[:800] + ("..." if len(clause.content) > 800 else ""))
            
            if clause.risk_indicators:
                st.markdown("**⚠️ Risk Indicators:**")
                for indicator in clause.risk_indicators:
                    st.markdown(f"- {indicator.replace('_', ' ').title()}")
            
            if clause.amounts:
                st.markdown(f"**💰 Amounts:** {', '.join(clause.amounts)}")
            
            if clause.dates:
                st.markdown(f"**📅 Dates:** {', '.join(clause.dates)}")
    
    if displayed == 0:
        st.info("No clauses match your search criteria.")
    elif displayed < len(clauses):
        st.info(f"Showing {displayed} of {len(clauses)} clauses. Enable 'Show All Clauses' in settings to see more.")


def render_ai_analysis_tab(results, settings):
    """Render the AI analysis tab"""
    st.header("🤖 AI-Powered Analysis")
    
    llm_analysis = results.get('llm_analysis')
    
    if not settings.get('api_key'):
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to enable AI analysis.")
        
        st.markdown("""
        ### What AI Analysis provides:
        - Plain-language contract summary
        - Clause-by-clause explanations
        - Risk mitigation suggestions
        - Renegotiation recommendations
        - Indian law compliance guidance
        """)
        return
    
    if llm_analysis:
        st.markdown(llm_analysis)
    else:
        st.info("AI analysis will appear here after processing a document.")
    
    st.markdown("---")
    
    # Additional AI features
    st.subheader("💡 Additional Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Generate Detailed Summary", use_container_width=True):
            with st.spinner("Generating summary..."):
                analyzer = LegalAnalyzer(api_key=settings['api_key'])
                if analyzer.is_available() and st.session_state.contract_text:
                    result = analyzer.summarize_contract(st.session_state.contract_text[:10000])
                    if result.success:
                        st.markdown(result.content)
                    else:
                        st.error(f"Error: {result.error}")
    
    with col2:
        if st.button("⚖️ Check Indian Law Compliance", use_container_width=True):
            with st.spinner("Checking compliance..."):
                analyzer = LegalAnalyzer(api_key=settings['api_key'])
                if analyzer.is_available() and st.session_state.contract_text:
                    contract_type = st.session_state.contract_type.contract_type if st.session_state.contract_type else "General"
                    result = analyzer.check_compliance(st.session_state.contract_text[:10000], contract_type)
                    if result.success:
                        st.markdown(result.content)
                    else:
                        st.error(f"Error: {result.error}")
    
    # Clause explanation
    st.markdown("---")
    st.subheader("🔍 Explain a Clause")
    
    clause_text = st.text_area(
        "Paste a clause to get a plain-language explanation:",
        height=100,
        placeholder="Enter contract clause text here..."
    )
    
    if st.button("Explain Clause") and clause_text:
        with st.spinner("Generating explanation..."):
            analyzer = LegalAnalyzer(api_key=settings['api_key'])
            if analyzer.is_available():
                result = analyzer.explain_clause(clause_text)
                if result.success:
                    st.markdown(result.content)
                else:
                    st.error(f"Error: {result.error}")


def render_export_tab(results, settings):
    """Render the export tab"""
    st.header("📥 Export Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 PDF Report")
        st.markdown("Generate a comprehensive PDF report with all analysis results.")
        
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Generating PDF..."):
                exporter = PDFExporter()
                
                if exporter.is_available():
                    # Prepare data
                    summary = {
                        'contract_type': results['classification'].contract_type,
                        'parties': results['data_dimensions'].get('parties', []),
                        'word_count': results['metadata'].get('word_count', 0),
                        'language': results['metadata'].get('language', 'en')
                    }
                    
                    risk_report = {
                        'overall_score': results['risk_report'].overall_score,
                        'overall_level': results['risk_report'].overall_level.value,
                        'high_risk_count': results['risk_report'].high_risk_count,
                        'medium_risk_count': results['risk_report'].medium_risk_count,
                        'low_risk_count': results['risk_report'].low_risk_count,
                        'summary': results['risk_report'].summary,
                        'findings': [
                            {
                                'risk_type': f.risk_type,
                                'risk_level': f.risk_level.value if hasattr(f.risk_level, 'value') else f.risk_level,
                                'score': f.score,
                                'description': f.description,
                                'suggestion': f.suggestion
                            }
                            for f in results['risk_report'].findings[:10]
                        ]
                    }
                    
                    clauses = [
                        {
                            'clause_id': c.clause_id,
                            'title': c.title,
                            'category': c.category,
                            'content': c.content
                        }
                        for c in results['clauses'][:15]
                    ]
                    
                    pdf_path = exporter.generate_report(
                        summary,
                        risk_report,
                        clauses,
                        results.get('llm_analysis', '')
                    )
                    
                    if pdf_path:
                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=f.read(),
                                file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        st.success(f"PDF generated successfully!")
                        
                        # Log export
                        st.session_state.audit_logger.log_export("document", "PDF", pdf_path)
                    else:
                        st.error("Failed to generate PDF.")
                else:
                    st.error("PDF export not available. Please install fpdf2: pip install fpdf2")
    
    with col2:
        st.subheader("📋 Copy Summary")
        st.markdown("Copy a text summary to clipboard.")
        
        # Generate text summary
        summary_text = f"""
CONTRACT ANALYSIS SUMMARY
========================

Contract Type: {results['classification'].contract_type}
Confidence: {results['classification'].confidence:.0%}
Word Count: {results['metadata'].get('word_count', 0)}

RISK ASSESSMENT
---------------
Overall Score: {results['risk_report'].overall_score}/10
Risk Level: {results['risk_report'].overall_level.value}
High Risk Clauses: {results['risk_report'].high_risk_count}
Medium Risk Clauses: {results['risk_report'].medium_risk_count}

Summary: {results['risk_report'].summary}

PARTIES IDENTIFIED
------------------
{chr(10).join('- ' + p for p in results['data_dimensions'].get('parties', [])[:5]) or 'None identified'}

Generated by Contract Analysis Bot
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        st.text_area("Summary Text", summary_text, height=300)
        st.info("Select all text above and copy (Ctrl+C)")
    
    st.markdown("---")
    
    # Audit log
    st.subheader("📜 Audit Log")
    
    if st.checkbox("Show audit log"):
        audit_summary = st.session_state.audit_logger.get_session_summary()
        st.json(audit_summary)
        
        recent_logs = st.session_state.audit_logger.get_recent_logs(5)
        for log in recent_logs:
            st.markdown(f"- `{log['timestamp']}`: {log['event_type']}")


def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get settings
    settings = render_sidebar()
    
    # Main content area
    st.markdown("---")
    
    # File upload section
    st.subheader("📤 Upload Contract")
    
    uploaded_file = st.file_uploader(
        "Choose a contract file",
        type=['pdf', 'docx', 'txt'],
        help="Upload a PDF, DOCX, or TXT file containing your contract"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        
        with col2:
            analyze_button = st.button("🔍 Analyze Contract", type="primary", use_container_width=True)
        
        if analyze_button:
            results = process_document(uploaded_file, settings)
            
            if results:
                st.success("✅ Analysis complete!")
    
    # Display results if available
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("---")
        
        # Create tabs for different views
        tabs = st.tabs([
            "📊 Summary",
            "⚠️ Risk Assessment",
            "📝 Clauses",
            "🤖 AI Analysis",
            "📥 Export"
        ])
        
        with tabs[0]:
            render_summary_tab(results)
        
        with tabs[1]:
            render_risk_tab(results)
        
        with tabs[2]:
            render_clauses_tab(results, settings.get('show_all_clauses', False))
        
        with tabs[3]:
            render_ai_analysis_tab(results, settings)
        
        with tabs[4]:
            render_export_tab(results, settings)
    
    else:
        # Welcome message when no file uploaded
        st.markdown("""
        <div style="
            background: #f8f9fa;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            margin: 2rem 0;
        ">
            <h2>👋 Welcome to Contract Analysis Bot</h2>
            <p>Upload a contract document to get started with AI-powered analysis.</p>
            <br>
            <h4>What this tool does:</h4>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 1rem; margin-top: 1rem;">
                <div style="flex: 1; min-width: 200px;">
                    <h3>📋</h3>
                    <p><strong>Classify</strong><br>Identify contract type</p>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <h3>⚠️</h3>
                    <p><strong>Assess Risk</strong><br>Find risky clauses</p>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <h3>🧠</h3>
                    <p><strong>Explain</strong><br>Plain language summaries</p>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <h3>💡</h3>
                    <p><strong>Suggest</strong><br>Negotiation alternatives</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.8rem;">
        <p>Contract Analysis & Risk Assessment Bot | GUVI HCL Hackathon 2026</p>
        <p>⚠️ This tool provides AI-powered analysis and does not constitute legal advice.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
