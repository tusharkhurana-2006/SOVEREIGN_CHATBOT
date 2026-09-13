"""
================================================================================
SOVEREIGN RAG PIPELINE // ORCHESTRATION, RBAC & SYNTHESIS ENGINE
Air-Gapped Retrieval-Augmented Generation with Dynamic Redaction & Audit
================================================================================
"""

import re
import time
from typing import List, Dict, Any, Tuple, Optional
from vector_engine import SovereignVectorEngine, Chunk
from vault_manager import SovereignVaultManager, CLEARANCE_LEVELS


class SovereignRAGEngine:
    def __init__(self, vault: SovereignVaultManager, vector_engine: SovereignVectorEngine):
        self.vault = vault
        self.vector_engine = vector_engine
        self.audit_logs: List[Dict[str, Any]] = []
        self.reindex_knowledge_base()

    def reindex_knowledge_base(self):
        """Chunks and indexes all vault documents into the vector engine."""
        self.vector_engine.clear()
        docs = self.vault.get_all_documents()
        all_chunks = []

        for doc in docs:
            chunks = self.vector_engine.chunk_document(
                doc_id=doc["doc_id"],
                title=doc["title"],
                content=doc["content"],
                metadata={
                    "category": doc.get("category", "General"),
                    "clearance_level": doc.get("clearance_level", 1),
                    **doc.get("metadata", {})
                }
            )
            all_chunks.extend(chunks)

        self.vector_engine.add_chunks(all_chunks)
        print(f"[RAG Engine] Re-indexed {len(docs)} documents into {len(all_chunks)} semantic chunks.")

    @staticmethod
    def _redact_secrets(text: str, chunk_clearance: int, user_clearance: int) -> str:
        """
        Dynamically redacts sensitive credentials, passwords, tokens, and private keys
        if the user does not possess sufficient clearance.
        """
        redacted = text
        warning_tag = f"[REDACTED — CLEARANCE LEVEL {chunk_clearance} REQUIRED (User Level: {user_clearance})]"

        # Redact Passwords, Passcodes, and Keys
        redacted = re.sub(
            r'(Password:\s*`?|Passcode:\s*`?|Key Code:\s*`?|Master Key:\s*`?|Locker Key:\s*`?|Secret Key:\s*`?|Root Password:\s*`?)([^`\n\r]+)(`?)',
            rf'\1{warning_tag}\3',
            redacted,
            flags=re.IGNORECASE
        )
        # Redact Connection URI credentials
        redacted = re.sub(
            r'(postgresql:\/\/[^:]+:)([^@]+)(@)',
            rf'\1{warning_tag}\3',
            redacted
        )
        # Redact API Keys & Tokens (sk_live, sk_test, AKIA, Bearer tokens, secrets)
        redacted = re.sub(
            r'(sk_live_[A-Za-z0-9_]+|AKIA_[A-Za-z0-9_]+|wJalr[A-Za-z0-9\/+=]+|s\.root_[A-Za-z0-9_]+|s\.mag_[A-Za-z0-9_]+|whsec_[A-Za-z0-9_]+|SG\.[A-Za-z0-9_\.]+|P4\$\$w0rd_[A-Za-z0-9_!#]+)',
            warning_tag,
            redacted
        )
        # Redact Auth Tokens & Bearer Headers
        redacted = re.sub(
            r'(Auth Token:\s*`?|Token:\s*`?|Bearer\s+)([A-Za-z0-9_\-\.]{10,})',
            rf'\1{warning_tag}',
            redacted,
            flags=re.IGNORECASE
        )
        # Redact Private Keys
        redacted = re.sub(
            r'-----BEGIN RSA PRIVATE KEY-----[\s\S]*?-----END RSA PRIVATE KEY-----',
            f"-----BEGIN RSA PRIVATE KEY-----\n{warning_tag}\n-----END RSA PRIVATE KEY-----",
            redacted
        )
        return redacted

    def query(self, user_query: str, user_clearance: int = 1, top_k: int = 4) -> Dict[str, Any]:
        """
        Executes the full Sovereign RAG Pipeline:
        1. Query embedding & hybrid vector retrieval
        2. RBAC clearance filtering & secret redaction
        3. Augmented context generation
        4. Sovereign synthesis with strict citations
        5. Audit logging and trace generation
        """
        start_time = time.time()
        user_clearance = int(user_clearance)
        user_role = CLEARANCE_LEVELS.get(user_clearance, CLEARANCE_LEVELS[1])

        # Step 1: Retrieval
        raw_results = self.vector_engine.search(user_query, top_k=top_k)
        
        # Step 2: RBAC Filtering & Redaction
        retrieved_sources = []
        context_blocks = []
        redaction_occurred = False
        access_granted_count = 0

        for chunk, score, score_details in raw_results:
            chunk_clearance = chunk.metadata.get("clearance_level", 1)
            is_authorized = (user_clearance >= chunk_clearance)

            if is_authorized:
                processed_text = chunk.text
                status = "AUTHORIZED"
                access_granted_count += 1
            else:
                processed_text = self._redact_secrets(chunk.text, chunk_clearance, user_clearance)
                status = "REDACTED"
                redaction_occurred = True

            source_item = {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "title": chunk.title,
                "category": chunk.metadata.get("category", "General"),
                "clearance_level": chunk_clearance,
                "clearance_badge": CLEARANCE_LEVELS.get(chunk_clearance, {}).get("badge", f"L{chunk_clearance}"),
                "hybrid_score": score_details["hybrid_score"],
                "dense_score": score_details["dense_score"],
                "lexical_score": score_details["lexical_score"],
                "status": status,
                "is_authorized": is_authorized,
                "text": processed_text
            }
            retrieved_sources.append(source_item)
            context_blocks.append(f"### [SOURCE: {chunk.doc_id}] {chunk.title} (Clearance: L{chunk_clearance})\n{processed_text}")

        combined_context = "\n\n".join(context_blocks)

        # Step 3: Sovereign Response Synthesis
        synthesized_response = self._synthesize_response(
            query=user_query,
            sources=retrieved_sources,
            context=combined_context,
            user_clearance=user_clearance,
            user_role=user_role,
            redaction_occurred=redaction_occurred
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # Step 4: Audit Logging
        if access_granted_count == len(retrieved_sources) and len(retrieved_sources) > 0:
            verdict = "GRANTED"
        elif access_granted_count > 0 and redaction_occurred:
            verdict = "AUTHORIZED (WITH SENSITIVE SOURCES REDACTED)"
        elif redaction_occurred:
            verdict = "REDACTED (INSUFFICIENT CLEARANCE)"
        else:
            verdict = "NO RELEVANT CONTEXT"

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": user_query,
            "user_clearance": user_clearance,
            "user_role": user_role["name"],
            "docs_retrieved": [s["doc_id"] for s in retrieved_sources],
            "top_score": retrieved_sources[0]["hybrid_score"] if retrieved_sources else 0.0,
            "verdict": verdict,
            "latency_ms": elapsed_ms
        }
        self.audit_logs.insert(0, log_entry)
        if len(self.audit_logs) > 200:
            self.audit_logs.pop()

        # Step 5: Pipeline Trace (for visual inspector)
        pipeline_trace = {
            "query_analysis": {
                "raw_query": user_query,
                "tokens": self.vector_engine.tokenize(user_query),
                "user_clearance": user_clearance,
                "role_name": user_role["name"]
            },
            "vector_search": {
                "top_k_retrieved": len(retrieved_sources),
                "sources": retrieved_sources
            },
            "rbac_evaluation": {
                "access_granted_chunks": access_granted_count,
                "redacted_chunks": len(retrieved_sources) - access_granted_count,
                "verdict": verdict
            },
            "context_size_chars": len(combined_context),
            "latency_ms": elapsed_ms
        }

        return {
            "query": user_query,
            "response": synthesized_response,
            "sources": retrieved_sources,
            "verdict": verdict,
            "redaction_occurred": redaction_occurred,
            "user_role": user_role,
            "latency_ms": elapsed_ms,
            "trace": pipeline_trace
        }

    def _synthesize_response(self, query: str, sources: List[Dict[str, Any]], context: str, user_clearance: int, user_role: Dict[str, Any], redaction_occurred: bool) -> str:
        """
        Sovereign rule-based and context-directed RAG response generator.
        Provides clean markdown formatting, copyable code blocks, clear citations, and security warnings.
        """
        if not sources or sources[0]["hybrid_score"] < 0.15:
            return f"""### ⚠️ No Knowledge Match Found

No relevant records matching query: **"{query}"** were identified in the indexed Knowledge Vault.

**Suggestions:**
- Verify key technical terms (e.g. database names, service endpoints, employee IDs, secret names).
- Review active clearance level (**{user_role['name']}** - `{user_role['badge']}`).
- Ingest new documents or datasets via the **CSV & Excel Importer** or **Knowledge Base Manager** tab."""

        response_lines = []

        # Header with clearance tag
        response_lines.append(f"### 🔐 Sovereign Intelligence Response // Clearance: `{user_role['badge']}`")
        if redaction_occurred:
            response_lines.append(
                f"> **🔒 SECURITY NOTICE:** Certain confidential fields have been automatically redacted because your active clearance (**{user_role['name']}**) is below the document security threshold."
            )

        response_lines.append("\n#### 📋 Retrieved Context & Knowledge Records\n")

        # Synthesize knowledge from sources
        for s in sources:
            if s["hybrid_score"] >= 0.20:
                auth_badge = "✅ AUTHORIZED" if s["is_authorized"] else "⚠️ RESTRICTED ACCESS"
                response_lines.append(f"**Document:** `{s['doc_id']}` — **{s['title']}** [{auth_badge}]")
                response_lines.append(f"{s['text']}\n")

        # Summary of Citations
        response_lines.append("\n---\n#### 📚 Verified Citations & Relevance Breakdown")
        for idx, s in enumerate(sources, 1):
            score_pct = int(s["hybrid_score"] * 100)
            response_lines.append(
                f"{idx}. **[{s['doc_id']}]** *{s['title']}* — Category: `{s['category']}` | Relevance: `{score_pct}%` | Required: `{s['clearance_badge']}`"
            )

        return "\n".join(response_lines)

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        return self.audit_logs
