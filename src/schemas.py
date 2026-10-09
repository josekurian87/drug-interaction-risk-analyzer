from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

class LabMeasurement(BaseModel):
    value: float
    unit: str
    reference_range: str
    status: str
    interpretation: str

class MedicationOrder(BaseModel):
    name: str
    dosage: str
    route: str = "Oral"
    frequency: str = "Once daily"
    indication: Optional[str] = None

class PatientRecord(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    mrn: str
    conditions: List[str]
    current_medications: List[MedicationOrder]
    recent_labs: Dict[str, LabMeasurement]
    allergies: List[str] = []
    notes: Optional[str] = None

class DrugInteractionItem(BaseModel):
    interaction_id: str
    drug_a: str
    drug_b: str
    severity: Literal["Critical", "Moderate", "Informational"]
    mechanism_of_action: str
    contraindicated_conditions_or_labs: str
    recommended_alternative: str
    monitoring_protocol: str
    alert_suppression_criteria: Optional[str] = None

class RiskAnalysisResult(BaseModel):
    risk_level: Literal["Critical", "Moderate", "Informational"]
    is_suppressed: bool
    suppression_reason: Optional[str] = None
    context_factors: List[str] = Field(default_factory=list)
    clinical_summary: str
    recommended_action: str
    interaction_detected: bool = True
    interacting_drug: Optional[str] = None
    prescribed_drug: str
    retrieved_evidence: List[Dict[str, Any]] = Field(default_factory=list)

class AuditLogRecord(BaseModel):
    audit_id: str
    timestamp: str
    patient_id: str
    patient_name: str
    prescribed_drug: str
    interacting_drug: Optional[str] = "None"
    risk_tier: str
    is_suppressed: bool
    action_taken: str
    clinical_rationale: Optional[str] = ""
    clinician_id: str = "Dr. On-Duty Clinician"
