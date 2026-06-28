import subprocess
import json
import os

RUST_SANDBOX_PATH = os.path.join(os.path.dirname(__file__), "rust_sandbox")

def run_python_in_rust_sandbox(code: str, timeout_sec: int = 10) -> dict:
    """
    Execute Python code using the Rust CLI sandbox.
    Returns: {"output": str, "error": str | None, "duration_ms": int}
    """
    try:
        # Ensure binary exists
        if not os.path.exists(RUST_SANDBOX_PATH):
            return {
                "output": "",
                "error": "Rust sandbox binary not found. Run 'cargo build --release' in rust_sandbox/",
                "duration_ms": 0,
            }

        # Run the binary with code via stdin
        result = subprocess.run(
            [RUST_SANDBOX_PATH],
            input=code,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            encoding="utf-8",
        )

        # Parse JSON output
        try:
            data = json.loads(result.stdout.strip())
            return {
                "output": data.get("output", ""),
                "error": data.get("error"),
                "duration_ms": data.get("duration_ms", 0),
            }
        except json.JSONDecodeError:
            return {
                "output": "",
                "error": f"Invalid JSON from Rust sandbox: {result.stdout[:200]}",
                "duration_ms": 0,
            }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": f"Timeout after {timeout_sec} seconds",
            "duration_ms": timeout_sec * 1000,
        }
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "duration_ms": 0,
        }

# Optional: test if run directly
if __name__ == "__main__":
    code = "print('Hello from Rust sandbox!')"
    print(f"Testing Rust sandbox with: {code}")
    result = run_python_in_rust_sandbox(code)
    print(result)
