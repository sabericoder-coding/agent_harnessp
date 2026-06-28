import os
import json
import time
import ast
from openai import OpenAI
from dotenv import load_dotenv

# Import the smart sandbox
from sandbox_docker import run_python_in_sandbox

# Load environment variables
load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("âŒ GROQ_API_KEY not found in .env file")
    print("Get one free at: https://console.groq.com")
    exit(1)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

# Use mixtral (works well with tool calls)
MODEL_NAME = "llama-3.1-8b-instant"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Execute Python code and return stdout/stderr",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Write multi-line code with proper indentation.",
                    },
                },
                "required": ["code"],
            },
        },
    }
]

def run_agent(task: str, max_turns: int = 3, verbose: bool = True, use_docker_sandbox: bool = True):
    """
    Run the agent on a task.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a coding assistant. Use the execute_python tool to run Python code.\n"
                "Always use the tool to solve tasks."
            ),
        },
        {"role": "user", "content": task},
    ]

    turn = 0
    total_tokens = 0
    total_latency_ms = 0
    sandbox_method = "unknown"

    if verbose:
        sandbox_status = "Docker (with subprocess fallback)" if use_docker_sandbox else "subprocess only"
        print(f"ðŸ”’ Sandbox mode: {sandbox_status}")
        print(f"ðŸ¤– Model: {MODEL_NAME}")

    while turn < max_turns:
        turn += 1
        turn_start_time = time.time()

        if verbose:
            print(f"\n--- Turn {turn} ---")

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.1,
            )
        except Exception as e:
            if verbose:
                print(f"âŒ API error: {e}")
            return None, messages, {"error": str(e)}

        usage = response.usage
        if usage and verbose:
            turn_tokens = usage.total_tokens
            total_tokens += turn_tokens
            print(f"ðŸ“Š Tokens: {turn_tokens} (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")

        msg = response.choices[0].message
        messages.append(msg)

        turn_latency = int((time.time() - turn_start_time) * 1000)
        total_latency_ms += turn_latency
        if verbose:
            print(f"â±ï¸  Latency: {turn_latency}ms")

        # Check if agent is done (no tool call)
        if not msg.tool_calls:
            if verbose:
                print(f"âœ… Agent finished (no tool call)")
                print(f"ðŸ“ Final answer: {msg.content}")
            metrics = {
                "turns": turn,
                "total_tokens": total_tokens,
                "total_latency_ms": total_latency_ms,
                "sandbox_method": sandbox_method,
            }
            return msg.content, messages, metrics

        # Process each tool call
        for tool_call in msg.tool_calls:
            if tool_call.function.name == "execute_python":
                try:
                    # Parse the arguments
                    args = json.loads(tool_call.function.arguments)
                    code = args.get("code", "")
                    
                    if verbose:
                        print(f"ðŸ“ Code received:\n```python\n{code}\n```")
                    
                    # Syntax check
                    try:
                        ast.parse(code)
                    except SyntaxError as syntax_err:
                        if verbose:
                            print(f"âš ï¸  Syntax error: {syntax_err}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Syntax error: {syntax_err}. Please fix the code."
                        })
                        continue
                    
                    # Execute in sandbox
                    result = run_python_in_sandbox(code, timeout_sec=10, use_docker=use_docker_sandbox)
                    output = result["output"]
                    error = result["error"]
                    duration = result["duration_ms"]
                    sandbox_method = result.get("method", "unknown")
                    
                    if verbose:
                        if error:
                            print(f"âŒ Execution error ({duration}ms, {sandbox_method})")
                            print(f"   {error[:200]}")
                        else:
                            print(f"âœ… Execution success ({duration}ms, {sandbox_method})")
                            if output:
                                print(f"ðŸ“¤ Output: {output[:500]}")
                    
                    # Feed result back
                    if error:
                        tool_response = f"Error:\n{error}\n\nPlease fix the code."
                    else:
                        tool_response = f"Output:\n{output}" if output else "Code executed successfully (no output)."
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_response,
                    })
                    
                except json.JSONDecodeError as e:
                    if verbose:
                        print(f"âŒ JSON parse error: {e}")
                        print(f"   Raw arguments: {tool_call.function.arguments}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: Invalid JSON. Please provide valid JSON with a 'code' field."
                    })

    if verbose:
        print(f"âš ï¸  Max turns ({max_turns}) reached")
    
    metrics = {
        "turns": turn,
        "total_tokens": total_tokens,
        "total_latency_ms": total_latency_ms,
        "completed": False,
        "sandbox_method": sandbox_method,
    }
    return None, messages, metrics


if __name__ == "__main__":
    test_task = "Use execute_python to print 'Hello from sandbox'"
    print(f"Testing: {test_task}\n")
    answer, history, metrics = run_agent(test_task, max_turns=2, verbose=True, use_docker_sandbox=False)
    print(f"\nâœ… Final answer: {answer}")
    print(f"ðŸ“Š Metrics: {metrics}")
