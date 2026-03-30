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

    file_tools.save_state("task one", "coder", {"plan": "plan", "code": "code", "attempt": 2})

    loaded = file_tools.load_state("task one")

    assert loaded["task"] == "task one"
    assert loaded["step"] == "coder"
    assert loaded["plan"] == "plan"
    assert loaded["code"] == "code"
    assert loaded["attempt"] == 2


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
