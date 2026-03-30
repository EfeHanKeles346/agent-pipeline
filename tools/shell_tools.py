"""
Shell işlemleri — komut çalıştırma, dependency kurulumu, dev server başlatma
"""

import os
import subprocess
import signal
import config


def run_command(
    cmd: str | list[str],
    cwd: str = None,
    timeout: int = 120,
    silent: bool = False,
) -> dict:
    """
    Shell komutu çalıştır ve sonucu döndür.

    Args:
        cmd: Çalıştırılacak komut (string veya list)
        cwd: Çalışma dizini (default: config.WORKSPACE_DIR)
        timeout: Maksimum çalışma süresi (saniye)
        silent: True ise çıktıyı bastırma

    Returns:
        {"success": bool, "stdout": str, "stderr": str, "returncode": int}
    """
    if cwd is None:
        cwd = config.WORKSPACE_DIR

    if not os.path.exists(cwd):
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Dizin bulunamadı: {cwd}",
            "returncode": -1,
        }

    if not silent:
        cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
        print(f"  Komut çalıştırılıyor: {cmd_str}")
        print(f"  Dizin: {cwd}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=isinstance(cmd, str),
        )

        if not silent:
            if result.returncode == 0:
                print(f"  Komut başarılı (exit: {result.returncode})")
            else:
                print(f"  Komut başarısız (exit: {result.returncode})")
                if result.stderr:
                    print(f"  Hata: {result.stderr[:500]}")

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        if not silent:
            print(f"  UYARI: Komut {timeout}s timeout'a ulaştı!")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Timeout ({timeout}s)",
            "returncode": -1,
        }
    except FileNotFoundError as e:
        if not silent:
            print(f"  HATA: Komut bulunamadı: {e}")
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def detect_project_type(workspace_dir: str = None) -> str:
    """
    Workspace'teki projenin tipini algıla.

    Returns:
        "node" | "python" | "unknown"
    """
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    if os.path.exists(os.path.join(workspace_dir, "package.json")):
        return "node"
    if os.path.exists(os.path.join(workspace_dir, "requirements.txt")):
        return "python"
    if os.path.exists(os.path.join(workspace_dir, "pyproject.toml")):
        return "python"
    return "unknown"


def auto_install_dependencies(workspace_dir: str = None) -> dict | None:
    """
    Proje tipine göre dependency'leri otomatik kur.
    package.json varsa npm install, requirements.txt varsa pip install.

    Returns:
        run_command sonucu veya None (kurulum gerekmiyorsa)
    """
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    project_type = detect_project_type(workspace_dir)

    if project_type == "node":
        pkg_json = os.path.join(workspace_dir, "package.json")
        node_modules = os.path.join(workspace_dir, "node_modules")

        if os.path.exists(pkg_json):
            print("\n  package.json bulundu — npm install çalıştırılıyor...")
            return run_command("npm install", cwd=workspace_dir, timeout=180)

    elif project_type == "python":
        req_txt = os.path.join(workspace_dir, "requirements.txt")
        if os.path.exists(req_txt):
            print("\n  requirements.txt bulundu — pip install çalıştırılıyor...")
            return run_command(
                "pip install -r requirements.txt",
                cwd=workspace_dir,
                timeout=180,
            )

    return None


_dev_server_process = None


def start_dev_server(workspace_dir: str = None) -> dict:
    """
    Proje tipine göre dev server'ı arka planda başlat.
    Node: npm run dev, Python: python app.py / flask run

    Returns:
        {"success": bool, "message": str, "pid": int | None}
    """
    global _dev_server_process

    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    if _dev_server_process and _dev_server_process.poll() is None:
        return {
            "success": True,
            "message": f"Dev server zaten çalışıyor (PID: {_dev_server_process.pid})",
            "pid": _dev_server_process.pid,
        }

    project_type = detect_project_type(workspace_dir)

    if project_type == "node":
        pkg_json_path = os.path.join(workspace_dir, "package.json")
        cmd = _detect_node_start_cmd(pkg_json_path)
    elif project_type == "python":
        cmd = _detect_python_start_cmd(workspace_dir)
    else:
        return {
            "success": False,
            "message": "Proje tipi algılanamadı (package.json veya requirements.txt bulunamadı)",
            "pid": None,
        }

    if not cmd:
        return {
            "success": False,
            "message": "Başlatma komutu algılanamadı",
            "pid": None,
        }

    print(f"\n  Dev server başlatılıyor: {cmd}")
    print(f"  Dizin: {workspace_dir}")

    try:
        _dev_server_process = subprocess.Popen(
            cmd,
            cwd=workspace_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            preexec_fn=os.setsid,
        )

        return {
            "success": True,
            "message": f"Dev server başlatıldı (PID: {_dev_server_process.pid}) — {cmd}",
            "pid": _dev_server_process.pid,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Dev server başlatılamadı: {e}",
            "pid": None,
        }


def stop_dev_server():
    """Çalışan dev server'ı durdur."""
    global _dev_server_process
    if _dev_server_process and _dev_server_process.poll() is None:
        pid = _dev_server_process.pid
        print(f"  Dev server durduruluyor (PID: {pid})...")
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        _dev_server_process = None
        print("  Dev server durduruldu.")
    else:
        print("  Çalışan dev server yok.")


def _detect_node_start_cmd(pkg_json_path: str) -> str | None:
    """package.json'dan uygun start komutunu algıla."""
    import json
    try:
        with open(pkg_json_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        scripts = pkg.get("scripts", {})
        if "dev" in scripts:
            return "npm run dev"
        if "start" in scripts:
            return "npm start"
        return "npm run dev"
    except (json.JSONDecodeError, FileNotFoundError):
        return "npm run dev"


def _detect_python_start_cmd(workspace_dir: str) -> str | None:
    """Python projesi için uygun start komutunu algıla."""
    candidates = ["app.py", "main.py", "server.py", "run.py", "manage.py"]
    for candidate in candidates:
        if os.path.exists(os.path.join(workspace_dir, candidate)):
            if candidate == "manage.py":
                return "python manage.py runserver"
            return f"python {candidate}"
    return None
