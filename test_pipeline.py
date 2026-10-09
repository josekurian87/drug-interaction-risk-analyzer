import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("test_pipeline")

from src.patient_service import PatientService
from src.rag_engine import RAGEngine
from src.audit_logger import AuditLogger

def run_tests():
    logger.info("==================================================")
    logger.info("STARTING DRUG INTERACTION RISK ANALYZER TESTS")
    logger.info("==================================================")

    # 1. Test Patient Service
    logger.info("Test 1: Patient Service Loading...")
    patient_service = PatientService()
    patients = patient_service.get_all_patients()
    assert len(patients) >= 3, f"Expected at least 3 patients, found {len(patients)}"
    logger.info(f"Loaded {len(patients)} synthetic patients successfully.")
    
    p1 = patient_service.get_patient("PAT-1001")
    assert p1 is not None and p1.name == "Eleanor Vance"
    abnormal_p1 = patient_service.get_abnormal_labs("PAT-1001")
    assert "inr" in abnormal_p1 and "egfr" in abnormal_p1
    logger.info(f"P1 ({p1.name}) abnormal labs verified: INR={p1.recent_labs['inr'].value}, eGFR={p1.recent_labs['egfr'].value}")

    # 2. Test Audit Logger
    logger.info("\nTest 2: Audit Logger Verification...")
    audit_logger = AuditLogger()
    initial_count = len(audit_logger.get_all_entries())
    log_record = audit_logger.log_decision(
        patient_id="PAT-TEST",
        patient_name="Test Patient",
        prescribed_drug="TestDrug 10mg",
        risk_tier="Critical",
        is_suppressed=False,
        action_taken="Accepted Alternative",
        clinical_rationale="Automated test validation rationale"
    )
    assert log_record.audit_id.startswith("AUD-")
    df = audit_logger.get_as_dataframe()
    assert len(df) == initial_count + 1
    logger.info(f"Audit log successfully recorded entry: {log_record.audit_id}")

    # 3. Test RAG Engine Initialization & Vector Store
    logger.info("\nTest 3: RAG Engine Initialization & ChromaDB Vector Store...")
    rag_engine = RAGEngine()
    assert rag_engine.vector_store is not None
    logger.info("RAG Engine vector store initialized.")

    # 4. Test Case 1: Severe Contextual Risk (Eleanor Vance + Amiodarone)
    logger.info("\nTest 4: Running Case 1 (Severe Contextual Risk: Eleanor Vance + Amiodarone)...")
    res1 = rag_engine.analyze_prescription(p1, "Amiodarone 200mg daily")
    logger.info(f"Case 1 Result: Risk Level: {res1.risk_level} | Suppressed: {res1.is_suppressed}")
    logger.info(f"Context Factors: {res1.context_factors}")
    logger.info(f"Clinical Summary: {res1.clinical_summary}")
    logger.info(f"Recommended Action: {res1.recommended_action}")
    assert res1.risk_level == "Critical", f"Expected Critical, got {res1.risk_level}"
    assert res1.is_suppressed is False, f"Expected not suppressed, got {res1.is_suppressed}"
    logger.info("PASS Case 1: Critical alert triggered and contextual risk highlighted correctly.")

    # 5. Test Case 2: Benign / Contextually Suppressed (Marcus Chen + Azithromycin)
    logger.info("\nTest 5: Running Case 2 (Benign / Contextually Suppressed: Marcus Chen + Azithromycin)...")
    p2 = patient_service.get_patient("PAT-1002")
    res2 = rag_engine.analyze_prescription(p2, "Azithromycin 500mg daily for 5 days")
    logger.info(f"Case 2 Result: Risk Level: {res2.risk_level} | Suppressed: {res2.is_suppressed}")
    logger.info(f"Suppression Reason: {res2.suppression_reason}")
    logger.info(f"Context Factors: {res2.context_factors}")
    assert res2.is_suppressed is True, f"Expected suppressed alert, got {res2.is_suppressed}"
    logger.info("PASS Case 2: Alert fatigue eliminated! Benign interaction contextually suppressed.")

    # 6. Test Case 3: Polypharmacy Risk (Arthur Pendelton + Lisinopril)
    logger.info("\nTest 6: Running Case 3 (Elderly Polypharmacy: Arthur Pendelton + Lisinopril)...")
    p3 = patient_service.get_patient("PAT-1003")
    res3 = rag_engine.analyze_prescription(p3, "Lisinopril 10mg daily")
    logger.info(f"Case 3 Result: Risk Level: {res3.risk_level} | Suppressed: {res3.is_suppressed}")
    logger.info(f"Context Factors: {res3.context_factors}")
    assert res3.risk_level in ["Critical", "Moderate"]
    logger.info("PASS Case 3: Polypharmacy hyperkalemia/renal risk identified.")

    logger.info("\n==================================================")
    logger.info("ALL INTEGRATION TESTS PASSED SUCCESSFULLY! (100%)")
    logger.info("==================================================")

if __name__ == "__main__":
    run_tests()
