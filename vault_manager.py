"""
================================================================================
SOVEREIGN VAULT & ENTERPRISE KNOWLEDGE BASE MANAGER
Multi-Tier Sovereign Knowledge Repository with Dynamic Tabular Ingestion
================================================================================
"""

import json
import time
import os
from typing import List, Dict, Any, Optional

CLEARANCE_LEVELS = {
    1: {"name": "LEVEL 1: GENERAL / PUBLIC", "badge": "LEVEL-1", "color": "#00ff9d"},
    2: {"name": "LEVEL 2: INTERNAL / DEVELOPER", "badge": "LEVEL-2", "color": "#00f0ff"},
    3: {"name": "LEVEL 3: CONFIDENTIAL / OPERATIONS", "badge": "LEVEL-3", "color": "#ffb800"},
    4: {"name": "LEVEL 4: RESTRICTED / ADMIN (ROOT)", "badge": "LEVEL-4", "color": "#ff0055"}
}

DEFAULT_KNOWLEDGE_BASE = [
    # =========================================================================
    # LEVEL 1: GENERAL / PUBLIC
    # =========================================================================
    {
        "doc_id": "DOC-ARCH-001",
        "title": "Enterprise Cloud Architecture, DNS Registry & Service Ports",
        "category": "Architecture",
        "clearance_level": 1,
        "metadata": {
            "environment": "all",
            "owner": "infrastructure-team",
            "tags": ["dns", "architecture", "endpoints", "ports"]
        },
        "content": """# Enterprise Cloud Architecture & Service Endpoints

The core infrastructure operates across distributed multi-region cloud clusters.

### Public & Staging Service Endpoints
- **Staging Web App Gateway:** `https://staging.internal.enterprise.org` (Port: 443)
- **Developer API Gateway:** `https://api-dev.enterprise.org/v1`
- **Internal Monitoring Dashboard:** `https://grafana.internal.enterprise.org:3000`
- **Identity Provider (SSO OAuth2):** `https://auth.internal.enterprise.org/oauth2`
- **Public CDN Origin:** `https://assets.enterprise.org/dist`

### Microservice Port Allocations
- Authentication & SSO Service: Port `8081`
- User Profile & Directory Service: Port `8082`
- Payment & Billing Service: Port `8083`
- Vector Search & Ingestion Service: Port `8084`
- Audit & Security Logging Service: Port `8085`"""
    },
    {
        "doc_id": "DOC-DIR-002",
        "title": "Corporate Personnel & Department Directory",
        "category": "Organization",
        "clearance_level": 1,
        "metadata": {
            "environment": "corporate",
            "owner": "people-operations",
            "tags": ["directory", "personnel", "departments", "roles"]
        },
        "content": """# Corporate Personnel & Department Directory

### Key Department Leads & Coordinators
- **Head of Engineering:** Alex Mercer (alex.mercer@enterprise.org) | Ext: `101`
- **Lead DevOps Engineer:** Sunita Soren (sunita.soren@enterprise.org) | Ext: `102`
- **Principal Security Architect:** David Roy (david.roy@enterprise.org) | Ext: `103`
- **Data Engineering Lead:** Rajesh Sharma (rajesh.sharma@enterprise.org) | Ext: `104`
- **Product Management Lead:** Ananya Deshmukh (ananya.deshmukh@enterprise.org) | Ext: `105`

### Support & Incident Hotlines
- General IT Helpdesk: `helpdesk@enterprise.org` | Ext: `500`
- 24/7 Security Operations Center (SOC): `soc@enterprise.org` | Ext: `911`"""
    },

    # =========================================================================
    # LEVEL 2: INTERNAL / DEVELOPER
    # =========================================================================
    {
        "doc_id": "DOC-STG-DB-003",
        "title": "Staging Database & Cache Cluster Credentials",
        "category": "Database Credentials",
        "clearance_level": 2,
        "metadata": {
            "environment": "staging",
            "owner": "data-engineering",
            "tags": ["postgres", "redis", "database", "staging"]
        },
        "content": """# Staging Cluster Database Credentials

Staging databases contain sanitized, anonymized seed records for testing and integration.

### Staging PostgreSQL Connection String
- **Host:** `postgres-stg.internal.enterprise.org`
- **Port:** `5432`
- **Database:** `enterprise_staging_db`
- **Username:** `stg_app_user`
- **Password:** `Stg_P@ssw0rd_9824!_Secured`
- **Full URI:** `postgresql://stg_app_user:Stg_P@ssw0rd_9824!_Secured@postgres-stg.internal.enterprise.org:5432/enterprise_staging_db`

### Staging Redis Cache Cluster
- **Cluster Endpoint:** `redis-stg.cache.internal.enterprise.org:6379`
- **Auth Token:** `stg_redis_auth_token_f8a92b3c4d`"""
    },
    {
        "doc_id": "DOC-API-004",
        "title": "Third-Party Sandbox API Tokens (Stripe, Twilio, SendGrid)",
        "category": "API Keys",
        "clearance_level": 2,
        "metadata": {
            "environment": "sandbox",
            "owner": "backend-team",
            "tags": ["api-keys", "stripe", "twilio", "sendgrid", "sandbox"]
        },
        "content": """# Third-Party Integration Sandbox Keys

Use these test keys for integration testing in non-production pipelines.

### Stripe Sandbox (Test Mode)
- **Publishable Key:** `pk_test_51Mz002ABcdEFG9876543210ZYX`
- **Secret Key:** `sk_test_51Mz002ABcdEFG9876543210ZYX_TestSecretKey89`
- **Webhook Secret:** `whsec_test_99887766554433221100aabbcc`

### Twilio Test Account
- **Account SID:** `AC_test_88f9a2b1c4e67890123456789abcdef0`
- **Auth Token:** `test_auth_tok_77665544332211aabbcc`
- **Sandbox Number:** `+15005550006`

### SendGrid Sandbox
- **API Key:** `SG.test_sandbox_key_998877.aaabbbcccdddeeefff111222333`"""
    },

    # =========================================================================
    # LEVEL 3: CONFIDENTIAL / OPERATIONS
    # =========================================================================
    {
        "doc_id": "DOC-PROD-RO-005",
        "title": "Production Read-Replica DB & Kubernetes Ingress Tokens",
        "category": "Infrastructure",
        "clearance_level": 3,
        "metadata": {
            "environment": "production",
            "owner": "devops-team",
            "tags": ["prod", "replica", "k8s", "read-only"]
        },
        "content": """# Production Read-Replica Cluster & K8s Gateway

Confidential read-only credentials for telemetry engines, reporting, and DevOps analytics.

### Production Read-Replica PostgreSQL (Read-Only)
- **Host:** `db-prod-ro.internal.enterprise.org`
- **Port:** `5432`
- **Database:** `enterprise_production_vault`
- **Username:** `svc_telemetry_ro`
- **Password:** `ProdRO_Key_#99812_VaultSecured`
- **Connection String:** `postgresql://svc_telemetry_ro:ProdRO_Key_#99812_VaultSecured@db-prod-ro.internal.enterprise.org:5432/enterprise_production_vault?sslmode=require`

### Kubernetes EKS Cluster Access Token
- **Cluster ARN:** `arn:aws:eks:us-east-1:123456789012:cluster/prod-k8s-enterprise`
- **Service Account:** `system:serviceaccount:monitoring:telemetry-viewer`
- **Bearer Token:** `Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InByb2Qta2hzLTIwMjYifQ.k8s_confidential_bearer_9988776655`"""
    },
    {
        "doc_id": "DOC-RUNBOOK-006",
        "title": "Enterprise Credential Rotation & Emergency Revocation Runbook",
        "category": "Security Policy",
        "clearance_level": 3,
        "metadata": {
            "environment": "production",
            "owner": "security-team",
            "tags": ["runbook", "rotation", "incident-response", "security"]
        },
        "content": """# Enterprise Secret Rotation & Emergency Revocation Protocol

### Standard 90-Day Rotation Schedule
1. Generate a new high-entropy 256-bit token or asymmetric cryptographic keypair.
2. Ingest the updated secret into Sovereign Vault under label `next-generation`.
3. Conduct zero-downtime rolling restart of microservices.
4. Validate monitoring metrics on Grafana before deprecating legacy tokens.

### Emergency Incident Revocation
If credential compromise is suspected:
- Execute: `python -m vault.cli --revoke-token <TOKEN_ID> --broadcast-all`
- Apply immediate IAM quarantine: `aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AWSDenyAll --user-name <USER>`."""
    },

    # =========================================================================
    # LEVEL 4: RESTRICTED / ADMIN (ROOT)
    # =========================================================================
    {
        "doc_id": "DOC-PROD-ROOT-007",
        "title": "Production Master PostgreSQL Root & High-Privilege Secrets",
        "category": "Master Credentials",
        "clearance_level": 4,
        "metadata": {
            "environment": "production",
            "owner": "ciso-office",
            "tags": ["root", "master-db", "top-secret", "admin"]
        },
        "content": """# RESTRICTED: Production Master PostgreSQL Root Credentials

CRITICAL: Direct access restricted to Level-4 Authorized Administrators.

### Production Master PostgreSQL (Primary Write Cluster)
- **Primary Master Host:** `db-prod-primary.internal.enterprise.org`
- **Port:** `5432`
- **Master Database:** `enterprise_production_vault`
- **Root Admin User:** `superadmin_root`
- **Master Password:** `P4$$w0rd_PROD_ROOT_2026!#998_MasterVaultX`
- **Primary Master URI:** `postgresql://superadmin_root:P4$$w0rd_PROD_ROOT_2026!#998_MasterVaultX@db-prod-primary.internal.enterprise.org:5432/enterprise_production_vault?sslmode=verify-full`

### Production Master Redis Write Cluster
- **Master Host:** `redis-prod-master.internal.enterprise.org:6379`
- **Master Auth Key:** `prod_master_redis_secret_token_9988_a1b2c3d4e5f6`"""
    },
    {
        "doc_id": "DOC-AWS-ROOT-008",
        "title": "AWS Production Master IAM Root & KMS Master Encryption Key",
        "category": "Cloud Master Keys",
        "clearance_level": 4,
        "metadata": {
            "environment": "production",
            "owner": "ciso-office",
            "tags": ["aws", "kms", "iam", "root-keys"]
        },
        "content": """# RESTRICTED: AWS Production Master IAM & KMS Master Key

### AWS Master Production Account
- **AWS Account ID:** `1234-5678-9012`
- **Root IAM Access Key ID:** `AKIA_PROD_ROOT_998877665544`
- **Root Secret Access Key:** `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY2026PROD`
- **Master KMS Key ID:** `arn:aws:kms:us-east-1:123456789012:key/77f9a8b1-c4d6-4e89-b123-998877665544`

### Production Stripe Live Secret Key
- **Live Secret Key:** `sk_live_51Mz002ABcdEFG9876543210PROD_LiveSecretKey998877`
- **Live Webhook Secret:** `whsec_live_99887766554433221100aabbccddeeff99`

### Sovereign Master Zero-Trust Root Token
- **Vault Token:** `s.root_master_token_2026_sovereign_rag_vault_999`"""
    },
    {
        "doc_id": "DOC-TLS-ROOT-009",
        "title": "Master Wildcard SSL/TLS Private Key (*.enterprise.org)",
        "category": "Certificates",
        "clearance_level": 4,
        "metadata": {
            "environment": "production",
            "owner": "security-officer",
            "tags": ["ssl", "tls", "private-key", "certificate"]
        },
        "content": """# RESTRICTED: Wildcard SSL/TLS Master RSA Private Key

Domain: `*.enterprise.org` | Expiration: `2028-12-31` | Issuer: `Enterprise Root CA`

### Master RSA Private Key
```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0r5z9K7vNq2w8XjL1mQp3tY6uI4vA7B9C1D3E5F7G9H1J3K5
L7M9N1P3Q5R7S9T1U3V5W7X9Y1Z3A5B7C9D1E3F5G7H9J1K3L5M7N9P1Q3R5S7T1
U3V5W7X9Y1Z3A5B7C9D1E3F5G7H9J1K3L5M7N9P1Q3R5S7T1U3V5W7X9Y1Z3A5B7
[...2048-BIT ENCRYPTED MASTER CERTIFICATE KEY...]
eF6gH7jK9mN1pQ3rS5tU7vW9xY1zA3bC5dE7fG9hJ1kL3mN5pQ7rS9tU1vW3xY5z
-----END RSA PRIVATE KEY-----
```"""
    }
]


