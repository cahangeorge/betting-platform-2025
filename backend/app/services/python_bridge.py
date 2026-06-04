import asyncio
import json
import os
import tempfile
from pathlib import Path

from app.config import get_settings

settings = get_settings()

PENALTYBLOG_PYTHON = settings.penaltyblog_python or str(
    Path(__file__).resolve().parent.parent.parent.parent / "penaltyblog" / ".venv" / "bin" / "python"
)
PENALTYBLOG_BRIDGE = settings.penaltyblog_bridge or str(
    Path(__file__).resolve().parent.parent.parent / "scripts" / "penaltyblog_bridge.py"
)
SOCCERDATA_PYTHON = settings.soccerdata_python or str(
    Path(__file__).resolve().parent.parent.parent.parent / "soccerdata" / ".venv" / "bin" / "python"
)
SOCCERDATA_BRIDGE = settings.soccerdata_bridge or str(
    Path(__file__).resolve().parent.parent.parent / "scripts" / "soccerdata_bridge.py"
)
ODDSHARVESTER_PYTHON = settings.oddsharvester_python or str(
    Path(__file__).resolve().parent.parent.parent.parent / "OddsHarvester" / ".venv" / "bin" / "python"
)

TEMP_DIR = Path(tempfile.gettempdir()) / "bet-bridge"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

BRIDGE_TIMEOUT = 180


class BridgeError(Exception):
    pass


async def run_bridge(
    payload: dict,
    python_bin: str,
    bridge_script: str,
    label: str = "bridge",
    timeout: int = BRIDGE_TIMEOUT,
) -> dict:
    output_path = TEMP_DIR / f"{label}_{os.getpid()}_{id(payload)}.json"
    cmd = [python_bin, bridge_script, "--payload", json.dumps(payload), "--output", str(output_path)]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise BridgeError(f"{label} request timed out after {timeout}s")

        if proc.returncode != 0:
            stderr_text = stderr.decode().strip() if stderr else ""
            raise BridgeError(stderr_text or f"{label} bridge exited with code {proc.returncode}")

        if not output_path.exists():
            raise BridgeError(f"{label} bridge produced no output file")

        text = output_path.read_text()
        output_path.unlink(missing_ok=True)
        parsed = json.loads(text)

        if not parsed.get("ok"):
            raise BridgeError(parsed.get("error", f"{label} bridge returned failure"))

        return parsed["result"]
    except BridgeError:
        raise
    except Exception as e:
        raise BridgeError(f"{label} bridge error: {e}") from e


async def run_penaltyblog(payload: dict) -> dict:
    return await run_bridge(payload, PENALTYBLOG_PYTHON, PENALTYBLOG_BRIDGE, label="penaltyblog")


async def run_soccerdata(payload: dict) -> dict:
    return await run_bridge(payload, SOCCERDATA_PYTHON, SOCCERDATA_BRIDGE, label="soccerdata")


async def run_oddsharvester(args: list[str]) -> str:
    cmd = [ODDSHARVESTER_PYTHON, "-m", "OddsHarvester", *args]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=BRIDGE_TIMEOUT)
        if proc.returncode != 0:
            raise BridgeError(stderr.decode().strip() or f"OddsHarvester exited with code {proc.returncode}")
        return stdout.decode().strip()
    except asyncio.TimeoutError:
        proc.kill()
        raise BridgeError("OddsHarvester request timed out")


