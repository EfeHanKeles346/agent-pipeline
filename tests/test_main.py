import main as pipeline_main
import pytest


def _code_block(text: str) -> str:
    return f"### `main.py`\n```python\n{text}\n```\n"


class _UnexpectedPlanner:
    def __init__(self, *args, **kwargs):
        pass

    def plan(self, *args, **kwargs):
        raise AssertionError("Planner çalışmamalıydı")


class _TrackingCoder:
    code_calls = 0
    fix_calls = 0
    feedbacks = []

    def __init__(self, *args, **kwargs):
        pass

    def code(self, *args, **kwargs):
        type(self).code_calls += 1
        return _code_block("print('initial')")

    def fix(self, previous_code, feedback, memory="", existing_files=""):
        type(self).fix_calls += 1
        type(self).feedbacks.append(feedback)
        return _code_block("print('fixed')")


class _TrackingReviewer:
    review_calls = 0

    def __init__(self, *args, **kwargs):
        pass

    def review(self, *args, **kwargs):
        type(self).review_calls += 1
        return {"approved": True, "score": 8, "summary": "Review ok", "issues": []}


class _TrackingTester:
    test_calls = 0

    def __init__(self, *args, **kwargs):
        pass

    def test(self, *args, **kwargs):
        type(self).test_calls += 1
        return {"passed": True, "issues": [], "summary": "ok"}


class _TrackingCommitter:
    summarize_calls = 0

    def __init__(self, *args, **kwargs):
        pass

    def summarize(self, *args, **kwargs):
        type(self).summarize_calls += 1
        return {
            "memory_entry": "## Task Tamamlandı: Memory Task\n- AI summary",
            "important_patterns": ["Use shared helper"],
        }


def test_run_single_task_resumes_from_build_step(monkeypatch: pytest.MonkeyPatch):
    save_steps = []
    build_calls = []

    monkeypatch.setattr(
        pipeline_main,
        "load_state",
        lambda task: {
            "task": task,
            "step": "build",
            "plan": "saved plan",
            "code": _code_block("print('saved')"),
            "review_summary": "Saved review",
        },
    )
    monkeypatch.setattr(pipeline_main, "PlannerAgent", _UnexpectedPlanner)
    monkeypatch.setattr(pipeline_main, "CoderAgent", _TrackingCoder)
    monkeypatch.setattr(pipeline_main, "ReviewerAgent", _TrackingReviewer)
    monkeypatch.setattr(pipeline_main, "TesterAgent", _TrackingTester)
    monkeypatch.setattr(pipeline_main, "read_workspace_files", lambda: "")
    monkeypatch.setattr(pipeline_main, "save_code_files", lambda code: ["/tmp/main.py"])
    monkeypatch.setattr(pipeline_main, "save_state", lambda task, step, data: save_steps.append(step))
    monkeypatch.setattr(pipeline_main, "clear_state", lambda: None)
    monkeypatch.setattr(pipeline_main, "mark_task_done", lambda task: None)
    monkeypatch.setattr(pipeline_main, "update_memory", lambda task, files: None)
    monkeypatch.setattr(pipeline_main, "write_log", lambda task, log: None)
    monkeypatch.setattr(pipeline_main, "auto_install_dependencies", lambda: None)
    monkeypatch.setattr(pipeline_main, "detect_project_type", lambda: "python")
    monkeypatch.setattr(pipeline_main, "get_build_command", lambda project_type: "python -m compileall -q .")
    monkeypatch.setattr(
        pipeline_main,
        "run_command",
        lambda *args, **kwargs: build_calls.append(args[0]) or {"success": True, "stdout": "", "stderr": "", "returncode": 0},
    )
    monkeypatch.setattr(pipeline_main.config, "SEND_WORKSPACE_CONTEXT", False)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_TESTER", False)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_COMMITTER", False)

    _TrackingCoder.code_calls = 0
    _TrackingCoder.fix_calls = 0
    _TrackingReviewer.review_calls = 0

    result = pipeline_main.run_single_task(
        task_info={"task": "resume build"},
        task_number=1,
        total_tasks=1,
        memory="",
        auto_install=False,
    )

    assert result is True
    assert _TrackingCoder.code_calls == 0
    assert _TrackingReviewer.review_calls == 0
    assert build_calls == ["python -m compileall -q ."]
    assert "tester" in save_steps


