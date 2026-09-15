"""
================================================================================
INDIAN SOVEREIGN DATASETS & CREDENTIAL REGISTRIES
Comprehensive Indian Enterprise, Defense, Cloud & Infrastructure Datasets
================================================================================
"""

INDIAN_CYBER_NIC_DATASET_CSV = """Personnel_ID,Officer_Name,Designation,Agency_Department,Station_City,Clearance_Level,Assigned_Subsystem,Access_Token,Emergency_Passcode
IND-NIC-101,Dr. Rajesh Kumar Sharma,Chief Information Security Officer,NIC National Data Center,New Delhi,4,MeghRaj Cloud Master Node,NIC-ROOT-99824,DEL-SEC-ROOT
IND-CERT-202,Ananya Deshmukh,Lead Threat Intelligence Analyst,CERT-In Cyber Defense Hub,Bengaluru,3,National Incident Response Grid,CERT-TOK-4412,BLR-ALERT-303
IND-ISRO-303,Vikramaditya Rao,Telemetry & Ground Station Engineer,ISRO Space Applications Centre,Sriharikota / Bengaluru,3,NavIC Satellite Telemetry Gateway,ISRO-SAT-7719,SHAR-LINK-550
IND-NPCI-404,Priya Sundaram,UPI 2.0 Core Settlement Architect,NPCI Payment Data Center,Mumbai,3,UPI Instant Settlement Switch,UPI-SWITCH-8821,BOM-UPI-994
IND-C-DAC-505,Amitabh Mukherjee,Param Supercomputing Lead Administrator,C-DAC Supercomputing Facility,Pune,4,Param Ganga High-Performance Cluster,PARAM-ROOT-1100,PUN-HPC-881
IND-UIDAI-606,Kavita Reddy,Aadhaar CIDR Security Controller,UIDAI Central Data Repository,Manesar / Hyderabad,4,Aadhaar Biometric Auth Gateway,UIDAI-HSM-6632,HYD-AUTH-202
IND-BHEL-707,Suresh Kumar Verma,Power Grid SCADA Automation Specialist,BHEL Heavy Electricals Hub,Bhopal,2,Thermal Turbine SCADA Cluster,SCADA-BHEL-3390,BPL-PWR-710
IND-CIL-808,Harpreet Singh Sandhu,Underground Haulage & Ventilation Incharge,Coal India (ECL) Deep Mines,Dhanbad / Asansol,2,Deep Seam Ventilation Shaft #3,CIL-VENT-1904,DHN-MINE-402
IND-RAIL-909,Deepak Nair,Kavach Anti-Collision Signal Operator,Indian Railways Northern Zone,Lucknow,2,Kavach ATP Train Protection System,KVCH-SIG-5011,LKO-RAIL-821
IND-INT-010,Aarav Mehta,Junior Cloud Operations Trainee,MeghRaj Developer Sandbox,Noida,1,Public Microservice Registry,DEV-SANDBOX-101,NDA-TRAIN-001"""

INDIAN_CRITICAL_INFRA_DATASET_CSV = """Asset_ID,Facility_Name,State_Region,Operating_PSU,Clearance_Level,Supervising_Officer,Control_Protocol,Master_Key_Secret,Emergency_Hotline
INFRA-ONGC-01,Mumbai High Offshore Platform Alpha,Maharashtra / Offshore,ONGC Ltd,4,Capt. Sunil Gavaskar,SCADA Industrial Modbus-TCP,ONGC-OFFSHORE-ROOT-909,1800-22-ONGC
INFRA-ISRO-02,Satish Dhawan Space Centre (SDSC-SHAR),Andhra Pradesh,ISRO,4,Dr. K. Sivasubramanian,Launch Control Telemetry Bus,SHAR-LAUNCH-SEC-4411,08623-225000
INFRA-NTPC-03,Vindhyachal Super Thermal Power Station,Madhya Pradesh,NTPC Ltd,3,Er. Mohan Lal Patel,Generator Turbine DCS Protocol,NTPC-TURB-PWR-8820,1800-11-NTPC
INFRA-GAIL-04,Hazira-Vijaipur-Jagdishpur (HVJ) Gas Pipeline,Gujarat-UP Corridor,GAIL India,3,Pooja Narang,Gas Flow SCADA & Pressure Telemetry,GAIL-HVJ-FLOW-7731,1800-22-GAIL
INFRA-SAIL-05,Bhilai Steel Plant Blast Furnace #8,Chhattisgarh,SAIL,2,Tanmay Banerjee,Metallurgical Furnace Automation,SAIL-BHILAI-BF8-552,0788-222200
INFRA-NHAI-06,Delhi-Mumbai Expressway Automated Toll SCADA,Rajasthan Corridor,NHAI,2,Ritu Choudhary,FASTag RFID Master Concentrator,NHAI-TOLL-GATE-3310,1033-NHAI
INFRA-DRDO-07,Integrated Test Range (ITR) Chandipur,Odisha,DRDO,4,Dr. Arunachalam Roy,Radar Tracking & Telecommand Bus,DRDO-ITR-RADAR-0099,06782-272000"""

