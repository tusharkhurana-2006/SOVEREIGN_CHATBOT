"""
================================================================================
SOVEREIGN RAG CHATBOT & ENTERPRISE KNOWLEDGE VAULT
Air-Gapped, Zero-External-Dependency Local Application & Server
With Credential Authentication Gate, Indian Sample Datasets & LAN Support
================================================================================
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import time
import socket
import csv
import io
from typing import Any, Dict, List, Optional

from vector_engine import SovereignVectorEngine
from vault_manager import SovereignVaultManager, CLEARANCE_LEVELS
from rag_engine import SovereignRAGEngine
from qr_generator import generate_qr_svg
from auth_manager import SovereignAuthManager
from indian_datasets import (
    INDIAN_CYBER_NIC_DATASET_CSV,
    INDIAN_CRITICAL_INFRA_DATASET_CSV,
    INDIAN_BANKING_NPCI_DATASET_CSV,
    SAMPLE_INDIAN_OFFICERS
)

PORT = 8000

# Initialize Global Sovereign Services
vault_manager = SovereignVaultManager("vault_knowledge_base.json")
vector_engine = SovereignVectorEngine(embedding_dim=128, hybrid_alpha=0.65)
rag_engine = SovereignRAGEngine(vault=vault_manager, vector_engine=vector_engine)
auth_manager = SovereignAuthManager()

# Pre-register default Indian datasets into Vault & Auth Registry
def seed_indian_datasets():
    reader = csv.DictReader(io.StringIO(INDIAN_CYBER_NIC_DATASET_CSV.strip()))
    rows = list(reader)
    existing_ids = set(vault_manager.documents.keys())
    if not any("IND-NIC-101" in str(eid) for eid in existing_ids):
        vault_manager.ingest_tabular_rows(rows)
    auth_manager.register_users_from_tabular_rows(rows)
    rag_engine.reindex_knowledge_base()



seed_indian_datasets()


def get_local_lan_ip() -> str:
    """Detects local LAN IP for phone & local network access without remote internet."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# PWA Web App Manifest for Phone Standalone Installation
