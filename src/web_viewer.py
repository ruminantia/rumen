"""Web viewer for Rumen LLM processing system.

This module generates a static HTML/CSS/JS website for managing and monitoring
the Rumen LLM processing system.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def create_web_viewer(viewer_dir: str = "/app/viewer") -> None:
    """Create the web viewer interface.

    Args:
        viewer_dir: Directory to create viewer files in
    """
    logger.info("Creating web viewer...")

    # Create directories
    assets_dir = os.path.join(viewer_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Create static files
    create_index_html(viewer_dir)
    create_stylesheet(assets_dir)
    create_javascript(assets_dir)

    logger.info(f"✅ Web viewer created at {viewer_dir}")


def create_index_html(viewer_dir: str) -> None:
    """Create index.html file."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐄 Rumen - LLM Processing System</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🐄 Rumen</h1>
            <div class="header-controls">
                <button id="settings-toggle" aria-label="Settings">⚙️</button>
                <button id="theme-toggle" aria-label="Toggle theme">◐</button>
            </div>
        </header>

        <!-- Navigation Tabs -->
        <nav class="nav-tabs">
            <button class="nav-tab active" data-tab="dashboard">Dashboard</button>
            <button class="nav-tab" data-tab="inputs">Input Files</button>
            <button class="nav-tab" data-tab="outputs">Output Files</button>
        </nav>

        <!-- Settings Overlay -->
        <div id="settings-overlay" class="settings-overlay">
            <div class="settings-container">
                <div class="settings-header">
                    <h2>Settings</h2>
                    <button id="settings-close" aria-label="Close settings">✕</button>
                </div>
                <div class="settings-content">
                    <h3>Configuration (config.ini)</h3>
                    <textarea id="config-content" class="config-editor" spellcheck="false">Loading...</textarea>
                    <div class="settings-actions">
                        <button id="save-config" class="save-button">Save Changes</button>
                        <span id="save-status" class="save-status"></span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard-tab" class="tab-content active">
            <div class="status-section">
                <h2>System Status</h2>
                <div class="status-grid">
                    <div class="status-card" id="file-monitor-status">
                        <div class="status-label">File Monitor</div>
                        <div class="status-value">Loading...</div>
                    </div>
                    <div class="status-card">
                        <div class="status-label">Enabled Folders</div>
                        <div class="status-value" id="enabled-folders-count">-</div>
                    </div>
                    <div class="status-card">
                        <div class="status-label">Total Input Files</div>
                        <div class="status-value" id="total-input-files">-</div>
                    </div>
                    <div class="status-card">
                        <div class="status-label">Total Output Files</div>
                        <div class="status-value" id="total-output-files">-</div>
                    </div>
                </div>
            </div>

            <div class="folders-section">
                <h2>Configured Folders</h2>
                <div id="folders-grid" class="folders-grid">
                    <div class="loading">Loading folder configurations...</div>
                </div>
            </div>

            <div class="logs-section">
                <div class="logs-header">
                    <h3>Logs</h3>
                    <div class="logs-controls">
                        <button id="refresh-logs">Refresh</button>
                        <button id="toggle-logs">Show Logs</button>
                    </div>
                </div>
                <div id="logs-content" class="logs-hidden">
                    <div class="logs-text"></div>
                </div>
            </div>
        </div>

        <!-- Input Files Tab -->
        <div id="inputs-tab" class="tab-content">
            <div class="browser-section">
                <div class="browser-header">
                    <h2>Input Files</h2>
                    <div class="browser-controls">
                        <select id="input-folder-select">
                            <option value="">Select folder...</option>
                        </select>
                        <button id="refresh-inputs" class="btn-secondary">Refresh</button>
                    </div>
                </div>
                <div id="input-files-grid" class="files-grid">
                    <div class="placeholder">Select a folder to view files</div>
                </div>
            </div>
            <div id="input-file-content" class="file-content hidden">
                <div class="file-content-header">
                    <h3 id="input-file-title">File Content</h3>
                    <button id="close-input-content" class="btn-secondary">Close</button>
                </div>
                <pre id="input-file-text"></pre>
            </div>
        </div>

        <!-- Output Files Tab -->
        <div id="outputs-tab" class="tab-content">
            <div class="browser-section">
                <div class="browser-header">
                    <h2>Output Files</h2>
                    <div class="browser-controls">
                        <select id="output-folder-select">
                            <option value="">Select folder...</option>
                        </select>
                        <button id="refresh-outputs" class="btn-secondary">Refresh</button>
                    </div>
                </div>
                <div id="output-files-grid" class="files-grid">
                    <div class="placeholder">Select a folder to view files</div>
                </div>
            </div>
            <div id="output-file-content" class="file-content hidden">
                <div class="file-content-header">
                    <h3 id="output-file-title">File Content</h3>
                    <button id="close-output-content" class="btn-secondary">Close</button>
                </div>
                <div id="output-file-text" class="markdown-content"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
    <script src="assets/app.js"></script>
