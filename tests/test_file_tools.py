from pathlib import Path

import config
import pytest
from tools import file_tools


def test_save_code_files_saves_single_file(tmp_path: Path):
    coder_output = """## Dosyalar

### `src/app.py`
```python
print("hello")
```
"""

    saved = file_tools.save_code_files(coder_output, workspace_dir=str(tmp_path))

    target = tmp_path / "src" / "app.py"
    assert saved == [str(target)]
    assert target.read_text(encoding="utf-8") == 'print("hello")\n'


def test_save_code_files_returns_empty_list_for_empty_output(tmp_path: Path):
    saved = file_tools.save_code_files("", workspace_dir=str(tmp_path))

    assert saved == []


def test_save_code_files_blocks_writing_outside_workspace(tmp_path: Path):
    coder_output = """### `../escape.py`
```python
print("nope")
```
"""

    saved = file_tools.save_code_files(coder_output, workspace_dir=str(tmp_path))

    assert saved == []
    assert not (tmp_path.parent / "escape.py").exists()


def test_save_code_files_saves_multiple_files(tmp_path: Path):
    coder_output = """### `a.py`
```python
print("a")
```

### `nested/b.py`
```python
print("b")
```
"""

    saved = file_tools.save_code_files(coder_output, workspace_dir=str(tmp_path))

    assert len(saved) == 2
    assert (tmp_path / "a.py").exists()
    assert (tmp_path / "nested" / "b.py").exists()


def test_save_code_files_preserves_nested_markdown_fences(tmp_path: Path):
    coder_output = """### `README.md`
```md
# Example

```python
print("hello")
```

More text.
```
"""

    saved = file_tools.save_code_files(coder_output, workspace_dir=str(tmp_path))
    content = (tmp_path / "README.md").read_text(encoding="utf-8")

    assert len(saved) == 1
    assert '```python' in content
    assert 'print("hello")' in content
    assert "More text." in content


def test_read_workspace_files_returns_empty_string_for_empty_dir(tmp_path: Path):
    result = file_tools.read_workspace_files(workspace_dir=str(tmp_path))

    assert result == ""


def test_read_workspace_files_respects_context_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config, "MAX_WORKSPACE_CONTEXT_CHARS", 80)
    monkeypatch.setattr(config, "MAX_FILE_SIZE", 1000)

    (tmp_path / "a.py").write_text("print('a')\n" * 3, encoding="utf-8")
    (tmp_path / "b.py").write_text("print('b')\n" * 3, encoding="utf-8")

    result = file_tools.read_workspace_files(workspace_dir=str(tmp_path))

    assert "context limiti nedeniyle atlandı" in result


def test_read_workspace_files_prioritizes_config_files(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"name":"demo"}', encoding="utf-8")
    (tmp_path / "src.py").write_text("print('app')\n", encoding="utf-8")

    result = file_tools.read_workspace_files(workspace_dir=str(tmp_path))

    assert result.index("### `package.json`") < result.index("### `src.py`")


def test_read_workspace_files_ignores_ignored_directories(tmp_path: Path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.js").write_text("console.log('x')", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('ok')", encoding="utf-8")

    result = file_tools.read_workspace_files(workspace_dir=str(tmp_path))

    assert "ignored.js" not in result
    assert "src/main.py" in result


