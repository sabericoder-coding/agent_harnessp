import subprocess
import tempfile
import time
import os

def run_python_in_subprocess(code: str, timeout_sec: int = 10) -> dict:
    """
    Execute Python code in a subprocess (no Docker isolation).
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    start = time.time()
    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            encoding="utf-8",
        )
        duration_ms = int((time.time() - start) * 1000)
        if result.returncode == 0:
            return {"output": result.stdout.strip(), "error": None, "duration_ms": duration_ms}
        else:
            return {"output": "", "error": result.stderr.strip(), "duration_ms": duration_ms}
    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start) * 1000)
        return {"output": "", "error": f"Timeout after {timeout_sec} seconds", "duration_ms": duration_ms}
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        return {"output": "", "error": str(e), "duration_ms": duration_ms}
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass

# Alias for direct import if needed
run_python_in_sandbox = run_python_in_subprocess