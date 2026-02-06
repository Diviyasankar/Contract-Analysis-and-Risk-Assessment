"""
PDF Exporter Module
Generates professional PDF reports from contract analysis
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Try to import fpdf2
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class ContractReportPDF(FPDF):
    """
    Custom PDF class for contract analysis reports
    """
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Page header"""
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(41, 128, 185)  # Blue
        self.cell(0, 10, 'Contract Analysis Report', 0, 1, 'C')
        self.set_draw_color(41, 128, 185)
        self.line(10, 20, 200, 20)
        self.ln(5)
    
    def footer(self):
        """Page footer"""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')
    
    def chapter_title(self, title: str):
        """Add a chapter title"""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(44, 62, 80)  # Dark blue
        self.set_fill_color(236, 240, 241)  # Light gray
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(4)
    
    def section_title(self, title: str):
        """Add a section title"""
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(52, 73, 94)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)
    
    def body_text(self, text: str):
        """Add body text"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        # Handle encoding issues
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, safe_text)
        self.ln(2)
    
    def add_risk_badge(self, level: str):
        """Add a colored risk badge"""
        colors = {
            'LOW': (46, 204, 113),      # Green
            'MEDIUM': (241, 196, 15),    # Yellow
            'HIGH': (231, 76, 60),       # Red
            'CRITICAL': (155, 89, 182)   # Purple
        }
        
        color = colors.get(level.upper(), (149, 165, 166))
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        
        badge_width = self.get_string_width(level) + 6
        self.cell(badge_width, 6, level, 0, 0, 'C', True)
        self.set_text_color(0, 0, 0)
        self.ln(8)
    
    def add_table(self, headers: List[str], data: List[List[str]], 
                  col_widths: List[int] = None):
        """Add a table to the PDF"""
        if not col_widths:
            col_widths = [190 // len(headers)] * len(headers)
        
        # Header
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(52, 73, 94)
        self.set_text_color(255, 255, 255)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C', True)
        self.ln()
        
        # Data rows
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)
        
        for row_idx, row in enumerate(data):
            # Alternate row colors
            if row_idx % 2 == 0:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(255, 255, 255)
            
            for i, cell in enumerate(row):
                # Truncate long text
                cell_text = str(cell)[:50] + '...' if len(str(cell)) > 50 else str(cell)
                safe_text = cell_text.encode('latin-1', 'replace').decode('latin-1')
                self.cell(col_widths[i], 6, safe_text, 1, 0, 'L', True)
            self.ln()
        
        self.ln(5)


class PDFExporter:
    """
    Exports contract analysis to PDF reports
    """
    
    def __init__(self, output_dir: str = "data/exports"):
        """
        Initialize PDF exporter
        
        Args:
            output_dir: Directory for saving PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def is_available(self) -> bool:
        """Check if PDF export is available"""
        return FPDF_AVAILABLE
    
    def generate_report(self, 
                        contract_summary: Dict,
                        risk_report: Dict,
                        clauses: List[Dict],
                        llm_analysis: str = None,
                        filename: str = None) -> Optional[str]:
        """
        Generate comprehensive PDF report
        
        Args:
            contract_summary: Contract summary data
            risk_report: Risk assessment results
            clauses: Extracted clauses
            llm_analysis: LLM-generated analysis
            filename: Output filename (optional)
            
        Returns:
            Path to generated PDF or None if failed
        """
        if not FPDF_AVAILABLE:
            return None
        
        try:
            pdf = ContractReportPDF()
            pdf.alias_nb_pages()
            pdf.add_page()
            
            # Title page info
            pdf.set_font('Helvetica', 'B', 20)
            pdf.set_text_color(44, 62, 80)
            pdf.cell(0, 20, 'Contract Analysis Report', 0, 1, 'C')
            
            pdf.set_font('Helvetica', '', 12)
            pdf.set_text_color(127, 140, 141)
            pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}', 0, 1, 'C')
            pdf.ln(10)
            
            # Contract Summary Section
            pdf.chapter_title('1. Contract Summary')
            
            if contract_summary:
                summary_data = [
                    ['Contract Type', contract_summary.get('contract_type', 'Unknown')],
                    ['Parties', ', '.join(contract_summary.get('parties', [])[:3]) or 'Not identified'],
                    ['Word Count', str(contract_summary.get('word_count', 'N/A'))],
                    ['Language', contract_summary.get('language', 'English')]
                ]
                
                for item in summary_data:
                    pdf.set_font('Helvetica', 'B', 10)
                    pdf.cell(50, 6, item[0] + ':', 0, 0)
                    pdf.set_font('Helvetica', '', 10)
                    safe_value = item[1].encode('latin-1', 'replace').decode('latin-1')
                    pdf.cell(0, 6, safe_value, 0, 1)
                
                pdf.ln(5)
            
            # Risk Assessment Section
            pdf.chapter_title('2. Risk Assessment')
            
            if risk_report:
                # Overall score
                score = risk_report.get('overall_score', 0)
                level = risk_report.get('overall_level', 'LOW')
                if hasattr(level, 'value'):
                    level = level.value
                
                pdf.section_title('Overall Risk')
                pdf.set_font('Helvetica', 'B', 16)
                pdf.cell(30, 10, f'{score}/10', 0, 0)
                pdf.add_risk_badge(level)
                
                # Risk summary
                pdf.body_text(risk_report.get('summary', 'No summary available.'))
                
                # Risk counts
                pdf.section_title('Risk Distribution')
                risk_data = [
                    ['High Risk', str(risk_report.get('high_risk_count', 0))],
                    ['Medium Risk', str(risk_report.get('medium_risk_count', 0))],
                    ['Low Risk', str(risk_report.get('low_risk_count', 0))]
                ]
                pdf.add_table(['Category', 'Count'], risk_data, [100, 90])
                
                # Top findings
                findings = risk_report.get('findings', [])
                if findings:
                    pdf.section_title('Key Findings')
                    
                    for i, finding in enumerate(findings[:5]):
                        risk_type = finding.risk_type if hasattr(finding, 'risk_type') else finding.get('risk_type', 'Unknown')
                        risk_level = finding.risk_level if hasattr(finding, 'risk_level') else finding.get('risk_level', 'MEDIUM')
                        if hasattr(risk_level, 'value'):
                            risk_level = risk_level.value
                        description = finding.description if hasattr(finding, 'description') else finding.get('description', '')
                        suggestion = finding.suggestion if hasattr(finding, 'suggestion') else finding.get('suggestion', '')
                        
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(0, 6, f'{i+1}. {risk_type} [{risk_level}]', 0, 1)
                        pdf.set_font('Helvetica', '', 9)
                        pdf.body_text(f'Issue: {description}')
                        if suggestion:
                            pdf.set_font('Helvetica', 'I', 9)
                            pdf.body_text(f'Suggestion: {suggestion}')
                        pdf.ln(3)
            
            # Clause Analysis Section
            if clauses:
                pdf.add_page()
                pdf.chapter_title('3. Clause Analysis')
                
                for i, clause in enumerate(clauses[:10]):  # Limit to 10 clauses
                    clause_id = clause.get('clause_id', clause.get('number', f'{i+1}'))
                    title = clause.get('title', 'Untitled')
                    category = clause.get('category', 'general')
                    content = clause.get('content', '')[:200]
                    
                    safe_title = title.encode('latin-1', 'replace').decode('latin-1')
                    pdf.section_title(f'Clause {clause_id}: {safe_title}')
                    
                    pdf.set_font('Helvetica', 'I', 9)
                    pdf.cell(0, 5, f'Category: {category}', 0, 1)
                    
                    pdf.set_font('Helvetica', '', 9)
                    safe_content = content.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, safe_content + '...')
                    pdf.ln(5)
            
            # LLM Analysis Section
            if llm_analysis:
                pdf.add_page()
                pdf.chapter_title('4. AI-Powered Analysis')
                pdf.body_text(llm_analysis[:5000])  # Limit length
            
            # Recommendations Section
            pdf.add_page()
            pdf.chapter_title('5. Recommendations')
            
            recommendations = [
                'Review all HIGH and CRITICAL risk clauses with legal counsel',
                'Consider renegotiating unfavorable terms before signing',
                'Ensure all parties are correctly identified',
                'Verify jurisdiction and dispute resolution terms',
                'Check for any missing standard clauses (confidentiality, liability cap)'
            ]
            
            for i, rec in enumerate(recommendations):
                pdf.set_font('Helvetica', '', 10)
                pdf.cell(0, 6, f'{i+1}. {rec}', 0, 1)
            
            # Disclaimer
            pdf.ln(10)
            pdf.set_font('Helvetica', 'I', 8)
            pdf.set_text_color(127, 140, 141)
            pdf.multi_cell(0, 4, 
                'DISCLAIMER: This report is generated by an AI-powered tool and is intended for '
                'informational purposes only. It does not constitute legal advice. Please consult '
                'a qualified legal professional before making any decisions based on this analysis.')
            
            # Save PDF
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"contract_analysis_{timestamp}.pdf"
            
            output_path = self.output_dir / filename
            pdf.output(str(output_path))
            
            return str(output_path)
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def generate_simple_report(self, content: str, title: str = "Analysis Report") -> Optional[str]:
        """
        Generate a simple PDF with text content
        
        Args:
            content: Text content for the PDF
            title: Report title
            
        Returns:
            Path to generated PDF or None if failed
        """
        if not FPDF_AVAILABLE:
            return None
        
        try:
            pdf = ContractReportPDF()
            pdf.alias_nb_pages()
            pdf.add_page()
            
            pdf.set_font('Helvetica', 'B', 16)
            safe_title = title.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 10, safe_title, 0, 1, 'C')
            pdf.ln(10)
            
            pdf.body_text(content)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"report_{timestamp}.pdf"
            pdf.output(str(output_path))
            
            return str(output_path)
            
        except Exception as e:
            print(f"Error generating simple PDF: {e}")
            return None


# Quick test
if __name__ == "__main__":
    print("PDF Exporter Module")
    print("=" * 50)
    print(f"FPDF available: {FPDF_AVAILABLE}")
    
    if FPDF_AVAILABLE:
        exporter = PDFExporter()
        
        # Test data
        summary = {
            "contract_type": "Employment Agreement",
            "parties": ["ABC Corp", "John Doe"],
            "word_count": 2500,
            "language": "English"
        }
        
        risk_report = {
            "overall_score": 6.5,
            "overall_level": "MEDIUM",
            "high_risk_count": 2,
            "medium_risk_count": 3,
            "low_risk_count": 5,
            "summary": "Contract has moderate risk with some concerning clauses.",
            "findings": []
        }
        
        clauses = [
            {"clause_id": "1", "title": "Definitions", "category": "definitions", "content": "Sample content..."},
            {"clause_id": "2", "title": "Scope", "category": "scope", "content": "Sample content..."}
        ]
        
        path = exporter.generate_report(summary, risk_report, clauses)
        if path:
            print(f"Generated PDF: {path}")
        else:
            print("Failed to generate PDF")
