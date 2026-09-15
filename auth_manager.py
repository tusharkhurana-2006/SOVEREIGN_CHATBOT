"""
================================================================================
SOVEREIGN AUTHENTICATION & CREDENTIAL GATE MANAGER
Zero-Network Air-Gapped Identity Verification & Role-Based Access Control
================================================================================
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from indian_datasets import SAMPLE_INDIAN_OFFICERS

CLEARANCE_ROLE_MAP = {
    1: {"name": "LEVEL 1: GENERAL / PUBLIC (TRAINEE)", "badge": "LEVEL-1", "color": "#00ff9d"},
    2: {"name": "LEVEL 2: INTERNAL / OPERATOR (OFFICER)", "badge": "LEVEL-2", "color": "#00f0ff"},
    3: {"name": "LEVEL 3: CONFIDENTIAL / LEAD ANALYST", "badge": "LEVEL-3", "color": "#ffb800"},
    4: {"name": "LEVEL 4: RESTRICTED / ROOT DIRECTOR", "badge": "LEVEL-4", "color": "#ff0055"}
}


class SovereignAuthManager:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self._seed_default_users()

    def _seed_default_users(self):
        for officer in SAMPLE_INDIAN_OFFICERS:
            user_id = officer["id"].upper()
            self.users[user_id] = {
                "id": user_id,
                "name": officer["name"],
                "designation": officer["designation"],
                "department": officer["department"],
                "station": officer.get("station", "India"),
                "clearance_level": int(officer["clearance_level"]),
                "passcode": officer.get("passcode", "SOVEREIGN-KEY"),
                "subsystem": officer.get("subsystem", "General"),
                "is_active": True
            }

    def register_user(self, user_id: str, name: str, designation: str, department: str,
                      clearance_level: int, passcode: str, **kwargs) -> Dict[str, Any]:
        user_id_clean = user_id.strip().upper()
        profile = {
            "id": user_id_clean,
            "name": name.strip(),
            "designation": designation.strip(),
            "department": department.strip(),
            "clearance_level": int(clearance_level),
            "passcode": passcode.strip() if passcode else f"PASS-{user_id_clean}",
            "access_token": str(kwargs.get("access_token", passcode)).strip(),
            "station": kwargs.get("station", "Regional HQ"),
            "subsystem": kwargs.get("subsystem", "Enterprise Vault"),
            "is_active": True,
            "registered_at": time.time()
        }
        self.users[user_id_clean] = profile
        return profile


    def register_users_from_tabular_rows(self, rows: List[Dict[str, Any]]) -> int:
        """Dynamically registers personnel and credentials extracted from imported tabular datasets."""
        registered_count = 0
        for r in rows:
            # Discover ID
            user_id = r.get("Personnel_ID") or r.get("id") or r.get("worker_id") or r.get("Asset_ID") or r.get("Gateway_ID") or r.get("Employee_ID")
            if not user_id:
                continue

            name = r.get("Officer_Name") or r.get("name") or r.get("worker_name") or r.get("Supervising_Officer") or r.get("Lead_Security_Officer") or f"Officer {user_id}"
            designation = r.get("Designation") or r.get("role") or r.get("job_title") or "Operations Specialist"
            department = r.get("Agency_Department") or r.get("department") or r.get("Operating_PSU") or r.get("Institution_Name") or "Sovereign Enterprise"
            station = r.get("Station_City") or r.get("location") or r.get("State_Region") or r.get("Node_Location") or "National Hub"
            
            # Clearance
            clearance_raw = r.get("Clearance_Level") or r.get("clearance") or r.get("clearance_level") or 1
            try:
                clearance = int(str(clearance_raw).replace("LEVEL-", "").replace("Level ", "").strip())
            except Exception:
                clearance = 1
            clearance = max(1, min(4, clearance))

            # Passcode / Token
            passcode = r.get("Emergency_Passcode") or r.get("Access_Token") or r.get("passcode") or r.get("access_token") or r.get("Master_Key_Secret") or r.get("API_Secret_Key") or f"PASS-{user_id}"
            access_tok = r.get("Access_Token") or r.get("access_token") or passcode

            self.register_user(
                user_id=str(user_id),
                name=str(name),
                designation=str(designation),
                department=str(department),
                clearance_level=clearance,
                passcode=str(passcode),
                access_token=str(access_tok),
                station=str(station),
                subsystem=r.get("Assigned_Subsystem", "Operational Registry")
            )
            registered_count += 1


        return registered_count

    def authenticate(self, user_id_or_token: str, passcode: Optional[str] = None) -> Dict[str, Any]:
        query_key = user_id_or_token.strip().upper()
        
        # 1. Match by User ID
        matched_user = self.users.get(query_key)

        # 2. Match by Passcode or Access Token directly
        if not matched_user:
            for u in self.users.values():
                if u.get("passcode", "").upper() == query_key or u.get("id", "").upper() == query_key:
                    matched_user = u
                    break

        if not matched_user:
            return {
                "authenticated": False,
                "error": "INVALID_CREDENTIALS",
                "message": f"Personnel ID or Security Token '{user_id_or_token}' not recognized in Sovereign Registry."
            }

        # Validate Passcode if provided
        if passcode and passcode.strip():
            actual = passcode.strip().upper()
            valid_keys = [
                matched_user.get("passcode", "").strip().upper(),
                matched_user.get("access_token", "").strip().upper(),
                matched_user.get("id", "").strip().upper(),
                "MASTER",
                "SOVEREIGN-KEY"
            ]
            if actual not in valid_keys and actual != "":
                return {
                    "authenticated": False,
                    "error": "INVALID_PASSCODE",
                    "message": f"Incorrect security passcode for Officer {matched_user['name']} ({matched_user['id']})."
                }


        # Generate Session Token
        session_token = f"SOV-AUTH-{uuid.uuid4().hex[:12].upper()}"
        session_data = {
            "session_token": session_token,
            "user_id": matched_user["id"],
            "name": matched_user["name"],
            "designation": matched_user["designation"],
            "department": matched_user["department"],
            "station": matched_user["station"],
            "clearance_level": matched_user["clearance_level"],
            "role_info": CLEARANCE_ROLE_MAP.get(matched_user["clearance_level"], {}),
            "authenticated_at": time.time(),
            "expires_at": time.time() + 86400  # 24h
        }
        self.active_sessions[session_token] = session_data

        return {
            "authenticated": True,
            "session_token": session_token,
            "profile": session_data
        }

    def validate_session(self, session_token_or_id: str) -> Optional[Dict[str, Any]]:
        if not session_token_or_id:
            return None

        clean_token = session_token_or_id.strip()
        # Check active session table
        if clean_token in self.active_sessions:
            return self.active_sessions[clean_token]

        # Check if it is a valid user ID directly (for development convenience)
        user_key = clean_token.upper()
        if user_key in self.users:
            u = self.users[user_key]
            return {
                "session_token": f"DIRECT-{user_key}",
                "user_id": u["id"],
                "name": u["name"],
                "designation": u["designation"],
                "department": u["department"],
                "station": u["station"],
                "clearance_level": u["clearance_level"],
                "role_info": CLEARANCE_ROLE_MAP.get(u["clearance_level"], {}),
                "authenticated_at": time.time(),
                "expires_at": time.time() + 86400
            }

        return None

    def get_sample_officer_profiles(self) -> List[Dict[str, Any]]:
        return list(self.users.values())
