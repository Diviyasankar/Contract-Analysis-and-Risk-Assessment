"""
UI Components Module
Streamlit UI components for the contract analysis application
"""

import streamlit as st
from typing import Dict, List, Any, Optional


class UIComponents:
    """
    Reusable Streamlit UI components for contract analysis
    """
    
    # Color schemes
    COLORS = {
        'primary': '#2980b9',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#3498db',
        'dark': '#2c3e50',
        'light': '#ecf0f1'
    }
    
    RISK_COLORS = {
        'LOW': '#27ae60',
        'MEDIUM': '#f39c12', 
        'HIGH': '#e74c3c',
        'CRITICAL': '#9b59b6'
    }
    
    @staticmethod
    def render_header():
        """Render application header"""
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
            font-size: 2.5rem;
        }
        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        </style>
        <div class="main-header">
            <h1>📄 Contract Analysis & Risk Assessment Bot</h1>
            <p>GenAI-powered Legal Assistant for Indian SMEs</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_risk_score(score: float, level: str):
        """Render risk score with visual indicator"""
        color = UIComponents.RISK_COLORS.get(level.upper(), '#95a5a6')
        
        st.markdown(f"""
        <div style="
            background: {color}20;
            border-left: 4px solid {color};
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="margin: 0; color: {color};">Overall Risk Score</h3>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Based on clause analysis</p>
                </div>
                <div style="
                    background: {color};
                    color: white;
                    padding: 0.5rem 1.5rem;
                    border-radius: 5px;
                    font-size: 1.5rem;
                    font-weight: bold;
                ">
                    {score}/10 {level}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_risk_distribution(high: int, medium: int, low: int):
        """Render risk distribution chart"""
        total = high + medium + low
        if total == 0:
            total = 1  # Avoid division by zero
        
        st.markdown("""
        <style>
        .risk-bar {
            display: flex;
            height: 30px;
            border-radius: 5px;
            overflow: hidden;
            margin: 1rem 0;
        }
        .risk-segment {
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.8rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="risk-bar">
            <div class="risk-segment" style="width: {high/total*100}%; background: #e74c3c;">
                {high if high > 0 else ''}
            </div>
            <div class="risk-segment" style="width: {medium/total*100}%; background: #f39c12;">
                {medium if medium > 0 else ''}
            </div>
            <div class="risk-segment" style="width: {low/total*100}%; background: #27ae60;">
                {low if low > 0 else ''}
            </div>
        </div>
        <div style="display: flex; justify-content: space-around; font-size: 0.8rem;">
            <span>🔴 High: {high}</span>
            <span>🟡 Medium: {medium}</span>
            <span>🟢 Low: {low}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_clause_card(clause: Dict, expanded: bool = False):
        """Render a clause analysis card"""
        clause_id = clause.get('clause_id', clause.get('number', '?'))
        title = clause.get('title', 'Untitled Clause')
        category = clause.get('category', 'general')
        content = clause.get('content', '')
        risk_indicators = clause.get('risk_indicators', [])
        
        # Determine risk level for styling
        if risk_indicators:
            risk_level = 'HIGH' if any(r in ['unlimited_liability', 'one_sided_indemnity', 'unilateral_termination'] 
                                       for r in risk_indicators) else 'MEDIUM'
            border_color = UIComponents.RISK_COLORS[risk_level]
        else:
            border_color = UIComponents.RISK_COLORS['LOW']
        
        with st.expander(f"📋 Clause {clause_id}: {title}", expanded=expanded):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Category:** {category.replace('_', ' ').title()}")
            
            with col2:
                if risk_indicators:
                    st.markdown(f"⚠️ **{len(risk_indicators)} risk(s)**")
            
            st.markdown("---")
            st.markdown("**Content:**")
            st.text(content[:500] + "..." if len(content) > 500 else content)
            
            if risk_indicators:
                st.markdown("**Risk Indicators:**")
                for indicator in risk_indicators:
                    st.markdown(f"- {indicator.replace('_', ' ').title()}")
    
    @staticmethod
    def render_finding_card(finding: Dict):
        """Render a risk finding card"""
        risk_type = finding.get('risk_type', 'Unknown Risk')
        risk_level = finding.get('risk_level', 'MEDIUM')
        if hasattr(risk_level, 'value'):
            risk_level = risk_level.value
        score = finding.get('score', 5)
        description = finding.get('description', '')
        suggestion = finding.get('suggestion', '')
        indian_law = finding.get('indian_law_reference', '')
        
        color = UIComponents.RISK_COLORS.get(risk_level, '#95a5a6')
        
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #ddd;
            border-left: 4px solid {color};
            border-radius: 5px;
            padding: 1rem;
            margin: 0.5rem 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: {color};">{risk_type}</h4>
                <span style="
                    background: {color};
                    color: white;
                    padding: 0.2rem 0.5rem;
                    border-radius: 3px;
                    font-size: 0.8rem;
                ">{risk_level} ({score}/10)</span>
            </div>
            <p style="margin: 0.5rem 0; color: #555;">{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if suggestion:
            st.info(f"💡 **Suggestion:** {suggestion}")
        
        if indian_law:
            st.caption(f"📚 **Indian Law Reference:** {indian_law}")
    
    @staticmethod
    def render_contract_summary(summary: Dict):
        """Render contract summary section"""
        st.subheader("📊 Contract Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Type", summary.get('contract_type', 'Unknown'))
        
        with col2:
            parties = summary.get('parties', [])
            st.metric("Parties", len(parties))
        
        with col3:
            st.metric("Words", f"{summary.get('word_count', 0):,}")
        
        with col4:
            st.metric("Language", summary.get('language', 'EN').upper())
        
        if parties:
            st.markdown("**Identified Parties:**")
            for party in parties[:5]:
                st.markdown(f"- {party}")
    
    @staticmethod
    def render_extraction_results(extraction: Dict):
        """Render data extraction results"""
        st.subheader("📝 Extracted Information")
        
        tabs = st.tabs(["Parties & Dates", "Financial", "Legal Terms", "Other"])
        
        with tabs[0]:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Parties:**")
                for party in extraction.get('parties', [])[:5]:
                    st.markdown(f"- {party}")
            with col2:
                st.markdown("**Key Dates:**")
                for date in extraction.get('dates', [])[:5]:
                    st.markdown(f"- {date}")
        
        with tabs[1]:
            st.markdown("**Financial Amounts:**")
            for amount in extraction.get('financial_amounts', [])[:10]:
                st.markdown(f"- {amount}")
            
            if extraction.get('duration'):
                st.markdown(f"**Duration:** {extraction['duration']}")
        
        with tabs[2]:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Jurisdiction:**")
                st.write(extraction.get('jurisdiction', 'Not specified'))
            with col2:
                st.markdown("**Governing Law:**")
                st.write(extraction.get('governing_law', 'Not specified'))
            
            if extraction.get('termination_conditions'):
                st.markdown("**Termination Conditions:**")
                for condition in extraction['termination_conditions'][:3]:
                    st.markdown(f"- {condition}")
        
        with tabs[3]:
            if extraction.get('ip_rights'):
                st.markdown("**IP Rights Mentions:**")
                for ip in extraction['ip_rights'][:3]:
                    st.markdown(f"- {ip}")
            
            if extraction.get('confidentiality_terms'):
                st.markdown("**Confidentiality:**")
                st.write(extraction['confidentiality_terms'][0][:200] + "...")
    
    @staticmethod
    def render_sidebar():
        """Render sidebar with info and settings"""
        with st.sidebar:
            st.image("https://via.placeholder.com/150x50?text=Logo", width=150)
            
            st.markdown("---")
            st.markdown("### 📁 Supported Formats")
            st.markdown("- PDF documents")
            st.markdown("- Word documents (.docx)")
            st.markdown("- Plain text files (.txt)")
            
            st.markdown("---")
            st.markdown("### 🌐 Languages")
            st.markdown("- English")
            st.markdown("- Hindi (हिंदी)")
            
            st.markdown("---")
            st.markdown("### ⚙️ Settings")
            
            risk_threshold = st.slider("Risk Alert Threshold", 1, 10, 5)
            show_all_clauses = st.checkbox("Show All Clauses", value=False)
            enable_hindi = st.checkbox("Enable Hindi Translation", value=True)
            
            st.markdown("---")
            st.markdown("### 📞 Help")
            st.markdown("For support, contact:")
            st.markdown("📧 support@example.com")
            
            return {
                'risk_threshold': risk_threshold,
                'show_all_clauses': show_all_clauses,
                'enable_hindi': enable_hindi
            }
    
    @staticmethod  
    def render_loading():
        """Render loading animation"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div class="loader"></div>
            <p>Analyzing contract...</p>
        </div>
        <style>
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_error(message: str):
        """Render error message"""
        st.error(f"❌ {message}")
    
    @staticmethod
    def render_success(message: str):
        """Render success message"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def render_info(message: str):
        """Render info message"""
        st.info(f"ℹ️ {message}")
    
    @staticmethod
    def render_warning(message: str):
        """Render warning message"""
        st.warning(f"⚠️ {message}")


# Export for use
__all__ = ['UIComponents']
