"""
================================================================================
UNIT TESTS // SOVEREIGN RAG COAL MINES WORKER & CREDENTIAL REGISTRY
================================================================================
"""

import os
from vector_engine import SovereignVectorEngine
from vault_manager import SovereignVaultManager
from rag_engine import SovereignRAGEngine

def test_coal_mines_rag_pipeline():
    test_db = "test_vault_coal_mine.json"
    if os.path.exists(test_db):
        os.remove(test_db)

    print(">>> 1. Initializing Sovereign Coal Mines Vault...")
    vault = SovereignVaultManager(test_db)
    print(f"Loaded {len(vault.documents)} worker personnel records.")
    assert len(vault.documents) >= 9, "Expected at least 9 default worker records"

    print("\n>>> 2. Initializing Hybrid Vector Engine...")
    vector_engine = SovereignVectorEngine()
    rag = SovereignRAGEngine(vault, vector_engine)
    assert len(vector_engine.chunks) > 0, "Expected chunks to be indexed"
    print(f"Indexed {len(vector_engine.chunks)} chunks into hybrid vector space.")

    print("\n>>> 3. Testing Worker Lookup: Continuous Miner Operator (Worker ID MINE-OPS-4108)...")
    res_cm = rag.query("Find Continuous Miner Operator with Worker ID MINE-OPS-4108", user_clearance=2)
    assert "Harpreet Singh Sandhu" in res_cm["response"], "Expected Harpreet Singh Sandhu in response"
    assert "MINE-OPS-4108" in res_cm["response"], "Expected Worker ID in response"
    print(f"SUCCESS: Continuous Miner Operator found (Score: {res_cm['sources'][0]['hybrid_score']}).")

    print("\n>>> 4. Testing Worker Lookup: Blasting & Explosives Engineer (Worker ID MINE-EXP-2044)...")
    res_blast = rag.query("Who is the Blasting & Explosives Engineer with Worker ID MINE-EXP-2044?", user_clearance=3)
    assert "Vikramaditya Singh" in res_blast["response"], "Expected Vikramaditya Singh in response"
    assert "Shotfirer Certificate" in res_blast["response"], "Expected DGMS certification in response"
    print(f"SUCCESS: Blasting Engineer record retrieved (Score: {res_blast['sources'][0]['hybrid_score']}).")

    print("\n>>> 5. Testing RBAC Redaction: Explosives Passcode queried by Level 1 (Trainee)...")
    res_l1 = rag.query("What is the underground explosives magazine passcode for Vikramaditya Singh?", user_clearance=1)
    assert "[REDACTED" in res_l1["response"], "Explosives passcode must be redacted for Level 1"
    assert "EXPL-BLAST-7729" not in res_l1["response"], "Passcode must not leak to unauthorized trainee"
    print(f"SUCCESS: Explosives magazine passcode strictly REDACTED for Level 1 user.")

    print("\n>>> 6. Testing Authorized Access: Explosives Passcode queried by Level 4 (Mine Manager)...")
    res_l4 = rag.query("What is the underground explosives magazine passcode for Vikramaditya Singh?", user_clearance=4)
    assert "EXPL-BLAST-7729" in res_l4["response"], "Passcode should be visible to authorized Mine Manager"
    print(f"SUCCESS: Explosives passcode authorized for Level 4 Mine Manager.")

    # Clean up test db
    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n=================================================================")
    print("  ALL COAL MINES WORKER RAG TESTS PASSED! (100% PURE PYTHON)")
    print("=================================================================")

if __name__ == "__main__":
    test_coal_mines_rag_pipeline()