</body>
</html>
"""

    html_path = os.path.join(viewer_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.debug(f"Created {html_path}")
# Helper functions for web viewer

def create_stylesheet(assets_dir: str) -> None:
    """Create style.css file matching Pasture aesthetic."""
    import os
    import logging
    logger = logging.getLogger(__name__)
    
    css_content = """/* Rumen Viewer - Minimalist CSS */
:root { --bg-primary: #fff; --bg-secondary: #f6f6f6; --bg-hover: #e8e8e8; --text-primary: #000; --text-secondary: #666; --border: #ccc; --accent: #f60; --success: #4caf50; --error: #f44336; }
[data-theme="dark"] { --bg-primary: #1a1a1a; --bg-secondary: #2a2a2a; --bg-hover: #3a3a3a; --text-primary: #e0e0e0; --text-secondary: #a0a0a0; --border: #444; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Verdana, Geneva, sans-serif; font-size: 14px; line-height: 1.6; background: var(--bg-primary); color: var(--text-primary); }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 2px solid var(--accent); margin-bottom: 20px; }
header h1 { font-size: 24px; color: var(--accent); }
.header-controls button { background: var(--bg-secondary); border: 1px solid var(--border); padding: 8px 12px; cursor: pointer; font-size: 18px; transition: background 0.2s; }
.header-controls button:hover { background: var(--bg-hover); }

/* Settings Overlay */
.settings-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 1000; justify-content: center; align-items: center; }
.settings-overlay.active { display: flex; }
.settings-container { background: var(--bg-secondary); padding: 25px; border-radius: 8px; max-width: 800px; width: 90%; max-height: 85vh; overflow-y: auto; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); }
.settings-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid var(--border); }
.settings-header h2 { margin: 0; font-size: 20px; color: var(--text-primary); }
#settings-close { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 4px; padding: 8px 12px; cursor: pointer; font-size: 18px; transition: background 0.2s; }
#settings-close:hover { background: var(--bg-hover); }
.settings-content h3 { margin-bottom: 15px; font-size: 16px; color: var(--text-primary); }
.settings-actions { display: flex; align-items: center; gap: 15px; }
.save-button { background: var(--accent); color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold; transition: opacity 0.2s; }
.save-button:hover { opacity: 0.9; }
.save-status { font-size: 14px; }
.save-status.success { color: var(--success); }
.save-status.error { color: var(--error); }

