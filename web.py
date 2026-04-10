#!/usr/bin/env python3
"""ThinkingPipe Web UI - 브라우저에서 사물쇼츠 파이프라인 실행"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from flask import Flask, render_template_string, request, jsonify
from pipeline.idea import generate_idea
from pipeline.script import generate_script
from pipeline.hook import optimize_hook

app = Flask(__name__)

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ThinkingPipe - 사물쇼츠 AI 파이프라인</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --border: #2a2a3a;
    --text: #e8e8f0;
    --text-dim: #8888a0;
    --accent: #6366f1;
    --accent-glow: rgba(99, 102, 241, 0.3);
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
    --cyan: #06b6d4;
  }

  body {
    font-family: 'Noto Sans KR', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Hero Header */
  .hero {
    text-align: center;
    padding: 60px 20px 40px;
    position: relative;
  }
  .hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 600px;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
    opacity: 0.4;
    pointer-events: none;
  }
  .hero h1 {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #818cf8, #6366f1, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
  }
  .hero p {
    color: var(--text-dim);
    font-size: 1.1rem;
    font-weight: 300;
  }

  /* Pipeline Steps Indicator */
  .pipeline-steps {
    display: flex;
    justify-content: center;
    gap: 8px;
    padding: 30px 20px;
    flex-wrap: wrap;
  }
  .step-dot {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-dim);
    transition: all 0.4s ease;
  }
  .step-dot.active {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
    box-shadow: 0 0 20px var(--accent-glow);
  }
  .step-dot.done {
    background: rgba(34, 197, 94, 0.15);
    border-color: var(--green);
    color: var(--green);
  }
  .step-arrow {
    color: var(--border);
    font-size: 0.7rem;
  }

  /* Main Container */
  .container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 20px 80px;
  }

  /* Input Card */
  .input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 30px;
  }
  .input-card label {
    display: block;
    font-weight: 500;
    margin-bottom: 10px;
    font-size: 0.95rem;
  }
  .input-row {
    display: flex;
    gap: 12px;
  }
  .input-row input {
    flex: 1;
    padding: 14px 18px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-size: 1.1rem;
    font-family: inherit;
    outline: none;
    transition: border 0.2s;
  }
  .input-row input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-glow);
  }
  .input-row input::placeholder { color: var(--text-dim); }

  .btn {
    padding: 14px 28px;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn-primary {
    background: var(--accent);
    color: white;
  }
  .btn-primary:hover { filter: brightness(1.15); transform: translateY(-1px); }
  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  .btn-outline {
    background: transparent;
    color: var(--accent);
    border: 1px solid var(--accent);
  }
  .btn-outline:hover { background: rgba(99,102,241,0.1); }

  .mode-toggle {
    display: flex;
    gap: 8px;
    margin-top: 14px;
  }
  .mode-toggle label {
    font-size: 0.85rem;
    color: var(--text-dim);
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
  }
  .mode-toggle input[type="checkbox"] {
    accent-color: var(--accent);
  }

  /* Result Cards */
  .result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    margin-bottom: 20px;
    overflow: hidden;
    animation: slideUp 0.4s ease;
  }
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .result-header {
    padding: 18px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    background: var(--surface2);
  }
  .result-header h3 {
    font-size: 1rem;
    font-weight: 700;
  }
  .result-header .badge {
    font-size: 0.75rem;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 500;
  }
  .badge-live { background: rgba(34,197,94,0.15); color: var(--green); }
  .badge-dry { background: rgba(234,179,8,0.15); color: var(--yellow); }
  .badge-loading {
    background: rgba(99,102,241,0.15);
    color: var(--accent);
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .result-body { padding: 24px; }

  /* Thinking OS Stage Display */
  .stage-grid {
    display: grid;
    gap: 12px;
  }
  .stage-item {
    display: flex;
    gap: 14px;
    padding: 14px;
    background: var(--bg);
    border-radius: 10px;
    border-left: 3px solid var(--border);
  }
  .stage-item:nth-child(1) { border-left-color: #818cf8; }
  .stage-item:nth-child(2) { border-left-color: #6366f1; }
  .stage-item:nth-child(3) { border-left-color: #4f46e5; }
  .stage-item:nth-child(4) { border-left-color: var(--red); }
  .stage-item:nth-child(5) { border-left-color: var(--green); }
  .stage-num {
    font-size: 1.5rem;
    font-weight: 900;
    color: var(--text-dim);
    min-width: 30px;
  }
  .stage-content { flex: 1; }
  .stage-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-dim);
    letter-spacing: 0.05em;
    margin-bottom: 4px;
  }
  .stage-text { font-size: 0.95rem; line-height: 1.5; }

  /* Script Sections */
  .script-section {
    padding: 16px;
    background: var(--bg);
    border-radius: 10px;
    margin-bottom: 10px;
  }
  .script-time {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--cyan);
    background: rgba(6,182,212,0.1);
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
  }
  .script-label {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-dim);
    margin-left: 8px;
  }
  .script-text {
    font-size: 1.05rem;
    line-height: 1.7;
    margin-top: 6px;
  }

  /* Hook Alternatives */
  .hook-alt {
    padding: 14px;
    background: var(--bg);
    border-radius: 10px;
    margin-bottom: 10px;
    border: 1px solid transparent;
    transition: border 0.2s;
  }
  .hook-alt.recommended {
    border-color: var(--green);
    background: rgba(34,197,94,0.05);
  }
  .hook-alt .hook-text {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 4px;
  }
  .hook-alt .hook-strategy {
    font-size: 0.85rem;
    color: var(--text-dim);
  }
  .rec-badge {
    display: inline-block;
    font-size: 0.7rem;
    background: var(--green);
    color: black;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 700;
    margin-left: 8px;
  }

  /* Meta info */
  .meta-row {
    display: flex;
    gap: 20px;
    padding: 12px 0;
    border-top: 1px solid var(--border);
    margin-top: 16px;
    font-size: 0.85rem;
    color: var(--text-dim);
  }
  .meta-row span { display: flex; align-items: center; gap: 4px; }

  /* Full Script Display */
  .full-script {
    padding: 20px;
    background: var(--bg);
    border-radius: 10px;
    font-size: 1.05rem;
    line-height: 1.8;
    white-space: pre-wrap;
    border: 1px solid var(--border);
  }

  /* Loading spinner */
  .spinner {
    display: inline-block;
    width: 18px; height: 18px;
    border: 2px solid var(--border);
    border-top: 2px solid var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Responsive */
  @media (max-width: 600px) {
    .hero h1 { font-size: 2rem; }
    .input-row { flex-direction: column; }
    .pipeline-steps { gap: 4px; }
    .step-arrow { display: none; }
  }
</style>
</head>
<body>

<div class="hero">
  <h1>ThinkingPipe</h1>
  <p>Thinking OS 5 Steps applied to 60-second Object Monologue Shorts</p>
</div>

<div class="pipeline-steps" id="steps">
  <div class="step-dot" data-step="0">1. Idea Frame</div>
  <span class="step-arrow">&rarr;</span>
  <div class="step-dot" data-step="1">2. 60s Script</div>
  <span class="step-arrow">&rarr;</span>
  <div class="step-dot" data-step="2">3. Hook Optimize</div>
  <span class="step-arrow">&rarr;</span>
  <div class="step-dot" data-step="3">4. Complete</div>
</div>

<div class="container">
  <div class="input-card">
    <label>What object should speak today?</label>
    <div class="input-row">
      <input type="text" id="topic" placeholder="pencil, umbrella, eraser, cup..." value="pencil" autofocus />
      <button class="btn btn-primary" id="runBtn" onclick="runPipeline()">Run Pipeline</button>
    </div>
    <div class="mode-toggle">
      <label><input type="checkbox" id="dryRun" checked /> Dry-Run (no API calls)</label>
    </div>
  </div>

  <div id="results"></div>
</div>

<script>
const stepsEl = document.querySelectorAll('.step-dot');
const resultsEl = document.getElementById('results');

function setStep(idx) {
  stepsEl.forEach((el, i) => {
    el.classList.remove('active', 'done');
    if (i < idx) el.classList.add('done');
    if (i === idx) el.classList.add('active');
  });
}

function addCard(title, badge, badgeClass, bodyHTML) {
  const card = document.createElement('div');
  card.className = 'result-card';
  card.innerHTML = `
    <div class="result-header">
      <h3>${title}</h3>
      <span class="badge ${badgeClass}">${badge}</span>
    </div>
    <div class="result-body">${bodyHTML}</div>
  `;
  resultsEl.appendChild(card);
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  return card;
}

function renderIdea(data) {
  const stages = [
    { num: '1', label: 'Phenomenon', text: data.stage1_phenomenon },
    { num: '2', label: 'Pattern', text: data.stage2_pattern },
    { num: '3', label: 'Structure', text: data.stage3_structure },
    { num: '4', label: 'Deconstruct', text: data.stage4_deconstruct },
    { num: '5', label: 'Redesign', text: data.stage5_redesign },
  ];
  let html = `<div style="margin-bottom:14px;color:var(--text-dim);font-size:0.9rem;">
    <strong>Persona:</strong> ${data.persona}<br/>
    <strong>Hook:</strong> ${data.hook_question}<br/>
    <strong>Emotion Arc:</strong> ${data.emotional_arc}
  </div><div class="stage-grid">`;
  stages.forEach(s => {
    html += `<div class="stage-item">
      <div class="stage-num">${s.num}</div>
      <div class="stage-content">
        <div class="stage-label">${s.label}</div>
        <div class="stage-text">${s.text}</div>
      </div>
    </div>`;
  });
  html += '</div>';
  return html;
}

function renderScript(data) {
  let html = '';
  if (data.sections) {
    data.sections.forEach(s => {
      html += `<div class="script-section">
        <span class="script-time">${s.time}</span>
        <span class="script-label">${s.label}</span>
        <div class="script-text">${s.text}</div>
      </div>`;
    });
  }
  html += `<div class="meta-row">
    <span>Characters: ${data.char_count || '?'}</span>
    <span>Est. duration: ${data.estimated_seconds || '?'}s</span>
  </div>`;
  html += `<div style="margin-top:16px;">
    <strong style="font-size:0.85rem;color:var(--text-dim);">Full Script</strong>
    <div class="full-script">${data.script || ''}</div>
  </div>`;
  return html;
}

function renderHook(data) {
  let html = `<div style="margin-bottom:14px;">
    <span style="color:var(--text-dim);font-size:0.9rem;">Current hook:</span><br/>
    <span style="font-size:1.1rem;">${data.original_hook}</span>
  </div>
  <div style="color:var(--text-dim);font-size:0.85rem;margin-bottom:16px;">${data.analysis}</div>`;

  if (data.alternatives) {
    data.alternatives.forEach((alt, i) => {
      const isRec = i === data.recommended;
      html += `<div class="hook-alt ${isRec ? 'recommended' : ''}">
        <div class="hook-text">${alt.hook}${isRec ? '<span class="rec-badge">RECOMMENDED</span>' : ''}</div>
        <div class="hook-strategy">${alt.strategy}</div>
      </div>`;
    });
  }
  if (data.reason) {
    html += `<div style="margin-top:12px;font-size:0.85rem;color:var(--text-dim);">${data.reason}</div>`;
  }
  return html;
}

async function runPipeline() {
  const topic = document.getElementById('topic').value.trim();
  const dryRun = document.getElementById('dryRun').checked;
  if (!topic) return;

  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.textContent = 'Running...';
  resultsEl.innerHTML = '';
  setStep(0);

  const badge = dryRun ? 'DRY-RUN' : 'LIVE';
  const badgeClass = dryRun ? 'badge-dry' : 'badge-live';

  try {
    // Step 1: Idea
    const loadingCard = addCard('Step 1/3 - Idea Frame', 'generating...', 'badge-loading',
      '<div><span class="spinner"></span>Generating Thinking OS 5-stage idea frame...</div>');

    const ideaRes = await fetch('/api/idea', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, dry_run: dryRun })
    });
    const idea = await ideaRes.json();
    loadingCard.remove();
    addCard(`Step 1/3 - Idea Frame: ${idea.topic}`, badge, badgeClass, renderIdea(idea));
    setStep(1);

    // Step 2: Script
    const loadingCard2 = addCard('Step 2/3 - 60s Script', 'generating...', 'badge-loading',
      '<div><span class="spinner"></span>Writing 60-second monologue script...</div>');

    const scriptRes = await fetch('/api/script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idea, dry_run: dryRun })
    });
    const script = await scriptRes.json();
    loadingCard2.remove();
    addCard(`Step 2/3 - Script: ${script.title}`, badge, badgeClass, renderScript(script));
    setStep(2);

    // Step 3: Hook
    const loadingCard3 = addCard('Step 3/3 - Hook Optimization', 'analyzing...', 'badge-loading',
      '<div><span class="spinner"></span>Analyzing and optimizing the hook...</div>');

    const hookRes = await fetch('/api/hook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ script, dry_run: dryRun })
    });
    const hook = await hookRes.json();
    loadingCard3.remove();
    addCard('Step 3/3 - Hook Optimization', badge, badgeClass, renderHook(hook));
    setStep(3);

  } catch (err) {
    addCard('Error', 'ERROR', 'badge-dry', `<div style="color:var(--red)">${err.message}</div>`);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Run Pipeline';
  }
}

// Enter key
document.getElementById('topic').addEventListener('keydown', e => {
  if (e.key === 'Enter') runPipeline();
});
</script>
</body>
</html>
"""

import yaml

def load_config():
    p = Path("config.yaml")
    if p.exists():
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    return {}

CONFIG = load_config()

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/idea", methods=["POST"])
def api_idea():
    data = request.json
    topic = data.get("topic", "pencil")
    dry_run = data.get("dry_run", True)
    result = generate_idea(topic, CONFIG, dry_run=dry_run)
    return jsonify(result)

@app.route("/api/script", methods=["POST"])
def api_script():
    data = request.json
    idea = data.get("idea", {})
    dry_run = data.get("dry_run", True)
    result = generate_script(idea, CONFIG, dry_run=dry_run)
    return jsonify(result)

@app.route("/api/hook", methods=["POST"])
def api_hook():
    data = request.json
    script_data = data.get("script", {})
    dry_run = data.get("dry_run", True)
    result = optimize_hook(script_data, CONFIG, dry_run=dry_run)
    return jsonify(result)


if __name__ == "__main__":
    print("ThinkingPipe Web UI: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
