"""
================================================================================
SOVEREIGN CREDENTIAL & COAL MINES PERSONNEL VAULT MANAGER
Manages Multi-Tier Sovereign Credential Repositories and Coal Mine Personnel Datasets
================================================================================
"""

import json
import time
import os
from typing import List, Dict, Any, Optional

CLEARANCE_LEVELS = {
    1: {"name": "LEVEL 1: GENERAL MINER / INTERN", "badge": "LEVEL-1", "color": "#00ff9d"},
    2: {"name": "LEVEL 2: CERTIFIED OPERATOR / DRILLER", "badge": "LEVEL-2", "color": "#00f0ff"},
    3: {"name": "LEVEL 3: OVERMAN / SAFETY OFFICER", "badge": "LEVEL-3", "color": "#ffb800"},
    4: {"name": "LEVEL 4: MINE MANAGER / CHIEF AGENT", "badge": "LEVEL-4", "color": "#ff0055"}
}

DEFAULT_CREDENTIAL_KNOWLEDGE_BASE = [
    # =========================================================================
    # COAL MINES WORKERS REGISTRY & PERSONNEL DATASET
    # =========================================================================
    {
        "doc_id": "MINE-WRK-001",
        "title": "Personnel Record: Rajesh Kumar Sharma — Chief Mine Manager (First Class Certificate)",
        "category": "Coal Mine Management",
        "clearance_level": 4,
        "metadata": {
            "worker_id": "MINE-MGR-1001",
            "job_title": "Chief Mine Manager & Statutory Agent",
            "mine_division": "Deep Seam Shaft #4 (Underground)",
            "shift": "General Shift (08:00 - 17:00)",
            "statutory_cert": "DGMS First Class Mine Manager Certificate #CC-98214"
        },
        "content": """# Statutory Personnel Record: Chief Mine Manager

### Worker Identity & Designation
- **Worker ID:** `MINE-MGR-1001`
- **Full Name:** Rajesh Kumar Sharma
- **Job Title:** Chief Mine Manager & Statutory Agent
- **Department:** Mine Operations & Statutory Compliance
- **Assigned Division:** Deep Seam Shaft #4 & Main Incline Portal
- **DGMS Statutory Certification:** First Class Manager's Certificate of Competency (Coal) #CC-98214
- **Date of Joining:** 2014-03-15 | **Experience:** 18 Years

### Critical Operational Access & Master Credentials
- **Central Mine Control Radio Call-Sign:** `COMMAND-LEADER-01` (Freq: `156.800 MHz`)
- **Main Winding Engine Master Key Code:** `WIND-MSTR-9944-ALPHA`
- **Explosives Magazine Master Vault Token:** `s.mag_root_token_shaft4_2026_99812`
- **Emergency Rescue Protocol Clearance:** Level 4 (Full Incident Command Authority)
- **Direct Emergency Phone:** `+91-98765-01001`"""
    },
    {
        "doc_id": "MINE-WRK-002",
        "title": "Personnel Record: Vikramaditya Singh — Blasting & Explosives Engineer",
        "category": "Explosives & Blasting",
        "clearance_level": 3,
        "metadata": {
            "worker_id": "MINE-EXP-2044",
            "job_title": "Blasting & Explosives Engineer",
            "mine_division": "Pit #3 Coal Seam (Drift Section)",
            "shift": "Shift-A (06:00 - 14:00)",
            "statutory_cert": "DGMS Overman & Shotfirer Certificate #SF-55410"
        },
        "content": """# Statutory Personnel Record: Blasting & Explosives Engineer

### Worker Identity & Designation
- **Worker ID:** `MINE-EXP-2044`
- **Full Name:** Vikramaditya Singh
- **Job Title:** Blasting & Explosives Engineer / Lead Shotfirer
- **Department:** Drilling & Blasting Operations
- **Assigned Division:** Pit #3 Coal Seam (Drift Section)
- **DGMS Statutory Certification:** Shotfirer Certificate #SF-55410 | Gas Testing Certified
- **Date of Joining:** 2018-07-22 | **Experience:** 9 Years

### Explosives Locker Access & Authorization
- **Designated Magazine Locker:** Underground Sub-Magazine Locker #B-12
- **Daily Explosives Allocation Limit:** 250 kg Slurry Explosives / 80 Electric Detonators
- **Magazine Locker Passcode:** `Passcode: EXPL-BLAST-7729!_ShotfireSecured`
- **Emergency Detonator Circuit Test Key:** `DET-KEY-8831-OMEGA`
- **Emergency Radio Call-Sign:** `BLAST-CONTROL-4` (Freq: `158.450 MHz`)"""
    },
    {
        "doc_id": "MINE-WRK-003",
        "title": "Personnel Record: Ananya Deshmukh — Underground Ventilation & Gas Safety Officer",
        "category": "Ventilation & Gas Safety",
        "clearance_level": 3,
        "metadata": {
            "worker_id": "MINE-SAF-3012",
            "job_title": "Underground Ventilation Officer & Gas Analyst",
            "mine_division": "North Ventilation Shaft & Return Airway #2",
            "shift": "Shift-B (14:00 - 22:00)",
            "statutory_cert": "DGMS Gas Testing & Ventilation Certificate #GT-99214"
        },
        "content": """# Statutory Personnel Record: Ventilation Officer & Gas Analyst

### Worker Identity & Designation
- **Worker ID:** `MINE-SAF-3012`
- **Full Name:** Ananya Deshmukh
- **Job Title:** Underground Ventilation Officer & Gas Analyst
- **Department:** Safety, Ventilation & Environmental Monitoring
- **Assigned Division:** North Ventilation Shaft & Return Airway #2
- **DGMS Statutory Certification:** DGMS Gas Testing Certificate #GT-99214 | Overman License #OM-44120
- **Date of Joining:** 2019-11-10 | **Experience:** 7 Years

### Gas Monitoring Sensor & Telemetry Credentials
- **Methane (CH4) Sensor Calibration Node:** `methane-telemetry-shaft2.internal.mine.ai`
- **Carbon Monoxide (CO) Multi-Gas Telemetry Token:** `Token: gas_telemetry_tok_4412_methane_ch4_safe`
- **Main Fan Telemetry Dashboard URI:** `http://ventilation-fan.internal.mine.ai:8080/monitor`
- **Self-Contained Self-Rescuer (SCSR) Station #4 Locker Key:** `SCSR-LOCK-4412`"""
    },
    {
        "doc_id": "MINE-WRK-004",
        "title": "Personnel Record: Harpreet Singh Sandhu — Continuous Miner Operator",
        "category": "Heavy Equipment Operations",
        "clearance_level": 2,
        "metadata": {
            "worker_id": "MINE-OPS-4108",
            "job_title": "Continuous Miner Operator (Heavy Machinery)",
            "mine_division": "Panel-C Longwall Face (Underground)",
            "shift": "Shift-A (06:00 - 14:00)",
            "statutory_cert": "Heavy Earth Moving Machinery (HEMM) Operator License #HM-88120"
        },
        "content": """# Statutory Personnel Record: Continuous Miner Operator

### Worker Identity & Designation
- **Worker ID:** `MINE-OPS-4108`
- **Full Name:** Harpreet Singh Sandhu
- **Job Title:** Continuous Miner Operator (Heavy Machinery)
- **Department:** Mechanized Coal Extraction & Heading Development
- **Assigned Division:** Panel-C Longwall Face (Underground)
- **Assigned Machinery:** Joy Global Continuous Miner #CM-04 (1100V Dual-Drum Shearer)
- **Certification:** HEMM Heavy Equipment Operator #HM-88120 | Vocational Training Certified
- **Date of Joining:** 2020-02-14 | **Experience:** 6 Years

### Machinery Operation & Safe Codes
- **Continuous Miner Machine ID:** `CM-JOY-04-NORTH`
- **Operator Ignition Badge Code:** `Badge: OP-CM04-KEY-9912`
- **Shuttle Car Link Frequency:** Channel 4 (`154.200 MHz`)
- **Emergency Hydraulic Shutoff Protocol:** Pull Red Safety Cable at Operator Console Section B"""
    },
    {
        "doc_id": "MINE-WRK-005",
        "title": "Personnel Record: Mohammad Imran Khan — Dragline & Shovel Operator",
        "category": "Opencast Heavy Machinery",
        "clearance_level": 2,
        "metadata": {
            "worker_id": "MINE-OPS-4219",
            "job_title": "Dragline & Heavy Shovel Operator",
            "mine_division": "Opencast Zone Bravo (Overburden Excavation)",
            "shift": "Shift-C (22:00 - 06:00 Night)",
            "statutory_cert": "HEMM Class-1 Dragline Certification #DL-77312"
        },
        "content": """# Statutory Personnel Record: Dragline & Shovel Operator

### Worker Identity & Designation
- **Worker ID:** `MINE-OPS-4219`
- **Full Name:** Mohammad Imran Khan
- **Job Title:** Dragline & Heavy Shovel Operator
- **Department:** Opencast Overburden Removal Division
- **Assigned Division:** Opencast Zone Bravo (Highwall Section)
- **Assigned Machinery:** 24/96 Walking Dragline (Bucket Capacity: 24 m³)
- **Certification:** HEMM Class-1 Dragline Operator #DL-77312
- **Date of Joining:** 2017-05-01 | **Experience:** 9 Years

### Operational Access
- **Dragline Machine Call-Sign:** `DRAGLINE-BRAVO-01`
- **Walkie-Talkie Channel:** Channel 7 (`157.925 MHz`)
- **Highwall Geotechnical Radar Monitor:** `http://georadar-zoneb.internal.mine.ai:5000`"""
    },
    {
        "doc_id": "MINE-WRK-006",
        "title": "Personnel Record: Sunita Soren — Shift Overman & Roof Bolting Supervisor",
        "category": "Strata Control & Supervision",
        "clearance_level": 3,
        "metadata": {
            "worker_id": "MINE-SUP-5021",
            "job_title": "Shift Overman & Strata Control Supervisor",
            "mine_division": "East Dip Section (Depillaring District)",
            "shift": "Shift-A (06:00 - 14:00)",
            "statutory_cert": "DGMS Overman Certificate of Competency #OM-77329"
        },
        "content": """# Statutory Personnel Record: Shift Overman & Strata Control

### Worker Identity & Designation
- **Worker ID:** `MINE-SUP-5021`
- **Full Name:** Sunita Soren
- **Job Title:** Shift Overman & Strata Control Supervisor
- **Department:** Underground Production & Strata Control
- **Assigned Division:** East Dip Section (Depillaring District)
- **DGMS Statutory Certification:** Overman Certificate of Competency #OM-77329 | First Aid Certified
- **Date of Joining:** 2016-09-18 | **Experience:** 10 Years

### Statutory Supervision & Strata Control Credentials
- **Strata Load Cell Telemetry Portal:** `http://strata-eastdip.internal.mine.ai`
- **Hydraulic Prop Setting Pressure Threshold:** Minimum `250 bar` (Resin Grout Roof Bolts)
- **Overman Logbook Digital Signature Key:** `OM-SIGN-5021-SOREN`
- **Emergency Depillaring Alarm Broadcast Code:** `Passcode: ALARM-DEPILLAR-8812!_EvacuateZone`"""
    },
    {
        "doc_id": "MINE-WRK-007",
        "title": "Personnel Record: Rameshwar Prasad Murmu — Coal Face Driller & Roof Bolter",
        "category": "Face Operations",
        "clearance_level": 1,
        "metadata": {
            "worker_id": "MINE-DRL-6110",
            "job_title": "Coal Face Driller & Roof Support Technician",
            "mine_division": "Pit #3 Coal Seam (Heading Section)",
            "shift": "Shift-B (14:00 - 22:00)",
            "statutory_cert": "Vocational Coal Mining Training Certificate #VTC-2021-99"
        },
        "content": """# Statutory Personnel Record: Coal Face Driller

### Worker Identity & Designation
- **Worker ID:** `MINE-DRL-6110`
- **Full Name:** Rameshwar Prasad Murmu
- **Job Title:** Coal Face Driller & Roof Support Technician
- **Department:** Face Heading & Roof Support Installation
- **Assigned Division:** Pit #3 Coal Seam (Heading Section)
- **Training Certification:** VTC Certified Miner #VTC-2021-99
- **Date of Joining:** 2021-08-12 | **Experience:** 5 Years

### Assigned Equipment & Gear
- **Pneumatic Rotary Drill Machine:** `PNEUM-DRL-08`
- **Cap Lamp & Biometric Smart Helmet ID:** `HELMET-TAG-6110`
- **Assigned Gas Mask / SCSR Model:** Fenzy Biocell SCSR (60 min oxygen supply)
- **Shift Reporting Station:** Pit #3 Substation Attendance Room"""
    },
    {
        "doc_id": "MINE-WRK-008",
        "title": "Personnel Record: Tanmay Kulkarni — Electrical Supervisor & Winding Technician",
        "category": "Electrical & Mechanical",
        "clearance_level": 3,
        "metadata": {
            "worker_id": "MINE-ELEC-7033",
            "job_title": "Senior Electrical Supervisor & Flameproof Apparatus Inspector",
            "mine_division": "Main Shaft Winding House & Underground Substations",
            "shift": "General Shift (08:00 - 17:00)",
            "statutory_cert": "DGMS Electrical Supervisor Certificate (Mining) #ES-33109"
        },
        "content": """# Statutory Personnel Record: Electrical Supervisor

### Worker Identity & Designation
- **Worker ID:** `MINE-ELEC-7033`
- **Full Name:** Tanmay Kulkarni
- **Job Title:** Senior Electrical Supervisor & Flameproof Apparatus Inspector
- **Department:** Electrical & Mechanical Engineering
- **Assigned Division:** Main Shaft Winding House & Underground Substations 1-4
- **DGMS Statutory Certification:** Electrical Supervisor Certificate (Mines) #ES-33109
- **Date of Joining:** 2015-10-04 | **Experience:** 11 Years

### High-Voltage Switchgear & Substation Credentials
- **3.3 kV Underground Transformer Substation Access:** Substation #1, #2, #3
- **Flameproof (FLP) Switchgear Master Lockout Code:** `FLP-SWITCH-LOCK-7712`
- **Winding Engine Electrical Trip System URI:** `http://shaft4-winder.internal.mine.ai:9090`
- **Substation PLC Master Key:** `Passcode: PLC_SUBSTATION_KEY_#33109_VaultFLP`"""
    },
    {
        "doc_id": "MINE-WRK-009",
        "title": "Personnel Record: David Anthony Roy — Mine Rescue Team Captain & Paramedic",
        "category": "Emergency & Mine Rescue",
        "clearance_level": 4,
        "metadata": {
            "worker_id": "MINE-RSC-8005",
            "job_title": "Mine Rescue Team Captain & Incident Commander",
            "mine_division": "Central Mine Rescue Station (CMRS Division)",
            "shift": "On-Call Emergency Response (24/7 Standby)",
            "statutory_cert": "DGMS Certified Rescue Brigade Captain #RSC-1004"
        },
        "content": """# Statutory Personnel Record: Mine Rescue Brigade Captain

### Worker Identity & Designation
- **Worker ID:** `MINE-RSC-8005`
- **Full Name:** David Anthony Roy
- **Job Title:** Mine Rescue Team Captain & Incident Commander
- **Department:** Central Mine Rescue Station & Disaster Response Unit
- **Assigned Division:** Central Mine Rescue Station (Underground Emergency Hub)
- **DGMS Statutory Certification:** Certified Mine Rescue Brigade Leader #RSC-1004
- **Date of Joining:** 2013-01-20 | **Experience:** 13 Years

### Emergency Rescue Command & Inundation Protocol
- **Central Siren Emergency Trigger Passcode:** `Passcode: SIREN_EMERGENCY_TRIGGER_2026_CMRS_99`
- **Self-Contained Breathing Apparatus (SCBA) BG4 Locker Code:** `BG4-O2-LOCKER-8801`
- **Emergency Evacuation Chute Door Code:** `CHUTE-EVAC-9941-ROOT`
- **Emergency Direct Hotline:** `+91-98765-08005` | Call Sign: `RESCUE-ALPHA-LEADER`"""
    }
]