.nav-tabs { display: flex; gap: 5px; margin-bottom: 20px; border-bottom: 1px solid var(--border); }
.nav-tab { background: var(--bg-secondary); border: 1px solid var(--border); padding: 10px 20px; cursor: pointer; }
.nav-tab.active { background: var(--bg-primary); font-weight: bold; }
.tab-content { display: none; }
.tab-content.active { display: block; }
.status-section, .folders-section, .config-section, .browser-section { background: var(--bg-secondary); padding: 20px; border-radius: 4px; margin-bottom: 20px; }
.logs-section { margin-top: 30px; background: var(--bg-secondary); padding: 20px; border-radius: 4px; }
.status-section h2, .folders-section h2, .config-section h2 { margin-bottom: 15px; font-size: 18px; }
.status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
.status-card { background: var(--bg-primary); padding: 15px; border-radius: 4px; border: 1px solid var(--border); }
.status-label { font-size: 12px; text-transform: uppercase; color: var(--text-secondary); }
.status-value { font-size: 24px; font-weight: bold; color: var(--accent); }
.status-value.running { color: var(--success); }
.status-value.stopped { color: var(--error); }
.folders-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
.folder-card { background: var(--bg-primary); padding: 15px; border-radius: 4px; border: 1px solid var(--border); }
.folder-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.folder-name { font-weight: bold; }
.folder-status { font-size: 11px; padding: 3px 8px; border-radius: 3px; text-transform: uppercase; background: var(--border); color: var(--text-secondary); }
.folder-status.enabled { background: var(--success); color: white; }
.folder-status.disabled { background: var(--error); color: white; }
.folder-info { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
.config-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
.config-editor { width: 100%; min-height: 500px; font-family: monospace; font-size: 13px; padding: 15px; background: var(--bg-primary); border: 1px solid var(--border); resize: vertical; }
.btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; background: var(--bg-primary); }
.btn-primary { background: var(--accent); color: white; border-color: var(--accent); }
.browser-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
.browser-controls { display: flex; gap: 10px; }
.browser-controls select { padding: 6px 12px; border-radius: 4px; background: var(--bg-primary); border: 1px solid var(--border); }
.files-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; max-height: 600px; overflow-y: auto; }
.file-card { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 4px; padding: 12px; cursor: pointer; }
.file-card:hover { background: var(--bg-hover); }
.file-name { font-weight: bold; margin-bottom: 5px; }
.file-meta { font-size: 11px; color: var(--text-secondary); }
.file-content { margin-top: 20px; }
.file-content.hidden { display: none; }
#input-file-text, #output-file-text { background: var(--bg-primary); border: 1px solid var(--border); padding: 15px; max-height: 600px; overflow-y: auto; }
.logs-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.logs-header h3 { font-size: 18px; color: var(--text-primary); margin: 0; }
.logs-controls { display: flex; gap: 10px; }
.logs-controls button { background: var(--bg-primary); border: 1px solid var(--border); padding: 6px 12px; border-radius: 3px; cursor: pointer; font-size: 13px; transition: background 0.2s; }
.logs-controls button:hover { background: var(--bg-hover); }
#logs-content { max-height: 400px; overflow-y: auto; transition: max-height 0.3s ease; }
#logs-content.logs-hidden { max-height: 0; overflow: hidden; }
.logs-text { background: var(--bg-primary); padding: 15px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4; white-space: pre-wrap; word-wrap: break-word; color: var(--text-primary); }
.log-line { margin-bottom: 2px; }
.log-info { color: #4a9eff; }
.log-warning { color: #ffa500; }
.log-error { color: #ff4444; }
.placeholder { text-align: center; padding: 50px; color: var(--text-secondary); font-style: italic; }
.loading { text-align: center; padding: 30px; color: var(--text-secondary); }

/* Markdown content styling */
#input-file-text h1, #output-file-text h1,
#input-file-text h2, #output-file-text h2,
#input-file-text h3, #output-file-text h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    color: var(--text-primary);
    font-weight: bold;
}
#input-file-text h1, #output-file-text h1 { font-size: 24px; }
#input-file-text h2, #output-file-text h2 { font-size: 20px; }
#input-file-text h3, #output-file-text h3 { font-size: 16px; }
#input-file-text p, #output-file-text p { margin-bottom: 15px; line-height: 1.6; }
#input-file-text pre, #output-file-text pre {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 15px;
    overflow-x: auto;
    margin-bottom: 15px;
}
#input-file-text code, #output-file-text code {
    background: var(--bg-secondary);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 13px;
}
#input-file-text pre code, #output-file-text pre code {
    background: transparent;
    padding: 0;
}
#input-file-text a, #output-file-text a {
    color: var(--accent);
    text-decoration: none;
}
#input-file-text a:hover, #output-file-text a:hover { text-decoration: underline; }
#input-file-text ul, #output-file-text ul,
#input-file-text ol, #output-file-text ol {
    margin-left: 20px;
    margin-bottom: 15px;
}
#input-file-text li, #output-file-text li { margin-bottom: 5px; }
#input-file-text blockquote, #output-file-text blockquote {
    border-left: 3px solid var(--accent);
    padding-left: 15px;
    margin-left: 0;
    margin-bottom: 15px;
    color: var(--text-secondary);
}
#input-file-text table, #output-file-text table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 15px;
}
#input-file-text th, #output-file-text th,
#input-file-text td, #output-file-text td {
    border: 1px solid var(--border);
    padding: 8px 12px;
    text-align: left;
}
#input-file-text th, #output-file-text th {
    background: var(--bg-secondary);
    font-weight: bold;
}
"""

    css_path = os.path.join(assets_dir, "style.css")
    with open(css_path, "w") as f:
        f.write(css_content)
    logger.debug(f"Created {css_path}")


def create_javascript(assets_dir: str) -> None:
    """Create app.js file with application logic."""
    import os
    import logging
    logger = logging.getLogger(__name__)
    
    js_content = """// Rumen Viewer App
