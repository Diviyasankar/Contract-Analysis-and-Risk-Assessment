"""
Audit Logger Module
JSON-based audit logging for contract analysis activities
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib


class AuditLogger:
    """
    Maintains audit trail of all contract analysis activities
    """
    
    def __init__(self, log_dir: str = "logs/audit"):
        """
        Initialize the audit logger
        
        Args:
            log_dir: Directory for storing audit logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = self._generate_session_id()
        self.session_log_file = self.log_dir / f"session_{self.session_id}.json"
        self.session_entries: List[Dict] = []
        
        # Initialize session
        self._log_event("session_start", {"message": "Audit session started"})
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return timestamp
    
    def _get_timestamp(self) -> str:
        """Get current ISO timestamp"""
        return datetime.now().isoformat()
    
    def _hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content for integrity verification"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event to the audit trail
        
        Args:
            event_type: Type of event
            data: Event data
        """
        entry = {
            "timestamp": self._get_timestamp(),
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data
        }
        
        self.session_entries.append(entry)
        self._save_session_log()
    
    def _save_session_log(self):
        """Save session log to file"""
        try:
            with open(self.session_log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": self.session_id,
                    "start_time": self.session_entries[0]["timestamp"] if self.session_entries else "",
                    "entries": self.session_entries
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving audit log: {e}")
    
    def log_document_upload(self, filename: str, file_size: int, 
                            content_hash: str = None, metadata: Dict = None):
        """
        Log document upload event
        
        Args:
            filename: Name of uploaded file
            file_size: Size in bytes
            content_hash: Hash of content (optional)
            metadata: Additional metadata
        """
        self._log_event("document_upload", {
            "filename": filename,
            "file_size_bytes": file_size,
            "content_hash": content_hash or "not_computed",
            "metadata": metadata or {}
        })
    
    def log_analysis_start(self, document_id: str, analysis_type: str):
        """
        Log start of analysis
        
        Args:
            document_id: Identifier for the document
            analysis_type: Type of analysis being performed
        """
        self._log_event("analysis_start", {
            "document_id": document_id,
            "analysis_type": analysis_type
        })
    
    def log_analysis_complete(self, document_id: str, analysis_type: str,
                               results_summary: Dict = None, duration_ms: int = None):
        """
        Log completion of analysis
        
        Args:
            document_id: Identifier for the document
            analysis_type: Type of analysis performed
            results_summary: Summary of results (no sensitive data)
            duration_ms: Duration in milliseconds
        """
        self._log_event("analysis_complete", {
            "document_id": document_id,
            "analysis_type": analysis_type,
            "results_summary": results_summary or {},
            "duration_ms": duration_ms
        })
    
    def log_risk_finding(self, document_id: str, risk_type: str, 
                          risk_level: str, clause_id: str = None):
        """
        Log a risk finding
        
        Args:
            document_id: Identifier for the document
            risk_type: Type of risk identified
            risk_level: Severity level
            clause_id: Related clause identifier
        """
        self._log_event("risk_finding", {
            "document_id": document_id,
            "risk_type": risk_type,
            "risk_level": risk_level,
            "clause_id": clause_id
        })
    
    def log_llm_call(self, model: str, prompt_type: str, 
                     tokens_used: int = None, success: bool = True):
        """
        Log LLM API call
        
        Args:
            model: Model used
            prompt_type: Type of prompt
            tokens_used: Number of tokens used
            success: Whether call succeeded
        """
        self._log_event("llm_call", {
            "model": model,
            "prompt_type": prompt_type,
            "tokens_used": tokens_used,
            "success": success
        })
    
    def log_export(self, document_id: str, export_format: str, 
                   export_path: str = None):
        """
        Log document export
        
        Args:
            document_id: Identifier for the document
            export_format: Format exported to
            export_path: Path where exported (optional, may be redacted)
        """
        self._log_event("export", {
            "document_id": document_id,
            "export_format": export_format,
            "export_path": export_path or "not_specified"
        })
    
    def log_user_action(self, action: str, details: Dict = None):
        """
        Log user action
        
        Args:
            action: Action performed
            details: Action details
        """
        self._log_event("user_action", {
            "action": action,
            "details": details or {}
        })
    
    def log_error(self, error_type: str, error_message: str, 
                  context: Dict = None):
        """
        Log error event
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        self._log_event("error", {
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        })
    
    def end_session(self, summary: Dict = None):
        """
        End the audit session
        
        Args:
            summary: Session summary
        """
        self._log_event("session_end", {
            "message": "Audit session ended",
            "total_events": len(self.session_entries),
            "summary": summary or {}
        })
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of current session
        
        Returns:
            Dictionary with session statistics
        """
        event_counts = {}
        for entry in self.session_entries:
            event_type = entry["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "total_events": len(self.session_entries),
            "event_counts": event_counts,
            "start_time": self.session_entries[0]["timestamp"] if self.session_entries else None,
            "log_file": str(self.session_log_file)
        }
    
    def get_recent_logs(self, count: int = 10) -> List[Dict]:
        """
        Get recent log entries
        
        Args:
            count: Number of entries to return
            
        Returns:
            List of recent log entries
        """
        return self.session_entries[-count:]
    
    @staticmethod
    def list_sessions(log_dir: str = "logs/audit") -> List[Dict]:
        """
        List all audit sessions
        
        Returns:
            List of session summaries
        """
        sessions = []
        log_path = Path(log_dir)
        
        if not log_path.exists():
            return sessions
        
        for log_file in log_path.glob("session_*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id"),
                        "start_time": data.get("start_time"),
                        "event_count": len(data.get("entries", [])),
                        "file": str(log_file)
                    })
            except Exception:
                continue
        
        return sorted(sessions, key=lambda x: x.get("start_time", ""), reverse=True)


# Quick test
if __name__ == "__main__":
    logger = AuditLogger()
    
    print("Audit Logger Module")
    print("=" * 50)
    print(f"Session ID: {logger.session_id}")
    print(f"Log file: {logger.session_log_file}")
    
    # Test logging
    logger.log_document_upload("test_contract.pdf", 102400)
    logger.log_analysis_start("doc_001", "full_analysis")
    logger.log_risk_finding("doc_001", "unlimited_liability", "HIGH", "clause_4.2")
    logger.log_analysis_complete("doc_001", "full_analysis", 
                                  {"risk_score": 7.5, "clauses_analyzed": 15})
    
    summary = logger.get_session_summary()
    print(f"\nSession Summary:")
    print(f"  Total events: {summary['total_events']}")
    print(f"  Event types: {summary['event_counts']}")
    
    logger.end_session()
