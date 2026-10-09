import json
import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config FIRST before any other Streamlit commands
st.set_page_config(
    page_title="MedShield | Drug Interaction Risk Analyzer",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.patient_service import PatientService
from src.rag_engine import RAGEngine
from src.audit_logger import AuditLogger
from src.config import DRUG_INTERACTIONS_FILE

# Modern Medical Dashboard Custom CSS
st.markdown("""
<style>
    /* Global Typography & Palette */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* Clinical Header */
    .clinical-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
        border: 1px solid #334155;
    }
    .clinical-header h1 {
        margin: 0;
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #f8fafc;
    }
    .clinical-header p {
        margin: 0.35rem 0 0 0;
        font-size: 0.95rem;
        color: #94a3b8;
    }

    /* Status Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
    }

    /* Cards */
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Lab Metric Chips */
    .lab-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
        gap: 10px;
        margin-top: 0.5rem;
    }
    .lab-chip {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 10px;
        text-align: center;
    }
    .lab-chip-name {
        font-size: 0.72rem;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
    }
    .lab-chip-val {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        margin: 2px 0;
    }
    .lab-chip-status {
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
    }
    .lab-normal {
        background: #dcfce7;
        color: #15803d;
    }
    .lab-warning {
        background: #fef3c7;
        color: #b45309;
    }
    .lab-critical {
        background: #fee2e2;
        color: #b91c1c;
    }

    /* Alert Banners */
    .alert-critical {
        background: #fef2f2;
        border-left: 6px solid #ef4444;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        border-top: 1px solid #fecaca;
        border-right: 1px solid #fecaca;
        border-bottom: 1px solid #fecaca;
    }
    .alert-moderate {
        background: #fffbeb;
        border-left: 6px solid #f59e0b;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        border-top: 1px solid #fde68a;
        border-right: 1px solid #fde68a;
        border-bottom: 1px solid #fde68a;
    }
    .alert-suppressed {
        background: #f0fdf4;
        border-left: 6px solid #10b981;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        border-top: 1px solid #bbf7d0;
        border-right: 1px solid #bbf7d0;
        border-bottom: 1px solid #bbf7d0;
    }

    /* Context Callout Box */
    .context-callout {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        margin: 0.75rem 0;
        font-size: 0.92rem;
    }

    /* Condition Badges */
    .badge-condition {
        background: #e0e7ff;
        color: #3730a3;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
    }

    /* Button Styling */
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services in Session State
@st.cache_resource
def get_patient_service():
    return PatientService()

@st.cache_resource
def get_rag_engine():
    return RAGEngine()

@st.cache_resource
def get_audit_logger():
    return AuditLogger()

patient_service = get_patient_service()
rag_engine = get_rag_engine()
audit_logger = get_audit_logger()

# Session State for Active Order & Analysis
if "active_prescribed_drug" not in st.session_state:
    st.session_state.active_prescribed_drug = "Amiodarone 200mg daily"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "selected_patient_id" not in st.session_state:
    st.session_state.selected_patient_id = "PAT-1001"
if "action_feedback" not in st.session_state:
    st.session_state.action_feedback = None

# TOP CLINICAL HEADER
st.markdown("""
<div class="clinical-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1>💊 MedShield | Drug Interaction Risk Analyzer</h1>
            <p>Precision Contextual Clinical Decision Support &bull; Eliminating EHR Alert Fatigue with FHIR RAG</p>
        </div>
        <div style="display: flex; gap: 10px; margin-top: 6px;">
            <div class="status-pill"><div class="status-dot"></div> ChromaDB Vector Store Active</div>
            <div class="status-pill"><div class="status-dot"></div> GenAILab LLM Online</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR: PATIENT SELECTOR & EHR SUMMARY
patients = patient_service.get_all_patients()
patient_options = {f"{p.name} ({p.patient_id}) - Age {p.age}": p.patient_id for p in patients}

with st.sidebar:
    st.markdown("### 👤 Patient Selection")
    
    # Reverse lookup for selectbox
    current_index = 0
    for idx, (label, pid) in enumerate(patient_options.items()):
        if pid == st.session_state.selected_patient_id:
            current_index = idx
            break

    selected_label = st.selectbox(
        "Choose Patient Profile",
        options=list(patient_options.keys()),
        index=current_index,
        key="patient_selector_dropdown"
    )
    selected_pid = patient_options[selected_label]
    
    if selected_pid != st.session_state.selected_patient_id:
        st.session_state.selected_patient_id = selected_pid
        st.session_state.analysis_result = None
        st.session_state.action_feedback = None
        st.rerun()

    active_patient = patient_service.get_patient(st.session_state.selected_patient_id)

    if active_patient:
        st.markdown("---")
        st.markdown(f"**Medical Record #:** `{active_patient.mrn}`")
        st.markdown(f"**Sex / Age:** {active_patient.gender}, {active_patient.age} years old")
        
        st.markdown("**Active Clinical Diagnoses:**")
        conditions_html = "".join([f'<span class="badge-condition">{c}</span>' for c in active_patient.conditions])
        st.markdown(conditions_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**🧪 Key Laboratory & Organ Markers:**")
        labs_html = ['<div class="lab-grid">']
        for lab_key, lab in active_patient.recent_labs.items():
            status_class = "lab-normal"
            if "high" in lab.status.lower() or "critical" in lab.status.lower():
                status_class = "lab-critical"
            elif "low" in lab.status.lower():
                status_class = "lab-warning"
            
            labs_html.append(f"""
                <div class="lab-chip">
                    <div class="lab-chip-name">{lab_key}</div>
                    <div class="lab-chip-val">{lab.value}</div>
                    <span class="lab-chip-status {status_class}">{lab.status}</span>
                </div>
            """)
        labs_html.append('</div>')
        st.markdown("".join(labs_html), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**📋 Current Active Prescriptions:**")
        for med in active_patient.current_medications:
            st.markdown(f"- **{med.name}** {med.dosage} &bull; *{med.frequency}*")
            if med.indication:
                st.caption(f"  ↳ Indication: {med.indication}")

        st.markdown("---")
        st.markdown(f"**Allergies:** {', '.join(active_patient.allergies) if active_patient.allergies else 'NKDA'}")
        if active_patient.notes:
            st.caption(f"**Clinical Note:** {active_patient.notes}")

# MAIN CONTENT AREA: TABS
tab_analysis, tab_audit, tab_knowledge = st.tabs([
    "🩺 Clinical Workspace & Risk Analysis", 
    "📜 Live HIPAA Audit Trail", 
    "📚 Pharmacological Knowledge Base & RAG Inspector"
])

# ==========================================
# TAB 1: CLINICAL WORKSPACE & RISK ANALYSIS
# ==========================================
with tab_analysis:
    st.markdown("#### ⚡ Prescription Order Simulation")
    st.caption("Quickly load pre-configured high-impact clinical scenarios to see how MedShield resolves alert fatigue vs. critical threats:")

    # Quick Scenario Buttons
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🔴 Case 1: Amiodarone\n(Eleanor Vance - Severe Risk)", use_container_width=True):
            st.session_state.selected_patient_id = "PAT-1001"
            st.session_state.active_prescribed_drug = "Amiodarone 200mg daily"
            st.session_state.analysis_result = None
            st.session_state.action_feedback = None
            st.rerun()
    with c2:
        if st.button("🟢 Case 2: Azithromycin\n(Marcus Chen - Suppressed)", use_container_width=True):
            st.session_state.selected_patient_id = "PAT-1002"
            st.session_state.active_prescribed_drug = "Azithromycin 500mg daily (5-day course)"
            st.session_state.analysis_result = None
            st.session_state.action_feedback = None
            st.rerun()
    with c3:
        if st.button("🔴 Case 3: Lisinopril\n(Arthur - Hyperkalemia)", use_container_width=True):
            st.session_state.selected_patient_id = "PAT-1003"
            st.session_state.active_prescribed_drug = "Lisinopril 10mg daily"
            st.session_state.analysis_result = None
            st.session_state.action_feedback = None
            st.rerun()
    with c4:
        if st.button("⚠️ Case 4: Ibuprofen\n(Arthur - Renal Decomp.)", use_container_width=True):
            st.session_state.selected_patient_id = "PAT-1003"
            st.session_state.active_prescribed_drug = "Ibuprofen 600mg PO TID"
            st.session_state.analysis_result = None
            st.session_state.action_feedback = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Order Input Form
    with st.container():
        st.markdown(f"**New Prescription for {active_patient.name} (MRN: {active_patient.mrn}):**")
        col_input, col_dose, col_btn = st.columns([3, 2, 2])
        
        with col_input:
            prescribed_drug_input = st.text_input(
                "Medication Name", 
                value=st.session_state.active_prescribed_drug,
                placeholder="e.g. Amiodarone, Azithromycin, Lisinopril..."
            )
        with col_dose:
            dosage_input = st.text_input(
                "Dosage / Regimen", 
                value="Standard clinical dosage", 
                placeholder="e.g. 200mg PO daily"
            )
        with col_btn:
            st.write("") # spacing
            st.write("")
            analyze_clicked = st.button("⚡ Analyze Risk with RAG", type="primary", use_container_width=True)

    # Execute Analysis
    if analyze_clicked:
        with st.spinner("Retrieving pharmacological knowledge from ChromaDB and evaluating patient labs..."):
            result = rag_engine.analyze_prescription(
                patient=active_patient,
                prescribed_drug=prescribed_drug_input,
                dosage=dosage_input
            )
            st.session_state.analysis_result = result
            st.session_state.action_feedback = None

    # Display Action Toast / Feedback if any
    if st.session_state.action_feedback:
        st.success(st.session_state.action_feedback)

    # Display Analysis Result Card
    res = st.session_state.analysis_result
    if res:
        st.markdown("---")
        
        # 1. RISK LEVEL BANNER
        if res.risk_level == "Critical":
            st.markdown(f"""
            <div class="alert-critical">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #991b1b;">
                        🔴 CRITICAL INTERACTION DETECTED — ACTION REQUIRED
                    </div>
                    <span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.82rem;">
                        TIER 1 CRITICAL
                    </span>
                </div>
                <div style="margin-top: 6px; font-size: 0.96rem; color: #7f1d1d;">
                    Concomitant administration of <strong>{res.prescribed_drug}</strong> with <strong>{res.interacting_drug or 'Active Regimen'}</strong> poses severe patient harm.
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif res.risk_level == "Moderate":
            st.markdown(f"""
            <div class="alert-moderate">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #92400e;">
                        🟡 MODERATE INTERACTION — CLINICAL MONITORING REQUIRED
                    </div>
                    <span style="background: #f59e0b; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.82rem;">
                        TIER 2 MODERATE
                    </span>
                </div>
                <div style="margin-top: 6px; font-size: 0.96rem; color: #78350f;">
                    Caution advised for <strong>{res.prescribed_drug}</strong> with <strong>{res.interacting_drug or 'Active Regimen'}</strong>. Dose titration or lab tracking indicated.
                </div>
            </div>
            """, unsafe_allow_html=True)

        else: # Informational / Suppressed
            st.markdown(f"""
            <div class="alert-suppressed">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #065f46;">
                        🟢 ALERT FATIGUE ELIMINATED: BENIGN CLINICAL CONTEXT
                    </div>
                    <span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.82rem;">
                        TIER 3 SUPPRESSED
                    </span>
                </div>
                <div style="margin-top: 6px; font-size: 0.96rem; color: #047857;">
                    Standard EHRs flag a generic warning for this pair, but patient's preserved organ function and normal lab biomarkers confirm safety.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. CONTEXTUAL FACTORS CALLOUT
        st.markdown("##### 🧬 Triggering Clinical Context & Laboratory Values")
        if res.is_suppressed:
            st.markdown(f"""
            <div class="context-callout" style="border-left: 4px solid #10b981;">
                <strong>✅ Alert Fatigue Suppression Rationale:</strong><br>
                {res.suppression_reason or 'Patient organ profile and baseline labs demonstrate full clearance reserve.'}
            </div>
            """, unsafe_allow_html=True)
        else:
            factors_list = "".join([f"<li><strong>{f}</strong></li>" for f in res.context_factors]) if res.context_factors else "<li>Baseline patient clinical vulnerability identified.</li>"
            st.markdown(f"""
            <div class="context-callout" style="border-left: 4px solid #ef4444;">
                <strong>⚠️ Specific Patient Context Factors Elevating Risk:</strong>
                <ul style="margin: 6px 0 2px 20px; padding: 0;">
                    {factors_list}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 3. CLINICAL SUMMARY & MECHANISM
        st.markdown("##### 🔬 Pharmacological Mechanism & Threat Evaluation")
        st.info(res.clinical_summary)

        # 4. RECOMMENDED CLINICAL ACTION
        st.markdown("##### 💡 Evidence-Based Recommendation")
        st.success(f"**Action Protocol:** {res.recommended_action}")

        # 5. ACTIONABLE DECISION BAR
        st.markdown("##### 🩺 Clinical Action Bar")
        st.caption("Select an action below to update prescription order and automatically record a HIPAA-compliant audit entry:")

        act_col1, act_col2, act_col3 = st.columns(3)

        with act_col1:
            # Action 1: Accept Alternate Drug
            recommended_alt = "Apixaban 5mg BID" if "amiodarone" in res.prescribed_drug.lower() else "Acetaminophen 1000mg PO TID"
            if st.button("✅ Accept Alternate Drug", use_container_width=True, type="secondary"):
                entry = audit_logger.log_decision(
                    patient_id=active_patient.patient_id,
                    patient_name=active_patient.name,
                    prescribed_drug=res.prescribed_drug,
                    interacting_drug=res.interacting_drug,
                    risk_tier=res.risk_level,
                    is_suppressed=res.is_suppressed,
                    action_taken=f"Accepted Alternative: {recommended_alt}",
                    clinical_rationale=f"Replaced {res.prescribed_drug} with evidence-based alternative to eliminate adverse drug event risk."
                )
                st.session_state.action_feedback = f"✅ Order updated! Substituted with {recommended_alt}. Recorded in Audit Trail ({entry.audit_id})."
                st.rerun()

        with act_col2:
            # Action 2: Adjust Dose
            with st.popover("⚖️ Adjust Dosage", use_container_width=True):
                st.write("**Modify Dosage or Regimen**")
                adjusted_dose_input = st.text_input("New Dose Instructions", value="Reduce dose by 50% with serial lab checks")
                if st.button("Confirm Dose Adjustment"):
                    entry = audit_logger.log_decision(
                        patient_id=active_patient.patient_id,
                        patient_name=active_patient.name,
                        prescribed_drug=res.prescribed_drug,
                        interacting_drug=res.interacting_drug,
                        risk_tier=res.risk_level,
                        is_suppressed=res.is_suppressed,
                        action_taken="Dose Adjusted",
                        clinical_rationale=f"Dose adjusted: {adjusted_dose_input}"
                    )
                    st.session_state.action_feedback = f"⚖️ Dose adjustment recorded: '{adjusted_dose_input}' (Audit ID: {entry.audit_id})."
                    st.rerun()

        with act_col3:
            # Action 3: Override Alert with Clinical Reason
            with st.popover("⚠️ Override Alert", use_container_width=True):
                st.write("**Override Alert with Justification**")
                reason_option = st.selectbox(
                    "Clinical Justification Reason",
                    options=[
                        "Inpatient setting with continuous telemetry monitoring",
                        "Short-course bridge therapy (<= 48 hours)",
                        "Clinical benefit decisively outweighs pharmacokinetic risk",
                        "Patient previously tolerated this combination without adverse events",
                        "Alternate agents contraindicated or clinically ineffective"
                    ]
                )
                clinician_notes = st.text_area("Optional Clinician Notes", placeholder="e.g. Checked by attending cardiologist...")
                if st.button("Confirm Clinical Override", type="primary"):
                    full_rationale = f"{reason_option}. {clinician_notes}".strip()
                    entry = audit_logger.log_decision(
                        patient_id=active_patient.patient_id,
                        patient_name=active_patient.name,
                        prescribed_drug=res.prescribed_drug,
                        interacting_drug=res.interacting_drug,
                        risk_tier=res.risk_level,
                        is_suppressed=res.is_suppressed,
                        action_taken="Overridden with Clinical Reason",
                        clinical_rationale=full_rationale
                    )
                    st.session_state.action_feedback = f"⚠️ Alert overridden by clinician: '{reason_option}' (Audit ID: {entry.audit_id})."
                    st.rerun()

        # 6. RETRIEVED PHARMACOLOGICAL EVIDENCE (CHROMA RAG INSPECTOR)
        with st.expander("🔍 View Retrieved Pharmacological Evidence Chunks (ChromaDB Vector Retrieval)"):
            if res.retrieved_evidence:
                for idx, ev in enumerate(res.retrieved_evidence, 1):
                    st.markdown(f"**Knowledge Chunk #{idx}** (Relevance Score: `{ev.get('relevance_score', 0):.2f}`)")
                    st.code(ev.get("content", ""), language="text")
            else:
                st.caption("No ChromaDB vector chunks retrieved.")

# ==========================================
# TAB 2: LIVE HIPAA AUDIT TRAIL
# ==========================================
with tab_audit:
    st.markdown("#### 📜 HIPAA-Compliant Prescription Audit Trail")
    st.caption("Immutable tamper-evident logging of all contextual alert interactions, substitutions, dose titrations, and clinician overrides.")

    audit_df = audit_logger.get_as_dataframe()

    # Metrics Summary Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Events Logged", len(audit_df))
    with m2:
        critical_count = len(audit_df[audit_df["Risk Tier"] == "Critical"]) if not audit_df.empty else 0
        st.metric("Critical Alerts Handled", critical_count)
    with m3:
        suppressed_count = len(audit_df[audit_df["Suppressed"] == "Yes"]) if not audit_df.empty else 0
        st.metric("Alert Fatigue Suppressed", suppressed_count)
    with m4:
        override_count = len(audit_df[audit_df["Action Taken"].str.contains("Override", case=False, na=False)]) if not audit_df.empty else 0
        st.metric("Clinical Overrides", override_count)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtering Controls
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        patient_filter = st.selectbox("Filter by Patient", ["All Patients"] + sorted(audit_df["Patient"].unique().tolist()) if not audit_df.empty else ["All Patients"])
    with f_col2:
        tier_filter = st.selectbox("Filter by Risk Tier", ["All Tiers", "Critical", "Moderate", "Informational"])
    with f_col3:
        search_query = st.text_input("Search Clinical Rationale / Drug", placeholder="e.g. Warfarin, Apixaban...")

    filtered_df = audit_df.copy()
    if not filtered_df.empty:
        if patient_filter != "All Patients":
            filtered_df = filtered_df[filtered_df["Patient"] == patient_filter]
        if tier_filter != "All Tiers":
            filtered_df = filtered_df[filtered_df["Risk Tier"] == tier_filter]
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Prescribed Drug"].str.contains(search_query, case=False, na=False) |
                filtered_df["Clinician Rationale"].str.contains(search_query, case=False, na=False) |
                filtered_df["Action Taken"].str.contains(search_query, case=False, na=False)
            ]

    # Render Table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp": st.column_config.TextColumn("UTC Timestamp", width="medium"),
            "Audit ID": st.column_config.TextColumn("Audit ID", width="small"),
            "Risk Tier": st.column_config.TextColumn("Risk Tier", width="small"),
            "Action Taken": st.column_config.TextColumn("Action Taken", width="medium"),
            "Clinician Rationale": st.column_config.TextColumn("Clinical Justification", width="large")
        }
    )

    # Export Buttons
    exp_c1, exp_c2, _ = st.columns([1.5, 1.5, 4])
    with exp_c1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"hipaa_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with exp_c2:
        json_data = filtered_df.to_json(orient="records", indent=2).encode('utf-8')
        st.download_button(
            label="📥 Export JSON",
            data=json_data,
            file_name=f"hipaa_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# ==========================================
# TAB 3: PHARMACOLOGICAL KNOWLEDGE BASE
# ==========================================
with tab_knowledge:
    st.markdown("#### 📚 Pharmacological Knowledge Base & Vector Index")
    st.caption("Standard DrugBank/RxNorm interaction entries indexed into ChromaDB embeddings for vector similarity retrieval:")

    if DRUG_INTERACTIONS_FILE.exists():
        with open(DRUG_INTERACTIONS_FILE, "r", encoding="utf-8") as f:
            interactions = json.load(f)

        for item in interactions:
            severity_badge = "🔴 Critical" if item["severity"] == "Critical" else ("🟡 Moderate" if item["severity"] == "Moderate" else "🟢 Informational")
            with st.expander(f"{item['drug_a']} + {item['drug_b']} ({severity_badge}) - ID: {item['interaction_id']}"):
                st.markdown(f"**Mechanism of Action:**\n{item['mechanism_of_action']}")
                st.markdown(f"**Contraindicated Labs / Conditions:**\n`{item['contraindicated_conditions_or_labs']}`")
                st.markdown(f"**Recommended Alternative:**\n{item['recommended_alternative']}")
                st.markdown(f"**Monitoring Protocol:**\n{item['monitoring_protocol']}")
                if item.get("alert_suppression_criteria"):
                    st.markdown(f"**Alert Fatigue Suppression Criteria:**\n*{item['alert_suppression_criteria']}*")

        st.markdown("---")
        if st.button("🔄 Force Rebuild ChromaDB Vector Index"):
            with st.spinner("Rebuilding ChromaDB vector embeddings..."):
                rag_engine.rebuild_index()
                st.success("ChromaDB vector store rebuilt successfully!")