INDIAN_BANKING_NPCI_DATASET_CSV = """Gateway_ID,Institution_Name,Node_Location,Network_Protocol,Clearance_Level,Lead_Security_Officer,API_Secret_Key,Encrypted_Token,Daily_Volume_Lakhs
BANK-NPCI-01,National Payments Corporation of India (NPCI),Mumbai (BKC),UPI-ISO-8583-v2,4,Priya Sundaram,NPCI_PROD_MASTER_KEY_9924,tok_live_npci_88294a,45000
BANK-RBI-02,Reserve Bank of India (RBI) e-Kuber Core Banking,Mumbai (Fort),RTGS / NEFT Core Bus,4,Raghavan Nambiar,RBI_EKUBER_ROOT_SEC_001,tok_live_rbi_ekuber_771,98000
BANK-SBI-03,State Bank of India YONO Core Gateway,Navi Mumbai,OAuth2 REST / mTLS,3,Siddharth Joshi,SBI_YONO_GATEWAY_KEY_3340,tok_stg_sbi_yono_552,28000
BANK-HDFC-04,HDFC Bank Corporate API Gateway,Pune Hinjewadi,ISO-20022 Financial Bus,3,Meera Kulkarni,HDFC_CORP_API_SECRET_6619,tok_live_hdfc_corp_441,21000
BANK-ICICI-05,ICICI Bank iMobile IMPS Switch,Hyderabad Gachibowli,ISO-8583 Financial Switch,3,Girish Venkatraman,ICICI_IMPS_SECRET_KEY_1109,tok_live_icici_imps_99,19500
BANK-UIDAI-06,Aadhaar e-KYC Financial Verification Hub,Bengaluru,Aadhaar Auth XML 2.5,4,Kavita Reddy,UIDAI_EKYC_MASTER_SEC_8821,tok_live_uidai_ekyc_332,12000"""


SAMPLE_INDIAN_OFFICERS = [
    {
        "id": "IND-NIC-101",
        "name": "Dr. Rajesh Kumar Sharma",
        "designation": "Chief Information Security Officer",
        "department": "NIC National Data Center",
        "station": "New Delhi",
        "clearance_level": 4,
        "passcode": "NIC-ROOT-99824",
        "subsystem": "MeghRaj Cloud Master Node"
    },
    {
        "id": "IND-CERT-202",
        "name": "Ananya Deshmukh",
        "designation": "Lead Threat Intelligence Analyst",
        "department": "CERT-In Cyber Defense Hub",
        "station": "Bengaluru",
        "clearance_level": 3,
        "passcode": "CERT-TOK-4412",
        "subsystem": "National Incident Response Grid"
    },
    {
        "id": "IND-ISRO-303",
        "name": "Vikramaditya Rao",
        "designation": "Telemetry & Satellite Link Engineer",
        "department": "ISRO Telemetry & Space Hub",
        "station": "Sriharikota / Bengaluru",
        "clearance_level": 3,
        "passcode": "ISRO-SAT-7719",
        "subsystem": "NavIC Satellite Telemetry Gateway"
    },
    {
        "id": "IND-NPCI-404",
        "name": "Priya Sundaram",
        "designation": "UPI 2.0 Core Settlement Architect",
        "department": "NPCI Payment Data Center",
        "station": "Mumbai",
        "clearance_level": 3,
        "passcode": "UPI-SWITCH-8821",
        "subsystem": "UPI Instant Settlement Switch"
    },
    {
        "id": "IND-BHEL-707",
        "name": "Suresh Kumar Verma",
        "designation": "SCADA Automation Specialist",
        "department": "BHEL Heavy Electricals Hub",
        "station": "Bhopal",
        "clearance_level": 2,
        "passcode": "SCADA-BHEL-3390",
        "subsystem": "Thermal Turbine SCADA Cluster"
    },
    {
        "id": "IND-INT-010",
        "name": "Aarav Mehta",
        "designation": "Junior Cloud Operations Trainee",
        "department": "MeghRaj Developer Sandbox",
        "station": "Noida",
        "clearance_level": 1,
        "passcode": "DEV-SANDBOX-101",
        "subsystem": "Public Microservice Registry"
    }
]