class SovereignVaultManager:
    """
    Manages documents, credentials, and tabular datasets in the Sovereign Knowledge Base.
    Provides persistence, clearance indexing, and dynamic schema ingestion.
    """
    def __init__(self, storage_file: str = "vault_knowledge_base.json"):
        self.storage_file = storage_file
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.load_or_initialize()

    def load_or_initialize(self):
        """Loads knowledge base from disk or initializes defaults."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = {doc["doc_id"]: doc for doc in data}
                    return
            except Exception as e:
                print(f"[Vault] Failed to load {self.storage_file}, re-initializing default vault: {e}")

        # Initialize defaults
        self.documents = {doc["doc_id"]: doc for doc in DEFAULT_KNOWLEDGE_BASE}
        self.save()

    def save(self):
        """Persists knowledge base to disk as JSON."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.documents.values()), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Vault] Error persisting vault: {e}")

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return list(self.documents.values())

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.documents.get(doc_id)

    def add_document(self, title: str, category: str, clearance_level: int, content: str, metadata: Optional[Dict[str, Any]] = None, custom_id: Optional[str] = None) -> Dict[str, Any]:
        doc_id = custom_id or f"DOC-CUSTOM-{int(time.time() * 1000) % 100000}"
        doc = {
            "doc_id": doc_id,
            "title": title,
            "category": category,
            "clearance_level": int(clearance_level),
            "metadata": metadata or {"environment": "general", "owner": "admin", "tags": ["custom"]},
            "content": content,
            "created_at": time.time()
        }
        self.documents[doc_id] = doc
        self.save()
        return doc

    def ingest_tabular_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dynamically ingests ANY tabular dataset (from CSV or Excel upload).
        Auto-formats all column fields into a structured knowledge document.
        """
        added_docs = []
        for idx, row in enumerate(rows):
            clean_row = {str(k).strip(): str(v).strip() for k, v in row.items() if str(k).strip()}
            if not clean_row:
                continue

            # Normalized keys
            norm = {k.lower().replace(" ", "_").replace("-", "_"): v for k, v in clean_row.items()}

            # Extract identifier and title if present, otherwise auto-generate
            record_id = (
                norm.get("id") or norm.get("worker_id") or norm.get("employee_id") or 
                norm.get("item_id") or norm.get("asset_id") or norm.get("code") or 
                f"REC-{1000 + len(self.documents) + idx}"
            )
            title_main = (
                norm.get("name") or norm.get("title") or norm.get("job_title") or 
                norm.get("full_name") or norm.get("service") or norm.get("asset_name") or 
                f"Record {record_id}"
            )
            category = (
                norm.get("category") or norm.get("department") or norm.get("type") or 
                norm.get("division") or "Imported Dataset"
            )

            # Determine clearance level
            clearance_raw = norm.get("clearance_level") or norm.get("clearance") or norm.get("level") or "1"
            try:
                clearance = int(str(clearance_raw).replace("level", "").replace("l", "").strip())
                clearance = max(1, min(4, clearance))
            except Exception:
                lower_vals = " ".join(norm.values()).lower()
                if "admin" in lower_vals or "root" in lower_vals or "secret" in lower_vals:
                    clearance = 4
                elif "confidential" in lower_vals or "prod" in lower_vals or "supervisor" in lower_vals:
                    clearance = 3
                elif "internal" in lower_vals or "dev" in lower_vals or "operator" in lower_vals:
                    clearance = 2
                else:
                    clearance = 1

            doc_id = f"DOC-IMPORT-{str(record_id).replace(' ', '_').upper()}"
            doc_title = f"{category}: {title_main} ({record_id})"

            # Build markdown document preserving all dynamic columns
            content_lines = [
                f"# Structured Record: {title_main}",
                "",
                "### Record Attributes & Fields"
            ]
            for key, val in clean_row.items():
                if val:
                    content_lines.append(f"- **{key}:** `{val}`")

            doc_content = "\n".join(content_lines)

            doc = {
                "doc_id": doc_id,
                "title": doc_title,
                "category": category,
                "clearance_level": clearance,
                "metadata": {
                    "record_id": record_id,
                    "title": title_main,
                    "category": category,
                    "source": "tabular_import",
                    "fields": list(clean_row.keys())
                },
                "content": doc_content,
                "created_at": time.time()
            }
            self.documents[doc_id] = doc
            added_docs.append(doc)

        self.save()
        return added_docs

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            self.save()
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        counts_by_level = {1: 0, 2: 0, 3: 0, 4: 0}
        categories = {}
        for doc in self.documents.values():
            lvl = doc.get("clearance_level", 1)
            counts_by_level[lvl] = counts_by_level.get(lvl, 0) + 1
            cat = doc.get("category", "General")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_documents": len(self.documents),
            "clearance_distribution": counts_by_level,
            "categories": categories
        }
