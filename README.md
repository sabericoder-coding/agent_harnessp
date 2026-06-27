[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sabericoder-coding/agent-harness)

# Codex‑Style Agent Harness

**A production‑minded agent harness for LLM code execution with sandboxing, observability, and multi‑layer debugging.**

This project demonstrates the core competencies required for the **OpenAI Codex Core Agents** role:
- Agent harness design (tool calling → execution → feedback loop)
- Sandboxed code execution (Docker + subprocess fallback)
- Evaluation frameworks with pass/fail metrics
- Debugging across model, harness, and runtime layers
- Observability (tokens, latency, retries)

---

## 🏗️ Architecture

```
User Task → Agent Harness → LLM (Groq/Mixtral) → Tool Call (execute_python)
                                              ↓
                                        Sandbox (Docker / Subprocess)
                                              ↓
                                    Output/Error → Back to LLM
                                              ↓
                                      Final Answer or Retry
```

**Key components:**
- **LLM**: Groq API (`llama-3.1-8b-instant`) with function calling
- **Sandbox**: Hybrid — Docker (with memory/CPU/network limits) + subprocess fallback
- **Syntax validation**: AST parsing before execution
- **Retry logic**: Automatic recovery from syntax errors and missing tool calls
- **Observability**: Token counting, per‑turn latency, retry tracking

---

## 🔍 Multi‑Layer Debugging (OpenAI Signal)

During development, I encountered and resolved failures across three distinct layers:

### Layer 1: Harness Issues
**Problem**: The agent loop would hang when the LLM returned malformed tool calls.  
**Diagnosis**: Added structured logging and inspected raw API responses.  
**Fix**: Implemented JSON validation with graceful error messages fed back to the LLM.

```python
try:
    args = json.loads(tool_call.function.arguments)
except json.JSONDecodeError as e:
    messages.append({
        "role": "tool",
        "content": f"Invalid JSON: {e}. Please provide valid arguments."
    })
    continue
```

### Layer 2: Model Behavior Issues
**Problem**: The model generated Python with syntax errors — combining statements with semicolons (`total=0; for i in range(10): total+=i`).  
**Diagnosis**: Isolated the issue to model output by running the same code manually.  
**Fix**: Multi‑pronged approach:
1. **Prompt engineering** – Explicit system message forbidding semicolons before `for`/`if`
2. **Pre‑execution AST validation** – Catch syntax errors before they reach the sandbox
3. **Retry loop** – Feed syntax error back to the model for self‑correction

```python
try:
    ast.parse(code)
except SyntaxError as syntax_err:
    messages.append({
        "role": "tool",
        "content": f"Syntax error: {syntax_err}. Please use proper multi‑line formatting."
    })
    continue  # Model retries
```

### Layer 3: Runtime/Infrastructure Issues
**Problem**: Some models on Groq's free tier returned no tool calls (silent failure).  
**Diagnosis**:
- Checked API status (200 OK, but empty `tool_calls`)
- Tested with multiple models
- Researched Groq's documentation

**Fix**: Switched to `llama-3.1-8b-instant` with enhanced prompt engineering, achieving 100% pass rate on eval tasks.

---

## 📊 Evaluation Results

| Task | Success | Tokens | Latency |
|------|---------|--------|---------|
| Print 'Hello from sandbox' | ✅ | 987 | 1,188ms |
| Calculate 15 * 37 | ✅ | 948 | 387ms |
| Sum 1 to 10 with loop | ✅ | 669 | 293ms |

**Success rate: 100% (3/3 tasks)**  
**Total tokens consumed: 2,604**  
**Total latency: 1,868ms (1.9s)**  
**Average response time: ~623ms**

### Sample Output
```
EVALUATION SUMMARY
==================================================
✅ PASS | Use execute_python to print 'Hello from sandbox'
         Tokens: 987 | Latency: 1188ms
✅ PASS | Calculate 15 * 37 and print the result
         Tokens: 948 | Latency: 387ms
✅ PASS | Write a loop that sums numbers 1 to 10 and print the sum
         Tokens: 669 | Latency: 293ms

📊 TOTAL: 3/3 tasks passed
📊 Total tokens consumed: 2604
📊 Total latency: 1868ms (1.9s)
```

---

## 🚀 Quick Start

### One‑Click Demo (Recommended)
Click the badge at the top of this README to launch the project in GitHub Codespaces — no setup required.

Once the Codespace opens, run:
```bash
python eval_tasks.py
```

### Local Setup
```bash
git clone https://github.com/sabericoder-coding/agent-harness
cd agent-harness
pip install -r requirements.txt
```

Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_key_here
```

Run the evaluation:
```bash
python eval_tasks.py
```

---

## 📁 Project Structure

```
agent-harness/
├── .devcontainer/
│   └── devcontainer.json   # Codespace configuration
├── harness.py              # Main agent loop with tool calling
├── sandbox_docker.py       # Docker sandbox with security limits
├── sandbox_subprocess.py   # Subprocess fallback (no Docker)
├── eval_tasks.py           # Evaluation suite with metrics
├── test_api.py             # API connection test utility
├── requirements.txt        # Dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

---

## 🛡️ Security & Isolation

### Docker Sandbox (Production Ready)
- **Memory limit**: 128MB
- **CPU limit**: 0.5 cores
- **No network access**: `network_disabled=True`
- **Read‑only filesystem**: `read_only=True`
- **No privilege escalation**: `security_opt=["no-new-privileges:true"]`
- **Dropped capabilities**: `cap_drop=["ALL"]`
- **Process limit**: `pids_limit=100`

### Automatic Fallback
If Docker is unavailable, the system gracefully falls back to subprocess execution — ensuring your agent never fails due to infrastructure issues.

### Syntax Validation
AST parsing before execution prevents malformed code from ever reaching the sandbox, saving time and reducing errors.

### API Key Security
Credentials are loaded via environment variables — never hardcoded in the source code.

---

## 📈 Observability

Your agent harness provides real‑time insight into its operation:

- **Per‑turn token usage**: Prompt tokens, completion tokens, and total
- **Latency tracking**: Milliseconds per turn
- **Retry counter**: Tracks syntax errors and recovery attempts
- **Sandbox method**: Shows whether Docker or subprocess was used
- **Evaluation metrics**: Pass/fail status for each task

---

## 🎯 Why This Matters for OpenAI Codex

The Codex Core Agents team builds the **harness** — the critical layer between models and real‑world action. This project demonstrates:

1. **Hands‑on across the stack** – From prompt engineering (`harness.py`) to execution sandbox (`sandbox_docker.py`) to evals (`eval_tasks.py`).

2. **Debugging from evidence** – The multi‑layer debugging section above shows systematic root‑cause analysis across model, harness, and runtime.

3. **Production thinking** – Token tracking, latency metrics, retry logic, and graceful error handling with Docker fallback.

4. **Research proximity** – The retry loop and syntax validation can be used to generate training data for improving model code generation.

---

## 🧪 Testing

### API Connection Test
Verify your Groq API key is working correctly:
```bash
python test_api.py
```

### Full Evaluation Suite
Run all three benchmark tasks:
```bash
python eval_tasks.py
```

### Single Task Test
```bash
python harness.py
```

---

## 📝 License

MIT — Free for open‑source and portfolio use.

---

## 🙏 Acknowledgements

- **Groq** for free API access to `llama-3.1-8b-instant`
- **OpenAI** for the inspiration (Codex Core Agents team)

---

**Built as part of my application for AI Systems Engineer, Codex Agents @ OpenAI**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sabericoder-coding/agent-harness)
