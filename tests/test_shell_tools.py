from pathlib import Path

from tools.shell_tools import detect_project_type


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
