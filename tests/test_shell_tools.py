from pathlib import Path
import stat

import pytest

import tools.shell_tools as shell_tools
from tools.shell_tools import (
    auto_install_dependencies,
    detect_project_type,
    get_build_command,
    get_dev_server_command,
    get_install_command,
)


def test_detect_project_type_returns_node_for_package_json(tmp_path: Path):
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")

    assert detect_project_type(str(tmp_path)) == "node"


def test_detect_project_type_returns_python_for_requirements(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    assert detect_project_type(str(tmp_path)) == "python"


def test_detect_project_type_returns_python_for_pyproject(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    assert detect_project_type(str(tmp_path)) == "python"


def test_detect_project_type_returns_unknown_when_no_markers_exist(tmp_path: Path):
    assert detect_project_type(str(tmp_path)) == "unknown"


@pytest.mark.parametrize(
    ("filename", "content", "expected"),
    [
        ("setup.py", "from setuptools import setup\n", "python"),
        ("go.mod", "module demo\n", "go"),
        ("Cargo.toml", "[package]\nname='demo'\n", "rust"),
        ("pom.xml", "<project />\n", "java_maven"),
        ("build.gradle", "plugins {}\n", "java_gradle"),
        ("build.gradle.kts", "plugins {}\n", "java_gradle"),
        ("CMakeLists.txt", "project(Demo)\n", "cpp_cmake"),
        ("Makefile", "all:\n\t@echo ok\n", "cpp_make"),
        ("app.csproj", "<Project />\n", "dotnet"),
        ("demo.sln", "Microsoft Visual Studio Solution File\n", "dotnet"),
    ],
)
def test_detect_project_type_supports_multiple_languages(
    tmp_path: Path,
    filename: str,
    content: str,
    expected: str,
):
    (tmp_path / filename).write_text(content, encoding="utf-8")

    assert detect_project_type(str(tmp_path)) == expected


def test_detect_project_type_prioritizes_node_over_makefile(tmp_path: Path):
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / "Makefile").write_text("all:\n\t@echo ok\n", encoding="utf-8")

    assert detect_project_type(str(tmp_path)) == "node"


@pytest.mark.parametrize(
    ("project_type", "filename", "expected"),
    [
        ("node", "package.json", "npm install"),
        ("python", "requirements.txt", "pip install -r requirements.txt"),
        ("go", "go.mod", "go mod download"),
        ("rust", "Cargo.toml", "cargo fetch"),
        ("java_maven", "pom.xml", "mvn dependency:resolve"),
        ("java_gradle", "build.gradle", "gradle dependencies"),
        ("cpp_cmake", "CMakeLists.txt", "mkdir -p build && cd build && cmake .."),
        ("dotnet", "app.csproj", "dotnet restore"),
    ],
)
def test_get_install_command_returns_expected_command(
    tmp_path: Path,
    project_type: str,
    filename: str,
    expected: str,
):
    (tmp_path / filename).write_text("marker\n", encoding="utf-8")

    assert get_install_command(project_type, str(tmp_path)) == expected


def test_get_install_command_uses_editable_install_for_pyproject(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    assert get_install_command("python", str(tmp_path)) == "pip install -e ."


@pytest.mark.parametrize(
    ("project_type", "workspace_setup", "expected"),
    [
        ("node", lambda path: (path / "package.json").write_text("{}", encoding="utf-8"), "npm run build"),
        ("python", lambda path: (path / "main.py").write_text("print('x')\n", encoding="utf-8"), "python -m compileall -q ."),
        ("go", lambda path: (path / "go.mod").write_text("module demo\n", encoding="utf-8"), "go build ./..."),
        ("rust", lambda path: (path / "Cargo.toml").write_text("[package]\nname='demo'\n", encoding="utf-8"), "cargo build"),
        ("cpp_cmake", lambda path: (path / "CMakeLists.txt").write_text("project(Demo)\n", encoding="utf-8"), "mkdir -p build && cd build && cmake .. && cmake --build ."),
        ("cpp_make", lambda path: (path / "Makefile").write_text("all:\n\t@echo ok\n", encoding="utf-8"), "make"),
        ("dotnet", lambda path: (path / "demo.sln").write_text("solution\n", encoding="utf-8"), "dotnet build"),
    ],
)
def test_get_build_command_returns_expected_command(
    tmp_path: Path,
    project_type: str,
    workspace_setup,
    expected: str,
):
    workspace_setup(tmp_path)

    assert get_build_command(project_type, str(tmp_path)) == expected


def test_get_build_command_prefers_wrappers_when_available(tmp_path: Path):
    (tmp_path / "pom.xml").write_text("<project />\n", encoding="utf-8")
    (tmp_path / "mvnw").write_text("#!/bin/sh\n", encoding="utf-8")
    (tmp_path / "build.gradle").write_text("plugins {}\n", encoding="utf-8")
    (tmp_path / "gradlew").write_text("#!/bin/sh\n", encoding="utf-8")

    assert get_build_command("java_maven", str(tmp_path)) == "./mvnw compile"
    assert get_install_command("java_maven", str(tmp_path)) == "./mvnw dependency:resolve"
    assert get_build_command("java_gradle", str(tmp_path)) == "./gradlew build"
    assert get_install_command("java_gradle", str(tmp_path)) == "./gradlew dependencies"


def test_auto_install_dependencies_runs_expected_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    (tmp_path / "go.mod").write_text("module demo\n", encoding="utf-8")
    calls = []

    def fake_run(cmd, cwd=None, timeout=120, silent=False):
        calls.append((cmd, cwd, timeout, silent))
        return {"success": True, "stdout": "", "stderr": "", "returncode": 0}

    monkeypatch.setattr(shell_tools, "run_command", fake_run)

    result = auto_install_dependencies(str(tmp_path))

    assert result["success"] is True
    assert calls[0][0] == "go mod download"
    assert calls[0][1] == str(tmp_path)


def test_auto_install_dependencies_returns_none_for_cpp_make(tmp_path: Path):
    (tmp_path / "Makefile").write_text("all:\n\t@echo ok\n", encoding="utf-8")

    assert auto_install_dependencies(str(tmp_path)) is None


def test_get_dev_server_command_supports_multiple_project_types(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('server')\n", encoding="utf-8")
    assert get_dev_server_command("python", str(tmp_path)) == "python main.py"

    (tmp_path / "main.go").write_text("package main\nfunc main() {}\n", encoding="utf-8")
    assert get_dev_server_command("go", str(tmp_path)) == "go run ."

    assert get_dev_server_command("rust", str(tmp_path)) == "cargo run"
    assert get_dev_server_command("dotnet", str(tmp_path)) == "dotnet run"


def test_get_dev_server_command_detects_cpp_binaries(tmp_path: Path):
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    binary = build_dir / "main"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)

    assert get_dev_server_command("cpp_cmake", str(tmp_path)) == "./build/main"