const state = { currentTab: 'dashboard' };

document.addEventListener('DOMContentLoaded', async () => {
    setupTabs();
    setupEventListeners();
    initializeTheme();
    await loadDashboard();
});

function initializeTheme() {
    const savedTheme = localStorage.getItem('rumen-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function setupTabs() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
}

function switchTab(name) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector(`[data-tab="${name}"]`).classList.add('active');
    document.getElementById(`${name}-tab`).classList.add('active');
    state.currentTab = name;
    if (name === 'dashboard') loadDashboard();
    else if (name === 'inputs') loadInputFolders();
    else if (name === 'outputs') loadOutputFolders();
}

function setupEventListeners() {
    // Settings overlay
    const settingsOverlay = document.getElementById('settings-overlay');
    const settingsToggle = document.getElementById('settings-toggle');
    const settingsClose = document.getElementById('settings-close');

    settingsToggle.addEventListener('click', () => {
        settingsOverlay.classList.add('active');
        loadConfig();
    });

    settingsClose.addEventListener('click', () => {
        settingsOverlay.classList.remove('active');
    });

    // Close overlay when clicking outside
    settingsOverlay.addEventListener('click', (e) => {
        if (e.target === settingsOverlay) {
            settingsOverlay.classList.remove('active');
        }
    });

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('rumen-theme', next);
    });

    document.getElementById('save-config').addEventListener('click', saveConfig);

    // Logs controls
    document.getElementById('toggle-logs').addEventListener('click', () => {
        const logsContent = document.getElementById('logs-content');
        const toggleBtn = document.getElementById('toggle-logs');

        if (logsContent.classList.contains('logs-hidden')) {
            logsContent.classList.remove('logs-hidden');
            toggleBtn.textContent = 'Hide Logs';
            loadLogs();
        } else {
            logsContent.classList.add('logs-hidden');
            toggleBtn.textContent = 'Show Logs';
        }
    });

    document.getElementById('refresh-logs').addEventListener('click', () => {
        if (!document.getElementById('logs-content').classList.contains('logs-hidden')) {
            loadLogs();
        }
    });

    // Input folder dropdown
    document.getElementById('input-folder-select').addEventListener('change', (e) => {
        if (e.target.value) loadInputFiles(e.target.value);
    });
    document.getElementById('refresh-inputs').addEventListener('click', () => {
        const folder = document.getElementById('input-folder-select').value;
        if (folder) loadInputFiles(folder);
    });

    // Output folder dropdown
    document.getElementById('output-folder-select').addEventListener('change', (e) => {
        if (e.target.value) loadOutputFiles(e.target.value);
    });
    document.getElementById('refresh-outputs').addEventListener('click', () => {
        const folder = document.getElementById('output-folder-select').value;
        if (folder) loadOutputFiles(folder);
    });

    // File content viewers
    document.getElementById('close-input-content').addEventListener('click', () => {
        document.getElementById('input-file-content').classList.add('hidden');
    });
    document.getElementById('close-output-content').addEventListener('click', () => {
        document.getElementById('output-file-content').classList.add('hidden');
    });
}

