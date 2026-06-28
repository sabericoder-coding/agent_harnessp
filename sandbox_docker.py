
from rust_sandbox_wrapper import run_python_in_rust_sandbox as run_rust

def run_python_in_sandbox(code: str, timeout_sec: int = 10, use_docker: bool = True, use_rust: bool = False) -> dict:
    """
    Smart sandbox: tries Rust â†’ Docker â†’ subprocess fallback.
    """
    if use_rust:
        result = run_rust(code, timeout_sec)
        result["method"] = "rust"
        return result

    if use_docker and DOCKER_AVAILABLE:
        result = run_python_in_docker_sandbox(code, timeout_sec)
        result["method"] = "docker"
        return result
    else:
        from sandbox_subprocess import run_python_in_subprocess
        result = run_python_in_subprocess(code, timeout_sec)
        result["method"] = "subprocess"
        return result
        
import docker
import tempfile
import os
import time

try:
    docker_client = docker.from_env()
    docker_client.ping()
    DOCKER_AVAILABLE = True
except Exception as e:
    DOCKER_AVAILABLE = False
    print(f"âš ï¸ Docker not available: {e}")
    print("   Falling back to subprocess sandbox. Install Docker for isolation.")

def run_python_in_docker_sandbox(code: str, timeout_sec: int = 10) -> dict:
    """
    Execute Python code inside a Docker container with strict isolation.
    """
    if not DOCKER_AVAILABLE:
        return {
            "output": "",
            "error": "Docker not available. Install Docker Desktop or use subprocess sandbox.",
            "duration_ms": 0,
        }
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    start = time.time()
    container = None
    try:
        container = docker_client.containers.run(
            image="python:3.11-slim",
            command="python /script.py",
            volumes={tmp_path: {"bind": "/script.py", "mode": "ro"}},
            working_dir="/",
            mem_limit="128m",
            memswap_limit="128m",
            nano_cpus=int(0.5 * 1e9),
            network_disabled=True,
            read_only=True,
            security_opt=["no-new-privileges:true"],
            cap_drop=["ALL"],
            pids_limit=100,
            timeout=timeout_sec,
            detach=True,
        )
        result = container.wait(timeout=timeout_sec)
        logs = container.logs(stdout=True, stderr=True).decode("utf-8")
        duration_ms = int((time.time() - start) * 1000)
        
        success = result["StatusCode"] == 0
        output = logs if success else ""
        error = None if success else logs
        
        return {
            "output": output.strip(),
            "error": error,
            "duration_ms": duration_ms,
        }
    except docker.errors.ContainerError as e:
        duration_ms = int((time.time() - start) * 1000)
        error_msg = e.stderr.decode("utf-8") if e.stderr else str(e)
        return {"output": "", "error": f"Container error: {error_msg}", "duration_ms": duration_ms}
    except docker.errors.TimeoutError:
        duration_ms = int((time.time() - start) * 1000)
        return {"output": "", "error": f"Timeout after {timeout_sec} seconds", "duration_ms": duration_ms}
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        return {"output": "", "error": f"Execution error: {str(e)}", "duration_ms": duration_ms}
    finally:
        if container:
            try:
                container.remove(force=True)
            except:
                pass
        try:
            os.unlink(tmp_path)
        except:
            pass

def run_python_in_sandbox(code: str, timeout_sec: int = 10, use_docker: bool = True) -> dict:
    """
    Smart sandbox: uses Docker if available and requested, otherwise subprocess fallback.
    """
    if use_docker and DOCKER_AVAILABLE:
        result = run_python_in_docker_sandbox(code, timeout_sec)
        result["method"] = "docker"
        return result
    else:
        from sandbox_subprocess import run_python_in_subprocess
        result = run_python_in_subprocess(code, timeout_sec)
        result["method"] = "subprocess"
        return result

if __name__ == "__main__":
    test_code = "print('Hello from Docker sandbox!')"
    print(f"Testing Docker sandbox with: {test_code}")
    result = run_python_in_docker_sandbox(test_code)
    print(f"Output: {result['output']}")
    print(f"Error: {result['error']}")
    print(f"Duration: {result['duration_ms']}ms")
