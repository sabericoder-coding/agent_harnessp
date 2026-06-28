
from harness import run_agent

TASKS = [
    "Use execute_python to print 'Hello from sandbox'",
    "Calculate 15 * 37 and print the result",
    "Write a loop that sums numbers 1 to 10 and print the sum",
]

def run_eval():
    results = []
    total_tokens = 0
    total_latency = 0
    
    for i, task in enumerate(TASKS, 1):
        print(f"\n{'='*60}")
        print(f"EVAL TASK {i}: {task}")
        print('='*60)
        
        try:
            answer, history, metrics = run_agent(
                task, 
                max_turns=3, 
                verbose=True, 
                use_docker_sandbox=False
            )
            success = answer is not None and len(answer) > 0
            results.append({"task": task, "success": success, "answer": answer, "metrics": metrics})
            total_tokens += metrics.get("total_tokens", 0)
            total_latency += metrics.get("total_latency_ms", 0)
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({"task": task, "success": False, "error": str(e)})
    
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    passed = 0
    for r in results:
        status = "✅ PASS" if r["success"] else "❌ FAIL"
        print(f"{status} | {r['task']}")
        if r.get("metrics"):
            print(f"       Tokens: {r['metrics'].get('total_tokens', 0)} | Latency: {r['metrics'].get('total_latency_ms', 0)}ms")
        passed += 1 if r["success"] else 0
    
    print(f"\n📊 TOTAL: {passed}/{len(TASKS)} tasks passed")
    print(f"📊 Total tokens consumed: {total_tokens}")
    print(f"📊 Total latency: {total_latency}ms ({total_latency/1000:.1f}s)")

if __name__ == "__main__":
    run_eval()
