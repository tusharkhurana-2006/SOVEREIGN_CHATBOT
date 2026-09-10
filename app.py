"""
================================================================================
SOVEREIGN PYTHON RAG CHATBOT & CREDENTIAL KNOWLEDGE BASE
100% Python Single-File Air-Gapped Web Application & REST Server
================================================================================
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import time

from vector_engine import SovereignVectorEngine
from vault_manager import SovereignVaultManager, CLEARANCE_LEVELS
from rag_engine import SovereignRAGEngine

PORT = 8000

# Initialize Global Sovereign Services
vault_manager = SovereignVaultManager("vault_knowledge_base.json")
vector_engine = SovereignVectorEngine(embedding_dim=128, hybrid_alpha=0.65)
rag_engine = SovereignRAGEngine(vault=vault_manager, vector_engine=vector_engine)

# Embedded HTML / CSS / JS Interface
UI_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SOVEREIGN RAG // Air-Gapped Enterprise Credential & Security Knowledge Base</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --bg-primary: #05070d;
      --bg-secondary: #0a0e1a;
      --bg-card: rgba(14, 20, 34, 0.75);
      --bg-card-hover: rgba(20, 28, 48, 0.85);
      --border-subtle: rgba(0, 240, 255, 0.15);
      --border-active: rgba(0, 240, 255, 0.6);
      --border-danger: rgba(255, 0, 85, 0.5);
      
      --color-cyan: #00f0ff;
      --color-magenta: #ff0055;
      --color-amber: #ffb800;
      --color-emerald: #00ff9d;
      
      --text-main: #e2e8f0;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      
      --font-sans: 'Inter', sans-serif;
      --font-display: 'Space Grotesk', sans-serif;
      --font-mono: 'Fira Code', monospace;
      
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --shadow-hud: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      background-color: var(--bg-primary);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      overflow-x: hidden;
      line-height: 1.5;
      background-image: 
        radial-gradient(circle at 10% 15%, rgba(0, 240, 255, 0.04) 0%, transparent 40%),
        radial-gradient(circle at 90% 85%, rgba(0, 255, 157, 0.04) 0%, transparent 40%),
        linear-gradient(to bottom, rgba(5, 7, 13, 0.96), rgba(5, 7, 13, 0.98));
    }
    
    .scanlines {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
      background-size: 100% 3px;
      pointer-events: none; z-index: 9999; opacity: 0.4;
    }
    
    /* Top Bar */
    .top-bar {
      background: rgba(10, 14, 26, 0.9);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 8px 24px;
      display: flex; justify-content: space-between; align-items: center;
      font-family: var(--font-mono); font-size: 0.8rem;
      position: sticky; top: 0; z-index: 100;
    }
    
    .badge-clearance {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 4px 12px; border-radius: var(--radius-sm);
      font-weight: 700; letter-spacing: 0.05em;
    }
    
    .role-select {
      background: rgba(0, 0, 0, 0.6);
      border: 1px solid var(--border-subtle);
      color: var(--color-cyan);
      font-family: var(--font-mono);
      font-size: 0.78rem;
      padding: 4px 10px;
      border-radius: var(--radius-sm);
      outline: none;
      cursor: pointer;
    }
    
    .pulse-dot {
      width: 8px; height: 8px; border-radius: 50%;
      box-shadow: 0 0 8px currentColor;
      animation: pulse 1.6s infinite ease-in-out;
    }
    @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.3); } }
    
    /* Container */
    .app-container { max-width: 1560px; margin: 0 auto; padding: 20px; }
    
    .app-header {
      display: flex; justify-content: space-between; align-items: flex-end;
      margin-bottom: 20px; padding-bottom: 16px;
      border-bottom: 1px solid var(--border-subtle);
    }
    
    .brand-title {
      font-family: var(--font-display); font-size: 1.9rem; font-weight: 700;
      background: linear-gradient(135deg, #ffffff 30%, var(--color-cyan) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      display: flex; align-items: center; gap: 12px;
    }
    
    /* Tabs */
    .nav-tabs { display: flex; gap: 8px; margin-bottom: 20px; overflow-x: auto; }
    .tab-btn {
      background: var(--bg-card); border: 1px solid var(--border-subtle);
      color: var(--text-muted); padding: 10px 18px; border-radius: var(--radius-md);
      font-family: var(--font-display); font-size: 0.9rem; font-weight: 600;
      cursor: pointer; transition: all 0.2s; white-space: nowrap;
      display: flex; align-items: center; gap: 8px;
    }
    .tab-btn:hover { background: var(--bg-card-hover); color: var(--text-main); }
    .tab-btn.active {
      background: linear-gradient(180deg, rgba(0, 240, 255, 0.15) 0%, rgba(0, 240, 255, 0.03) 100%);
      border-color: var(--color-cyan); color: var(--color-cyan);
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.15);
    }
    
    .tab-panel { display: none; }
    .tab-panel.active { display: block; animation: fadeIn 0.25s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
    
    /* Layouts */
    .chat-layout { display: grid; grid-template-columns: 1fr 380px; gap: 20px; height: 680px; }
    @media (max-width: 1024px) { .chat-layout { grid-template-columns: 1fr; height: auto; } }
    
    .glass-panel {
      background: var(--bg-card); backdrop-filter: blur(16px);
      border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);
      box-shadow: var(--shadow-hud); display: flex; flex-direction: column; overflow: hidden;
    }
    
    .panel-header {
      padding: 12px 18px; background: rgba(10, 14, 26, 0.85);
      border-bottom: 1px solid var(--border-subtle);
      display: flex; justify-content: space-between; align-items: center;
      font-family: var(--font-display); font-weight: 700; font-size: 0.95rem;
    }
    
    /* Chat Messages Box */
    .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
    
    .msg-bubble {
      max-width: 88%; padding: 14px 18px; border-radius: var(--radius-md);
      font-size: 0.92rem; line-height: 1.6; word-break: break-word;
    }
    .msg-bubble.user {
      align-self: flex-end; background: rgba(0, 240, 255, 0.12);
      border: 1px solid rgba(0, 240, 255, 0.3); color: #ffffff;
      border-bottom-right-radius: 2px;
    }
    .msg-bubble.assistant {
      align-self: flex-start; background: rgba(14, 20, 36, 0.9);
      border: 1px solid var(--border-subtle); color: var(--text-main);
      border-bottom-left-radius: 2px; width: 100%;
    }
    
    .msg-bubble pre {
      background: #020408; border: 1px solid rgba(0, 240, 255, 0.2);
      padding: 12px; border-radius: var(--radius-sm); margin: 10px 0;
      overflow-x: auto; font-family: var(--font-mono); font-size: 0.82rem;
      color: var(--color-cyan);
    }
    .msg-bubble code {
      font-family: var(--font-mono); font-size: 0.85em;
      background: rgba(0, 240, 255, 0.08); padding: 2px 6px; border-radius: 3px;
      color: var(--color-cyan);
    }
    .msg-bubble blockquote {
      border-left: 3px solid var(--color-amber); background: rgba(255, 184, 0, 0.08);
      padding: 8px 12px; margin: 10px 0; font-size: 0.88rem; color: #ffdd88;
    }
    
    /* Input Area */
    .chat-input-row {
      padding: 14px 18px; background: rgba(8, 12, 22, 0.95);
      border-top: 1px solid var(--border-subtle); display: flex; gap: 10px;
    }
    .chat-input {
      flex: 1; background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm); padding: 12px 16px; color: var(--text-main);
      font-family: var(--font-sans); font-size: 0.92rem; outline: none;
    }
    .chat-input:focus { border-color: var(--color-cyan); box-shadow: 0 0 12px rgba(0, 240, 255, 0.2); }
    
    .btn-send {
      background: rgba(0, 240, 255, 0.15); border: 1px solid var(--color-cyan);
      color: var(--color-cyan); padding: 0 20px; border-radius: var(--radius-sm);
      font-family: var(--font-mono); font-weight: 700; cursor: pointer; transition: all 0.2s;
    }
    .btn-send:hover { background: var(--color-cyan); color: #000; box-shadow: 0 0 16px var(--color-cyan); }
    
    /* Quick Prompt Chips */
    .quick-chips { display: flex; gap: 8px; padding: 8px 18px; background: #070a14; overflow-x: auto; }
    .chip {
      background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
      color: var(--text-muted); font-size: 0.75rem; padding: 4px 10px; border-radius: 12px;
      white-space: nowrap; cursor: pointer; transition: all 0.2s;
    }
    .chip:hover { background: rgba(0, 240, 255, 0.1); border-color: var(--color-cyan); color: var(--color-cyan); }
    
    /* Citations Drawer */
    .sources-list { padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
    .source-card {
      background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md); padding: 12px; font-size: 0.82rem;
    }
    .source-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .source-score { font-family: var(--font-mono); font-weight: 700; color: var(--color-cyan); }
    
    /* Tables */
    .data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; }
    .data-table th {
      background: rgba(10, 14, 26, 0.95); color: var(--color-cyan);
      font-family: var(--font-display); padding: 12px 14px; border-bottom: 2px solid var(--border-subtle);
    }
    .data-table td { padding: 12px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
    .data-table tr:hover td { background: rgba(0, 240, 255, 0.02); }
    
    /* Pipeline Step Box */
    .pipeline-step {
      background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md); padding: 16px; margin-bottom: 14px;
    }
    .step-title {
      font-family: var(--font-display); font-size: 0.95rem; font-weight: 700;
      color: var(--color-cyan); display: flex; justify-content: space-between; margin-bottom: 8px;
    }
    
    /* Buttons */
    .btn-hud {
      background: rgba(0, 240, 255, 0.08); border: 1px solid var(--border-subtle);
      color: var(--color-cyan); padding: 8px 14px; border-radius: var(--radius-sm);
      font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600; cursor: pointer;
    }
    .btn-hud:hover { background: rgba(0, 240, 255, 0.2); border-color: var(--color-cyan); }
    .btn-hud.danger { border-color: var(--border-danger); color: var(--color-magenta); }
    
    /* Form Inputs */
    .form-input {
      width: 100%; background: #04060c; border: 1px solid var(--border-subtle);
      padding: 10px 12px; border-radius: var(--radius-sm); color: var(--text-main);
      font-family: var(--font-sans); font-size: 0.88rem; margin-bottom: 12px; outline: none;
    }
  </style>
</head>
<body>
  <div class="scanlines"></div>

  <!-- Top Clearance HUD -->
  <header class="top-bar">
    <div style="display: flex; align-items: center; gap: 14px;">
      <span id="top-clearance-badge" class="badge-clearance" style="background: rgba(0, 255, 157, 0.12); border: 1px solid rgba(0, 255, 157, 0.4); color: #00ff9d;">
        <span class="pulse-dot" style="color: #00ff9d;"></span>
        LEVEL-1: GENERAL MINER / INTERN
      </span>
      <span style="color: var(--text-dim);">STATUTORY ROLE:</span>
      <select id="role-selector" class="role-select">
        <option value="1">Level 1 — General Miner / Trainee</option>
        <option value="2">Level 2 — Certified Equipment Operator / Driller</option>
        <option value="3">Level 3 — Shift Overman / Safety Officer</option>
        <option value="4" selected>Level 4 — Mine Manager / Rescue Captain (Root)</option>
      </select>
    </div>

    <div style="display: flex; align-items: center; gap: 18px;">
      <span>RAG ENGINE: <b style="color: var(--color-emerald);">100% PURE PYTHON</b></span>
      <span>INDEX: <b style="color: var(--color-cyan);">COAL MINES PERSONNEL &amp; PASSCODES</b></span>
      <span>STORAGE: <b style="color: var(--color-amber);">AIR-GAPPED VAULT</b></span>
    </div>
  </header>

  <div class="app-container">
    <!-- Brand Header -->
    <div class="app-header">
      <div>
        <h1 class="brand-title">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-cyan)" stroke-width="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
          </svg>
          SOVEREIGN RAG // COAL MINES WORKERS &amp; CREDENTIAL REGISTRY
        </h1>
        <p style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
          Air-Gapped Sovereign Personnel Intelligence: Worker IDs, Particular Job Titles, DGMS Certifications &amp; Safety Passcodes
        </p>
      </div>

      <div style="display: flex; gap: 10px;">
        <button id="btn-reindex" class="btn-hud">
          🔄 RE-INDEX COAL MINE WORKERS
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs">
      <button class="tab-btn active" data-tab="tab-chat">💬 Worker Query Chatbot</button>
      <button class="tab-btn" data-tab="tab-importer">📥 CSV &amp; Excel Importer</button>
      <button class="tab-btn" data-tab="tab-inspector">🔍 RAG Pipeline Inspector</button>
      <button class="tab-btn" data-tab="tab-kb">📂 Coal Mines Personnel Registry</button>
      <button class="tab-btn" data-tab="tab-audit">🛡️ Safety &amp; Access Audit Logs</button>
    </nav>

    <!-- ==================================================================== -->
    <!-- TAB 1: CHATBOT & CITATIONS -->
    <!-- ==================================================================== -->
    <section id="tab-chat" class="tab-panel active">
      <div class="chat-layout">
        <!-- Main Chat Box -->
        <div class="glass-panel">
          <div class="panel-header">
            <span>MINE OPERATIONS INTELLIGENCE CONSOLE</span>
            <span id="chat-status" style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--color-emerald);">READY</span>
          </div>

          <div class="quick-chips">
            <div class="chip" onclick="askPreset('Find Continuous Miner Operator with Worker ID MINE-OPS-4108')">Continuous Miner Op</div>
            <div class="chip" onclick="askPreset('Who is the Blasting & Explosives Engineer with Worker ID MINE-EXP-2044?')">Blasting Engineer</div>
            <div class="chip" onclick="askPreset('List details for Chief Mine Manager Rajesh Kumar Sharma')">Chief Mine Manager</div>
            <div class="chip" onclick="askPreset('Show Worker ID, Job Title and Division for the Ventilation Officer')">Ventilation Officer</div>
            <div class="chip" onclick="askPreset('Get emergency contact and rescue code for Mine Rescue Captain')">Rescue Captain</div>
          </div>

          <div id="chat-messages" class="chat-messages">
            <div class="msg-bubble assistant">
              <b>⛏️ Coal Mines Sovereign AI Assistant Initialized</b><br>
              Indexed with complete statutory personnel records across underground and opencast divisions. Query any worker by <b>Worker ID</b> (e.g. <code>MINE-OPS-4108</code>), <b>Job Title</b> (e.g. <i>Blasting Engineer, Continuous Miner Operator, Shift Overman</i>), or <b>Department</b>.<br><br>
              <i>Confidential access codes, explosives magazine passcodes, and master winding keys are automatically protected and redacted based on active statutory clearance.</i>
            </div>
          </div>

          <div class="chat-input-row">
            <input type="text" id="chat-input" class="chat-input" placeholder="Query credential vault (e.g., 'Find worker MINE-OPS-4108' or 'Who is the ventilation officer?')..." autocomplete="off">
            <button id="btn-send" class="btn-send">QUERY</button>
          </div>
        </div>

        <!-- Retrieved Sources & Citations Drawer -->
        <div class="glass-panel">
          <div class="panel-header">
            <span>RETRIEVED CITATIONS</span>
            <span id="sources-count" style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--color-cyan);">0 SOURCES</span>
          </div>
          <div id="sources-list" class="sources-list">
            <p style="color: var(--text-dim); font-size: 0.82rem; text-align: center; margin-top: 40px;">
              Retrieved knowledge chunks and similarity scores will appear here after each query.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================================================================== -->
    <!-- TAB 2: CSV & EXCEL DATASET IMPORTER -->
    <!-- ==================================================================== -->
    <section id="tab-importer" class="tab-panel">
      <div style="display: grid; grid-template-columns: 420px 1fr; gap: 20px;">
        <!-- Left: Upload & Input Controls Column -->
        <div class="glass-panel" style="padding: 20px;">
          <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
            <span>IMPORT WORKER DATASET (CSV / EXCEL)</span>
          </div>

          <!-- Drag and Drop Box -->
          <div id="drop-zone" style="border: 2px dashed var(--border-subtle); border-radius: var(--radius-md); padding: 24px 16px; text-align: center; cursor: pointer; transition: all 0.2s; background: rgba(0, 0, 0, 0.3); margin-bottom: 14px;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-cyan)" stroke-width="2" style="margin-bottom: 8px;">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <div style="font-weight: 600; font-size: 0.9rem; color: var(--text-main);">Drop CSV or Excel (.xlsx) file here</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">or click to select file from your system</div>
            <input type="file" id="file-input" accept=".csv, .tsv, .txt, .xlsx, .xls" style="display: none;">
          </div>

          <div style="display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap;">
            <button id="btn-load-sample" class="btn-hud" style="flex: 1; justify-content: center; font-size: 0.76rem;">
              ⚡ LOAD 10 SAMPLE WORKERS (CSV)
            </button>
            <button id="btn-download-template" class="btn-hud" style="justify-content: center; font-size: 0.76rem;">
              📥 TEMPLATE
            </button>
          </div>

          <label style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted);">Or Paste Raw CSV Data:</label>
          <textarea id="csv-text-input" class="form-input" style="height: 180px; resize: vertical; font-family: var(--font-mono); font-size: 0.76rem; line-height: 1.4;" placeholder="worker_id,worker_name,job_title,mine_division,statutory_cert,clearance_level,shift,passcode
MINE-WRK-201,Ajay Verma,Haulage & Winder Operator,Shaft #4 Incline,DGMS Winding License,2,Shift-A,WIND-PASS-201
MINE-WRK-202,Kavita Nair,Underground Environmental Chemist,Ventilation Lab,Gas Testing Cert,3,Shift-B,LAB-KEY-202"></textarea>

          <button id="btn-ingest-dataset" class="btn-send" style="width: 100%; height: 44px; margin-top: 6px;">
            🚀 INGEST &amp; RE-INDEX VECTOR SPACE
          </button>
        </div>

        <!-- Right: Tabular Preview & Ingestion Column -->
        <div class="glass-panel" style="padding: 20px;">
          <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
            <span>PARSED DATASET PREVIEW &amp; TELEMETRY</span>
            <span id="preview-row-count" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-cyan);">0 ROWS READY</span>
          </div>

          <div id="import-telemetry-box" style="display: none; background: rgba(0, 255, 157, 0.08); border: 1px solid rgba(0, 255, 157, 0.4); border-radius: var(--radius-md); padding: 12px 16px; margin-bottom: 14px; font-family: var(--font-mono); font-size: 0.82rem; color: #00ff9d;">
            <!-- Live telemetry -->
          </div>

          <div style="overflow-x: auto; max-height: 520px;">
            <table class="data-table">
              <thead>
                <tr id="preview-table-header">
                  <th>Worker ID</th>
                  <th>Name</th>
                  <th>Job Title</th>
                  <th>Division / Shaft</th>
                  <th>DGMS Certification</th>
                  <th>Clearance</th>
                  <th>Shift</th>
                  <th>Passcode</th>
                </tr>
              </thead>
              <tbody id="preview-table-body">
                <tr>
                  <td colspan="8" style="text-align: center; color: var(--text-dim); padding: 40px 0;">
                    No CSV or Excel data loaded yet. Drop a file or click <b>"LOAD 10 SAMPLE WORKERS"</b> to preview rows.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================================================================== -->
    <!-- TAB 3: RAG PIPELINE INSPECTOR -->
    <!-- ==================================================================== -->
    <section id="tab-inspector" class="tab-panel">
      <div class="glass-panel" style="padding: 24px;">
        <div class="panel-header" style="background: transparent; padding: 0 0 16px 0; margin-bottom: 20px;">
          <span>REAL-TIME RAG PIPELINE EXECUTION TRACE</span>
          <span id="trace-latency" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-emerald);">LATENCY: -- ms</span>
        </div>

        <!-- Step 1: Query Analysis -->
        <div class="pipeline-step">
          <div class="step-title">
            <span>STEP 1: QUERY PARSING &amp; TOKENIZATION</span>
            <span class="step-badge">INPUT PHASE</span>
          </div>
          <div id="trace-step-1" style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-muted);">
            No query executed yet.
          </div>
        </div>

        <!-- Step 2: Vector Search -->
        <div class="pipeline-step">
          <div class="step-title">
            <span>STEP 2: HYBRID VECTOR &amp; SEMANTIC RETRIEVAL</span>
            <span class="step-badge">TOP-K RETRIEVAL</span>
          </div>
          <div id="trace-step-2" style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-muted);">
            Awaiting query execution...
          </div>
        </div>

        <!-- Step 3: RBAC Evaluation -->
        <div class="pipeline-step">
          <div class="step-title">
            <span>STEP 3: ROLE-BASED ACCESS CONTROL (RBAC) &amp; REDACTION</span>
            <span class="step-badge">SECURITY POLICY</span>
          </div>
          <div id="trace-step-3" style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-muted);">
            Awaiting RBAC validation...
          </div>
        </div>

        <!-- Step 4: Final Synthesis -->
        <div class="pipeline-step">
          <div class="step-title">
            <span>STEP 4: AUGMENTED CONTEXT &amp; SYNTHESIS</span>
            <span class="step-badge">OUTPUT PHASE</span>
          </div>
          <div id="trace-step-4" style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-muted);">
            Awaiting response generation...
          </div>
        </div>
      </div>
    </section>

    <!-- ==================================================================== -->
    <!-- TAB 4: CREDENTIAL VAULT & KB MANAGER -->
    <!-- ==================================================================== -->
    <section id="tab-kb" class="tab-panel">
      <div style="display: grid; grid-template-columns: 1fr 380px; gap: 20px;">
        <!-- Knowledge List Table -->
        <div class="glass-panel" style="padding: 20px;">
          <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
            <span>INDEXED CREDENTIALS &amp; DOCUMENTS</span>
            <span id="kb-total-count" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-cyan);">9 DOCUMENTS</span>
          </div>

          <div style="overflow-x: auto;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Doc ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Clearance</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="kb-table-body">
                <!-- Dynamically loaded -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- Add Document Form -->
        <div class="glass-panel" style="padding: 20px;">
          <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
            <span>ADD NEW KNOWLEDGE ENTRY</span>
          </div>

          <form id="add-kb-form">
            <label style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted);">Document Title:</label>
            <input type="text" id="new-doc-title" class="form-input" placeholder="e.g. Production Redis Cluster Keys" required>

            <label style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted);">Category:</label>
            <input type="text" id="new-doc-category" class="form-input" placeholder="e.g. Database, API Keys, Security" required>

            <label style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted);">Clearance Level Requirement:</label>
            <select id="new-doc-clearance" class="form-input" style="cursor: pointer;">
              <option value="1">Level 1 — Public / Intern</option>
              <option value="2">Level 2 — Restricted / Junior Dev</option>
              <option value="3">Level 3 — Confidential / Senior DevOps</option>
              <option value="4" selected>Level 4 — Top Secret / Sec Lead</option>
            </select>

            <label style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted);">Content &amp; Credentials (Markdown / Key-Values):</label>
            <textarea id="new-doc-content" class="form-input" style="height: 140px; resize: vertical; font-family: var(--font-mono); font-size: 0.8rem;" placeholder="# Production API Token
- API Key: sk_live_custom_token_998877
- Port: 8080" required></textarea>

            <button type="submit" class="btn-send" style="width: 100%; height: 42px; margin-top: 6px;">
              💾 INGEST INTO SOVEREIGN VAULT
            </button>
          </form>
        </div>
      </div>
    </section>

    <!-- ==================================================================== -->
    <!-- TAB 5: AUDIT LOGS & MONITOR -->
    <!-- ==================================================================== -->
    <section id="tab-audit" class="tab-panel">
      <div class="glass-panel" style="padding: 20px;">
        <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
          <span>SECURITY &amp; ACCESS AUDIT TELEMETRY</span>
          <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--color-emerald);">REAL-TIME LOGGING</span>
        </div>

        <div style="overflow-x: auto;">
          <table class="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Query</th>
                <th>User Role</th>
                <th>Clearance</th>
                <th>Retrieved Docs</th>
                <th>Verdict</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody id="audit-table-body">
              <tr>
                <td colspan="7" style="text-align: center; color: var(--text-dim);">No queries logged yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>

  <!-- Client Application Script -->
  <script>
    let currentClearance = 4;
    
    // Tab Navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-tab');
        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(targetId).classList.add('active');
        
        if (targetId === 'tab-kb') loadKnowledgeBase();
        if (targetId === 'tab-audit') loadAuditLogs();
      });
    });
    
    // Role Switcher
    const roleSelector = document.getElementById('role-selector');
    const topBadge = document.getElementById('top-clearance-badge');
    
    const roleColors = {
      1: { bg: 'rgba(0, 255, 157, 0.12)', border: 'rgba(0, 255, 157, 0.4)', text: '#00ff9d', name: 'LEVEL-1: PUBLIC / INTERN' },
      2: { bg: 'rgba(0, 240, 255, 0.12)', border: 'rgba(0, 240, 255, 0.4)', text: '#00f0ff', name: 'LEVEL-2: RESTRICTED / JUNIOR' },
      3: { bg: 'rgba(255, 184, 0, 0.12)', border: 'rgba(255, 184, 0, 0.4)', text: '#ffb800', name: 'LEVEL-3: CONFIDENTIAL / DEVOPS' },
      4: { bg: 'rgba(255, 0, 85, 0.12)', border: 'rgba(255, 0, 85, 0.4)', text: '#ff0055', name: 'LEVEL-4: TOP SECRET / ROOT' }
    };
    
    roleSelector.addEventListener('change', (e) => {
      currentClearance = parseInt(e.target.value);
      const style = roleColors[currentClearance];
      topBadge.style.background = style.bg;
      topBadge.style.borderColor = style.border;
      topBadge.style.color = style.text;
      topBadge.innerHTML = `<span class="pulse-dot" style="color: ${style.text};"></span> ${style.name}`;
      
      appendSystemMessage(`Clearance role switched to <b>${style.name}</b>. Subsequent queries will be evaluated under this security policy.`);
    });
    
    // Chat Interaction
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const chatMessages = document.getElementById('chat-messages');
    
    async function submitQuery(queryText) {
      if (!queryText.trim()) return;
      
      appendUserMessage(queryText);
      chatInput.value = '';
      document.getElementById('chat-status').textContent = 'PROCESSING...';
      
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryText, clearance_level: currentClearance })
        });
        
        const data = await response.json();
        appendAssistantMessage(data.response);
        renderSources(data.sources);
        renderTrace(data.trace, data.latency_ms);
        document.getElementById('chat-status').textContent = 'READY';
      } catch (err) {
        appendAssistantMessage(`⚠️ **Error executing Sovereign RAG query:** ${err.message}`);
        document.getElementById('chat-status').textContent = 'ERROR';
      }
    }
    
    function askPreset(text) {
      chatInput.value = text;
      submitQuery(text);
    }
    
    btnSend.addEventListener('click', () => submitQuery(chatInput.value));
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') submitQuery(chatInput.value);
    });
    
    function appendUserMessage(text) {
      const bubble = document.createElement('div');
      bubble.className = 'msg-bubble user';
      bubble.textContent = text;
      chatMessages.appendChild(bubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function appendAssistantMessage(markdownText) {
      const bubble = document.createElement('div');
      bubble.className = 'msg-bubble assistant';
      bubble.innerHTML = formatMarkdown(markdownText);
      chatMessages.appendChild(bubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function appendSystemMessage(htmlText) {
      const bubble = document.createElement('div');
      bubble.className = 'msg-bubble assistant';
      bubble.style.borderLeft = '3px solid var(--color-cyan)';
      bubble.innerHTML = htmlText;
      chatMessages.appendChild(bubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Formatting Markdown (Code blocks, Headers, Bold, Blockquotes)
    function formatMarkdown(text) {
      let html = text
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/#### (.*)/g, '<h4 style="color: var(--color-cyan); margin: 8px 0;">$1</h4>')
        .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
        .replace(/\*([^*]+)\*/g, '<i>$1</i>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
      return html;
    }
    
    // Render Retrieved Citations
    function renderSources(sources) {
      const list = document.getElementById('sources-list');
      document.getElementById('sources-count').textContent = `${sources.length} SOURCES`;
      list.innerHTML = '';
      
      if (!sources || sources.length === 0) {
        list.innerHTML = '<p style="color: var(--text-dim); font-size: 0.82rem; text-align: center; margin-top: 40px;">No sources retrieved for query.</p>';
        return;
      }
      
      sources.forEach((s) => {
        const card = document.createElement('div');
        card.className = 'source-card';
        const scorePct = (s.hybrid_score * 100).toFixed(0);
        const authBadge = s.is_authorized 
          ? '<span style="color: #00ff9d; font-weight: 700;">AUTHORIZED</span>'
          : '<span style="color: #ff0055; font-weight: 700;">REDACTED</span>';
        
        card.innerHTML = `
          <div class="source-header">
            <span style="font-weight: 700; color: var(--text-main);">${s.doc_id}</span>
            <span class="source-score">${scorePct}% Match</span>
          </div>
          <div style="color: var(--color-cyan); font-size: 0.8rem; margin-bottom: 4px;">${s.title}</div>
          <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--text-dim); margin-bottom: 6px;">
            <span>Category: ${s.category}</span>
            <span>Req: ${s.clearance_badge} (${authBadge})</span>
          </div>
          <div style="background: #020408; padding: 8px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.75rem; max-height: 100px; overflow-y: auto;">
            ${s.text.replace(/\n/g, '<br>')}
          </div>
        `;
        list.appendChild(card);
      });
    }
    
    // Render Pipeline Trace
    function renderTrace(trace, latency) {
      if (!trace) return;
      document.getElementById('trace-latency').textContent = `LATENCY: ${latency} ms`;
      
      // Step 1
      document.getElementById('trace-step-1').innerHTML = `
        <b>Query:</b> "${trace.query_analysis.raw_query}"<br>
        <b>Extracted Tokens:</b> <code>[${trace.query_analysis.tokens.join(', ')}]</code><br>
        <b>User Clearance:</b> Level ${trace.query_analysis.user_clearance} (${trace.query_analysis.role_name})
      `;
      
      // Step 2
      let sourcesHtml = trace.vector_search.sources.map(s => 
        `• <b>[${s.doc_id}]</b> ${s.title} — Hybrid Score: <code>${s.hybrid_score}</code> (Dense: ${s.dense_score}, Lexical: ${s.lexical_score})`
      ).join('<br>');
      document.getElementById('trace-step-2').innerHTML = `
        <b>Top-K Retrieved:</b> ${trace.vector_search.top_k_retrieved} chunks<br>
        ${sourcesHtml}
      `;
      
      // Step 3
      document.getElementById('trace-step-3').innerHTML = `
        <b>Access Verdict:</b> <span style="color: ${trace.rbac_evaluation.verdict === 'GRANTED' ? '#00ff9d' : '#ff0055'}; font-weight: 700;">${trace.rbac_evaluation.verdict}</span><br>
        <b>Authorized Chunks:</b> ${trace.rbac_evaluation.access_granted_chunks} | <b>Redacted Chunks:</b> ${trace.rbac_evaluation.redacted_chunks}
      `;
      
      // Step 4
      document.getElementById('trace-step-4').innerHTML = `
        <b>Augmented Context Payload:</b> ${trace.context_size_chars} characters<br>
        <b>Synthesis Engine:</b> Sovereign Air-Gapped Rule-Directed Generator with Footnote Citations
      `;
    }
    
    // Load Knowledge Base
    async function loadKnowledgeBase() {
      try {
        const res = await fetch('/api/knowledge');
        const docs = await res.json();
        const tbody = document.getElementById('kb-table-body');
        document.getElementById('kb-total-count').textContent = `${docs.length} DOCUMENTS`;
        tbody.innerHTML = '';
        
        docs.forEach(doc => {
          const tr = document.createElement('tr');
          const badge = roleColors[doc.clearance_level] || roleColors[1];
          tr.innerHTML = `
            <td><code>${doc.doc_id}</code></td>
            <td><b>${doc.title}</b></td>
            <td><span style="color: var(--color-cyan);">${doc.category}</span></td>
            <td><span class="badge-clearance" style="background: ${badge.bg}; border: 1px solid ${badge.border}; color: ${badge.text}; font-size: 0.7rem;">${badge.name.split(':')[0]}</span></td>
            <td>
              <button class="btn-hud danger" onclick="deleteDocument('${doc.doc_id}')">DELETE</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      } catch (err) {
        console.error('Failed to load KB:', err);
      }
    }
    
    // Add Document
    const addKbForm = document.getElementById('add-kb-form');
    addKbForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('new-doc-title').value;
      const category = document.getElementById('new-doc-category').value;
      const clearance = parseInt(document.getElementById('new-doc-clearance').value);
      const content = document.getElementById('new-doc-content').value;
      
      try {
        const res = await fetch('/api/knowledge', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, category, clearance_level: clearance, content })
        });
        const result = await res.json();
        alert(`Document ${result.doc.doc_id} successfully ingested into Sovereign Vault!`);
        addKbForm.reset();
        loadKnowledgeBase();
      } catch (err) {
        alert(`Error ingesting document: ${err.message}`);
      }
    });
    
    // Delete Document
    async function deleteDocument(docId) {
      if (!confirm(`Are you sure you want to delete ${docId}?`)) return;
      try {
        await fetch(`/api/knowledge?id=${encodeURIComponent(docId)}`, { method: 'DELETE' });
        loadKnowledgeBase();
      } catch (err) {
        alert(`Error deleting document: ${err.message}`);
      }
    }
    
    // Reindex
    document.getElementById('btn-reindex').addEventListener('click', async () => {
      try {
        await fetch('/api/reindex', { method: 'POST' });
        alert('Vector space re-indexed successfully!');
        loadKnowledgeBase();
      } catch (err) {
        alert('Re-indexing failed: ' + err.message);
      }
    });
    
    // Load Audit Logs
    async function loadAuditLogs() {
      try {
        const res = await fetch('/api/audit');
        const logs = await res.json();
        const tbody = document.getElementById('audit-table-body');
        tbody.innerHTML = '';
        
        if (logs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-dim);">No queries logged yet.</td></tr>';
          return;
        }
        
        logs.forEach(l => {
          const tr = document.createElement('tr');
          const vColor = l.verdict === 'GRANTED' ? '#00ff9d' : (l.verdict === 'PARTIALLY REDACTED' ? '#ffb800' : '#ff0055');
          tr.innerHTML = `
            <td style="font-family: var(--font-mono); font-size: 0.75rem;">${l.timestamp}</td>
            <td><b>${l.query}</b></td>
            <td>${l.user_role}</td>
            <td><code>L${l.user_clearance}</code></td>
            <td><code>${l.docs_retrieved.join(', ') || 'None'}</code></td>
            <td><span style="color: ${vColor}; font-weight: 700;">${l.verdict}</span></td>
            <td style="font-family: var(--font-mono);">${l.latency_ms} ms</td>
          `;
          tbody.appendChild(tr);
        });
      } catch (err) {
        console.error('Failed to load audit logs:', err);
      }
    }
    
    // ------------------------------------------------------------------------
    // CSV & EXCEL DATASET IMPORTER ENGINE
    // ------------------------------------------------------------------------
    let parsedDatasetRows = [];
    
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const csvTextInput = document.getElementById('csv-text-input');
    const btnLoadSample = document.getElementById('btn-load-sample');
    const btnDownloadTemplate = document.getElementById('btn-download-template');
    const btnIngestDataset = document.getElementById('btn-ingest-dataset');
    const previewRowCount = document.getElementById('preview-row-count');
    const previewTableBody = document.getElementById('preview-table-body');
    const importTelemetryBox = document.getElementById('import-telemetry-box');
    
    // Drop zone interactions
    if (dropZone) {
      dropZone.addEventListener('click', () => fileInput.click());
      dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--color-cyan)';
        dropZone.style.background = 'rgba(0, 240, 255, 0.08)';
      });
      dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border-subtle)';
        dropZone.style.background = 'rgba(0, 0, 0, 0.3)';
      });
      dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border-subtle)';
        dropZone.style.background = 'rgba(0, 0, 0, 0.3)';
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          handleFile(e.dataTransfer.files[0]);
        }
      });
    }
    
    if (fileInput) {
      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
          handleFile(e.target.files[0]);
        }
      });
    }
    
    function handleFile(file) {
      const fileName = file.name.toLowerCase();
      const reader = new FileReader();
      
      if (fileName.endsWith('.csv') || fileName.endsWith('.txt') || fileName.endsWith('.tsv')) {
        reader.onload = (e) => {
          const text = e.target.result;
          csvTextInput.value = text;
          parseAndPreviewCSV(text);
        };
        reader.readAsText(file);
      } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        reader.onload = (e) => {
          // Read raw content and extract plain text tokens or fallback to CSV
          try {
            const text = new TextDecoder('utf-8').decode(new Uint8Array(e.target.result));
            // Extract printable strings from binary/XML
            const matches = text.match(/[A-Za-z0-9_\-\.\:\/\@\s\,\#\+]{4,}/g) || [];
            if (matches.length > 0) {
              const approxCsv = matches.slice(0, 100).join('\n');
              csvTextInput.value = approxCsv;
              parseAndPreviewCSV(approxCsv);
            } else {
              alert('Excel file loaded. Please confirm tabular headers in text editor.');
            }
          } catch (err) {
            alert('Error parsing Excel file: ' + err.message);
          }
        };
        reader.readAsArrayBuffer(file);
      }
    }
    
    // Robust CSV line parser
    function parseCSVLine(line) {
      const result = [];
      let current = '';
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"' || char === "'") {
          inQuotes = !inQuotes;
        } else if ((char === ',' || char === '\t') && !inQuotes) {
          result.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      result.push(current.trim());
      return result;
    }
    
    function parseAndPreviewCSV(csvText) {
      const lines = csvText.trim().split(/\r?\n/).filter(l => l.trim().length > 0);
      if (lines.length < 2) {
        previewRowCount.textContent = '0 ROWS READY';
        previewTableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-dim);">Invalid CSV format. Header and at least 1 data row required.</td></tr>';
        parsedDatasetRows = [];
        return;
      }
      
      const rawHeaders = parseCSVLine(lines[0]);
      const headers = rawHeaders.map(h => h.trim().toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_'));
      
      parsedDatasetRows = [];
      for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values.length === 0) continue;
        const row = {};
        headers.forEach((h, idx) => {
          row[h] = values[idx] !== undefined ? values[idx] : '';
        });
        parsedDatasetRows.push(row);
      }
      
      renderPreviewTable(parsedDatasetRows);
    }
    
    function renderPreviewTable(rows) {
      previewRowCount.textContent = `${rows.length} ROWS READY`;
      previewTableBody.innerHTML = '';
      
      if (rows.length === 0) {
        previewTableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 40px 0;">No rows loaded.</td></tr>';
        return;
      }
      
      rows.forEach((r, idx) => {
        const tr = document.createElement('tr');
        const workerId = r.worker_id || r.id || `MINE-WRK-${200 + idx}`;
        const name = r.worker_name || r.name || r.full_name || 'Worker';
        const jobTitle = r.job_title || r.title || r.designation || 'Mine Technician';
        const division = r.mine_division || r.division || r.section || 'General Sector';
        const cert = r.statutory_cert || r.certification || r.dgms_license || 'Standard Cert';
        const clearance = r.clearance_level || r.clearance || '1';
        const shift = r.shift || r.timing || 'General Shift';
        const passcode = r.passcode || r.access_code || r.secret || '—';
        
        tr.innerHTML = `
          <td><code>${workerId}</code></td>
          <td><b>${name}</b></td>
          <td><span style="color: var(--color-cyan);">${jobTitle}</span></td>
          <td>${division}</td>
          <td>${cert}</td>
          <td><span class="badge-clearance" style="font-size: 0.7rem; background: rgba(0, 240, 255, 0.1); border: 1px solid rgba(0, 240, 255, 0.3); color: var(--color-cyan);">L${clearance}</span></td>
          <td>${shift}</td>
          <td><code style="color: var(--color-magenta);">${passcode}</code></td>
        `;
        previewTableBody.appendChild(tr);
      });
    }
    
    // Live CSV Text Area Input Listener
    if (csvTextInput) {
      csvTextInput.addEventListener('input', () => {
        parseAndPreviewCSV(csvTextInput.value);
      });
    }
    
    // Sample 10 Coal Mine Workers Dataset
    const SAMPLE_CSV = `worker_id,worker_name,job_title,mine_division,statutory_cert,clearance_level,shift,passcode,phone
MINE-WRK-201,Ajay Kumar Verma,Continuous Miner Co-Pilot,Panel-D Longwall Face,HEMM License #HM-9912,2,Shift-A (06:00-14:00),JOY-PILOT-201,+91-98765-00201
MINE-WRK-202,Pooja Kumari Soren,Strata Geotechnical Inspector,North Incline Drift,DGMS Overman #OM-8831,3,Shift-B (14:00-22:00),GEO-STRATA-202,+91-98765-00202
MINE-WRK-203,Gurpreet Singh Brar,Haulage & Winding Engine Operator,Main Shaft House,DGMS Winding License #WN-4412,2,General Shift,WIND-MSTR-203,+91-98765-00203
MINE-WRK-204,Deepak Narayan Murthy,Underground Environmental Chemist,Ventilation Lab 3,Gas Testing Cert #GT-7721,3,Shift-A (06:00-14:00),LAB-GAS-204,+91-98765-00204
MINE-WRK-205,Santosh Yadav,Heavy Dumper Operator (100 Ton),Opencast Pit Bravo,HEMM Class-2 Dumper #DP-5510,2,Shift-C (Night),DUMP-KEY-205,+91-98765-00205
MINE-WRK-206,Manoj Kumar Hansda,Longwall Powered Roof Support Operator,Deep Seam Face 2,VTC Certified Operator #VTC-441,2,Shift-A (06:00-14:00),PRS-SHIELD-206,+91-98765-00206
MINE-WRK-207,Dr. Smita R. Banerjee,Chief Occupational Health & Mine Surgeon,Mine Medical Hospital,DGMS Medical Examiner #MED-009,4,General Shift,HOSP-ROOT-207,+91-98765-00207
MINE-WRK-208,Kishan Lal Mahato,Conveyor Belt & Feeder Breaker Tech,Main Drift Trunk Line,Mechanical Mining Cert #MECH-882,1,Shift-B (14:00-22:00),CNV-LOCK-208,+91-98765-00208
MINE-WRK-209,Albert Khalkho,Shotfirer & Secondary Blaster,Pit #4 Heading Section,DGMS Shotfirer Permit #SF-9910,3,Shift-A (06:00-14:00),BLAST-SUB-209,+91-98765-00209
MINE-WRK-210,Col. Arvind Rathore,Mine Security & Explosives Escort Lead,Main Security Gate & Armoury,Central Industrial Security Cert,4,24/7 Command,ARM-SEC-PASS-210,+91-98765-00210`;

    if (btnLoadSample) {
      btnLoadSample.addEventListener('click', () => {
        csvTextInput.value = SAMPLE_CSV;
        parseAndPreviewCSV(SAMPLE_CSV);
      });
    }
    
    // Download Sample CSV Template
    if (btnDownloadTemplate) {
      btnDownloadTemplate.addEventListener('click', () => {
        const blob = new Blob([SAMPLE_CSV], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'coal_mines_workers_template.csv';
        a.click();
        URL.revokeObjectURL(url);
      });
    }
    
    // Ingest Dataset into Sovereign RAG Vector Store
    if (btnIngestDataset) {
      btnIngestDataset.addEventListener('click', async () => {
        const csvRaw = csvTextInput.value.trim();
        if (!csvRaw && parsedDatasetRows.length === 0) {
          alert('Please upload a CSV/Excel file or paste CSV text first.');
          return;
        }
        
        btnIngestDataset.disabled = true;
        btnIngestDataset.textContent = '⏳ INGESTING & RE-INDEXING...';
        
        try {
          const res = await fetch('/api/upload-dataset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              rows: parsedDatasetRows.length > 0 ? parsedDatasetRows : null,
              csv_text: parsedDatasetRows.length === 0 ? csvRaw : null
            })
          });
          
          const data = await res.json();
          if (data.status === 'success') {
            importTelemetryBox.style.display = 'block';
            importTelemetryBox.innerHTML = `
              <b>✅ DATASET INGESTION COMPLETE!</b><br>
              • Ingested <b>${data.added_count}</b> new worker records into Sovereign Vault.<br>
              • Vector Space Re-Indexed: <b>${data.total_documents} total documents</b> across <b>${data.total_chunks} semantic chunks</b>.<br>
              • You can now query any of these newly uploaded workers in the <b>💬 Worker Query Chatbot</b> tab!
            `;
            
            // Reload KB table
            loadKnowledgeBase();
            alert(`🎉 Success! ${data.added_count} worker records indexed into hybrid vector space. Switch to the Chatbot tab to query them!`);
          } else {
            alert('Ingestion error: ' + (data.message || 'Unknown error'));
          }
        } catch (err) {
          alert('Failed to connect to Sovereign RAG server: ' + err.message);
        } finally {
          btnIngestDataset.disabled = false;
          btnIngestDataset.textContent = '🚀 INGEST & RE-INDEX VECTOR SPACE';
        }
      });
    }
    
    // Initial Load
    loadKnowledgeBase();
  </script>
</body>
</html>
"""


