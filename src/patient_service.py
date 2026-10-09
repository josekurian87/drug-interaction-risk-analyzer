import json
from typing import List, Optional, Dict
from pathlib import Path
from src.config import PATIENTS_FILE
from src.schemas import PatientRecord

class PatientService:
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or PATIENTS_FILE
        self._patients: Dict[str, PatientRecord] = {}
        self.reload()

    def reload(self) -> None:
        if not self.file_path.exists():
            self._patients = {}
            return

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._patients = {
                item["patient_id"]: PatientRecord.model_validate(item)
                for item in data
            }

    def get_all_patients(self) -> List[PatientRecord]:
        return list(self._patients.values())

    def get_patient(self, patient_id: str) -> Optional[PatientRecord]:
        return self._patients.get(patient_id)

    def get_patient_medication_names(self, patient_id: str) -> List[str]:
        patient = self.get_patient(patient_id)
        if not patient:
            return []
        return [med.name for med in patient.current_medications]

    def get_abnormal_labs(self, patient_id: str) -> Dict[str, dict]:
        """Returns only labs marked as High, Low, or Critical."""
        patient = self.get_patient(patient_id)
        if not patient:
            return {}
        
        abnormal = {}
        for test_name, lab in patient.recent_labs.items():
            if lab.status.lower() != "normal":
                abnormal[test_name] = lab.model_dump()
        return abnormal

    def format_patient_context(self, patient_id: str) -> str:
        """Formats comprehensive patient context for LLM prompt ingestion."""
        patient = self.get_patient(patient_id)
        if not patient:
            return "No patient record found."

        med_list = [f"- {m.name} {m.dosage} ({m.frequency})" for m in patient.current_medications]
        
        lab_list = []
        for test_name, lab in patient.recent_labs.items():
            lab_list.append(f"- {test_name.upper()}: {lab.value} {lab.unit} (Ref: {lab.reference_range}) -> Status: {lab.status} [{lab.interpretation}]")

        context = f"""PATIENT DEMOGRAPHICS & CLINICAL RECORD:
Name: {patient.name} | Age: {patient.age} | Gender: {patient.gender} | MRN: {patient.mrn}
Active Conditions: {", ".join(patient.conditions)}
Allergies: {", ".join(patient.allergies) if patient.allergies else "NKDA"}

CURRENT ACTIVE MEDICATIONS:
{chr(10).join(med_list)}

RECENT LAB RESULTS & ORGAN FUNCTION:
{chr(10).join(lab_list)}

CLINICAL NOTES:
{patient.notes or "None"}
"""
        return context
