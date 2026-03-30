import json
import sys

import main as pipeline_main
import pytest
import tools.file_tools as file_tools


def _code_block(text: str) -> str:
    return f"### `main.py`\n```python\n{text}\n```\n"


class _TrackingPlanner:
    plan_calls = 0
    plan_text = "plan"

    def __init__(self, *args, **kwargs):
        self.model = pipeline_main.config.MODELS["planner"]
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_api_calls = 0

    def plan(self, *args, **kwargs):
        type(self).plan_calls += 1
        self.total_input_tokens += 100
        self.total_output_tokens += 50
        self.total_api_calls += 1
        return type(self).plan_text


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
        self.model = pipeline_main.config.MODELS["coder"]
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_api_calls = 0

    def code(self, *args, **kwargs):
        type(self).code_calls += 1
        self.total_input_tokens += 120
        self.total_output_tokens += 60
        self.total_api_calls += 1
        return _code_block("print('initial')")

    def fix(self, previous_code, feedback, memory="", existing_files=""):
        type(self).fix_calls += 1
        type(self).feedbacks.append(feedback)
        self.total_input_tokens += 80
        self.total_output_tokens += 40
        self.total_api_calls += 1
        return _code_block("print('fixed')")


class _TrackingReviewer:
    review_calls = 0

    def __init__(self, *args, **kwargs):
        self.model = pipeline_main.config.MODELS["reviewer"]
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_api_calls = 0

    def review(self, *args, **kwargs):
        type(self).review_calls += 1
        self.total_input_tokens += 40
        self.total_output_tokens += 20
        self.total_api_calls += 1
        return {"approved": True, "score": 8, "summary": "Review ok", "issues": []}


class _TrackingTester:
    test_calls = 0

    def __init__(self, *args, **kwargs):
        self.model = pipeline_main.config.MODELS["tester"]
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_api_calls = 0

    def test(self, *args, **kwargs):
        type(self).test_calls += 1
        self.total_input_tokens += 25
        self.total_output_tokens += 10
        self.total_api_calls += 1
        return {"passed": True, "issues": [], "summary": "ok"}


class _TrackingCommitter:
    summarize_calls = 0

    def __init__(self, *args, **kwargs):
        self.model = pipeline_main.config.MODELS["committer"]
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_api_calls = 0

    def summarize(self, *args, **kwargs):
        type(self).summarize_calls += 1
        self.total_input_tokens += 15
        self.total_output_tokens += 5
        self.total_api_calls += 1
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

    assert result["success"] is True
    assert result["tokens"]["api_calls"] == 0
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

    assert result["success"] is True
    assert result["tokens"]["api_calls"] == 3
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
    _TrackingPlanner.plan_text = "## İlgili Dosyalar\n- RELEVANT: `src/helper.py` — helper\n"
    monkeypatch.setattr(pipeline_main, "PlannerAgent", _TrackingPlanner)
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
    _TrackingPlanner.plan_text = "plan"
    monkeypatch.setattr(pipeline_main, "PlannerAgent", _TrackingPlanner)
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

    assert result["success"] is True
    assert result["tokens"]["input"] == 275
    assert result["tokens"]["output"] == 135
    assert result["tokens"]["api_calls"] == 4
    assert result["tokens"]["cost_usd"] > 0
    assert _TrackingCommitter.summarize_calls == 1
    assert appended_entries == [("## Task Tamamlandı: Memory Task\n- AI summary", "memory summarize")]


def test_main_writes_pipeline_report_with_token_totals(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setattr(pipeline_main.config, "API_KEY", "test-key")
    monkeypatch.setattr(pipeline_main.config, "AUTO_INSTALL", False)
    monkeypatch.setattr(pipeline_main.config, "AUTO_DEV_SERVER", False)
    monkeypatch.setattr(pipeline_main.config, "LOGS_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline_main, "print_header", lambda: None)
    monkeypatch.setattr(pipeline_main, "print_task_list", lambda tasks: None)
    monkeypatch.setattr(pipeline_main, "read_memory", lambda: "memory")
    monkeypatch.setattr(
        file_tools,
        "read_todolist",
        lambda: [{"task": "Task A", "done": False, "line": 0}],
    )
    monkeypatch.setattr(
        pipeline_main,
        "get_pending_tasks",
        lambda: [{"task": "Task A"}],
    )
    monkeypatch.setattr(
        pipeline_main,
        "run_single_task",
        lambda **kwargs: {
            "success": True,
            "tokens": {
                "input": 1200,
                "output": 300,
                "api_calls": 4,
                "total": 1500,
                "cost_usd": 0.0081,
                "models": {
                    pipeline_main.config.MODELS["coder"]: {
                        "input": 1200,
                        "output": 300,
                        "api_calls": 4,
                        "total": 1500,
                        "cost_usd": 0.0081,
                    }
                },
            },
            "log_file": "/tmp/task-a.md",
        },
    )
    monkeypatch.setattr(sys, "argv", ["main.py"])

    pipeline_main.main()

    report_files = list(tmp_path.glob("pipeline_report_*.json"))
    assert len(report_files) == 1

    report = json.loads(report_files[0].read_text(encoding="utf-8"))
    assert report["tasks"][0]["name"] == "Task A"
    assert report["totals"]["success"] == 1
    assert report["totals"]["failed"] == 0
    assert report["totals"]["tokens"]["input"] == 1200
    assert report["totals"]["tokens"]["output"] == 300
    assert report["totals"]["tokens"]["api_calls"] == 4
    assert report["totals"]["cost_usd"] == 0.0081
