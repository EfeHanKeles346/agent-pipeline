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
        "node" | "python" | "go" | "rust" | "java_maven" | "java_gradle" |
        "cpp_cmake" | "cpp_make" | "dotnet" | "unknown"
    """
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    if _root_has_file(workspace_dir, "package.json"):
        return "node"

    if _root_has_any_file(workspace_dir, ("requirements.txt", "pyproject.toml", "setup.py")):
        return "python"

    if _root_has_file(workspace_dir, "go.mod"):
        return "go"

    if _root_has_file(workspace_dir, "Cargo.toml"):
        return "rust"

    if _root_has_file(workspace_dir, "pom.xml"):
        return "java_maven"

    if _root_has_any_file(workspace_dir, ("build.gradle", "build.gradle.kts")):
        return "java_gradle"

    if _find_file_with_suffix(workspace_dir, (".csproj", ".sln")):
        return "dotnet"

    if _root_has_file(workspace_dir, "CMakeLists.txt"):
        return "cpp_cmake"

    if _root_has_file(workspace_dir, "Makefile"):
        return "cpp_make"

    return "unknown"


def get_install_command(project_type: str, workspace_dir: str = None) -> str | None:
    """Proje tipine gore dependency kurulum komutunu don."""
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    if project_type == "node":
        return "npm install"

    if project_type == "python":
        if _root_has_file(workspace_dir, "requirements.txt"):
            return "pip install -r requirements.txt"
        if _root_has_any_file(workspace_dir, ("pyproject.toml", "setup.py")):
            return "pip install -e ."
        return None

    if project_type == "go":
        return "go mod download"

    if project_type == "rust":
        return "cargo fetch"

    if project_type == "java_maven":
        return "./mvnw dependency:resolve" if _root_has_file(workspace_dir, "mvnw") else "mvn dependency:resolve"

    if project_type == "java_gradle":
        return "./gradlew dependencies" if _root_has_file(workspace_dir, "gradlew") else "gradle dependencies"

    if project_type == "cpp_cmake":
        return "mkdir -p build && cd build && cmake .."

    if project_type == "dotnet":
        return "dotnet restore"

    return None


def get_build_command(project_type: str, workspace_dir: str = None) -> str | None:
    """Proje tipine gore build veya compile kontrol komutunu don."""
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    if project_type == "node":
        return "npm run build"

    if project_type == "python":
        return "python -m compileall -q ."

    if project_type == "go":
        return "go build ./..."

    if project_type == "rust":
        return "cargo build"

    if project_type == "java_maven":
        return "./mvnw compile" if _root_has_file(workspace_dir, "mvnw") else "mvn compile"

    if project_type == "java_gradle":
        return "./gradlew build" if _root_has_file(workspace_dir, "gradlew") else "gradle build"

    if project_type == "cpp_cmake":
        return "mkdir -p build && cd build && cmake .. && cmake --build ."

    if project_type == "cpp_make":
        return "make"

    if project_type == "dotnet":
        return "dotnet build"

    return None


def get_dev_server_command(project_type: str, workspace_dir: str = None) -> str | None:
    """Proje tipine gore calistirma komutunu belirle."""
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    if project_type == "node":
        pkg_json_path = os.path.join(workspace_dir, "package.json")
        return _detect_node_start_cmd(pkg_json_path)

    if project_type == "python":
        return _detect_python_start_cmd(workspace_dir)

    if project_type == "go":
        if _root_has_file(workspace_dir, "main.go") or _find_file_with_suffix(workspace_dir, (".go",)):
            return "go run ."
        return None

    if project_type == "rust":
        return "cargo run"

    if project_type == "cpp_cmake":
        return _detect_cpp_start_cmd(workspace_dir, build_dir_name="build")

    if project_type == "cpp_make":
        return _detect_cpp_start_cmd(workspace_dir, build_dir_name=None)

    if project_type == "java_maven":
        return "./mvnw exec:java" if _root_has_file(workspace_dir, "mvnw") else "mvn exec:java"

    if project_type == "java_gradle":
        return "./gradlew run" if _root_has_file(workspace_dir, "gradlew") else "gradle run"

    if project_type == "dotnet":
        return "dotnet run"

    return None


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
    install_cmd = get_install_command(project_type, workspace_dir)
    if not install_cmd:
        return None

    print(f"\n  Dependency kurulumu çalıştırılıyor ({project_type}): {install_cmd}")
    return run_command(
        install_cmd,
        cwd=workspace_dir,
        timeout=config.INSTALL_TIMEOUT_SECONDS,
    )


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

    cmd = get_dev_server_command(project_type, workspace_dir)
    if project_type == "unknown":
        return {
            "success": False,
            "message": "Proje tipi algılanamadı",
            "pid": None,
        }

    if not cmd:
        return {
            "success": False,
            "message": f"Başlatma komutu algılanamadı ({project_type})",
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
            "command": cmd,
            "pid": _dev_server_process.pid,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Dev server başlatılamadı: {e}",
            "command": cmd,
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


def _root_has_file(workspace_dir: str, filename: str) -> bool:
    return os.path.exists(os.path.join(workspace_dir, filename))


def _root_has_any_file(workspace_dir: str, filenames: tuple[str, ...]) -> bool:
    return any(_root_has_file(workspace_dir, filename) for filename in filenames)


def _find_file_with_suffix(workspace_dir: str, suffixes: tuple[str, ...]) -> str | None:
    try:
        for root, dirs, files in os.walk(workspace_dir):
            dirs.sort()
            for filename in sorted(files):
                if filename.endswith(suffixes):
                    return os.path.join(root, filename)
    except OSError:
        return None
    return None


def _detect_cpp_start_cmd(workspace_dir: str, build_dir_name: str | None) -> str | None:
    search_dir = workspace_dir if build_dir_name is None else os.path.join(workspace_dir, build_dir_name)
    if not os.path.isdir(search_dir):
        return None

    executable = _find_executable(search_dir)
    if not executable:
        return None

    rel_path = os.path.relpath(executable, workspace_dir)
    return f"./{rel_path}"


def _find_executable(search_dir: str) -> str | None:
    skipped_dirs = {"CMakeFiles", ".git", "__pycache__", "Testing", "_deps"}
    skipped_suffixes = (".o", ".a", ".so", ".dylib", ".dll", ".txt", ".cmake", ".ninja")

    try:
        for root, dirs, files in os.walk(search_dir):
            dirs[:] = [dirname for dirname in dirs if dirname not in skipped_dirs]
            dirs.sort()

            for filename in sorted(files):
                full_path = os.path.join(root, filename)
                if filename.endswith(skipped_suffixes):
                    continue
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
    except OSError:
        return None

    return None
