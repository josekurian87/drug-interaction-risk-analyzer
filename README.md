# 💊 MedShield AI: Life Sciences Drug Interaction Risk Analyzer
### Precision Contextual Decision Support Designed to Eliminate Clinician Alert Fatigue

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/vectorstore-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![LangChain](https://img.shields.io/badge/orchestration-LangChain-brightgreen.svg)](https://langchain.com/)

---

## 📋 Overview & The Clinical Problem

In current Electronic Health Record (EHR) systems, **over 90% of drug-drug interaction (DDI) alerts are overridden or ignored by clinicians**. This occurs because conventional systems trigger alerts blindly based solely on drug pairs, without considering the patient's actual organ function, kidney clearance, hepatic enzymes, baseline laboratory values, or treatment duration.

**MedShield AI** solves this critical life sciences challenge by combining **FHIR-style patient context**, **ChromaDB vector retrieval over pharmacological mechanisms**, and **LLM contextual clinical reasoning** to:
1. **Actively Suppress Benign / False Positive Alerts**: When a drug pair has a theoretical interaction but the patient's lab markers (eGFR, ALT/AST, CK) and treatment duration prove it is safe, the alert is suppressed (`is_suppressed: true`), preserving clinical focus.
2. **Elevate Severe Contextual Risks**: When baseline lab abnormalities (e.g. supratherapeutic INR or Stage 3b CKD) turn an interaction into a fatal threat, it elevates the risk to **Critical**, highlights the specific driving lab markers, and suggests evidence-based substitutes.
3. **Guarantee Tamper-Evident Auditability**: Logs every clinical decision (substitutions, dose adjustments, and overrides with mandatory clinical justification) to a HIPAA-compliant audit trail.

---

## 🏛️ System Architecture

```
                                  +-----------------------------+
                                  |     Clinician Order Entry   |
                                  |   (Patient + Prescribed Med)|
                                  +--------------+--------------+
                                                 |
                                                 v
+------------------------+               +---------------+               +------------------------+
| FHIR Patient Profile   |-------------->|   RAG Engine  |<--------------| Local ChromaDB Store   |
| - Age, Conditions      |               |  (Similarity  |               | - DrugBank / RxNorm    |
| - Active Medications   |               |   & Pairwise) |               | - Pharmacological Mech |
| - Real-time Labs       |               +-------+-------+               | - Suppression Rules    |
+------------------------+                       |                       +------------------------+
                                                 v
                                  +-----------------------------+
                                  | LLM Contextual Reasoning    |
                                  | (azure/gpt-4o-mini / MaaS)  |
                                  +--------------+--------------+
                                                 |
                       +-------------------------+-------------------------+
                       |                                                   |
                       v                                                   v
         +---------------------------+                       +---------------------------+
         |  CRITICAL CONTEXTUAL RISK |                       | ALERT FATIGUE SUPPRESSED  |
         |  - Red Alert Banner       |                       | - Emerald Green Badge     |
         |  - Specific Driving Labs  |                       | - Rationale: Safe Labs    |
         +-------------+-------------+                       +-------------+-------------+
                       |                                                   |
                       +-------------------------+-------------------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  | Interactive Action Bar      |
                                  | - Accept Alternate Drug     |
                                  | - Adjust Dosage             |
                                  | - Override Alert w/ Reason  |
                                  +--------------+--------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  | Live HIPAA Audit Trail      |
                                  | (data/audit_log.json)       |
                                  +-----------------------------+
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Integration Tests
To verify vector database indexing, patient context formatting, and LLM inference across all clinical scenarios:
```bash
python test_pipeline.py
```
*Expected result: `ALL INTEGRATION TESTS PASSED SUCCESSFULLY! (100%)`*

### 4. Launch the Clinical Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Included Clinical Scenarios

| Case # | Patient | Active Medication | Prescribed Drug | Lab Findings | Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1** | **Eleanor Vance** (72F) | Warfarin (5mg daily) | **Amiodarone** (200mg daily) | **INR 3.2** (Supratherapeutic), **eGFR 34** (Stage 3b CKD) | 🔴 **Critical Risk**: CYP2C9 inhibition dramatically multiplies Warfarin serum level on already elevated INR. Suggests Apixaban or 50% dose cut. |
| **Case 2** | **Marcus Chen** (45M) | Atorvastatin (20mg daily) | **Azithromycin** (500mg daily, 5d) | **eGFR 95** (Normal), **ALT 22** (Normal), **CK 85** (Normal) | 🟢 **Alert Fatigue Suppressed**: Azithromycin is an azalide with negligible CYP3A4 inhibition; normal liver/kidney labs confirm safety. |
| **Case 3** | **Arthur Pendelton** (81M) | Spironolactone (25mg) | **Lisinopril** (10mg daily) | **Potassium 5.2** (Hyperkalemic), **eGFR 38** (CKD 3a) | 🔴 **Critical Risk**: Dual RAAS blockade impairs potassium excretion, creating lethal cardiac dysrhythmia threat. |
| **Case 4** | **Arthur Pendelton** (81M) | Furosemide + Spironolactone | **Ibuprofen** (600mg TID) | **Potassium 5.2**, **HFrEF** (EF 35%) | 🔴 **Critical Risk**: NSAID inhibits renal prostaglandins, blunts loop diuresis, and triggers acute decompensation. |

---

## 🔒 HIPAA Audit Trail & Compliance

Every prescriber interaction is captured in `data/audit_log.json` with:
- **Audit ID**: Unique identifier (e.g. `AUD-99101`)
- **UTC Timestamp**: ISO 8601 standardized format
- **Patient ID & MRN**: Patient context linkage
- **Risk Tier**: `Critical`, `Moderate`, or `Informational`
- **Alert Suppression State**: `True` / `False`
- **Clinician Action**:
  - `Accepted Alternative: {Drug}`
  - `Dose Adjusted`
  - `Overridden with Clinical Reason`
- **Mandatory Clinical Justification**: Required reason when an alert is overridden
- **Provider ID**: Attending clinician identification

The dashboard includes **Export to CSV** and **Export to JSON** capabilities for EHR interoperability and clinical governance audits.