class SovereignVaultManager:
    """
    Manages documents, credentials, and Coal Mines Personnel records.
    Provides persistence, clearance indexing, and metadata tagging.
    """
    def __init__(self, storage_file: str = "vault_knowledge_base.json"):
        self.storage_file = storage_file
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.load_or_initialize()

    def load_or_initialize(self):
        """Loads knowledge base from disk or initializes defaults."""
        # Check if we should initialize with the new rich coal mines worker registry
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = {doc["doc_id"]: doc for doc in data}
                    
                    # If old generic dataset without coal mine workers, upgrade to coal mine dataset
                    has_coal_mine = any("MINE" in doc.get("doc_id", "") for doc in self.documents.values())
                    if not has_coal_mine:
                        print("[Vault] Upgrading vault with Coal Mines Workers Dataset...")
                        self.documents = {doc["doc_id"]: doc for doc in DEFAULT_CREDENTIAL_KNOWLEDGE_BASE}
                        self.save()
                    return
            except Exception as e:
                print(f"[Vault] Failed to load {self.storage_file}, re-initializing default vault: {e}")

        # Initialize defaults
        self.documents = {doc["doc_id"]: doc for doc in DEFAULT_CREDENTIAL_KNOWLEDGE_BASE}
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
        doc_id = custom_id or f"MINE-CUSTOM-{int(time.time() * 1000) % 100000}"
        doc = {
            "doc_id": doc_id,
            "title": title,
            "category": category,
            "clearance_level": int(clearance_level),
            "metadata": metadata or {"environment": "coal-mine", "owner": "safety-admin", "tags": ["personnel", "coal-mine"]},
            "content": content,
            "created_at": time.time()
        }
        self.documents[doc_id] = doc
        self.save()
        return doc

    def ingest_tabular_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ingests a list of row dictionaries (from CSV or Excel upload) into the Sovereign Vault.
        Auto-maps columns to worker personnel documents.
        """
        added_docs = []
        for idx, row in enumerate(rows):
            # Normalize keys to lowercase
            norm = {str(k).strip().lower().replace(" ", "_").replace("-", "_"): str(v).strip() for k, v in row.items()}
            
            worker_id = norm.get("worker_id") or norm.get("id") or norm.get("employee_id") or f"MINE-WRK-{1000 + len(self.documents) + idx}"
            name = norm.get("worker_name") or norm.get("name") or norm.get("full_name") or f"Worker {worker_id}"
            job_title = norm.get("job_title") or norm.get("title") or norm.get("designation") or "Mine Technician"
            category = norm.get("category") or norm.get("department") or norm.get("division") or "Coal Mine Operations"
            division = norm.get("mine_division") or norm.get("division") or norm.get("section") or norm.get("shaft") or "General Mine Sector"
            cert = norm.get("statutory_cert") or norm.get("certification") or norm.get("dgms_license") or "Standard Mining Certification"
            shift = norm.get("shift") or norm.get("timing") or "General Shift"
            passcode = norm.get("passcode") or norm.get("access_code") or norm.get("locker_key") or norm.get("secret") or ""
            phone = norm.get("phone") or norm.get("emergency_contact") or ""
            
            # Determine clearance level (1 to 4)
            clearance_raw = norm.get("clearance_level") or norm.get("clearance") or "1"
            try:
                clearance = int(str(clearance_raw).replace("level", "").replace("l", "").strip())
                clearance = max(1, min(4, clearance))
            except Exception:
                if "manager" in job_title.lower() or "rescue" in job_title.lower() or "director" in job_title.lower():
                    clearance = 4
                elif "engineer" in job_title.lower() or "overman" in job_title.lower() or "officer" in job_title.lower() or "supervisor" in job_title.lower():
                    clearance = 3
                elif "operator" in job_title.lower() or "driller" in job_title.lower():
                    clearance = 2
                else:
                    clearance = 1

            doc_id = f"MINE-CSV-{worker_id.replace(' ', '_').upper()}"
            title = f"Personnel Record: {name} — {job_title}"
            
            # Format content markdown
            content_lines = [
                f"# Statutory Personnel Record: {job_title}",
                "",
                "### Worker Identity & Designation",
                f"- **Worker ID:** `{worker_id}`",
                f"- **Full Name:** {name}",
                f"- **Job Title:** {job_title}",
                f"- **Department / Category:** {category}",
                f"- **Assigned Division / Shaft:** {division}",
                f"- **DGMS Statutory Certification:** {cert}",
                f"- **Shift Schedule:** {shift}"
            ]
            if phone:
                content_lines.append(f"- **Emergency Phone:** `{phone}`")
            if passcode:
                content_lines.extend([
                    "",
                    "### Operational Access & Confidential Passcode",
                    f"- **Magazine / Master Passcode:** `Passcode: {passcode}`"
                ])
                
            doc_content = "\n".join(content_lines)
            metadata = {
                "worker_id": worker_id,
                "name": name,
                "job_title": job_title,
                "category": category,
                "division": division,
                "statutory_cert": cert,
                "source": "csv_excel_import"
            }
            
            doc = {
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "clearance_level": clearance,
                "metadata": metadata,
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

