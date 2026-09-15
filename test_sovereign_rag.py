"""
================================================================================
UNIT TESTS // SOVEREIGN ENTERPRISE RAG & RBAC PIPELINE
================================================================================
"""

import os
from vector_engine import SovereignVectorEngine
from vault_manager import SovereignVaultManager
from rag_engine import SovereignRAGEngine


def test_sovereign_rag_pipeline():
    test_db = "test_vault_general.json"
    if os.path.exists(test_db):
        os.remove(test_db)

    print(">>> 1. Initializing Sovereign Enterprise Vault...")
    vault = SovereignVaultManager(test_db)
    print(f"Loaded {len(vault.documents)} enterprise knowledge records.")
    assert len(vault.documents) >= 9, "Expected at least 9 default enterprise documents"

    print("\n>>> 2. Initializing Hybrid Vector Engine...")
    vector_engine = SovereignVectorEngine()
    rag = SovereignRAGEngine(vault, vector_engine)
    assert len(vector_engine.chunks) > 0, "Expected chunks to be indexed"
    print(f"Indexed {len(vector_engine.chunks)} chunks into hybrid vector space.")

    print("\n>>> 3. Testing Staging DB Query (Level 2 Authorized)...")
    res_stg = rag.query("What are the staging PostgreSQL database connection parameters?", user_clearance=2)
    assert len(res_stg["sources"]) > 0, "Expected sources in staging DB response"
    assert "postgres-stg.internal.enterprise.org" in str(res_stg["sources"]), "Expected host in response"
    print(f"SUCCESS: Staging DB retrieved (Score: {res_stg['sources'][0]['hybrid_score']}).")

    print("\n>>> 4. Testing RBAC Redaction: AWS Root Key queried by Level 1 (Intern)...")
    res_l1 = rag.query("What is the AWS Master IAM Root Secret Access Key?", user_clearance=1)
    for src in res_l1["sources"]:
        if src["clearance_level"] > 1:
            assert "[REDACTED" in src["text"] or not src["is_authorized"], "Level 4 secret must be redacted for Level 1"
    print("SUCCESS: AWS Root credentials strictly REDACTED for Level 1 user.")

    print("\n>>> 5. Testing Authorized Access: AWS Root Key queried by Level 4 (Security Lead)...")
    res_l4 = rag.query("What is the AWS Master IAM Root Secret Access Key?", user_clearance=4)
    assert any("AWS" in s["title"] for s in res_l4["sources"]), "Level 4 user must retrieve AWS root secret"
    print("SUCCESS: AWS Root credentials authorized for Level 4 user.")

    print("\n>>> 6. Testing Dynamic Tabular CSV Row Ingestion & Search...")
    sample_rows = [
        {"id": "EMP-909", "name": "Dr. Sarah Chen", "role": "Principal Quantum Architect", "clearance": "4", "department": "Quantum Labs"}
    ]
    added = vault.ingest_tabular_rows(sample_rows)
    rag.reindex_knowledge_base()
    res_emp = rag.query("Who is the Principal Quantum Architect?", user_clearance=4)
    assert any("Dr. Sarah Chen" in s["text"] for s in res_emp["sources"]), "Ingested row should be retrievable"
    print(f"SUCCESS: Dynamically ingested employee record successfully retrieved.")

    # Clean up test db
    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n=================================================================")
    print("  ALL SOVEREIGN RAG TESTS PASSED! (100% PURE PYTHON)")
    print("=================================================================")


if __name__ == "__main__":
    test_sovereign_rag_pipeline()
