from agents.base import BaseAgent


def make_agent() -> BaseAgent:
    agent = BaseAgent.__new__(BaseAgent)
    agent.name = "test-agent"
    return agent


def test_parse_json_response_from_json_fence():
    agent = make_agent()

    result = agent._parse_json_response('```json\n{"ok": true}\n```', {})

    assert result == {"ok": True}


def test_parse_json_response_from_generic_fence():
    agent = make_agent()

    result = agent._parse_json_response('```\n{"value": 3}\n```', {})

    assert result == {"value": 3}


def test_parse_json_response_from_plain_object():
    agent = make_agent()

    result = agent._parse_json_response('prefix {"status": "done"} suffix', {})

    assert result == {"status": "done"}


def test_parse_json_response_returns_default_on_invalid_input():
    agent = make_agent()

    default = {"passed": False}
    result = agent._parse_json_response("not valid json", default)

    assert result["passed"] is False
    assert result["raw_response"] == "not valid json"


def test_parse_json_response_preserves_default_fields():
    agent = make_agent()

    default = {"approved": False, "issues": []}
    result = agent._parse_json_response("```json\n{broken}\n```", default)

    assert result["approved"] is False
    assert result["issues"] == []
    assert "raw_response" in result
