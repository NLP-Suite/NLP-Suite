"""Tests for the anonymous, opt-in usage tracking in usage_util.

The promises under test: nothing is sent (and nobody is asked) unless a key is configured; the user is
asked once and the answer sticks; a "no" creates no ID; the ID is stable across launches; and events
carry only the GUI's file name, never a path.
"""

import json
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import usage_util  # noqa: E402

KEY_ENV = {"NLP_SUITE_POSTHOG_KEY": "phc_test"}


class _Recorder:
    """Stands in for the consent question and the network, recording every call."""

    def __init__(self, answer=True):
        self.answer = answer
        self.asked = 0
        self.sent = []

    def ask(self):
        self.asked += 1
        return self.answer

    def post(self, payload):
        self.sent.append(payload)


def _track(rec, path, environ=KEY_ENV, event="gui_opened", tool="wordclouds_main.py"):
    return usage_util.track(
        event, {"tool": tool}, environ=environ, state_path=str(path), ask=rec.ask, post=rec.post, background=False
    )


def test_no_key_means_no_question_and_nothing_sent(tmp_path, monkeypatch):
    monkeypatch.setattr(usage_util, "POSTHOG_PROJECT_KEY", "")
    rec = _Recorder()
    path = tmp_path / "usage.json"
    assert _track(rec, path, environ={}) is None
    assert rec.asked == 0 and rec.sent == []
    assert not path.exists()


def test_do_not_track_wins_over_a_configured_key(tmp_path):
    rec = _Recorder()
    for value in ("1", "true", "yes"):
        assert _track(rec, tmp_path / "usage.json", environ={**KEY_ENV, "DO_NOT_TRACK": value}) is None
    assert _track(rec, tmp_path / "usage.json", environ={**KEY_ENV, "NLP_SUITE_NO_TELEMETRY": "1"}) is None
    assert rec.asked == 0 and rec.sent == []


def test_do_not_track_zero_does_not_opt_out():
    assert not usage_util.opted_out_by_env({"DO_NOT_TRACK": "0"})
    assert not usage_util.opted_out_by_env({})


def test_yes_is_asked_once_and_the_id_is_stable(tmp_path):
    rec = _Recorder(answer=True)
    path = tmp_path / "usage.json"
    first = _track(rec, path)
    second = _track(rec, path, event="run_clicked")
    assert rec.asked == 1
    assert len(rec.sent) == 2
    assert first["distinct_id"] == second["distinct_id"]
    uuid.UUID(first["distinct_id"], version=4)  # raises if it is not a uuid4
    stored = json.loads(path.read_text())
    assert stored == {"consent": True, "install_id": first["distinct_id"]}


def test_no_is_remembered_and_creates_no_id(tmp_path):
    rec = _Recorder(answer=False)
    path = tmp_path / "usage.json"
    assert _track(rec, path) is None
    assert _track(rec, path) is None
    assert rec.asked == 1 and rec.sent == []
    assert json.loads(path.read_text()) == {"consent": False}


def test_corrupt_state_file_is_treated_as_fresh(tmp_path):
    path = tmp_path / "usage.json"
    path.write_text("{not json")
    assert usage_util.load_state(str(path)) == {}
    path.write_text("[1, 2]")
    assert usage_util.load_state(str(path)) == {}


def test_payload_has_only_the_file_name_and_anonymous_flags(tmp_path):
    rec = _Recorder()
    payload = _track(rec, tmp_path / "usage.json", tool=usage_util.tool_name("/Users/someone/NLP/src/SVO_main.py"))
    props = payload["properties"]
    assert payload["api_key"] == "phc_test"
    assert payload["event"] == "gui_opened"
    assert props["tool"] == "SVO_main.py"
    assert props["$process_person_profile"] is False
    assert props["$geoip_disable"] is True
    assert "someone" not in json.dumps(payload)


def test_tool_name_handles_empty_input():
    assert usage_util.tool_name("") == "unknown"
    assert usage_util.tool_name(None) == "unknown"


def test_a_network_failure_is_swallowed(tmp_path):
    def failing_post(payload):
        raise OSError("offline")

    payload = usage_util.track(
        "gui_opened",
        {},
        environ=KEY_ENV,
        state_path=str(tmp_path / "usage.json"),
        ask=lambda: True,
        post=failing_post,
        background=False,
    )
    assert payload is not None  # the event was built; the failure only printed to the console


def test_env_key_overrides_the_built_in_key(monkeypatch):
    monkeypatch.setattr(usage_util, "POSTHOG_PROJECT_KEY", "phc_builtin")
    assert usage_util.get_project_key({}) == "phc_builtin"
    assert usage_util.get_project_key({"NLP_SUITE_POSTHOG_KEY": " phc_env "}) == "phc_env"


def test_post_payload_targets_the_capture_endpoint(monkeypatch):
    seen = {}

    class _Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["body"] = json.loads(request.data)
        seen["timeout"] = timeout
        return _Response()

    monkeypatch.setattr(usage_util.urllib.request, "urlopen", fake_urlopen)
    assert usage_util.post_payload({"event": "x"}, host="https://eu.i.posthog.com/") == 200
    assert seen == {"url": "https://eu.i.posthog.com/capture/", "body": {"event": "x"}, "timeout": 5}