async function loadDashboard() {
    const [statusRes, foldersRes] = await Promise.all([
        fetch('/api/web/status'),
        fetch('/api/web/folders')
    ]);
    const status = await statusRes.json();
    const folders = await foldersRes.json();
    
    document.querySelector('#file-monitor-status .status-value').textContent = status.file_monitor_running ? 'Running' : 'Stopped';
    document.querySelector('#file-monitor-status .status-value').className = 'status-value ' + (status.file_monitor_running ? 'running' : 'stopped');
    document.getElementById('enabled-folders-count').textContent = status.enabled_folders;
    document.getElementById('total-input-files').textContent = status.total_input_files;
    document.getElementById('total-output-files').textContent = status.total_output_files;
    
    const grid = document.getElementById('folders-grid');
    grid.innerHTML = folders.map(f => `
        <div class="folder-card">
            <div class="folder-header">
                <div class="folder-name">${f.name}</div>
                <div class="folder-status ${f.enabled ? 'enabled' : 'disabled'}">${f.enabled ? 'Enabled' : 'Disabled'}</div>
            </div>
            <div class="folder-info">
                <div>Path: ${f.path}</div>
                <div>Provider: ${f.provider}</div>
                <div>Model: ${f.model}</div>
                <div>Input files: ${f.input_files || 0}</div>
            </div>
        </div>
    `).join('');
}

async function loadConfig() {
    const res = await fetch('/api/web/config');
    const data = await res.json();
    if (data.success && data.content) {
        document.getElementById('config-content').value = data.content;
    } else {
        document.getElementById('config-content').value = 'Error loading configuration: ' + (data.error || 'Unknown error');
    }
}

async function saveConfig() {
    const content = document.getElementById('config-content').value;
    const saveStatus = document.getElementById('save-status');
    const saveButton = document.getElementById('save-config');

    saveButton.disabled = true;
    saveButton.textContent = 'Saving...';
    saveStatus.textContent = '';
    saveStatus.className = 'save-status';

    try {
        const res = await fetch('/api/web/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({content})
        });
        const data = await res.json();

        if (data.success) {
            saveStatus.textContent = '✓ Configuration saved! Reloading UI...';
            saveStatus.className = 'save-status success';
            setTimeout(() => {
                // Reload the dashboard to pick up new settings
                loadDashboard();
                // Close the modal
                document.getElementById('settings-overlay').classList.remove('active');
                // Clear the status message
                setTimeout(() => {
                    saveStatus.textContent = '';
                }, 2000);
            }, 1000);
        } else {
            saveStatus.textContent = '✗ Error: ' + (data.error || 'Unknown error');
            saveStatus.className = 'save-status error';
        }
    } catch (error) {
        saveStatus.textContent = '✗ Error: ' + error.message;
        saveStatus.className = 'save-status error';
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = 'Save Changes';
        setTimeout(() => {
            saveStatus.textContent = '';
        }, 5000);
    }
}