PWA_MANIFEST = {
    "name": "Sovereign RAG // Offline Vault",
    "short_name": "SovereignRAG",
    "description": "Air-Gapped Sovereign RAG Chatbot & Credential Knowledge Vault",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "background_color": "#05070d",
    "theme_color": "#00f0ff",
    "orientation": "any",
    "icons": [
        {
            "src": "/api/icon.svg",
            "sizes": "192x192 512x512",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}

# Service Worker for 100% Offline Client Caching
SERVICE_WORKER_JS = r"""// Sovereign RAG Offline Service Worker
const CACHE_NAME = 'sovereign-rag-v2';
const OFFLINE_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/api/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(OFFLINE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.status === 200) {
          const resClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, resClone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          if (event.request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/');
          }
        });
      })
  );
});
"""

# App Icon SVG
APP_ICON_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00f0ff" />
      <stop offset="100%" stop-color="#00ff9d" />
    </linearGradient>
  </defs>
  <rect width="120" height="120" rx="24" fill="#05070d" stroke="#00f0ff" stroke-width="3" />
  <path d="M60 20 L95 38 V65 C95 86 60 102 60 102 C60 102 25 86 25 65 V38 Z" fill="none" stroke="url(#g)" stroke-width="6" stroke-linejoin="round" />
  <circle cx="60" cy="55" r="12" fill="none" stroke="#00f0ff" stroke-width="4" />
  <path d="M60 67 V78" stroke="#00ff9d" stroke-width="5" stroke-linecap="round" />
</svg>"""


# Embedded Offline HTML / CSS / JS Interface (Zero Remote Network Dependencies)
UI_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
  <title>SOVEREIGN RAG // Secure Knowledge & Credential Vault</title>
  
  <!-- PWA & Mobile Meta Tags -->
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#05070d">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <link rel="apple-touch-icon" href="/api/icon.svg">

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
      
      /* Offline System Font Stack */
      --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      --font-display: system-ui, -apple-system, 'Segoe UI', 'Trebuchet MS', sans-serif;
      --font-mono: 'Cascadia Code', 'Fira Code', 'Consolas', 'Courier New', monospace;
      
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
      padding-bottom: env(safe-area-inset-bottom);
      background-image: 
        radial-gradient(circle at 10% 15%, rgba(0, 240, 255, 0.04) 0%, transparent 40%),
        radial-gradient(circle at 90% 85%, rgba(0, 255, 157, 0.04) 0%, transparent 40%),
        linear-gradient(to bottom, rgba(5, 7, 13, 0.96), rgba(5, 7, 13, 0.98));
    }
    
    /* Top Bar */
    .top-bar {
      background: rgba(10, 14, 26, 0.94);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 10px 20px;
      display: flex; justify-content: space-between; align-items: center;
      font-family: var(--font-mono); font-size: 0.8rem;
      position: sticky; top: 0; z-index: 100;
      flex-wrap: wrap; gap: 10px;
    }
    
    .badge-clearance {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 5px 14px; border-radius: var(--radius-sm);
      font-weight: 700; letter-spacing: 0.05em; font-size: 0.78rem;
    }
    
    .btn-phone-hud {
      background: rgba(0, 255, 157, 0.12);
      border: 1px solid var(--color-emerald);
      color: var(--color-emerald);
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: inline-flex; align-items: center; gap: 6px;
      transition: all 0.2s;
    }
    .btn-phone-hud:hover {
      background: var(--color-emerald);
      color: #000;
      box-shadow: 0 0 14px rgba(0, 255, 157, 0.4);
    }
    
    .pulse-dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: var(--color-cyan);
      box-shadow: 0 0 8px currentColor;
      animation: pulse 1.6s infinite ease-in-out;
    }
    .pulse-dot.emerald { background: var(--color-emerald); }
    .pulse-dot.magenta { background: var(--color-magenta); }
    @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.3); } }
    
    /* Container */
    .app-container { max-width: 1600px; margin: 0 auto; padding: 20px; }
    
    .app-header {
      display: flex; justify-content: space-between; align-items: flex-end;
      margin-bottom: 20px; padding-bottom: 16px;
      border-bottom: 1px solid var(--border-subtle);
      flex-wrap: wrap; gap: 12px;
    }
    
    .brand-title {
      font-family: var(--font-display); font-size: 1.85rem; font-weight: 700;
      background: linear-gradient(135deg, #ffffff 30%, var(--color-cyan) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      display: flex; align-items: center; gap: 12px;
    }
    
    /* Tabs */
    .nav-tabs { 
      display: flex; gap: 8px; margin-bottom: 20px; 
      overflow-x: auto; -webkit-overflow-scrolling: touch;
      padding-bottom: 4px;
    }
    .tab-btn {
      background: var(--bg-card); border: 1px solid var(--border-subtle);
      color: var(--text-muted); padding: 10px 18px; border-radius: var(--radius-md);
      font-family: var(--font-display); font-size: 0.9rem; font-weight: 600;
      cursor: pointer; transition: all 0.2s; white-space: nowrap;
      display: flex; align-items: center; gap: 8px; min-height: 42px;
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
    .chat-layout { display: grid; grid-template-columns: 1fr 380px; gap: 20px; height: 720px; }
    
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
    
    /* Auth Gate Banner & Modal */
    .auth-gate-box {
      background: rgba(10, 14, 26, 0.95);
      border: 1px solid var(--border-active);
      border-radius: var(--radius-md);
      padding: 18px 20px;
      margin-bottom: 16px;
      box-shadow: 0 0 24px rgba(0, 240, 255, 0.15);
    }
    .officer-badge-active {
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.3);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 14px;
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
    
    /* Input Area */
    .chat-input-row {
      padding: 14px 18px; background: rgba(8, 12, 22, 0.95);
      border-top: 1px solid var(--border-subtle); display: flex; gap: 10px;
    }
    .chat-input {
      flex: 1; background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm); padding: 12px 16px; color: var(--text-main);
      font-family: var(--font-sans); font-size: 0.92rem; outline: none; min-height: 44px;
    }
    .chat-input:focus { border-color: var(--color-cyan); box-shadow: 0 0 12px rgba(0, 240, 255, 0.2); }
    .chat-input:disabled { opacity: 0.5; cursor: not-allowed; background: rgba(0,0,0,0.7); }
    
    .btn-send {
      background: rgba(0, 240, 255, 0.15); border: 1px solid var(--color-cyan);
      color: var(--color-cyan); padding: 0 20px; border-radius: var(--radius-sm);
      font-family: var(--font-mono); font-weight: 700; cursor: pointer; transition: all 0.2s; min-height: 44px;
    }
    .btn-send:hover:not(:disabled) { background: var(--color-cyan); color: #000; box-shadow: 0 0 16px var(--color-cyan); }
    .btn-send:disabled { opacity: 0.5; cursor: not-allowed; border-color: var(--text-dim); color: var(--text-dim); }
    
    /* Quick Prompt Chips */
    .quick-chips { display: flex; gap: 8px; padding: 8px 18px; background: #070a14; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .chip {
      background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
      color: var(--text-muted); font-size: 0.75rem; padding: 6px 12px; border-radius: 12px;
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
    
    .badge-tag {
      padding: 3px 8px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700;
    }
    .badge-lvl1 { background: rgba(0, 240, 255, 0.12); color: var(--color-cyan); border: 1px solid var(--color-cyan); }
    .badge-lvl2 { background: rgba(0, 255, 157, 0.12); color: var(--color-emerald); border: 1px solid var(--color-emerald); }
    .badge-lvl3 { background: rgba(255, 184, 0, 0.12); color: var(--color-amber); border: 1px solid var(--color-amber); }
    .badge-lvl4 { background: rgba(255, 0, 85, 0.12); color: var(--color-magenta); border: 1px solid var(--color-magenta); }
    
    /* Dataset Cards in Column 1 */
    .dataset-card {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 14px;
      margin-bottom: 12px;
      transition: all 0.2s;
    }
    .dataset-card:hover {
      border-color: var(--color-cyan);
      background: rgba(0, 240, 255, 0.04);
    }
    
    /* Forms & Controls */
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-label { font-size: 0.8rem; font-family: var(--font-mono); color: var(--text-muted); }
    .form-input, .form-select, .form-textarea {
      background: rgba(0, 0, 0, 0.5); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm); padding: 10px 14px; color: var(--text-main);
      font-family: var(--font-sans); font-size: 0.88rem; outline: none;
    }
    .form-textarea { resize: vertical; min-height: 120px; font-family: var(--font-mono); }
    .form-input:focus, .form-select:focus, .form-textarea:focus { border-color: var(--color-cyan); }
    
    .btn-hud {
      background: rgba(0, 240, 255, 0.1); border: 1px solid var(--border-subtle);
      color: var(--color-cyan); padding: 9px 16px; border-radius: var(--radius-sm);
      font-family: var(--font-mono); font-size: 0.8rem; font-weight: 700;
      cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px;
    }
    .btn-hud:hover { background: rgba(0, 240, 255, 0.2); border-color: var(--color-cyan); }
    
    /* Modal */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(8px);
      display: flex; justify-content: center; align-items: center; z-index: 1000;
    }
    .modal-card {
      background: var(--bg-secondary); border: 1px solid var(--border-active);
      border-radius: var(--radius-lg); box-shadow: 0 0 40px rgba(0, 240, 255, 0.25);
      animation: modalPop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes modalPop { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
    .modal-header {
      padding: 16px 20px; border-bottom: 1px solid var(--border-subtle);
      display: flex; justify-content: space-between; align-items: center;
    }
    .btn-close { background: none; border: none; color: var(--text-muted); font-size: 1.5rem; cursor: pointer; }
    .btn-close:hover { color: var(--color-magenta); }
    
    .mode-card {
      background: rgba(0, 0, 0, 0.35); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md); padding: 12px 14px;
    }
    
    /* Responsive Media Queries for Mobile Screens */
    @media (max-width: 1100px) {
      .chat-layout { grid-template-columns: 1fr; height: auto; }
      .chat-messages { height: 450px; }
      .form-grid { grid-template-columns: 1fr; }
    }
    
    @media (max-width: 768px) {
      .top-bar { padding: 8px 12px; }
      .app-container { padding: 10px; }
      .app-header { flex-direction: column; align-items: flex-start; gap: 8px; }
      .brand-title { font-size: 1.35rem; }
      .tab-btn { padding: 8px 12px; font-size: 0.8rem; min-height: 40px; }
      .chat-messages { height: 380px; padding: 12px; }
      .msg-bubble { max-width: 95%; padding: 10px 14px; font-size: 0.88rem; }
      .chat-input-row { padding: 10px; }
      .modal-card { width: 95% !important; max-height: 92vh; overflow-y: auto; }
    }
  </style>
</head>
<body>

  <!-- Top Classification & Role Bar -->
  <header class="top-bar">
    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
      <span class="badge-clearance badge-lvl4" id="top-clearance-badge">
        <span class="pulse-dot emerald" id="top-pulse-dot"></span>
        <span id="role-display-text">AIR-GAPPED // AUTHENTICATED: LEVEL-4 (ROOT DIRECTOR)</span>
      </span>
      <span style="color: var(--text-dim); font-size: 0.72rem;" class="hide-mobile">ZERO-INTERNET RUNTIME</span>
    </div>

    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
      <button id="btn-phone-modal" class="btn-phone-hud">
        <span class="pulse-dot emerald"></span>
        <span>📱 PHONE &amp; OFFLINE ACCESS</span>
      </button>

      <button id="btn-auth-switch" class="btn-hud" style="font-size: 0.76rem; padding: 5px 12px; border-color: var(--color-cyan);">
        🔑 SWITCH CREDENTIALS
      </button>
    </div>
  </header>

  <div class="app-container">
    <!-- Brand Header -->
    <div class="app-header">
      <div>
        <h1 class="brand-title">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-cyan)" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          SOVEREIGN RAG // SECURE KNOWLEDGE VAULT
        </h1>
        <div style="color: var(--text-muted); font-size: 0.82rem; margin-top: 4px;">
          Air-Gapped Hybrid Vector Retrieval &bull; Credential Authentication Gate &bull; Indian Sovereign Datasets &bull; 100% Offline
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('chat')">
        💬 Sovereign Chatbot
      </button>
      <button class="tab-btn" onclick="switchTab('importer')">
        📥 Indian Datasets &amp; CSV Loader
      </button>
      <button class="tab-btn" onclick="switchTab('inspector')">
        🔍 RAG Pipeline Inspector
      </button>
      <button class="tab-btn" onclick="switchTab('vault')">
        📂 Knowledge Base &amp; Vault
      </button>
      <button class="tab-btn" onclick="switchTab('audit')">
        🛡️ Security &amp; Audit Logs
      </button>
    </nav>

    <!-- ==================================================================== -->
    <!-- TAB 1: SOVEREIGN CHATBOT -->
    <!-- ==================================================================== -->
    <section id="tab-chat" class="tab-panel active">
      <!-- Officer Active ID Card -->
      <div id="auth-officer-banner" class="officer-badge-active">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 1.3rem;">🇮🇳</span>
          <div>
            <div style="font-weight: 700; color: #fff; font-size: 0.9rem;">
              <span id="officer-name">Dr. Rajesh Kumar Sharma</span> 
              <span style="color: var(--color-cyan); font-family: var(--font-mono); font-size: 0.8rem;" id="officer-id">(IND-NIC-101)</span>
            </div>
            <div style="font-size: 0.76rem; color: var(--text-muted);" id="officer-dept">
              Chief Information Security Officer &bull; NIC National Data Center &bull; MeghRaj Cloud Node
            </div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span class="badge-tag badge-lvl4" id="officer-lvl-tag">LEVEL-4 (ROOT ADMIN)</span>
          <button class="btn-hud" onclick="openAuthModal()" style="font-size: 0.72rem; padding: 4px 10px;">
            CHANGE ID
          </button>
        </div>
      </div>

      <!-- Credential Barrier Warning (When Logged Out) -->
      <div id="auth-lock-banner" class="auth-gate-box" style="display: none; border-color: var(--color-magenta);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 1.6rem;">🔒</span>
            <div>
              <div style="font-weight: 700; color: var(--color-magenta); font-size: 0.95rem;">CREDENTIAL AUTHENTICATION REQUIRED TO ACCESS CHAT</div>
              <div style="font-size: 0.78rem; color: var(--text-muted);">
                The Sovereign Intelligence Console requires an authenticated Personnel ID and Security Passcode.
              </div>
            </div>
          </div>
          <button class="btn-send" onclick="openAuthModal()" style="font-size: 0.8rem; padding: 0 16px; height: 38px;">
            🔑 AUTHENTICATE NOW
          </button>
        </div>
      </div>

      <div class="chat-layout">
        <!-- Main Chat Area -->
        <div class="glass-panel">
          <div class="panel-header">
            <span>SOVEREIGN INTELLIGENCE CONSOLE</span>
            <span id="chat-status" style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--color-emerald);">READY</span>
          </div>

          <div class="quick-chips">
            <div class="chip" onclick="askPreset('What are the master root credentials for NIC MeghRaj Cloud node?')">NIC Cloud Root</div>
            <div class="chip" onclick="askPreset('Show Indian Cyber Defense and CERT-In threat intelligence roster')">CERT-In Personnel</div>
            <div class="chip" onclick="askPreset('Show UPI 2.0 switch and NPCI payment settlement keys')">NPCI UPI Keys</div>
            <div class="chip" onclick="askPreset('What is the NavIC ground station telemetry passcode for ISRO?')">ISRO Satellite Key</div>
            <div class="chip" onclick="askPreset('What are the staging PostgreSQL database connection parameters?')">Staging DB</div>
          </div>

          <div id="chat-messages" class="chat-messages">
            <div class="msg-bubble assistant">
              <b>🔐 Sovereign AI Assistant Initialized</b><br>
              Connected to local sovereign knowledge vault. Query any indexed knowledge, database credentials, API tokens, personnel records, or uploaded datasets.<br><br>
              <i>Confidential passwords, private keys, and restricted tokens are automatically protected and redacted based on active clearance.</i>
            </div>
          </div>

          <div class="chat-input-row">
            <input type="text" id="chat-input" class="chat-input" placeholder="Query knowledge base (e.g. 'What is the staging DB host?' or 'Find employee records')..." autocomplete="off">
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
    <!-- TAB 2: INDIAN DATASETS & CSV IMPORTER (3-COLUMN DEDICATED LAYOUT) -->
    <!-- ==================================================================== -->
    <section id="tab-importer" class="tab-panel">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 20px;">
        
        <!-- COLUMN 1: 🇮🇳 DEDICATED INDIAN SAMPLE DATASETS -->
        <div class="glass-panel" style="padding: 20px;">
          <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span>🇮🇳</span>
              <span>INDIAN SOVEREIGN SAMPLE DATASETS</span>
            </div>
          </div>

          <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 14px;">
            Select any pre-configured Indian sovereign dataset to immediately populate the editor and re-index the vector space:
          </p>

          <!-- Card 1: NIC Cyber & Cloud -->
          <div class="dataset-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
              <span style="font-weight: 700; color: var(--color-cyan); font-size: 0.88rem;">National Cyber &amp; NIC Cloud Registry</span>
              <span class="badge-tag badge-lvl4">LEVEL 1-4</span>
            </div>
            <div style="font-size: 0.76rem; color: var(--text-muted); margin-bottom: 10px;">
              NIC MeghRaj, CERT-In, ISRO Telemetry, C-DAC Param Supercomputing, UIDAI CIDR &amp; NPCI UPI 2.0 Credentials.
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn-hud" onclick="loadIndianSampleDataset('cyber')" style="flex: 1; justify-content: center; font-size: 0.76rem;">
                ⚡ LOAD NIC DATASET
              </button>
            </div>
          </div>

          <!-- Card 2: Critical Infrastructure -->
          <div class="dataset-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
              <span style="font-weight: 700; color: var(--color-emerald); font-size: 0.88rem;">Critical Infrastructure &amp; PSU Assets</span>
              <span class="badge-tag badge-lvl3">LEVEL 2-4</span>
            </div>
            <div style="font-size: 0.76rem; color: var(--text-muted); margin-bottom: 10px;">
              ONGC Offshore, NTPC Turbines, GAIL Gas Pipeline, SAIL Bhilai, NHAI FASTag &amp; DRDO Test Range SCADA.
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn-hud" onclick="loadIndianSampleDataset('infra')" style="flex: 1; justify-content: center; font-size: 0.76rem;">
                ⚡ LOAD INFRA DATASET
              </button>
            </div>
          </div>

          <!-- Card 3: Banking & Payment Switch -->
          <div class="dataset-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
              <span style="font-weight: 700; color: var(--color-amber); font-size: 0.88rem;">Indian Banking &amp; UPI Switch Hub</span>
              <span class="badge-tag badge-lvl4">LEVEL 3-4</span>
            </div>
            <div style="font-size: 0.76rem; color: var(--text-muted); margin-bottom: 10px;">
              NPCI UPI Core, RBI e-Kuber, SBI YONO Gateway, HDFC ISO-20022 &amp; Aadhaar e-KYC Hub Keys.
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn-hud" onclick="loadIndianSampleDataset('banking')" style="flex: 1; justify-content: center; font-size: 0.76rem;">
                ⚡ LOAD BANKING DATASET
              </button>
            </div>
          </div>
        </div>

        <!-- COLUMN 2: CUSTOM CSV / EXCEL UPLOADER & RAW EDITOR -->
        <div class="glass-panel" style="padding: 20px;">
          <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
            <span>CUSTOM FILE UPLOAD &amp; EDITOR</span>
          </div>

          <!-- Drag and Drop Box -->
          <div id="drop-zone" style="border: 2px dashed var(--border-subtle); border-radius: var(--radius-md); padding: 20px 16px; text-align: center; cursor: pointer; transition: all 0.2s; background: rgba(0, 0, 0, 0.3); margin-bottom: 14px;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-cyan)" stroke-width="2" style="margin-bottom: 6px;">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <div style="font-weight: 600; font-size: 0.88rem; color: var(--text-main);">Drop CSV or Excel (.xlsx) file here</div>
            <div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 2px;">or click to browse local files</div>
            <input type="file" id="file-input" accept=".csv, .tsv, .txt, .xlsx, .xls" style="display: none;">
          </div>

          <div style="display: flex; gap: 8px; margin-bottom: 10px;">
            <button id="btn-download-template" class="btn-hud" style="flex: 1; justify-content: center; font-size: 0.76rem;">
              📥 DOWNLOAD TEMPLATE (CSV)
            </button>
          </div>

          <label style="font-size: 0.76rem; font-family: var(--font-mono); color: var(--text-muted);">Raw Tabular Text / CSV Editor:</label>
          <textarea id="csv-text-input" class="form-input" style="height: 180px; resize: vertical; font-family: var(--font-mono); font-size: 0.74rem; line-height: 1.4;" placeholder="Personnel_ID,Officer_Name,Designation,Agency_Department,Station_City,Clearance_Level,Assigned_Subsystem,Access_Token,Emergency_Passcode"></textarea>

          <button id="btn-ingest-dataset" class="btn-send" style="width: 100%; height: 44px; margin-top: 10px;">
            🚀 INGEST &amp; RE-INDEX VECTOR SPACE
          </button>
        </div>

        <!-- COLUMN 3: PARSED SCHEMA PREVIEW & INGESTION TELEMETRY -->
        <div class="glass-panel" style="padding: 20px;">
          <div class="panel-header" style="background: transparent; padding: 0 0 14px 0; margin-bottom: 14px;">
            <span>PARSED SCHEMA &amp; TELEMETRY</span>
            <span id="preview-row-count" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-cyan);">0 ROWS READY</span>
          </div>

          <div id="import-telemetry-box" style="display: none; background: rgba(0, 255, 157, 0.08); border: 1px solid rgba(0, 255, 157, 0.4); border-radius: var(--radius-md); padding: 12px 14px; margin-bottom: 14px; font-family: var(--font-mono); font-size: 0.8rem; color: #00ff9d;">
            <!-- Live telemetry -->
          </div>

          <div style="overflow-x: auto; max-height: 480px;">
            <table class="data-table">
              <thead id="preview-table-head">
                <tr>
                  <th>ID</th>
                  <th>Officer / Title</th>
                  <th>Agency / Dept</th>
                  <th>Clearance</th>
                  <th>Attributes Preview</th>
                </tr>
              </thead>
              <tbody id="preview-table-body">
                <tr>
                  <td colspan="5" style="text-align: center; color: var(--text-dim); padding: 40px 0;">
                    Click any <b>"LOAD DATASET"</b> button on the left to preview parsed rows.
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
        <div class="panel-header" style="background: transparent; padding: 0 0 16px 0; margin-bottom: 16px;">
          <span>RAG PIPELINE EXECUTION TRACE &amp; LATENCY METRICS</span>
          <span id="trace-latency" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-cyan);">LATENCY: 0.0ms</span>
        </div>

        <div id="inspector-content">
          <p style="color: var(--text-dim); text-align: center; padding: 60px 0; font-size: 0.9rem;">
            Run a query in the <b>💬 Sovereign Chatbot</b> tab to inspect the full step-by-step vector scoring, token analysis, RBAC evaluation, and context assembly trace.
          </p>
        </div>
      </div>
    </section>

    <!-- ==================================================================== -->
    <!-- TAB 4: KNOWLEDGE BASE & VAULT MANAGER -->
    <!-- ==================================================================== -->
    <section id="tab-vault" class="tab-panel">
      <div class="glass-panel" style="padding: 24px; margin-bottom: 24px;">
        <div class="panel-header" style="background: transparent; padding: 0 0 16px 0; margin-bottom: 16px;">
          <span>ADD NEW DOCUMENT OR SECRET TO SOVEREIGN VAULT</span>
        </div>

        <form id="form-add-doc">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">DOCUMENT TITLE / SERVICE NAME:</label>
              <input type="text" id="doc-title" class="form-input" placeholder="e.g. NIC Data Center Node" required>
            </div>
            <div class="form-group">
              <label class="form-label">CATEGORY:</label>
              <input type="text" id="doc-category" class="form-input" placeholder="e.g. Cloud Infrastructure" required>
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 16px;">
            <label class="form-label">MINIMUM REQUIRED CLEARANCE LEVEL:</label>
            <select id="doc-clearance" class="form-select">
              <option value="1">Level 1: Public / Intern</option>
              <option value="2">Level 2: Restricted / Operator</option>
              <option value="3">Level 3: Confidential / Ops Lead</option>
              <option value="4" selected>Level 4: Top Secret / Root Admin</option>
            </select>
          </div>

          <div class="form-group" style="margin-bottom: 16px;">
            <label class="form-label">DOCUMENT BODY / SECRETS / CREDENTIALS (MARKDOWN SUPPORTED):</label>
            <textarea id="doc-content" class="form-textarea" placeholder="### Credentials & Connection Details
- Host: nic-node.cloud.gov.in
- Auth Token: nic_secret_998124
- Port: 443" required></textarea>
          </div>

          <button type="submit" class="btn-hud" style="width: 100%; justify-content: center; height: 44px;">
            🔒 SAVE TO VAULT &amp; RE-INDEX VECTOR SPACE
          </button>
        </form>
      </div>

      <!-- Live Vault Documents Table -->
      <div class="glass-panel" style="padding: 24px;">
        <div class="panel-header" style="background: transparent; padding: 0 0 16px 0; margin-bottom: 16px;">
          <span>INDEXED SOVEREIGN VAULT DOCUMENTS</span>
          <span id="vault-doc-count" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-cyan);">0 DOCUMENTS</span>
        </div>

        <div style="overflow-x: auto;">
          <table class="data-table">
            <thead>
              <tr>
                <th>Doc ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Clearance Tier</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="vault-table-body">
              <tr>
                <td colspan="5" style="text-align: center; color: var(--text-dim); padding: 30px;">Loading vault records...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================================================================== -->
    <!-- TAB 5: AUDIT LOGS -->
    <!-- ==================================================================== -->
    <section id="tab-audit" class="tab-panel">
      <div class="glass-panel" style="padding: 24px;">
        <div class="panel-header" style="background: transparent; padding: 0 0 16px 0; margin-bottom: 16px;">
          <span>AIR-GAPPED SECURITY &amp; ACCESS AUDIT TRAIL</span>
          <button class="btn-hud" onclick="loadAuditLogs()" style="font-size: 0.75rem; padding: 4px 10px;">
            🔄 REFRESH
          </button>
        </div>

        <div style="overflow-x: auto;">
          <table class="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Officer / Role</th>
                <th>User Query</th>
                <th>Verdict / Policy</th>
                <th>Retrieved Docs</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody id="audit-table-body">
              <tr>
                <td colspan="6" style="text-align: center; color: var(--text-dim); padding: 30px;">No audit events recorded in this session.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>

  <!-- ==================================================================== -->
  <!-- MODAL: SOVEREIGN CREDENTIAL & IDENTITY GATE -->
  <!-- ==================================================================== -->
  <div id="auth-modal" class="modal-overlay" style="display: none;">
    <div class="modal-card" style="max-width: 680px; width: 95%;">
      <div class="modal-header">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 1.4rem;">🔐</span>
          <div>
            <div style="font-family: var(--font-display); font-weight: 700; font-size: 1.1rem; color: #fff;">SOVEREIGN IDENTITY &amp; CREDENTIAL GATE</div>
            <div style="font-size: 0.75rem; color: var(--color-cyan); font-family: var(--font-mono);">ROLE-BASED CLEARANCE VERIFICATION</div>
          </div>
        </div>
        <button onclick="closeAuthModal()" class="btn-close">&times;</button>
      </div>

      <div class="modal-body" style="padding: 20px;">
        <!-- Quick Login Cards (Sample Indian Officers) -->
        <div style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted); margin-bottom: 10px;">
          ⚡ 1-CLICK QUICK AUTHENTICATE AS SAMPLE INDIAN SOVEREIGN PERSONNEL:
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;">
          <div class="mode-card" style="cursor: pointer;" onclick="quickLogin('IND-NIC-101', 'NIC-ROOT-99824')">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-weight: 700; color: #fff; font-size: 0.82rem;">Dr. Rajesh Sharma</span>
              <span class="badge-tag badge-lvl4">LEVEL-4 (ROOT)</span>
            </div>
            <div style="font-size: 0.72rem; color: var(--color-cyan);">IND-NIC-101 &bull; CISO, NIC Cloud</div>
          </div>

          <div class="mode-card" style="cursor: pointer;" onclick="quickLogin('IND-CERT-202', 'CERT-TOK-4412')">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-weight: 700; color: #fff; font-size: 0.82rem;">Ananya Deshmukh</span>
              <span class="badge-tag badge-lvl3">LEVEL-3 (OPS)</span>
            </div>
            <div style="font-size: 0.72rem; color: var(--color-amber);">IND-CERT-202 &bull; CERT-In Threat Lead</div>
          </div>

          <div class="mode-card" style="cursor: pointer;" onclick="quickLogin('IND-ISRO-303', 'ISRO-SAT-7719')">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-weight: 700; color: #fff; font-size: 0.82rem;">Vikramaditya Rao</span>
              <span class="badge-tag badge-lvl3">LEVEL-3 (OPS)</span>
            </div>
            <div style="font-size: 0.72rem; color: var(--color-amber);">IND-ISRO-303 &bull; ISRO Satellite Lead</div>
          </div>

          <div class="mode-card" style="cursor: pointer;" onclick="quickLogin('IND-INT-010', 'DEV-SANDBOX-101')">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-weight: 700; color: #fff; font-size: 0.82rem;">Aarav Mehta</span>
              <span class="badge-tag badge-lvl1">LEVEL-1 (INTERN)</span>
            </div>
            <div style="font-size: 0.72rem; color: var(--color-cyan);">IND-INT-010 &bull; Cloud Trainee</div>
          </div>
        </div>

        <div style="text-align: center; color: var(--text-dim); font-size: 0.76rem; font-family: var(--font-mono); margin: 12px 0;">
          ─── OR ENTER CUSTOM PERSONNEL ID &amp; PASSCODE ───
        </div>

        <form id="form-auth-manual" onsubmit="handleManualAuth(event)">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">PERSONNEL ID / ACCESS TOKEN:</label>
              <input type="text" id="auth-input-id" class="form-input" placeholder="e.g. IND-NIC-101 or Asset ID" required>
            </div>
            <div class="form-group">
              <label class="form-label">SECURITY PASSCODE / KEY:</label>
              <input type="password" id="auth-input-pass" class="form-input" placeholder="e.g. NIC-ROOT-99824" required>
            </div>
          </div>

          <div id="auth-err-msg" style="display: none; color: var(--color-magenta); font-size: 0.78rem; font-family: var(--font-mono); margin-bottom: 12px;"></div>

          <button type="submit" class="btn-send" style="width: 100%; height: 44px;">
            🔓 VERIFY CREDENTIALS &amp; UNLOCK CONSOLE
          </button>
        </form>
      </div>
    </div>
  </div>

  <!-- ==================================================================== -->
  <!-- PHONE & OFFLINE MOBILE ACCESS MODAL -->
  <!-- ==================================================================== -->
  <div id="phone-modal" class="modal-overlay" style="display: none;">
    <div class="modal-card" style="max-width: 620px; width: 95%;">
      <div class="modal-header">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 1.4rem;">📱</span>
          <div>
            <div style="font-family: var(--font-display); font-weight: 700; font-size: 1.1rem; color: #fff;">OFFLINE PHONE &amp; MOBILE ACCESS</div>
            <div style="font-size: 0.75rem; color: var(--color-cyan); font-family: var(--font-mono);">ZERO INTERNET / LOCAL AIR-GAPPED SUITE</div>
          </div>
        </div>
        <button id="btn-close-phone-modal" class="btn-close">&times;</button>
      </div>

      <div class="modal-body" style="padding: 20px;">
        <!-- QR Code & Link Banner -->
        <div style="display: flex; gap: 20px; align-items: center; background: rgba(0,0,0,0.5); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 16px; margin-bottom: 20px; flex-wrap: wrap; justify-content: center;">
          <div id="phone-qr-container" style="background: #0a0e1a; padding: 10px; border-radius: 8px; border: 1px solid var(--border-active); display: flex; justify-content: center; align-items: center; min-width: 180px; min-height: 180px;">
            <!-- SVG QR Code is injected here -->
          </div>

          <div style="flex: 1; min-width: 240px;">
            <div style="font-size: 0.76rem; color: var(--text-muted); font-family: var(--font-mono); margin-bottom: 6px;">SCAN QR OR OPEN ON PHONE BROWSER:</div>
            <div id="phone-url-display" style="font-family: var(--font-mono); font-size: 1.05rem; font-weight: 700; color: var(--color-cyan); word-break: break-all; margin-bottom: 12px; background: rgba(0,240,255,0.08); padding: 8px 12px; border-radius: 6px; border: 1px dashed var(--color-cyan);">
              http://127.0.0.1:8000
            </div>
            <button id="btn-copy-phone-url" class="btn-hud" style="width: 100%; justify-content: center; font-size: 0.82rem; background: rgba(0,240,255,0.15); border-color: var(--color-cyan);">
              📋 COPY PHONE LINK
            </button>
          </div>
        </div>

        <!-- 3 Offline Phone Usage Modes -->
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <div class="mode-card">
            <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--color-emerald); font-size: 0.88rem; margin-bottom: 4px;">
              <span>📶 MODE 1: LOCAL WI-FI / PHONE HOTSPOT (NO INTERNET NEEDED)</span>
            </div>
            <p style="font-size: 0.78rem; color: var(--text-muted); margin: 0; line-height: 1.4;">
              Connect your phone and PC to the same Wi-Fi router or turn on your phone/PC mobile hotspot (mobile data can be OFF). Open the link or scan QR code above.
            </p>
          </div>

          <div class="mode-card">
            <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--color-cyan); font-size: 0.88rem; margin-bottom: 4px;">
              <span>📲 MODE 2: INSTALL AS STANDALONE PHONE APP (PWA)</span>
            </div>
            <p style="font-size: 0.78rem; color: var(--text-muted); margin: 0; line-height: 1.4;">
              Open the link in <b>Chrome</b> (Android) or <b>Safari</b> (iOS) and tap <b>"Add to Home Screen"</b> / <b>"Install App"</b>. It installs as a full-screen offline native app icon without browser borders!
            </p>
          </div>

          <div class="mode-card">
            <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--color-amber); font-size: 0.88rem; margin-bottom: 4px;">
              <span>⚡ MODE 3: RUN 100% DIRECTLY ON PHONE (TERMUX / PYDROID 3)</span>
            </div>
            <p style="font-size: 0.78rem; color: var(--text-muted); margin: 0; line-height: 1.4;">
              To run without your PC: On Android, install <b>Termux</b>, copy the folder to your phone, and run <code>python app.py</code>. The entire RAG pipeline runs 100% locally on your phone's processor!
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Client Script (100% Pure JavaScript, No CDNs) -->
  <script>
    // Register Service Worker for Offline PWA support
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then((reg) => {
          console.log('[Sovereign PWA] Service Worker active, offline ready:', reg.scope);
        }).catch((err) => {
          console.log('[Sovereign PWA] Service Worker registration failed:', err);
        });
      });
    }

    // Active Authenticated Officer State
    let currentAuthSession = {
      authenticated: true,
      session_token: "INIT-ROOT",
      user_id: "IND-NIC-101",
      name: "Dr. Rajesh Kumar Sharma",
      designation: "Chief Information Security Officer",
      department: "NIC National Data Center",
      station: "New Delhi",
      clearance_level: 4,
      subsystem: "MeghRaj Cloud Master Node"
    };

    let cachedVaultDocs = [];
    let parsedDatasetRows = [];

    // Tab Navigation
    function switchTab(tabId) {
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      
      const panel = document.getElementById('tab-' + tabId);
      if (panel) panel.classList.add('active');
      
      const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick')?.includes(tabId));
      if (activeBtn) activeBtn.classList.add('active');
      
      if (tabId === 'vault') loadKnowledgeBase();
      if (tabId === 'audit') loadAuditLogs();
    }

    // Auth Modal Handlers
    function openAuthModal() {
      document.getElementById('auth-modal').style.display = 'flex';
      document.getElementById('auth-err-msg').style.display = 'none';
    }
    function closeAuthModal() {
      document.getElementById('auth-modal').style.display = 'none';
    }
    document.getElementById('btn-auth-switch').addEventListener('click', openAuthModal);

    async function quickLogin(userId, passcode) {
      await performAuthentication(userId, passcode);
    }

    async function handleManualAuth(e) {
      e.preventDefault();
      const id = document.getElementById('auth-input-id').value.trim();
      const pass = document.getElementById('auth-input-pass').value.trim();
      await performAuthentication(id, pass);
    }

    async function performAuthentication(userId, passcode) {
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ personnel_id: userId, passcode: passcode })
        });
        const data = await res.json();
        if (data.authenticated) {
          currentAuthSession = data.profile;
          updateAuthUI();
          closeAuthModal();
          alert(`✅ Authenticated as ${currentAuthSession.name} (Clearance Level ${currentAuthSession.clearance_level})!`);
        } else {
          const errMsg = document.getElementById('auth-err-msg');
          errMsg.textContent = '❌ ' + (data.message || 'Authentication Failed');
          errMsg.style.display = 'block';
        }
      } catch (err) {
        alert('Authentication error: ' + err.message);
      }
    }

    function updateAuthUI() {
      const topBadge = document.getElementById('top-clearance-badge');
      const topPulse = document.getElementById('top-pulse-dot');
      const roleText = document.getElementById('role-display-text');
      const authBanner = document.getElementById('auth-officer-banner');
      const lockBanner = document.getElementById('auth-lock-banner');
      const chatInput = document.getElementById('chat-input');
      const btnSend = document.getElementById('btn-send');

      if (currentAuthSession && currentAuthSession.authenticated) {
        const lvl = currentAuthSession.clearance_level;
        topBadge.className = 'badge-clearance badge-lvl' + lvl;
        topPulse.className = 'pulse-dot emerald';
        roleText.textContent = `AIR-GAPPED // ${currentAuthSession.name.toUpperCase()} (LEVEL-${lvl})`;

        authBanner.style.display = 'flex';
        lockBanner.style.display = 'none';
        document.getElementById('officer-name').textContent = currentAuthSession.name;
        document.getElementById('officer-id').textContent = `(${currentAuthSession.user_id})`;
        document.getElementById('officer-dept').textContent = `${currentAuthSession.designation} • ${currentAuthSession.department}`;
        document.getElementById('officer-lvl-tag').className = 'badge-tag badge-lvl' + lvl;
        document.getElementById('officer-lvl-tag').textContent = `LEVEL-${lvl}`;

        chatInput.disabled = false;
        chatInput.placeholder = `Query knowledge base as ${currentAuthSession.name} (Clearance Level ${lvl})...`;
        btnSend.disabled = false;
      } else {
        topBadge.className = 'badge-clearance badge-lvl1';
        topPulse.className = 'pulse-dot magenta';
        roleText.textContent = 'AIR-GAPPED // ACCESS LOCKED (UNAUTHENTICATED)';

        authBanner.style.display = 'none';
        lockBanner.style.display = 'block';

        chatInput.disabled = true;
        chatInput.placeholder = '🔒 Authentication required. Click "AUTHENTICATE NOW" above...';
        btnSend.disabled = true;
      }
    }

    // Chat Execution
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const chatMessages = document.getElementById('chat-messages');
    const chatStatus = document.getElementById('chat-status');
    const sourcesList = document.getElementById('sources-list');
    const sourcesCount = document.getElementById('sources-count');

    async function sendQuery(queryText) {
      if (!currentAuthSession || !currentAuthSession.authenticated) {
        openAuthModal();
        return;
      }

      const query = queryText || chatInput.value.trim();
      if (!query) return;

      appendMessage('user', query);
      chatInput.value = '';
      chatStatus.textContent = 'PROCESSING QUERY...';
      chatStatus.style.color = 'var(--color-cyan)';

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            query: query, 
            auth_token: currentAuthSession.session_token,
            personnel_id: currentAuthSession.user_id,
            clearance_level: currentAuthSession.clearance_level 
          })
        });

        if (res.status === 401) {
          appendMessage('assistant', '🔒 <b>Access Denied:</b> Authentication required. Please log in with valid credentials.');
          currentAuthSession.authenticated = false;
          updateAuthUI();
          return;
        }

        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();

        // Render Assistant Response
        renderAssistantResponse(data);
        renderSources(data.sources || []);
        renderInspectorTrace(data.trace || {});
        chatStatus.textContent = 'READY (' + (data.latency_ms || 0) + 'ms)';
        chatStatus.style.color = 'var(--color-emerald)';
      } catch (err) {
        appendMessage('assistant', '⚠️ <b>Error connecting to Sovereign RAG Pipeline:</b> ' + err.message);
        chatStatus.textContent = 'ERROR';
        chatStatus.style.color = 'var(--color-magenta)';
      }
    }

    btnSend.addEventListener('click', () => sendQuery());
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendQuery();
    });

    function askPreset(promptText) {
      chatInput.value = promptText;
      sendQuery(promptText);
    }

    function appendMessage(role, text) {
      const div = document.createElement('div');
      div.className = 'msg-bubble ' + role;
      div.innerHTML = text;
      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function renderAssistantResponse(data) {
      const sources = data.sources || [];
      const redactionOccurred = data.redaction_occurred;

      let html = `<div style="margin-bottom: 8px;">`;
      if (redactionOccurred) {
        html += `<span class="badge-tag badge-lvl4" style="margin-bottom: 6px; display: inline-block;">⚠️ SENSITIVE SECRETS REDACTED (CLEARANCE LEVEL RESTRICTED)</span><br>`;
      } else {
        html += `<span class="badge-tag badge-lvl2" style="margin-bottom: 6px; display: inline-block;">✅ VERIFIED SOVEREIGN KNOWLEDGE RETRIEVAL</span><br>`;
      }
      html += `</div>`;

      if (sources.length === 0) {
        html += `<p>No matching records found in Sovereign Vault for this query.</p>`;
      } else {
        sources.forEach((src, idx) => {
          let text = src.text
            .replace(/### (.*)/g, '<h4 style="color:var(--color-cyan); margin: 8px 0 4px 0;">$1</h4>')
            .replace(/## (.*)/g, '<h3 style="color:#fff; margin: 10px 0 6px 0;">$1</h3>')
            .replace(/# (.*)/g, '<h2 style="color:#fff; margin: 12px 0 8px 0;">$1</h2>')
            .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
            .replace(/`([^`]+)`/g, '<code style="background:rgba(0,240,255,0.08);color:var(--color-cyan);padding:2px 4px;border-radius:3px;">$1</code>');

          html += `<div style="background: rgba(0,0,0,0.35); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <span style="font-weight:700; color:#fff; font-size:0.85rem;">[${idx+1}] ${src.title}</span>
              <span class="badge-tag badge-lvl${src.clearance_level}">LEVEL-${src.clearance_level}</span>
            </div>
            <div style="font-size:0.86rem; color:var(--text-main); line-height:1.5;">${text}</div>
          </div>`;
        });
      }

      appendMessage('assistant', html);
    }

    function renderSources(sources) {
      sourcesCount.textContent = sources.length + ' SOURCES';
      if (sources.length === 0) {
        sourcesList.innerHTML = `<p style="color: var(--text-dim); font-size: 0.82rem; text-align: center; margin-top: 40px;">No sources retrieved.</p>`;
        return;
      }

      sourcesList.innerHTML = sources.map((s, idx) => `
        <div class="source-card">
          <div class="source-header">
            <span style="font-weight:700; color:#fff; font-size:0.82rem;">${s.title}</span>
            <span class="source-score">${(s.hybrid_score * 100).toFixed(1)}%</span>
          </div>
          <div style="display:flex; gap:6px; margin-bottom:6px; font-size:0.72rem;">
            <span class="badge-tag badge-lvl${s.clearance_level}">LVL-${s.clearance_level}</span>
            <span style="color:var(--text-muted);">${s.category}</span>
          </div>
          <div style="font-size:0.78rem; color:var(--text-muted); max-height:80px; overflow-y:auto;">
            ${s.text.substring(0, 160)}...
          </div>
        </div>
      `).join('');
    }

    function renderInspectorTrace(trace) {
      const el = document.getElementById('inspector-content');
      const latencyEl = document.getElementById('trace-latency');
      if (trace.latency_ms) latencyEl.textContent = 'LATENCY: ' + trace.latency_ms + 'ms';

      el.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 16px;">
          <div class="source-card">
            <div style="color: var(--color-cyan); font-weight: 700; margin-bottom: 6px;">STEP 1: IDENTITY &amp; CLEARANCE VERIFICATION</div>
            <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">
              • Authenticated Officer: <b style="color:#fff;">${currentAuthSession.name}</b> (${currentAuthSession.user_id})<br>
              • Clearance Level: <b style="color:var(--color-cyan);">${currentAuthSession.clearance_level}</b> &bull; Department: ${currentAuthSession.department}<br>
              • Query Tokens: <span style="color:var(--color-cyan);">${(trace.query_analysis?.tokens || []).join(', ')}</span>
            </div>
          </div>

          <div class="source-card">
            <div style="color: var(--color-cyan); font-weight: 700; margin-bottom: 6px;">STEP 2: HYBRID VECTOR SEARCH (DENSE + BM25)</div>
            <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">
              • Top-K Chunks Retrieved: <b>${trace.vector_search?.top_k_retrieved || 0}</b><br>
              • Match Breakdown:
              <ul style="margin-left: 20px; margin-top: 4px;">
                ${(trace.vector_search?.sources || []).map(s => `
                  <li>[${s.chunk_id}] <b>${s.title}</b> &rarr; Hybrid: <span style="color:var(--color-cyan);">${s.hybrid_score}</span> | Dense: ${s.dense_score} | Lexical: ${s.lexical_score}</li>
                `).join('')}
              </ul>
            </div>
          </div>

          <div class="source-card">
            <div style="color: var(--color-cyan); font-weight: 700; margin-bottom: 6px;">STEP 3: RBAC ENFORCEMENT &amp; DYNAMIC REDACTION</div>
            <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">
              • Authorized Chunks: <b style="color:var(--color-emerald);">${trace.rbac_evaluation?.access_granted_chunks || 0}</b><br>
              • Redacted Chunks: <b style="color:var(--color-magenta);">${trace.rbac_evaluation?.redacted_chunks || 0}</b><br>
              • Pipeline Verdict: <b style="color:#fff;">${trace.rbac_evaluation?.verdict || 'AUTHORIZED'}</b>
            </div>
          </div>
        </div>
      `;
    }

    // ====================================================================
    // DATASET LOADER & IMPORTER
    // ====================================================================
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const csvTextInput = document.getElementById('csv-text-input');
    const btnDownloadTemplate = document.getElementById('btn-download-template');
    const btnIngestDataset = document.getElementById('btn-ingest-dataset');
    const previewRowCount = document.getElementById('preview-row-count');
    const previewTableHead = document.getElementById('preview-table-head');
    const previewTableBody = document.getElementById('preview-table-body');
    const importTelemetryBox = document.getElementById('import-telemetry-box');

    async function loadIndianSampleDataset(datasetType) {
      try {
        const res = await fetch('/api/datasets/sample?name=' + datasetType);
        const data = await res.json();
        if (data.csv) {
          csvTextInput.value = data.csv;
          const rows = parseCSVText(data.csv);
          renderTabularPreview(rows);
          alert(`🇮🇳 Loaded ${data.title} (${rows.length} records ready to ingest)!`);
        }
      } catch (err) {
        alert('Failed to load sample dataset: ' + err.message);
      }
    }

    function parseCSVText(csvText) {
      const lines = csvText.trim().split(/\r\n|\n/).filter(l => l.trim().length > 0);
      if (lines.length < 2) return [];

      const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
      const rows = [];

      for (let i = 1; i < lines.length; i++) {
        const line = lines[i];
        const values = [];
        let inQuote = false;
        let curVal = '';

        for (let j = 0; j < line.length; j++) {
          const char = line[j];
          if (char === '"' || char === "'") {
            inQuote = !inQuote;
          } else if (char === ',' && !inQuote) {
            values.push(curVal.trim().replace(/^["']|["']$/g, ''));
            curVal = '';
          } else {
            curVal += char;
          }
        }
        values.push(curVal.trim().replace(/^["']|["']$/g, ''));

        if (values.length === headers.length) {
          const rowObj = {};
          headers.forEach((h, idx) => { rowObj[h] = values[idx]; });
          rows.push(rowObj);
        }
      }
      return rows;
    }

    function renderTabularPreview(rows) {
      parsedDatasetRows = rows;
      previewRowCount.textContent = rows.length + ' ROWS READY';

      if (rows.length === 0) {
        previewTableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 40px 0;">No data loaded.</td></tr>`;
        return;
      }

      const keys = Object.keys(rows[0]);
      previewTableHead.innerHTML = `<tr>${keys.map(k => `<th>${k.toUpperCase()}</th>`).join('')}</tr>`;

      previewTableBody.innerHTML = rows.slice(0, 15).map(r => `
        <tr>
          ${keys.map((k, idx) => {
            let val = r[k] || '';
            if (idx === 0) return `<td style="font-family: var(--font-mono); font-weight: 700; color: var(--color-cyan);">${val}</td>`;
            if (k.toLowerCase().includes('clearance')) return `<td><span class="badge-tag badge-lvl${val}">LVL-${val}</span></td>`;
            if (k.toLowerCase().includes('passcode') || k.toLowerCase().includes('secret') || k.toLowerCase().includes('token')) {
              return `<td style="font-family:var(--font-mono); color:var(--color-amber);">•••••••• (${val.substring(0,3)}...)</td>`;
            }
            return `<td>${val}</td>`;
          }).join('')}
        </tr>
      `).join('');
    }

    if (dropZone) {
      dropZone.addEventListener('click', () => fileInput.click());
      dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--color-cyan)'; });
      dropZone.addEventListener('dragleave', () => { dropZone.style.borderColor = 'var(--border-subtle)'; });
      dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border-subtle)';
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
      });
    }

    if (fileInput) {
      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
      });
    }

    function handleFile(file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result;
        csvTextInput.value = text;
        const rows = parseCSVText(text);
        renderTabularPreview(rows);
      };
      reader.readAsText(file);
    }

    if (csvTextInput) {
      csvTextInput.addEventListener('input', () => {
        const rows = parseCSVText(csvTextInput.value);
        renderTabularPreview(rows);
      });
    }

    if (btnDownloadTemplate) {
      btnDownloadTemplate.addEventListener('click', async () => {
        const res = await fetch('/api/datasets/sample?name=cyber');
        const data = await res.json();
        const blob = new Blob([data.csv || ''], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'indian_sovereign_dataset_template.csv';
        a.click();
        URL.revokeObjectURL(url);
      });
    }

    if (btnIngestDataset) {
      btnIngestDataset.addEventListener('click', async () => {
        const csvRaw = csvTextInput.value.trim();
        if (!csvRaw && parsedDatasetRows.length === 0) {
          alert('Please upload a CSV/Excel file or load a sample dataset first.');
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
              <b>✅ DATASET INGESTION &amp; CREDENTIAL SYNC COMPLETE!</b><br>
              • Ingested <b>${data.added_count}</b> new records into Sovereign Vault.<br>
              • Registered <b>${data.registered_officers || data.added_count}</b> new personnel credentials in Authentication Gate.<br>
              • Vector Space Re-Indexed: <b>${data.total_documents} total documents</b> across <b>${data.total_chunks} semantic chunks</b>.<br>
              • Switch to the <b>💬 Sovereign Chatbot</b> tab to query the newly ingested records!
            `;
            loadKnowledgeBase();
            alert(`🎉 Success! ${data.added_count} records indexed and credentials synced. You can now query and authenticate with them!`);
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

    // Knowledge Base Management
    async function loadKnowledgeBase() {
      try {
        const res = await fetch('/api/knowledge');
        const docs = await res.json();
        cachedVaultDocs = docs;

        document.getElementById('vault-doc-count').textContent = docs.length + ' DOCUMENTS';
        const tbody = document.getElementById('vault-table-body');
        
        if (docs.length === 0) {
          tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 30px;">Vault is empty.</td></tr>`;
          return;
        }

        tbody.innerHTML = docs.map(d => `
          <tr>
            <td style="font-family: var(--font-mono); font-weight: 700; color: var(--color-cyan);">${d.doc_id}</td>
            <td style="font-weight: 600; color: #fff;">${d.title}</td>
            <td>${d.category || 'General'}</td>
            <td><span class="badge-tag badge-lvl${d.clearance_level}">LEVEL-${d.clearance_level}</span></td>
            <td>
              <button class="btn-hud" onclick="deleteDoc('${d.doc_id}')" style="padding: 2px 8px; font-size: 0.72rem; color: var(--color-magenta); border-color: var(--border-danger);">
                DELETE
              </button>
            </td>
          </tr>
        `).join('');
      } catch (err) {
        console.error('Failed to load KB:', err);
      }
    }

    async function deleteDoc(docId) {
      if (!confirm(`Delete document "${docId}" from Sovereign Vault?`)) return;
      try {
        await fetch('/api/knowledge?id=' + encodeURIComponent(docId), { method: 'DELETE' });
        loadKnowledgeBase();
      } catch (err) {
        alert('Failed to delete document: ' + err.message);
      }
    }

    // Add Document Form
    const formAddDoc = document.getElementById('form-add-doc');
    formAddDoc.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('doc-title').value.trim();
      const category = document.getElementById('doc-category').value.trim();
      const clearance = parseInt(document.getElementById('doc-clearance').value);
      const content = document.getElementById('doc-content').value.trim();

      try {
        const res = await fetch('/api/knowledge', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, category, clearance_level: clearance, content })
        });
        if (res.ok) {
          formAddDoc.reset();
          loadKnowledgeBase();
          alert('✅ Document successfully stored in vault & re-indexed!');
        }
      } catch (err) {
        alert('Error adding document: ' + err.message);
      }
    });

    // Audit Logs
    async function loadAuditLogs() {
      try {
        const res = await fetch('/api/audit');
        const logs = await res.json();
        const tbody = document.getElementById('audit-table-body');
        if (logs.length === 0) {
          tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 30px;">No audit events recorded yet.</td></tr>`;
          return;
        }

        tbody.innerHTML = logs.slice().reverse().map(l => {
          const dateStr = new Date(l.timestamp * 1000).toLocaleTimeString();
          return `
            <tr>
              <td style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted);">${dateStr}</td>
              <td style="color: var(--color-cyan); font-family: var(--font-mono); font-size: 0.78rem;">${l.officer_id || 'OFFICER'} (LVL-${l.user_clearance})</td>
              <td style="color: #fff; font-weight: 600;">${l.query}</td>
              <td><span style="font-family: var(--font-mono); font-size: 0.75rem; color: ${l.redaction_occurred ? 'var(--color-magenta)' : 'var(--color-emerald)'}">${l.verdict}</span></td>
              <td style="font-family: var(--font-mono); font-size: 0.75rem;">${(l.retrieved_docs || []).join(', ')}</td>
              <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--color-cyan);">${l.latency_ms}ms</td>
            </tr>
          `;
        }).join('');
      } catch (err) {
        console.error('Failed to load audit logs:', err);
      }
    }

    // Phone Modal Handlers
    const btnOpenPhoneModal = document.getElementById('btn-phone-modal');
    const btnClosePhoneModal = document.getElementById('btn-close-phone-modal');
    const phoneModal = document.getElementById('phone-modal');
    const phoneUrlDisplay = document.getElementById('phone-url-display');
    const phoneQrContainer = document.getElementById('phone-qr-container');
    const btnCopyPhoneUrl = document.getElementById('btn-copy-phone-url');

    async function loadNetworkInfo() {
      try {
        const res = await fetch('/api/network-info');
        const data = await res.json();
        if (data.phone_url) {
          phoneUrlDisplay.textContent = data.phone_url;
        }
        if (data.qr_svg) {
          phoneQrContainer.innerHTML = data.qr_svg;
        }
      } catch (err) {
        phoneUrlDisplay.textContent = window.location.origin;
      }
    }

    if (btnOpenPhoneModal) {
      btnOpenPhoneModal.addEventListener('click', () => {
        loadNetworkInfo();
        phoneModal.style.display = 'flex';
      });
    }

    if (btnClosePhoneModal) {
      btnClosePhoneModal.addEventListener('click', () => {
        phoneModal.style.display = 'none';
      });
    }

    phoneModal.addEventListener('click', (e) => {
      if (e.target === phoneModal) phoneModal.style.display = 'none';
    });

    if (btnCopyPhoneUrl) {
      btnCopyPhoneUrl.addEventListener('click', () => {
        navigator.clipboard.writeText(phoneUrlDisplay.textContent.trim()).then(() => {
          btnCopyPhoneUrl.textContent = '✅ COPIED TO CLIPBOARD!';
          setTimeout(() => { btnCopyPhoneUrl.textContent = '📋 COPY PHONE LINK'; }, 2000);
        }).catch(() => {
          prompt('Copy phone link manually:', phoneUrlDisplay.textContent.trim());
        });
      });
    }

    // Initial Startup Load
    updateAuthUI();
    loadKnowledgeBase();
    loadNetworkInfo();
    loadIndianSampleDataset('cyber');
  </script>
</body>
</html>
"""


class SovereignRAGHTTPHandler(http.server.BaseHTTPRequestHandler):
    """
    Pure Python HTTP REST API and UI Server.
    Handles static single-page UI, PWA assets, QR generation, Auth verification, and JSON REST endpoints.
    """
    protocol_version = "HTTP/1.1"

    def _send_json(self, data: Any, status_code: int = 200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _send_html(self, html_content: str):
        body = html_content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _send_text(self, text_content: str, content_type: str = 'application/javascript'):
        body = text_content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', f'{content_type}; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()


    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query_params = urllib.parse.parse_qs(parsed.query)

            # 1. Main Web UI
            if path == '/' or path == '/index.html':
                self._send_html(UI_HTML)
                return

            # 2. PWA Web App Manifest
            elif path == '/manifest.json':
                self._send_json(PWA_MANIFEST)
                return

            # 3. PWA Service Worker
            elif path == '/sw.js':
                self._send_text(SERVICE_WORKER_JS, 'application/javascript')
                return

            # 4. App Icon SVG
            elif path == '/api/icon.svg':
                self._send_text(APP_ICON_SVG, 'image/svg+xml')
                return

            # 5. REST API: Local Network Info & Phone Link
            elif path == '/api/network-info':
                local_ip = get_local_lan_ip()
                phone_url = f"http://{local_ip}:{PORT}"
                qr_svg = generate_qr_svg(phone_url, size_px=180, fg_color="#00f0ff", bg_color="#0a0e1a")
                self._send_json({
                    "localhost": f"http://localhost:{PORT}",
                    "lan_ip": local_ip,
                    "phone_url": phone_url,
                    "port": PORT,
                    "qr_svg": qr_svg
                })
                return

            # 6. REST API: Sample Indian Sovereign Datasets
            elif path == '/api/datasets/sample':
                dataset_name = query_params.get('name', ['cyber'])[0].lower()
                if dataset_name == 'infra':
                    self._send_json({
                        "name": "infra",
                        "title": "National Critical Infrastructure & PSU Assets",
                        "csv": INDIAN_CRITICAL_INFRA_DATASET_CSV
                    })
                elif dataset_name == 'banking':
                    self._send_json({
                        "name": "banking",
                        "title": "Indian Banking & Payment Switch Hub (NPCI / RBI / Aadhaar)",
                        "csv": INDIAN_BANKING_NPCI_DATASET_CSV
                    })
                else:
                    self._send_json({
                        "name": "cyber",
                        "title": "National Cyber Defense & NIC Cloud Registry (MeghRaj / CERT-In)",
                        "csv": INDIAN_CYBER_NIC_DATASET_CSV
                    })
                return

            # 7. REST API: Sample Indian Officer Profiles
            elif path == '/api/auth/profiles':
                profiles = auth_manager.get_sample_officer_profiles()
                self._send_json(profiles)
                return

            # 8. REST API: Knowledge Base
            elif path == '/api/knowledge':
                docs = vault_manager.get_all_documents()
                self._send_json(docs)
                return

            # 9. REST API: Audit Logs
            elif path == '/api/audit':
                logs = rag_engine.get_audit_logs()
                self._send_json(logs)
                return

            # 10. REST API: Stats
            elif path == '/api/stats':
                stats = vault_manager.get_stats()
                stats["total_indexed_chunks"] = len(vector_engine.chunks)
                self._send_json(stats)
                return

            # 11. REST API: Clearance Levels Metadata
            elif path == '/api/clearance-levels':
                self._send_json(CLEARANCE_LEVELS)
                return

            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._send_json({"status": "error", "message": str(e)}, 500)


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

            # 1. Credential Login & Identity Verification Endpoint
            if path == '/api/auth/login':
                personnel_id = payload.get('personnel_id', '')
                passcode = payload.get('passcode', '')
                auth_res = auth_manager.authenticate(personnel_id, passcode)
                if auth_res["authenticated"]:
                    self._send_json(auth_res, 200)
                else:
                    self._send_json(auth_res, 401)
                return

            # 2. Chat & RAG Query Endpoint (Enforces Credential Gate)
            elif path == '/api/chat':
                query_str = payload.get('query', '')
                auth_token = payload.get('auth_token', '')
                personnel_id = payload.get('personnel_id', '')
                
                # Verify active credentials
                session = auth_manager.validate_session(auth_token or personnel_id)
                if not session:
                    # Reject unauthenticated chat requests
                    self._send_json({
                        "error": "CREDENTIALS_REQUIRED",
                        "status": "UNAUTHENTICATED",
                        "message": "🔒 Access Denied: Valid Personnel ID and Security Passcode required to query Sovereign Vault."
                    }, 401)
                    return

                # Authenticated: execute RAG query with officer's verified clearance
                clearance_lvl = session.get('clearance_level', 1)
                result = rag_engine.query(user_query=query_str, user_clearance=clearance_lvl, top_k=4)
                
                # Tag officer details in audit trace
                if "trace" in result and "query_analysis" in result["trace"]:
                    result["trace"]["query_analysis"]["officer_id"] = session.get("user_id")
                    result["trace"]["query_analysis"]["officer_name"] = session.get("name")
                    result["trace"]["query_analysis"]["department"] = session.get("department")

                self._send_json(result)
                return

            # 3. Add New Knowledge Entry
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
                rag_engine.reindex_knowledge_base()
                self._send_json({"status": "success", "doc": doc})
                return

            # 4. Re-index Vector Space
            elif path == '/api/reindex':
                rag_engine.reindex_knowledge_base()
                self._send_json({
                    "status": "success",
                    "indexed_documents": len(vault_manager.documents),
                    "indexed_chunks": len(vector_engine.chunks)
                })
                return

            # 5. Upload CSV / Excel Dataset Endpoint (Syncs with Vault & Auth Registry)
            elif path == '/api/upload-dataset':
                rows = payload.get('rows', [])
                csv_text = payload.get('csv_text', '')
                
                if csv_text and not rows:
                    f = io.StringIO(csv_text.strip())
                    reader = csv.DictReader(f)
                    rows = [r for r in reader]
                    
                if rows:
                    added = vault_manager.ingest_tabular_rows(rows)
                    reg_count = auth_manager.register_users_from_tabular_rows(rows)
                    rag_engine.reindex_knowledge_base()
                    self._send_json({
                        "status": "success",
                        "added_count": len(added),
                        "registered_officers": reg_count,
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

    def address_string(self):
        # Prevent slow or hanging reverse DNS lookups in offline/air-gapped networks!
        try:
            return self.client_address[0]
        except Exception:
            return "127.0.0.1"

    def log_message(self, format, *args):
        try:
            sys.stdout.write(f"[Sovereign HTTP] {self.address_string()} - [{self.log_date_time_string()}] {format%args}\n")
            sys.stdout.flush()
        except Exception:
            pass



def run_app():
    global PORT
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    local_ip = get_local_lan_ip()
    
    print("===============================================================================")
    print("  SOVEREIGN RAG // INDIAN ENTERPRISE & DEFENSE SUITE ACTIVE")
    print(f"  Indexed Documents: {len(vault_manager.documents)}")
    print(f"  Indexed Semantic Chunks: {len(vector_engine.chunks)}")
    print(f"  Registered Personnel Credentials: {len(auth_manager.users)}")
    print("===============================================================================")
    print(f"  --> COMPUTER (LOCALHOST):    http://localhost:{PORT}")
    print(f"  --> PHONE / LAN ACCESS:      http://{local_ip}:{PORT}")
    print(f"  --> CREDENTIAL GATE:         Personnel Authentication Active")
    print("===============================================================================")
    sys.stdout.flush()

    for attempt_port in range(PORT, PORT + 50):
        try:
            http.server.ThreadingHTTPServer.allow_reuse_address = True
            with http.server.ThreadingHTTPServer(("0.0.0.0", attempt_port), SovereignRAGHTTPHandler) as httpd:
                PORT = attempt_port
                bound_port = httpd.server_address[1]
                print(f"  --> SERVER SUCCESSFULLY BOUND AND LISTENING ON PORT: {bound_port}")
                sys.stdout.flush()
                httpd.serve_forever()
        except (OSError, PermissionError) as err:
            continue




if __name__ == "__main__":
    run_app()