class SovereignRAGHTTPHandler(http.server.BaseHTTPRequestHandler):
    """
    Pure Python HTTP REST API and UI Server.
    Handles static single-page UI and JSON REST endpoints.
    """

    def _send_json(self, data: Any, status_code: int = 200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_content: str):
        body = html_content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        # 1. Main Web UI
        if path == '/' or path == '/index.html':
            self._send_html(UI_HTML)
            return

        # 2. REST API: Knowledge Base
        elif path == '/api/knowledge':
            docs = vault_manager.get_all_documents()
            self._send_json(docs)
            return

        # 3. REST API: Audit Logs
        elif path == '/api/audit':
            logs = rag_engine.get_audit_logs()
            self._send_json(logs)
            return

        # 4. REST API: Stats
        elif path == '/api/stats':
            stats = vault_manager.get_stats()
            stats["total_indexed_chunks"] = len(vector_engine.chunks)
            self._send_json(stats)
            return

        # 5. REST API: Clearance Levels Metadata
        elif path == '/api/clearance-levels':
            self._send_json(CLEARANCE_LEVELS)
            return

        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
            
            try:
                payload = json.loads(post_body) if post_body else {}
            except Exception:
                payload = {}

            # 1. Chat & RAG Query Endpoint
            if path == '/api/chat':
                query_str = payload.get('query', '')
                clearance_lvl = int(payload.get('clearance_level', 1))
                result = rag_engine.query(user_query=query_str, user_clearance=clearance_lvl, top_k=4)
                self._send_json(result)
                return

            # 2. Add New Knowledge Entry
            elif path == '/api/knowledge':
                title = payload.get('title', 'Untitled Document')
                category = payload.get('category', 'General')
                clearance_lvl = int(payload.get('clearance_level', 1))
                content = payload.get('content', '')
                doc = vault_manager.add_document(
                    title=title,
                    category=category,
                    clearance_level=clearance_lvl,
                    content=content
                )
                # Re-index in vector store
                rag_engine.reindex_knowledge_base()
                self._send_json({"status": "success", "doc": doc})
                return

            # 3. Re-index Vector Space
            elif path == '/api/reindex':
                rag_engine.reindex_knowledge_base()
                self._send_json({
                    "status": "success",
                    "indexed_documents": len(vault_manager.documents),
                    "indexed_chunks": len(vector_engine.chunks)
                })
                return

            # 4. Upload CSV / Excel Dataset Endpoint
            elif path == '/api/upload-dataset':
                rows = payload.get('rows', [])
                csv_text = payload.get('csv_text', '')
                
                if csv_text and not rows:
                    import csv
                    import io
                    f = io.StringIO(csv_text.strip())
                    reader = csv.DictReader(f)
                    rows = [r for r in reader]
                    
                if rows:
                    added = vault_manager.ingest_tabular_rows(rows)
                    rag_engine.reindex_knowledge_base()
                    self._send_json({
                        "status": "success",
                        "added_count": len(added),
                        "total_documents": len(vault_manager.documents),
                        "total_chunks": len(vector_engine.chunks),
                        "sample_doc": added[0] if added else None
                    })
                else:
                    self._send_json({"status": "error", "message": "No valid tabular rows or CSV text provided"}, 400)
                return

            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._send_json({"status": "error", "message": str(e)}, 500)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        if path == '/api/knowledge':
            doc_id = query_params.get('id', [None])[0]
            if doc_id and vault_manager.delete_document(doc_id):
                rag_engine.reindex_knowledge_base()
                self._send_json({"status": "deleted", "doc_id": doc_id})
            else:
                self.send_error(404, "Document ID not found")
            return
        else:
            self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):
        # Clean logging
        sys.stdout.write(f"[Sovereign HTTP] {self.address_string()} - [{self.log_date_time_string()}] {format%args}\n")
        sys.stdout.flush()


def run_app():
    global PORT
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("===============================================================================")
    print("  SOVEREIGN RAG PIPELINE // 100% PYTHON SERVER STARTING")
    print(f"  Indexed Documents: {len(vault_manager.documents)}")
    print(f"  Indexed Semantic Chunks: {len(vector_engine.chunks)}")
    print("===============================================================================")
    sys.stdout.flush()

    socketserver.TCPServer.allow_reuse_address = True
    for attempt_port in range(PORT, PORT + 50):
        try:
            with socketserver.TCPServer(("127.0.0.1", attempt_port), SovereignRAGHTTPHandler) as httpd:
                print(f"  --> LOCAL SERVER RUNNING AT: http://localhost:{attempt_port}")
                print(f"  --> LOCAL IP ADDRESS:       http://127.0.0.1:{attempt_port}")
                print("===============================================================================")
                sys.stdout.flush()
                httpd.serve_forever()
        except (OSError, PermissionError) as e:
            continue


if __name__ == "__main__":
    run_app()