def test_read_workspace_files_includes_cpp_and_makefiles(tmp_path: Path):
    (tmp_path / "CMakeLists.txt").write_text("project(Demo)\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (tmp_path / "include").mkdir()
    (tmp_path / "include" / "demo.hpp").write_text("#pragma once\n", encoding="utf-8")

    result = file_tools.read_workspace_files(workspace_dir=str(tmp_path))

    assert "### `CMakeLists.txt`" in result
    assert "### `src/main.cpp`" in result
    assert "### `include/demo.hpp`" in result
    assert result.index("### `CMakeLists.txt`") < result.index("### `src/main.cpp`")


def test_read_workspace_files_ignores_language_build_dirs(tmp_path: Path):
    for dirname in ("target", "vendor", "cmake-build-debug"):
        path = tmp_path / dirname
        path.mkdir()
        (path / "ignored.txt").write_text("ignored", encoding="utf-8")

    (tmp_path / "Cargo.toml").write_text("[package]\nname='demo'\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.rs").write_text("fn main() {}\n", encoding="utf-8")

    result = file_tools.read_workspace_files(workspace_dir=str(tmp_path))

    assert "ignored.txt" not in result
    assert "Cargo.toml" in result
    assert "src/main.rs" in result


def test_read_specific_files_reads_only_requested_entries(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('main')\n", encoding="utf-8")
    (tmp_path / "src" / "helper.py").write_text("print('helper')\n", encoding="utf-8")

    result = file_tools.read_specific_files(["src/helper.py"], workspace_dir=str(tmp_path))

    assert "src/helper.py" in result
    assert "src/main.py" not in result


def test_append_memory_entry_wraps_and_truncates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    memory_file = tmp_path / "memory.md"
    memory_file.write_text("# Project Memory\n\n## Project Overview\n- Demo\n", encoding="utf-8")
    monkeypatch.setattr(config, "MEMORY_FILE", str(memory_file))
    monkeypatch.setattr(config, "MAX_MEMORY_LINES", 8)

    file_tools.append_memory_entry("- Short AI summary", fallback_task="AI Task")

    content = memory_file.read_text(encoding="utf-8")

    assert "## Task Tamamlandı: AI Task" in content
    assert "- Short AI summary" in content


def test_read_todolist_parses_tasks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    todo = tmp_path / "todolist.md"
    todo.write_text("- [ ] First task\n- [x] Done task\n", encoding="utf-8")
    monkeypatch.setattr(config, "TODOLIST_FILE", str(todo))

    tasks = file_tools.read_todolist()

    assert [task["task"] for task in tasks] == ["First task", "Done task"]


def test_read_todolist_marks_done_and_pending(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    todo = tmp_path / "todolist.md"
    todo.write_text("- [x] Done\n- [ ] Pending\n", encoding="utf-8")
    monkeypatch.setattr(config, "TODOLIST_FILE", str(todo))

    tasks = file_tools.read_todolist()

    assert tasks[0]["done"] is True
    assert tasks[1]["done"] is False


def test_read_todolist_raises_when_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    missing = tmp_path / "missing.md"
    monkeypatch.setattr(config, "TODOLIST_FILE", str(missing))

    with pytest.raises(FileNotFoundError):
        file_tools.read_todolist()


def test_save_and_load_state_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_file = tmp_path / ".pipeline_state.json"
    monkeypatch.setattr(file_tools, "STATE_FILE", str(state_file))

    file_tools.save_state(
        "task one",
        "coder",
        {"plan": "plan", "code": "code", "attempt": 2, "review_summary": "ok"},
    )

    loaded = file_tools.load_state("task one")

    assert loaded["task"] == "task one"
    assert loaded["step"] == "coder"
    assert loaded["plan"] == "plan"
    assert loaded["code"] == "code"
    assert loaded["attempt"] == 2
    assert loaded["review_summary"] == "ok"


def test_load_state_returns_none_for_different_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_file = tmp_path / ".pipeline_state.json"
    monkeypatch.setattr(file_tools, "STATE_FILE", str(state_file))
    file_tools.save_state("task one", "planner", {"plan": "plan"})

    loaded = file_tools.load_state("task two")

    assert loaded is None


def test_clear_state_removes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_file = tmp_path / ".pipeline_state.json"
    monkeypatch.setattr(file_tools, "STATE_FILE", str(state_file))
    file_tools.save_state("task one", "planner", {"plan": "plan"})

    file_tools.clear_state()

    assert not state_file.exists()


def test_update_memory_truncates_old_task_blocks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    memory_file = tmp_path / "memory.md"
    memory_file.write_text(
        "# Project Memory\n\n"
        "## Project Overview\n"
        "- Name: Demo\n\n"
        "## Task Tamamlandı: Old 1\n"
        "- Tarih: 2026-03-31 00:01\n"
        "- Dosyalar: a.py\n\n"
        "## Task Tamamlandı: Old 2\n"
        "- Tarih: 2026-03-31 00:02\n"
        "- Dosyalar: b.py\n\n"
        "## Task Tamamlandı: Old 3\n"
        "- Tarih: 2026-03-31 00:03\n"
        "- Dosyalar: c.py\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config, "MEMORY_FILE", str(memory_file))
    monkeypatch.setattr(config, "WORKSPACE_DIR", str(tmp_path))
    monkeypatch.setattr(config, "MAX_MEMORY_LINES", 12)

    file_tools.update_memory("New Task", [str(tmp_path / "src" / "main.py")])

    content = memory_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    assert len(lines) <= 12
    assert "# Project Memory" in content
    assert "## Project Overview" in content
    assert "## Task Tamamlandı: New Task" in content
    assert "## Task Tamamlandı: Old 1" not in content
    assert "Eski kayıtlar kırpıldı" in content