def test_run_single_task_uses_build_feedback_loop(monkeypatch: pytest.MonkeyPatch):
    save_steps = []
    build_results = [
        {"success": False, "stdout": "", "stderr": "SyntaxError: invalid syntax", "returncode": 1},
        {"success": True, "stdout": "", "stderr": "", "returncode": 0},
    ]

    monkeypatch.setattr(pipeline_main, "load_state", lambda task: None)
    monkeypatch.setattr(
        pipeline_main,
        "PlannerAgent",
        type("Planner", (), {"plan": lambda self, **kwargs: "plan", "__init__": lambda self: None}),
    )
    monkeypatch.setattr(pipeline_main, "CoderAgent", _TrackingCoder)
    monkeypatch.setattr(pipeline_main, "ReviewerAgent", _TrackingReviewer)
    monkeypatch.setattr(pipeline_main, "TesterAgent", _TrackingTester)
    monkeypatch.setattr(pipeline_main, "read_workspace_files", lambda: "")
    monkeypatch.setattr(pipeline_main, "save_code_files", lambda code: ["/tmp/main.py"])
    monkeypatch.setattr(pipeline_main, "save_state", lambda task, step, data: save_steps.append(step))
    monkeypatch.setattr(pipeline_main, "clear_state", lambda: None)
    monkeypatch.setattr(pipeline_main, "mark_task_done", lambda task: None)
    monkeypatch.setattr(pipeline_main, "update_memory", lambda task, files: None)
    monkeypatch.setattr(pipeline_main, "write_log", lambda task, log: None)
    monkeypatch.setattr(pipeline_main, "auto_install_dependencies", lambda: None)
    monkeypatch.setattr(pipeline_main, "detect_project_type", lambda: "python")
    monkeypatch.setattr(pipeline_main, "get_build_command", lambda project_type: "python -m compileall -q .")
    monkeypatch.setattr(
        pipeline_main,
        "run_command",
        lambda *args, **kwargs: build_results.pop(0),
    )
    monkeypatch.setattr(pipeline_main.config, "SEND_WORKSPACE_CONTEXT", False)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_TESTER", False)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_COMMITTER", False)
    monkeypatch.setattr(pipeline_main.config, "MAX_REVIEW_ATTEMPTS", 1)
    monkeypatch.setattr(pipeline_main.config, "MAX_BUILD_RETRIES", 1)

    _TrackingCoder.code_calls = 0
    _TrackingCoder.fix_calls = 0
    _TrackingCoder.feedbacks = []
    _TrackingReviewer.review_calls = 0

    result = pipeline_main.run_single_task(
        task_info={"task": "build loop"},
        task_number=1,
        total_tasks=1,
        memory="",
        auto_install=False,
    )

    assert result is True
    assert _TrackingCoder.code_calls == 1
    assert _TrackingCoder.fix_calls == 1
    assert "Build hatası: python" in _TrackingCoder.feedbacks[0]
    assert "SyntaxError: invalid syntax" in _TrackingCoder.feedbacks[0]
    assert save_steps.count("build") >= 1
    assert "tester" in save_steps


def test_extract_relevant_files_from_plan():
    plan = """
## İlgili Dosyalar
- RELEVANT: `src/main.py` — ana akış burada
- RELEVANT: config.py — ayarlar burada
"""

    result = pipeline_main._extract_relevant_files_from_plan(plan)

    assert result == ["src/main.py", "config.py"]


def test_normalize_review_result_adds_missing_regression_check():
    review_result = {
        "approved": True,
        "score": 8,
        "summary": "ok",
        "issues": [],
    }

    normalized = pipeline_main._normalize_review_result(review_result)

    assert normalized["regression_check"]["checked"] is False
    assert normalized["regression_check"]["regressions_found"] == []


def test_normalize_review_result_promotes_regressions_to_issues():
    review_result = {
        "approved": True,
        "score": 8,
        "summary": "ok",
        "issues": [],
        "regression_check": {
            "checked": True,
            "files_compared": ["src/main.py"],
            "regressions_found": [{"file": "src/main.py", "description": "Removed validation"}],
        },
    }

    normalized = pipeline_main._normalize_review_result(review_result)

    assert normalized["approved"] is False
    assert normalized["issues"][0]["severity"] == "critical"
    assert normalized["issues"][0]["file"] == "src/main.py"


