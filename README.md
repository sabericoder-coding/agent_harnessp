# ⚡ Agent Harness

**An agent harness that turns LLMs into safe, executable code agents.**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sabericoder-coding/agent-harness)

## 🧠 What Is Really Agent Harness?

> **An agent harness is the orchestration layer between an LLM and the real world.**
>
> It translates language into action — safely, reliably, and observably.

```
User Task → Harness → LLM → Tool Call → Sandbox → Result → Harness → Answer
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER TASK                                  │
│                   "Calculate 15 * 37"                             │
└─────────────────────────────┬───────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: ORCHESTRATION (harness.py)                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ • Manages conversation history                             │  │
│  │ • Formats prompts + tool definitions                       │  │
│  │ • Calls LLM API (Groq)                                     │  │
│  │ • Parses structured tool calls                             │  │
│  │ • Feeds results back to LLM                                │  │
│  │ • Handles retries & errors                                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: EXECUTION (sandbox_docker.py)                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ • Docker container with enterprise security limits          │  │
│  │ • Memory: 128MB max                                        │  │
│  │ • CPU: 0.5 cores max                                       │  │
│  │ • Network: DISABLED                                        │  │
│  │ • Filesystem: READ-ONLY                                    │  │
│  │ • Timeout: 10 seconds                                      │  │
│  │ • Fallback: Subprocess (graceful degradation)              │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: EVALUATION (eval_tasks.py)                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ • 3 benchmark tasks                                        │  │
│  │ • Token usage tracking                                     │  │
│  │ • Latency measurement                                      │  │
│  │ • Pass/fail reporting                                      │  │
│  │ • Continuous improvement feedback                          │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

For simplicity let's call these 3 layers ORCHESTRATOR,EXECUTOR - EVALTOR

## 🧩 The Three Core Parts

### 1. ORCHESTRATOR  — *The Manager*

**What it does:** Runs the conversation loop with the LLM.

**Core concept:** Send messages → Get response → Parse tool calls → Repeat

```
User → "Calculate 15 * 37"
         ↓
LLM → "I'll use execute_python"
         ↓
Tool Call → {"code": "print(15 * 37)"}
```

### 2.  EXECUTOR — *The Hands*

**What it does:** Runs code safely in an isolated environment.

**Core concept:** Security layers (memory, CPU, network, filesystem)

```
Code → Docker Container (128MB, 0.5 CPU, no network, read-only)
         ↓
Output → "555"
```

### 3. EVALTOR — *The Eyes*

**What it does:** Tracks every action and metric.

**Core concept:** Measure to improve — tokens, latency, success rate

```
Each Turn → Tokens Used → Latency → Success/Fail
```

## 🔄 How They Work Together

```
1. USER GIVES TASK
   "Calculate 15 * 37"
   
2. ORCHESTRATOR SENDS TO LLM
   [System prompt + Tool definition + User task]
   
3. LLM RESPONDS WITH TOOL CALL
   {"name": "execute_python", "arguments": {"code": "print(15*37)"}}
   
4. SAFETY NET VALIDATES
   AST.parse(code) → ✅ Valid syntax
   
5. EXECUTOR RUNS IN DOCKER
   Python container → 128MB memory → No network → Read-only
   
6. EVALTOR CAPTURES RESULTS
   Output: "555" | Tokens: 948 | Latency: 387ms
   
7. ORCHESTRATOR FEEDS BACK TO LLM
   "Tool Result: Output: 555"
   
8. LLM GIVES FINAL ANSWER
   "15 times 37 equals 555."
   
9. USER RECEIVES ANSWER ✅
```

---

## ⚡ Quick Stats

| Metric | Result |
|--------|--------|
| Tasks Passed | 3/3 (100%) |
| Average Latency | ~623ms |
| Total Tokens | 2,604 |
| Security Layers | 7 (Docker) |
| Deployment | One‑click (Codespaces) |

---

## 🚀 Try It Now

```bash
# One click — no setup
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sabericoder-coding/agent-harness)

## 📂 Repo Structure

```
agent-harness/
├── harness.py              # Core agent loop
├── sandbox_docker.py       # Docker sandbox
├── sandbox_subprocess.py   # Fallback
├── eval_tasks.py           # 3 benchmark evals
├── .devcontainer/          # Codespaces config
└── README.md               # This file
