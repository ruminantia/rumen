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
    # Generate timestamp for cache-busting
    version = int(datetime.now().timestamp())

    html_content = f"""<!DOCTYPE html>
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
                <button id="calendar-toggle" aria-label="Toggle calendar">📅</button>
                <button id="settings-toggle" aria-label="Settings">⚙️</button>
                <button id="theme-toggle" aria-label="Toggle theme">◐</button>
            </div>
        </header>

        <div id="calendar-overlay" class="calendar-overlay">
            <div class="calendar-container">
                <div class="calendar-header">
                    <button id="prev-month">&lt;</button>
                    <h2 id="current-month"></h2>
                    <button id="next-month">&gt;</button>
                </div>
                <div id="calendar"></div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <nav class="nav-tabs">
            <button class="nav-tab active" data-tab="dashboard">Dashboard</button>
            <button class="nav-tab" data-tab="prompts">Prompts</button>
            <button class="nav-tab" data-tab="routines">Routines</button>
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
                        <div class="status-label">Monitoring</div>
                        <div class="status-value">Loading...</div>
                    </div>
                    <div class="status-card">
                        <div class="status-label">Enabled Routines</div>
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

            <div class="date-filter-section" id="dashboard-date-filter">
                <span class="date-filter-label">Showing results for:</span>
                <span class="date-filter-value" id="dashboard-current-date">Today</span>
            </div>

            <div class="folders-section">
                <h2>Routines</h2>
                <div id="folders-grid" class="folders-grid">
                    <div class="loading">Loading routine configurations...</div>
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

        <!-- Prompts Tab -->
        <div id="prompts-tab" class="tab-content">
            <div class="prompts-section">
                <div class="prompts-header">
                    <h2>Prompts</h2>
                    <div class="prompts-controls">
                        <button id="refresh-prompts" class="btn-secondary">Refresh</button>
                    </div>
                </div>
                <div id="prompts-grid" class="prompts-grid">
                    <div class="loading">Loading prompts...</div>
                </div>
            </div>
        </div>

        <!-- Prompt Editor Overlay -->
        <div id="prompt-overlay" class="settings-overlay">
            <div class="settings-container">
                <div class="settings-header">
                    <h2 id="prompt-overlay-title">Edit Prompt</h2>
                    <button id="prompt-close" aria-label="Close prompt editor">✕</button>
                </div>
                <div class="settings-content">
                    <textarea id="prompt-content" class="config-editor" spellcheck="false">Loading...</textarea>
                    <div class="settings-actions">
                        <button id="save-prompt" class="save-button">Save Changes</button>
                        <span id="prompt-save-status" class="save-status"></span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Routines Tab -->
        <div id="routines-tab" class="tab-content">
            <div class="routines-header">
                <select id="routine-select">
                    <option value="">Select routine...</option>
                </select>
            </div>

            <div id="routine-details" class="routine-details hidden">
                <div class="routine-details-header">
                    <h3 id="routine-name">Routine Details</h3>
                    <span id="routine-status" class="routine-status"></span>
                </div>
                <div class="routine-details-grid">
                    <div class="detail-item">
                        <span class="detail-label">Input Directory</span>
                        <span class="detail-value" id="detail-input-directory">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Output Directory</span>
                        <span class="detail-value" id="detail-output-directory">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Provider</span>
                        <span class="detail-value" id="detail-provider">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Model</span>
                        <span class="detail-value" id="detail-model">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Temperature</span>
                        <span class="detail-value" id="detail-temperature">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Max Tokens</span>
                        <span class="detail-value" id="detail-max-tokens">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Output Format</span>
                        <span class="detail-value" id="detail-output-format">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Delete Input Files</span>
                        <span class="detail-value" id="detail-delete-input">-</span>
                    </div>
                    <div class="detail-item detail-item-full">
                        <span class="detail-label">
                            System Prompt
                            <span id="detail-system-prompt-source" class="detail-source"></span>
                        </span>
                        <pre class="detail-value detail-prompt" id="detail-system-prompt">-</pre>
                    </div>
                    <div class="detail-item detail-item-full">
                        <span class="detail-label">
                            User Prompt Template
                            <span id="detail-user-prompt-source" class="detail-source"></span>
                        </span>
                        <pre class="detail-value detail-prompt" id="detail-user-prompt">-</pre>
                    </div>
                </div>
            </div>

            <div id="routines-stats" class="routines-stats hidden">
                <div class="stat-card">
                    <div class="stat-label">Total Processed</div>
                    <div class="stat-value" id="stat-total">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Success</div>
                    <div class="stat-value stat-success" id="stat-success">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Pending</div>
                    <div class="stat-value stat-pending" id="stat-pending">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Success Rate</div>
                    <div class="stat-value" id="stat-rate">0%</div>
                </div>
            </div>

            <div class="routines-main-content">
                <aside class="routines-sidebar">
                    <div id="routines-file-list"></div>
                </aside>

                <main class="routines-viewer">
                    <div class="routines-viewer-header">
                        <div class="file-info" id="selected-file-info">
                            <span class="file-info-text">Select a file to view</span>
                        </div>
                        <div class="view-toggles">
                            <button class="toggle-btn" data-view="input" title="View input">Input</button>
                            <button class="toggle-btn active" data-view="output" title="View output">Output</button>
                            <button class="toggle-btn" data-view="side-by-side" title="View side by side">Side by Side</button>
                        </div>
                    </div>
                    <div id="routines-content">
                        <div class="welcome">
                            <h2>Select a routine</h2>
                            <p>Choose a routine from the dropdown to view input and output files.</p>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
    <script src="assets/app.js?v={version}"></script>
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
:root { --bg-primary: #fff; --bg-secondary: #f6f6f6; --bg-hover: #e8e8e8; --text-primary: #000; --text-secondary: #666; --border: #ccc; --accent: #f60; --success: #4caf50; --error: #f44336; --calendar-today: #ffffcc; --calendar-has-content: #e6f3ff; }
[data-theme="dark"] { --bg-primary: #1a1a1a; --bg-secondary: #2a2a2a; --bg-hover: #3a3a3a; --text-primary: #e0e0e0; --text-secondary: #a0a0a0; --border: #444; --calendar-today: #3a3a00; --calendar-has-content: #1a2a3a; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Verdana, Geneva, sans-serif; font-size: 14px; line-height: 1.6; background: var(--bg-primary); color: var(--text-primary); overflow-x: hidden; }
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

/* Calendar Overlay */
.calendar-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 1000; justify-content: center; align-items: center; }
.calendar-overlay.active { display: flex; }
.calendar-container { background: var(--bg-secondary); padding: 20px; border-radius: 8px; max-width: 500px; width: 90%; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); }
.calendar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.calendar-header button { background: var(--bg-primary); border: 1px solid var(--border); padding: 5px 15px; cursor: pointer; border-radius: 3px; font-size: 16px; transition: background 0.2s; }
.calendar-header button:hover { background: var(--bg-hover); }
.calendar-header h2 { font-size: 18px; margin: 0; }
#calendar { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; width: 100%; }
.calendar-day { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 3px; cursor: pointer; transition: background 0.2s; font-size: 12px; min-height: 40px; }
.calendar-day.header { font-weight: bold; cursor: default; background: var(--bg-secondary); }
.calendar-day.empty { cursor: default; opacity: 0.3; }
.calendar-day.today { background: var(--calendar-today); font-weight: bold; }
.calendar-day.has-content { background: var(--calendar-has-content); font-weight: bold; }
.calendar-day.selected { background: var(--accent); color: white; }
.calendar-day:not(.header):not(.empty):hover { background: var(--bg-hover); }

.nav-tabs { display: flex; gap: 5px; margin-bottom: 20px; border-bottom: 1px solid var(--border); }
.nav-tab { background: var(--bg-secondary); border: 1px solid var(--border); padding: 10px 20px; cursor: pointer; }
.nav-tab.active { background: var(--bg-primary); font-weight: bold; }
.tab-content { display: none; }
.tab-content.active { display: block; }
.status-section, .folders-section, .config-section, .browser-section { background: var(--bg-secondary); padding: 20px; border-radius: 4px; margin-bottom: 20px; }
.logs-section { margin-top: 30px; background: var(--bg-secondary); padding: 20px; border-radius: 4px; }
.date-filter-section { background: var(--accent); color: white; padding: 12px 20px; border-radius: 4px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.date-filter-label { font-size: 13px; font-weight: 600; }
.date-filter-value { font-size: 14px; font-weight: bold; }
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

/* Prompts tab styles */
.prompts-section { background: var(--bg-secondary); padding: 20px; border-radius: 4px; margin-bottom: 20px; }
.prompts-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.prompts-header h2 { font-size: 18px; margin: 0; }
.prompts-controls { display: flex; gap: 10px; }
.prompts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
.prompt-card { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 4px; padding: 15px; cursor: pointer; transition: background 0.2s; }
.prompt-card:hover { background: var(--bg-hover); }
.prompt-name { font-weight: bold; font-size: 16px; margin-bottom: 8px; color: var(--text-primary); }
.prompt-path { font-size: 12px; color: var(--text-secondary); margin-bottom: 10px; }
.prompt-preview { font-size: 13px; color: var(--text-secondary); line-height: 1.4; max-height: 100px; overflow: hidden; text-overflow: ellipsis; white-space: pre-wrap; }

/* Routines tab styles */
.routines-header { margin-bottom: 20px; display: flex; gap: 10px; align-items: center; }
.routines-header select { padding: 8px 12px; border-radius: 4px; background: var(--bg-primary); border: 1px solid var(--border); font-size: 14px; }

.routines-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }
.routines-stats.hidden { display: none; }
.routines-stats .stat-card { background: var(--bg-secondary); padding: 15px; border-radius: 4px; border: 1px solid var(--border); text-align: center; }
.routines-stats .stat-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px; }
.routines-stats .stat-value { font-size: 28px; font-weight: bold; color: var(--accent); }
.routines-stats .stat-success { color: var(--success); }
.routines-stats .stat-pending { color: #ff9800; }

/* Routine details section */
.routine-details { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 4px; padding: 20px; margin-bottom: 20px; }
.routine-details.hidden { display: none; }
.routine-details-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
.routine-details-header h3 { margin: 0; font-size: 16px; color: var(--text-primary); }
.routine-status { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }
.routine-status.enabled { background: var(--success); color: white; }
.routine-status.disabled { background: var(--error); color: white; }

.routine-details-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.detail-item { display: flex; flex-direction: column; gap: 4px; }
.detail-item-full { grid-column: 1 / -1; }
.detail-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.detail-source { font-size: 10px; padding: 2px 6px; border-radius: 3px; background: var(--accent); color: white; text-transform: none; font-weight: normal; }
.detail-value { font-size: 13px; color: var(--text-primary); word-break: break-word; }
.detail-prompt { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 3px; padding: 10px; margin: 0; white-space: pre-wrap; word-break: break-word; font-size: 12px; max-height: 150px; overflow-y: auto; }

.routines-main-content { display: grid; grid-template-columns: 350px 1fr; gap: 20px; min-height: 600px; overflow: hidden; }
.routines-sidebar { background: var(--bg-secondary); border-radius: 4px; padding: 15px; overflow-y: auto; max-height: 800px; min-width: 0; }
.routines-viewer { background: var(--bg-secondary); border-radius: 4px; display: flex; flex-direction: column; max-height: 800px; min-width: 0; overflow: hidden; }

.routines-viewer-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; border-bottom: 1px solid var(--border); }
.file-info { flex: 1; }
.file-info-text { font-size: 13px; color: var(--text-secondary); }
.view-toggles { display: flex; gap: 5px; }
.toggle-btn { background: var(--bg-primary); border: 1px solid var(--border); padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; transition: background 0.2s; }
.toggle-btn:hover { background: var(--bg-hover); }
.toggle-btn.active { background: var(--accent); color: white; border-color: var(--accent); }

#routines-content { flex: 1; overflow-y: auto; overflow-x: hidden; padding: 20px; min-width: 0; }

.routines-file-item { padding: 12px; margin-bottom: 10px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 3px; cursor: pointer; transition: background 0.2s; overflow: hidden; }
.routines-file-item:hover { background: var(--bg-hover); }
.routines-file-item.selected { border-color: var(--accent); border-width: 2px; }
.routines-file-hash { font-size: 11px; color: var(--text-secondary); margin-bottom: 5px; font-family: monospace; }
.routines-file-meta { font-size: 12px; color: var(--text-primary); }
.routines-file-badge { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 10px; text-transform: uppercase; margin-left: 5px; }
.routines-file-badge.has-input { background: #e3f2fd; color: #1976d2; }
.routines-file-badge.has-output { background: #e8f5e9; color: #388e3c; }
[data-theme="dark"] .routines-file-badge.has-input { background: #1a2a3a; color: #64b5f6; }
[data-theme="dark"] .routines-file-badge.has-output { background: #1a2a1a; color: #81c784; }

#routines-content .welcome { text-align: center; padding: 100px 20px; color: var(--text-secondary); }
#routines-content h1 { font-size: 28px; margin-bottom: 20px; color: var(--text-primary); }
#routines-content h2 { font-size: 22px; margin-top: 25px; margin-bottom: 15px; color: var(--text-primary); }
#routines-content h3 { font-size: 18px; margin-top: 20px; margin-bottom: 10px; color: var(--text-primary); }
#routines-content p { margin-bottom: 15px; line-height: 1.7; }
#routines-content ul, #routines-content ol { margin-bottom: 15px; margin-left: 25px; }
#routines-content li { margin-bottom: 8px; line-height: 1.6; }
#routines-content pre { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 3px; padding: 15px; overflow-x: auto; margin-bottom: 15px; max-width: 100%; }
#routines-content code { background: var(--bg-primary); padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 13px; }
#routines-content pre code { background: none; padding: 0; }
#routines-content table { border-collapse: collapse; width: 100%; margin-bottom: 15px; overflow-x: auto; display: block; }
#routines-content th, #routines-content td { border: 1px solid var(--border); padding: 8px; text-align: left; }
#routines-content th { background: var(--bg-secondary); }
#routines-content a { color: var(--accent); text-decoration: none; }
#routines-content a:hover { text-decoration: underline; }
#routines-content blockquote { border-left: 3px solid var(--accent); padding-left: 15px; margin: 15px 0; color: var(--text-secondary); font-style: italic; }

/* Side by side view */
.side-by-side-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 100%; min-width: 0; }
.side-by-side-panel { overflow-y: auto; overflow-x: hidden; padding: 15px; background: var(--bg-primary); border-radius: 4px; border: 1px solid var(--border); min-width: 0; }
.side-by-side-panel h3 { font-size: 16px; margin-bottom: 15px; color: var(--accent); padding-bottom: 10px; border-bottom: 1px solid var(--border); }

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
const state = {
    currentTab: 'dashboard',
    currentMonth: new Date(),
    currentDate: null,  // Will be set to today's date during initialization
    datesWithContent: new Set()
};

document.addEventListener('DOMContentLoaded', async () => {
    // Set current date to today by default
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    state.currentDate = `${year}/${month}/${day}`;

    setupTabs();
    setupEventListeners();
    initializeTheme();
    await loadDatesWithContent();

    // Mark today as selected in calendar
    renderCalendar();

    // Load dashboard with today's date
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
    else if (name === 'prompts') loadPrompts();
    else if (name === 'routines') loadRoutineSelect();
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

    // Calendar overlay toggle
    const calendarOverlay = document.getElementById('calendar-overlay');
    const calendarToggle = document.getElementById('calendar-toggle');

    calendarToggle.addEventListener('click', () => {
        calendarOverlay.classList.toggle('active');
        renderCalendar();
    });

    // Close calendar when clicking outside
    calendarOverlay.addEventListener('click', (e) => {
        if (e.target === calendarOverlay) {
            calendarOverlay.classList.remove('active');
        }
    });

    // Month navigation
    document.getElementById('prev-month').addEventListener('click', () => {
        state.currentMonth.setMonth(state.currentMonth.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById('next-month').addEventListener('click', () => {
        state.currentMonth.setMonth(state.currentMonth.getMonth() + 1);
        renderCalendar();
    });

    // Close calendar when a date is selected
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('calendar-day') && e.target.classList.contains('has-content')) {
            calendarOverlay.classList.remove('active');
        }
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

    // Prompts controls
    document.getElementById('refresh-prompts').addEventListener('click', loadPrompts);
    document.getElementById('save-prompt').addEventListener('click', savePrompt);

    // Prompt overlay controls
    const promptOverlay = document.getElementById('prompt-overlay');
    const promptClose = document.getElementById('prompt-close');

    promptClose.addEventListener('click', () => {
        promptOverlay.classList.remove('active');
    });

    // Close overlay when clicking outside
    promptOverlay.addEventListener('click', (e) => {
        if (e.target === promptOverlay) {
            promptOverlay.classList.remove('active');
        }
    });

    // Routines controls
    document.getElementById('routine-select').addEventListener('change', (e) => {
        if (e.target.value) loadRoutineFiles(e.target.value);
    });

    // View toggle buttons (moved to viewer area)
    document.querySelectorAll('.routines-viewer-header .toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const routine = document.getElementById('routine-select').value;
            if (!routine || !currentFilePair) return;

            // Update button states
            document.querySelectorAll('.routines-viewer-header .toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Re-render with new view mode
            currentViewMode = btn.dataset.view;
            renderRoutineViewer();
        });
    });
}

async function loadDashboard() {
    // Build date filter parameter if a date is selected
    const dateParam = state.currentDate ? `?date=${encodeURIComponent(state.currentDate)}` : '';

    // Fetch basic status (doesn't need date filter)
    const statusRes = await fetch('/api/web/status');
    const status = await statusRes.json();

    // Fetch folders list (doesn't need date filter)
    const foldersRes = await fetch('/api/web/folders');
    const foldersList = await foldersRes.json();

    // Fetch detailed info for each folder with date filter
    const folderDetailsPromises = foldersList.map(f =>
        fetch(`/api/web/folders/${encodeURIComponent(f.name)}${dateParam}`)
    );
    const folderDetailsResponses = await Promise.all(folderDetailsPromises);
    const folderDetails = await Promise.all(folderDetailsResponses.map(r => r.json()));

    // Filter out failed requests and sum up totals
    const validFolderDetails = folderDetails.filter(d => d.success);
    const totalInputFiles = validFolderDetails.reduce((sum, f) => sum + (f.input_files || 0), 0);
    const totalOutputFiles = validFolderDetails.reduce((sum, f) => sum + (f.output_files || 0), 0);
    const enabledFolders = validFolderDetails.filter(f => f.enabled).length;

    // Update date filter display
    const dateDisplay = document.getElementById('dashboard-current-date');
    if (state.currentDate) {
        // Format date for display
        const dateParts = state.currentDate.split('/');
        const year = dateParts[0];
        const month = dateParts[1];
        const day = dateParts[2];
        const dateObj = new Date(year, month - 1, day);
        dateDisplay.textContent = dateObj.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } else {
        dateDisplay.textContent = 'All dates';
    }

    // Update status display
    document.querySelector('#file-monitor-status .status-value').textContent = status.file_monitor_running ? 'Running' : 'Stopped';
    document.querySelector('#file-monitor-status .status-value').className = 'status-value ' + (status.file_monitor_running ? 'running' : 'stopped');
    document.getElementById('enabled-folders-count').textContent = enabledFolders;
    document.getElementById('total-input-files').textContent = totalInputFiles;
    document.getElementById('total-output-files').textContent = totalOutputFiles;

    // Update folders grid
    const grid = document.getElementById('folders-grid');
    grid.innerHTML = validFolderDetails.map(f => `
        <div class="folder-card">
            <div class="folder-header">
                <div class="folder-name">${f.name}</div>
                <div class="folder-status ${f.enabled ? 'enabled' : 'disabled'}">${f.enabled ? 'Enabled' : 'Disabled'}</div>
            </div>
            <div class="folder-info">
                <div>Path: ${f.input_directory}</div>
                <div>Provider: ${f.provider}</div>
                <div>Model: ${f.model}</div>
                <div>Input files: ${f.input_files || 0}</div>
                <div>Output files: ${f.output_files || 0}</div>
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

// Routines management
let currentRoutine = null;
let currentViewMode = 'output';
let currentFilePair = null;
let routineFilePairs = []; // Array of {hash, inputFile, outputFile}

// Populate routine dropdown
async function loadRoutineSelect() {
    const select = document.getElementById('routine-select');
    const res = await fetch('/api/web/folders');
    const folders = await res.json();

    select.innerHTML = '<option value="">Select routine...</option>';
    folders.forEach(folder => {
        if (folder.enabled) {
            const option = document.createElement('option');
            option.value = folder.name;
            option.textContent = folder.name;
            select.appendChild(option);
        }
    });
}

// Extract hash from filename
function extractHash(filename) {
    // For input files: just the hash (e.g., "2e826333cb87f475f708d9cec64eea097b7d294581522b2777797d34c6cf7855.md")
    // For output files: format is {folder}_{hash}_{timestamp}_{uuid}.md
    // Extract the 64-char hash
    const hashMatch = filename.match(/([a-f0-9]{64})/);
    return hashMatch ? hashMatch[1] : null;
}

// Load routine details
async function loadRoutineDetails(routineName) {
    try {
        const res = await fetch(`/api/web/folders/${encodeURIComponent(routineName)}`);
        const data = await res.json();

        if (data.success) {
            // Update routine details section
            document.getElementById('routine-name').textContent = data.name;

            const statusEl = document.getElementById('routine-status');
            statusEl.textContent = data.enabled ? 'ENABLED' : 'DISABLED';
            statusEl.className = `routine-status ${data.enabled ? 'enabled' : 'disabled'}`;

            document.getElementById('detail-input-directory').textContent = data.input_directory;
            document.getElementById('detail-output-directory').textContent = data.output_directory;
            document.getElementById('detail-provider').textContent = data.provider;
            document.getElementById('detail-model').textContent = data.model;
            document.getElementById('detail-temperature').textContent = data.temperature;
            document.getElementById('detail-max-tokens').textContent = data.max_tokens;
            document.getElementById('detail-output-format').textContent = data.output_format;
            document.getElementById('detail-delete-input').textContent = data.delete_input_files ? 'Yes' : 'No';
            document.getElementById('detail-system-prompt').textContent = data.system_prompt;
            document.getElementById('detail-user-prompt').textContent = data.user_prompt_template;

            // Show prompt source indicators
            const systemPromptSource = document.getElementById('detail-system-prompt-source');
            const userPromptSource = document.getElementById('detail-user-prompt-source');

            if (data.prompt_source_info && data.prompt_source_info.system_prompt_file) {
                systemPromptSource.textContent = '📄 File';
                systemPromptSource.title = data.prompt_source_info.system_prompt_file;
            } else {
                systemPromptSource.textContent = '';
            }

            if (data.prompt_source_info && data.prompt_source_info.user_prompt_file) {
                userPromptSource.textContent = '📄 File';
                userPromptSource.title = data.prompt_source_info.user_prompt_file;
            } else {
                userPromptSource.textContent = '';
            }

            // Show the routine details section
            document.getElementById('routine-details').classList.remove('hidden');
        } else {
            console.error('Failed to load routine details:', data.error);
            document.getElementById('routine-details').classList.add('hidden');
        }
    } catch (error) {
        console.error('Error loading routine details:', error);
        document.getElementById('routine-details').classList.add('hidden');
    }
}

// Load files for selected routine
async function loadRoutineFiles(routineName) {
    currentRoutine = routineName;
    currentFilePair = null;

    const viewer = document.getElementById('routines-content');
    const fileInfo = document.getElementById('selected-file-info');
    fileInfo.innerHTML = '<span class="file-info-text">Select a file to view</span>';
    viewer.innerHTML = '<div class="loading">Loading files...</div>';

    // Load routine details
    await loadRoutineDetails(routineName);

    try {
        // Build URL with date filter if selected
        const dateParam = state.currentDate ? `?date=${encodeURIComponent(state.currentDate)}` : '';

        const [inputRes, outputRes] = await Promise.all([
            fetch(`/api/web/files/input/${encodeURIComponent(routineName)}${dateParam}`),
            fetch(`/api/web/files/output/${encodeURIComponent(routineName)}${dateParam}`)
        ]);

        const inputFiles = await inputRes.json();
        const outputFiles = await outputRes.json();

        // Group files by hash
        routineFilePairs = groupFilesByHash(inputFiles, outputFiles);

        // Update stats
        updateRoutineStats();

        renderRoutineFileList();

        // Show welcome message with date info
        const dateInfo = state.currentDate ? `<p>Showing results for <strong>${state.currentDate}</strong></p>` : '';
        viewer.innerHTML = `
            <div class="welcome">
                <h2>Select a file</h2>
                <p>Choose a file from the sidebar to view its contents.</p>
                ${dateInfo}
                <p><strong>Found ${routineFilePairs.length} file pairs</strong></p>
            </div>
        `;
    } catch (error) {
        viewer.innerHTML = '<div class="error">Failed to load files</div>';
        console.error(error);
    }
}

// Update stats display
function updateRoutineStats() {
    const statsContainer = document.getElementById('routines-stats');
    const total = routineFilePairs.length;
    const success = routineFilePairs.filter(p => p.outputFile).length;
    const pending = routineFilePairs.filter(p => p.inputFile && !p.outputFile).length;
    const rate = total > 0 ? ((success / total) * 100).toFixed(1) : 0;

    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-success').textContent = success;
    document.getElementById('stat-pending').textContent = pending;
    document.getElementById('stat-rate').textContent = rate + '%';

    statsContainer.classList.remove('hidden');
}

// Group input and output files by their hash
function groupFilesByHash(inputFiles, outputFiles) {
    const pairs = {};

    // Process input files
    inputFiles.forEach(file => {
        const hash = extractHash(file.name);
        if (hash) {
            if (!pairs[hash]) {
                pairs[hash] = { hash: hash, inputFile: null, outputFile: null };
            }
            pairs[hash].inputFile = file;
        }
    });

    // Process output files
    outputFiles.forEach(file => {
        const hash = extractHash(file.name);
        if (hash) {
            // Create pair if it doesn't exist (for output-only files like from chew)
            if (!pairs[hash]) {
                pairs[hash] = { hash: hash, inputFile: null, outputFile: null };
            }
            pairs[hash].outputFile = file;
        }
    });

    return Object.values(pairs);
}

// Render file list in sidebar (grouped by hash)
function renderRoutineFileList() {
    const container = document.getElementById('routines-file-list');
    container.innerHTML = '';

    if (routineFilePairs.length === 0) {
        container.innerHTML = '<div class="placeholder">No files found</div>';
        return;
    }

    // Sort by hash (most recent first based on input file modification time)
    const sorted = [...routineFilePairs].sort((a, b) => {
        const aTime = a.inputFile?.modified || 0;
        const bTime = b.inputFile?.modified || 0;
        return bTime - aTime;
    });

    sorted.forEach(pair => {
        const item = document.createElement('div');
        item.className = 'routines-file-item';
        item.dataset.hash = pair.hash;

        // Build badges
        let badges = '';
        if (pair.inputFile) badges += '<span class="routines-file-badge has-input">Input</span>';
        if (pair.outputFile) badges += '<span class="routines-file-badge has-output">Output</span>';

        // Display truncated hash
        const shortHash = pair.hash.substring(0, 16) + '...';

        item.innerHTML = `
            <div class="routines-file-hash">${shortHash}</div>
            <div class="routines-file-meta">
                ${badges}
            </div>
        `;

        item.addEventListener('click', () => selectRoutineFilePair(pair));
        container.appendChild(item);
    });
}

// Select a file pair from the sidebar
function selectRoutineFilePair(pair) {
    currentFilePair = pair;

    // Update selection in sidebar
    document.querySelectorAll('.routines-file-item').forEach(item => {
        item.classList.remove('selected');
        if (item.dataset.hash === pair.hash) {
            item.classList.add('selected');
        }
    });

    // Update file info display
    const fileInfo = document.getElementById('selected-file-info');
    const shortHash = pair.hash.substring(0, 16) + '...';
    fileInfo.innerHTML = `
        <span class="file-info-text">
            <strong>Hash:</strong> ${shortHash}<br>
            ${pair.inputFile ? '✓ Has Input' : '✗ No Input'} | ${pair.outputFile ? '✓ Has Output' : '✗ No Output'}
        </span>
    `;

    renderRoutineViewer();
}

// Render the main viewer area
async function renderRoutineViewer() {
    const viewer = document.getElementById('routines-content');

    if (!currentFilePair) {
        viewer.innerHTML = `
            <div class="welcome">
                <h2>Select a file</h2>
                <p>Choose a file from the sidebar to view its contents.</p>
            </div>
        `;
        return;
    }

    const { hash, inputFile, outputFile } = currentFilePair;
    const shortHash = hash.substring(0, 16) + '...';

    viewer.innerHTML = '<div class="loading">Loading...</div>';

    if (currentViewMode === 'side-by-side') {
        // Side by side view
        if (inputFile && outputFile) {
            const [inputRes, outputRes] = await Promise.all([
                fetch(`/api/web/file/content?path=${encodeURIComponent(inputFile.path)}`),
                fetch(`/api/web/file/content?path=${encodeURIComponent(outputFile.path)}`)
            ]);

            const inputData = await inputRes.json();
            const outputData = await outputRes.json();

            viewer.innerHTML = `
                <div class="side-by-side-container">
                    <div class="side-by-side-panel">
                        <h3>Input</h3>
                        ${inputData.success ? marked.parse(inputData.content) : '<div class="error">Failed to load</div>'}
                    </div>
                    <div class="side-by-side-panel">
                        <h3>Output</h3>
                        ${outputData.success ? marked.parse(outputData.content) : '<div class="error">Failed to load</div>'}
                    </div>
                </div>
            `;
        } else {
            // Missing one of the files
            const availableFile = inputFile || outputFile;
            const res = await fetch(`/api/web/file/content?path=${encodeURIComponent(availableFile.path)}`);
            const data = await res.json();
            viewer.innerHTML = `
                <p style="margin-bottom: 15px; color: var(--text-secondary);">
                    ${!inputFile ? '⚠️ Input file not available' : ''}
                    ${!outputFile ? '⚠️ Output file not available' : ''}
                </p>
                ${data.success ? marked.parse(data.content) : '<div class="error">Failed to load</div>'}
            `;
        }
    } else if (currentViewMode === 'input') {
        // Input view
        if (!inputFile) {
            viewer.innerHTML = '<div class="error">No input file available for this hash</div>';
            return;
        }
        const res = await fetch(`/api/web/file/content?path=${encodeURIComponent(inputFile.path)}`);
        const data = await res.json();
        viewer.innerHTML = data.success ? marked.parse(data.content) : '<div class="error">Failed to load</div>';
    } else {
        // Output view (default)
        if (!outputFile) {
            viewer.innerHTML = '<div class="error">No output file available for this hash</div>';
            return;
        }
        const res = await fetch(`/api/web/file/content?path=${encodeURIComponent(outputFile.path)}`);
        const data = await res.json();
        viewer.innerHTML = data.success ? marked.parse(data.content) : '<div class="error">Failed to load</div>';
    }
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Calendar functions
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}/${month}/${day}`;
}

async function loadDatesWithContent() {
    try {
        const res = await fetch('/api/web/dates');
        const data = await res.json();
        if (data.success && data.dates) {
            state.datesWithContent = new Set(data.dates);
        }
    } catch (error) {
        console.error('Failed to load dates:', error);
    }
}

function renderCalendar() {
    const calendar = document.getElementById('calendar');
    const monthHeader = document.getElementById('current-month');

    const year = state.currentMonth.getFullYear();
    const month = state.currentMonth.getMonth();

    monthHeader.textContent = state.currentMonth.toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric'
    });

    calendar.innerHTML = '';

    // Day headers
    ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-day header';
        header.textContent = day;
        calendar.appendChild(header);
    });

    // Get first day of month and days in month
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
        const empty = document.createElement('div');
        empty.className = 'calendar-day empty';
        calendar.appendChild(empty);
    }

    // Days of month
    const today = new Date();
    const todayStr = formatDate(today);

    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const dateStr = formatDate(date);

        const dayCell = document.createElement('div');
        dayCell.className = 'calendar-day';
        dayCell.textContent = day;
        dayCell.dataset.date = dateStr;

        if (dateStr === todayStr) {
            dayCell.classList.add('today');
        }

        if (state.datesWithContent.has(dateStr)) {
            dayCell.classList.add('has-content');
            dayCell.addEventListener('click', () => selectDate(dateStr));
        } else {
            dayCell.classList.add('empty');
        }

        if (dateStr === state.currentDate) {
            dayCell.classList.add('selected');
        }

        calendar.appendChild(dayCell);
    }
}

async function selectDate(date) {
    state.currentDate = date;

    // Update calendar
    document.querySelectorAll('.calendar-day').forEach(cell => {
        cell.classList.remove('selected');
        if (cell.dataset.date === date) {
            cell.classList.add('selected');
        }
    });

    // Reload data with date filter
    if (state.currentTab === 'dashboard') {
        await loadDashboard();
    } else if (state.currentTab === 'routines') {
        const routine = document.getElementById('routine-select').value;
        if (routine) {
            await loadRoutineFiles(routine);
        }
    }
}

// Prompts management
let currentPromptPath = null;

async function loadPrompts() {
    const container = document.getElementById('prompts-grid');
    container.innerHTML = '<div class="loading">Loading prompts...</div>';

    try {
        const res = await fetch('/api/web/prompts');
        const data = await res.json();

        if (!data.success || !data.prompts || data.prompts.length === 0) {
            container.innerHTML = '<div class="placeholder">No prompts found</div>';
            return;
        }

        container.innerHTML = data.prompts.map(prompt => `
            <div class="prompt-card" data-path="${prompt.path}">
                <div class="prompt-name">${prompt.name}</div>
                <div class="prompt-path">${prompt.path}</div>
                <div class="prompt-preview">${escapeHtml(prompt.preview || '')}</div>
            </div>
        `).join('');

        container.querySelectorAll('.prompt-card').forEach(card => {
            card.addEventListener('click', () => editPrompt(card.dataset.path));
        });
    } catch (error) {
        container.innerHTML = '<div class="error">Failed to load prompts</div>';
        console.error(error);
    }
}

async function editPrompt(promptPath) {
    const overlay = document.getElementById('prompt-overlay');
    const title = document.getElementById('prompt-overlay-title');
    const content = document.getElementById('prompt-content');

    title.textContent = `Edit: ${promptPath}`;
    content.value = 'Loading...';
    overlay.classList.add('active');
    currentPromptPath = promptPath;

    try {
        const res = await fetch(`/api/web/prompt?path=${encodeURIComponent(promptPath)}`);
        const data = await res.json();

        if (data.success) {
            content.value = data.content;
        } else {
            content.value = 'Error loading prompt: ' + (data.error || 'Unknown error');
        }
    } catch (error) {
        content.value = 'Error loading prompt: ' + error.message;
    }
}

async function savePrompt() {
    if (!currentPromptPath) {
        alert('No prompt selected');
        return;
    }

    const content = document.getElementById('prompt-content').value;
    const saveButton = document.getElementById('save-prompt');
    const saveStatus = document.getElementById('prompt-save-status');

    saveButton.disabled = true;
    saveButton.textContent = 'Saving...';
    saveStatus.textContent = '';
    saveStatus.className = 'save-status';

    try {
        const res = await fetch('/api/web/prompt', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: currentPromptPath, content})
        });
        const data = await res.json();

        if (data.success) {
            saveStatus.textContent = '✓ Prompt saved! Reloading application...';
            saveStatus.className = 'save-status success';
            setTimeout(() => {
                // Close the overlay
                document.getElementById('prompt-overlay').classList.remove('active');
                // Reload prompts
                loadPrompts();
                // Reload dashboard to pick up changes
                loadDashboard();
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
"""

    js_path = os.path.join(assets_dir, "app.js")
    with open(js_path, "w") as f:
        f.write(js_content)
    logger.debug(f"Created {js_path}")