async function loadLogs() {
    const logsText = document.querySelector('.logs-text');
    logsText.innerHTML = '<div class="loading">Loading logs...</div>';

    try {
        const response = await fetch('/api/web/logs');
        const logs = await response.text();

        // Format logs with syntax highlighting
        const formattedLogs = logs.split('\\n').map(line => {
            let className = 'log-line';
            if (line.includes('ERROR') || line.includes('❌')) {
                className += ' log-error';
            } else if (line.includes('WARNING') || line.includes('⚠️')) {
                className += ' log-warning';
            } else if (line.includes('INFO') || line.includes('✅') || line.includes('📊')) {
                className += ' log-info';
            }
            return `<div class="${className}">${escapeHtml(line)}</div>`;
        }).join('');

        logsText.innerHTML = formattedLogs || '<div class="stats-placeholder">No logs available</div>';

        // Auto-scroll to bottom
        const logsContent = document.getElementById('logs-content');
        logsContent.scrollTop = logsContent.scrollHeight;
    } catch (error) {
        logsText.innerHTML = '<div class="error">Failed to load logs</div>';
        console.error('Failed to load logs:', error);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Populate input folder dropdown when switching to inputs tab
async function loadInputFolders() {
    const res = await fetch('/api/web/folders');
    const folders = await res.json();
    const select = document.getElementById('input-folder-select');

    // Only populate if empty (except placeholder)
    if (select.options.length <= 1) {
        select.innerHTML = '<option value="">Select folder...</option>';
        folders.forEach(folder => {
            if (folder.enabled) {
                const option = document.createElement('option');
                option.value = folder.name;
                option.textContent = folder.name;
                select.appendChild(option);
            }
        });
    }
}

// Load input files for selected folder
async function loadInputFiles(folderName) {
    const container = document.getElementById('input-files-grid');
    container.innerHTML = '<div class="loading">Loading files...</div>';

    try {
        const res = await fetch(`/api/web/files/input/${encodeURIComponent(folderName)}`);
        const files = await res.json();

        if (!files || files.length === 0) {
            container.innerHTML = '<div class="placeholder">No files found</div>';
            return;
        }

        container.innerHTML = files.map(file => `
            <div class="file-card" data-file="${file.path}">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${formatFileSize(file.size)}</div>
            </div>
        `).join('');

        container.querySelectorAll('.file-card').forEach(card => {
            card.addEventListener('click', () => loadInputFileContent(card.dataset.file));
        });
    } catch (error) {
        container.innerHTML = '<div class="error">Failed to load files</div>';
        console.error(error);
    }
}

// Load input file content
async function loadInputFileContent(filePath) {
    const viewer = document.getElementById('input-file-content');
    const title = document.getElementById('input-file-title');
    const text = document.getElementById('input-file-text');

    title.textContent = filePath;
    text.innerHTML = '<div class="loading">Loading...</div>';
    viewer.classList.remove('hidden');

    try {
        const res = await fetch(`/api/web/file/content?path=${encodeURIComponent(filePath)}`);
        const data = await res.json();

        if (data.success) {
            // Render as markdown
            text.innerHTML = marked.parse(data.content);
        } else {
            text.innerHTML = '<div class="error">Error: ' + (data.error || 'Unknown error') + '</div>';
        }
    } catch (error) {
        text.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
    }
}

// Populate output folder dropdown
async function loadOutputFolders() {
    const res = await fetch('/api/web/folders');
    const folders = await res.json();
    const select = document.getElementById('output-folder-select');

    if (select.options.length <= 1) {
        select.innerHTML = '<option value="">Select folder...</option>';
        select.innerHTML += '<option value="all">All Output Files</option>';
        folders.forEach(folder => {
            if (folder.enabled) {
                const option = document.createElement('option');
                option.value = folder.name;
                option.textContent = folder.name + ' Output';
                select.appendChild(option);
            }
        });
    }
}

// Load output files
async function loadOutputFiles(folderName) {
    const container = document.getElementById('output-files-grid');
    container.innerHTML = '<div class="loading">Loading files...</div>';

    try {
        const res = await fetch(`/api/web/files/output/${encodeURIComponent(folderName)}`);
        const files = await res.json();

        if (!files || files.length === 0) {
            container.innerHTML = '<div class="placeholder">No files found</div>';
            return;
        }

        container.innerHTML = files.map(file => `
            <div class="file-card" data-file="${file.path}">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${formatFileSize(file.size)}</div>
            </div>
        `).join('');

        container.querySelectorAll('.file-card').forEach(card => {
            card.addEventListener('click', () => loadOutputFileContent(card.dataset.file));
        });
    } catch (error) {
        container.innerHTML = '<div class="error">Failed to load files</div>';
        console.error(error);
    }
}

// Load output file content
async function loadOutputFileContent(filePath) {
    const viewer = document.getElementById('output-file-content');
    const title = document.getElementById('output-file-title');
    const text = document.getElementById('output-file-text');

    title.textContent = filePath;
    text.innerHTML = '<div class="loading">Loading...</div>';
    viewer.classList.remove('hidden');

    try {
        const res = await fetch(`/api/web/file/content?path=${encodeURIComponent(filePath)}`);
        const data = await res.json();

        if (data.success) {
            text.innerHTML = marked.parse(data.content);
        } else {
            text.innerHTML = '<div class="error">Error: ' + (data.error || 'Unknown error') + '</div>';
        }
    } catch (error) {
        text.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
    }
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
"""

    js_path = os.path.join(assets_dir, "app.js")
    with open(js_path, "w") as f:
        f.write(js_content)
    logger.debug(f"Created {js_path}")
