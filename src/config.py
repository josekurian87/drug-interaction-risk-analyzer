import os
from pathlib import Path
import httpx

# Disable ChromaDB telemetry to avoid external network calls/SSL warnings in corporate environment
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

PATIENTS_FILE = DATA_DIR / "patients.json"
DRUG_INTERACTIONS_FILE = DATA_DIR / "drug_interactions.json"
AUDIT_LOG_FILE = DATA_DIR / "audit_log.json"

# API & LLM Configuration
GENAILAB_BASE_URL = os.getenv("GENAILAB_BASE_URL", "https://genailab.tcs.in")
GENAILAB_API_KEY = os.getenv("GENAILAB_API_KEY", os.getenv("OPENAI_API_KEY", "sk-Mut1gBVm37S5poWPFZR7rg"))

LLM_MODEL = os.getenv("LLM_MODEL", "azure/genailab-maas-gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "azure/genailab-maas-text-embedding-3-large")

def get_httpx_client(timeout: float = 30.0) -> httpx.Client:
    """Returns an httpx client with SSL verification disabled for corporate proxy compatibility."""
    return httpx.Client(verify=False, timeout=timeout)
