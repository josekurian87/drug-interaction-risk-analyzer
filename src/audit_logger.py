import json
import uuid
import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd
from src.config import AUDIT_LOG_FILE
from src.schemas import AuditLogRecord

class AuditLogger:
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or AUDIT_LOG_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def log_decision(
        self,
        patient_id: str,
        patient_name: str,
        prescribed_drug: str,
        risk_tier: str,
        is_suppressed: bool,
        action_taken: str,
        clinical_rationale: str = "",
        interacting_drug: Optional[str] = "None",
        clinician_id: str = "Dr. On-Duty Clinician, MD"
    ) -> AuditLogRecord:
        """Appends a new clinical action to the HIPAA audit log."""
        record = AuditLogRecord(
            audit_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            patient_id=patient_id,
            patient_name=patient_name,
            prescribed_drug=prescribed_drug,
            interacting_drug=interacting_drug or "None",
            risk_tier=risk_tier,
            is_suppressed=is_suppressed,
            action_taken=action_taken,
            clinical_rationale=clinical_rationale,
            clinician_id=clinician_id
        )

        entries = self.get_all_entries()
        entries.insert(0, record)  # most recent first

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in entries], f, indent=2)

        return record

    def get_all_entries(self) -> List[AuditLogRecord]:
        self._ensure_file_exists()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [AuditLogRecord.model_validate(item) for item in data]
        except Exception:
            return []

    def get_as_dataframe(self) -> pd.DataFrame:
        entries = self.get_all_entries()
        if not entries:
            return pd.DataFrame(columns=[
                "Timestamp", "Audit ID", "Patient", "Prescribed Drug", 
                "Risk Tier", "Suppressed", "Action Taken", "Clinician Rationale", "Provider"
            ])
        
        data = []
        for e in entries:
            data.append({
                "Timestamp": e.timestamp.replace("T", " ")[:19],
                "Audit ID": e.audit_id,
                "Patient ID": e.patient_id,
                "Patient": e.patient_name,
                "Prescribed Drug": e.prescribed_drug,
                "Interacting Drug": e.interacting_drug,
                "Risk Tier": e.risk_tier,
                "Suppressed": "Yes" if e.is_suppressed else "No",
                "Action Taken": e.action_taken,
                "Clinician Rationale": e.clinical_rationale,
                "Provider": e.clinician_id
            })
        return pd.DataFrame(data)