def test_run_single_task_uses_relevant_context_for_coder(monkeypatch: pytest.MonkeyPatch):
    coder_contexts = []

    class _CoderWithContext(_TrackingCoder):
        def code(self, plan, memory="", existing_files=""):
            coder_contexts.append(existing_files)
            return _code_block("print('initial')")

    monkeypatch.setattr(pipeline_main, "load_state", lambda task: None)
    monkeypatch.setattr(
        pipeline_main,
        "PlannerAgent",
        type(
            "Planner",
            (),
            {
                "__init__": lambda self: None,
                "plan": lambda self, **kwargs: "## İlgili Dosyalar\n- RELEVANT: `src/helper.py` — helper\n",
            },
        ),
    )
    monkeypatch.setattr(pipeline_main, "CoderAgent", _CoderWithContext)
    monkeypatch.setattr(pipeline_main, "ReviewerAgent", _TrackingReviewer)
    monkeypatch.setattr(pipeline_main, "TesterAgent", _TrackingTester)
    monkeypatch.setattr(pipeline_main, "read_workspace_files", lambda: "FULL CONTEXT")
    monkeypatch.setattr(pipeline_main, "read_specific_files", lambda files: "RELEVANT CONTEXT")
    monkeypatch.setattr(pipeline_main, "save_code_files", lambda code: ["/tmp/main.py"])
    monkeypatch.setattr(pipeline_main, "save_state", lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline_main, "clear_state", lambda: None)
    monkeypatch.setattr(pipeline_main, "mark_task_done", lambda task: None)
    monkeypatch.setattr(pipeline_main, "update_memory", lambda task, files: None)
    monkeypatch.setattr(pipeline_main, "append_memory_entry", lambda entry, fallback_task=None: None)
    monkeypatch.setattr(pipeline_main, "write_log", lambda task, log: None)
    monkeypatch.setattr(pipeline_main, "auto_install_dependencies", lambda: None)
    monkeypatch.setattr(pipeline_main, "detect_project_type", lambda: "unknown")
    monkeypatch.setattr(pipeline_main, "get_build_command", lambda project_type: None)
    monkeypatch.setattr(pipeline_main.config, "SEND_WORKSPACE_CONTEXT", True)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_TESTER", False)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_COMMITTER", False)
    monkeypatch.setattr(pipeline_main.config, "MAX_REVIEW_ATTEMPTS", 1)

    pipeline_main.run_single_task(
        task_info={"task": "relevant context"},
        task_number=1,
        total_tasks=1,
        memory="",
        auto_install=False,
    )

    assert coder_contexts == ["RELEVANT CONTEXT"]


def test_run_single_task_uses_committer_memory_summary(monkeypatch: pytest.MonkeyPatch):
    appended_entries = []

    monkeypatch.setattr(pipeline_main, "load_state", lambda task: None)
    monkeypatch.setattr(
        pipeline_main,
        "PlannerAgent",
        type("Planner", (), {"plan": lambda self, **kwargs: "plan", "__init__": lambda self: None}),
    )
    monkeypatch.setattr(pipeline_main, "CoderAgent", _TrackingCoder)
    monkeypatch.setattr(pipeline_main, "ReviewerAgent", _TrackingReviewer)
    monkeypatch.setattr(pipeline_main, "TesterAgent", _TrackingTester)
    monkeypatch.setattr(pipeline_main, "CommitterAgent", _TrackingCommitter)
    monkeypatch.setattr(pipeline_main, "read_workspace_files", lambda: "")
    monkeypatch.setattr(pipeline_main, "read_specific_files", lambda files: "")
    monkeypatch.setattr(pipeline_main, "save_code_files", lambda code: ["/workspace/main.py"])
    monkeypatch.setattr(pipeline_main, "save_state", lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline_main, "clear_state", lambda: None)
    monkeypatch.setattr(pipeline_main, "mark_task_done", lambda task: None)
    monkeypatch.setattr(pipeline_main, "update_memory", lambda task, files: (_ for _ in ()).throw(AssertionError("fallback kullanılmamalı")))
    monkeypatch.setattr(pipeline_main, "append_memory_entry", lambda entry, fallback_task=None: appended_entries.append((entry, fallback_task)))
    monkeypatch.setattr(pipeline_main, "write_log", lambda task, log: None)
    monkeypatch.setattr(pipeline_main, "auto_install_dependencies", lambda: None)
    monkeypatch.setattr(pipeline_main, "detect_project_type", lambda: "unknown")
    monkeypatch.setattr(pipeline_main, "get_build_command", lambda project_type: None)
    monkeypatch.setattr(pipeline_main.config, "SEND_WORKSPACE_CONTEXT", False)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_TESTER", False)
    monkeypatch.setattr(pipeline_main.config, "ENABLE_COMMITTER", True)
    monkeypatch.setattr(pipeline_main.config, "MAX_REVIEW_ATTEMPTS", 1)

    _TrackingCommitter.summarize_calls = 0

    result = pipeline_main.run_single_task(
        task_info={"task": "memory summarize"},
        task_number=1,
        total_tasks=1,
        memory="",
        auto_install=False,
    )

    assert result is True
    assert _TrackingCommitter.summarize_calls == 1
    assert appended_entries == [("## Task Tamamlandı: Memory Task\n- AI summary", "memory summarize")]
