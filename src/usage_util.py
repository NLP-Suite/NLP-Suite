"""Anonymous, opt-in usage tracking: which GUIs are opened and how often RUN is clicked.

Events go to PostHog (https://posthog.com) through its plain HTTP capture API, so the Suite needs no
extra package. Each install is identified only by a random ID (uuid4) kept in the user's home folder,
which is enough to tell one heavy user from many light ones without knowing who anyone is.

What is sent: the event name, the GUI's script name (e.g. "wordclouds_main.py"), the Suite release,
the operating system, and the Python version. What is never sent: names, file or folder paths, corpus
content, or the computer's user or host name.

Tracking happens only when ALL of these hold:
  1. a PostHog project key is configured (POSTHOG_PROJECT_KEY below, or the env var NLP_SUITE_POSTHOG_KEY);
  2. the user said yes to the one-time question (the answer is stored, so they are asked once per install);
  3. neither DO_NOT_TRACK nor NLP_SUITE_NO_TELEMETRY is set in the environment.
With the key emptied, every function here is a no-op and the user is never asked.

Sending runs in a background thread with a short timeout. A failure (offline, firewall, PostHog down) is
printed to the console and otherwise ignored, like the GitHub release check in GUI_util: usage counts are
not worth interrupting someone's analysis with a dialog.
"""

import json
import os
import platform
import sys
import threading
import urllib.request
import uuid

# PostHog's project key is designed to be public (it can only send events, not read them), so it is safe
# to ship in the code. Empty means tracking is off.
POSTHOG_PROJECT_KEY = "phc_p67xWvTnwQyhFzFfntzhQBbsGGRyrQ6acWwTjBKBNWUD"
POSTHOG_HOST = "https://us.i.posthog.com"

# Outside the repo, so the ID survives updates, re-clones and reinstalls of the Suite.
STATE_PATH = os.path.join(os.path.expanduser("~"), ".nlp_suite", "usage.json")

CONSENT_TITLE = "Help improve the NLP Suite"
CONSENT_MESSAGE = (
    "May the NLP Suite send anonymous usage counts to its developers?\n\n"
    "Sent: which tools you open, how often you click RUN, the Suite version, and your operating system, "
    "tagged with a random ID for this computer.\n\n"
    "Never sent: your name, your files or folder paths, or any of your texts. PostHog, the service that "
    "receives the counts, sees your computer's internet (IP) address, as any website does; the NLP Suite "
    "does not ask for it.\n\n"
    "You can change your mind at any time by deleting the file\n" + STATE_PATH
)


def get_project_key(environ=None):
    """The PostHog key to use, or '' when tracking is off. The env var wins, so testers can try it."""
    environ = os.environ if environ is None else environ
    return environ.get("NLP_SUITE_POSTHOG_KEY", "").strip() or POSTHOG_PROJECT_KEY


def opted_out_by_env(environ=None):
    """True when the environment asks for no tracking (DO_NOT_TRACK is a cross-tool convention)."""
    environ = os.environ if environ is None else environ
    for name in ("DO_NOT_TRACK", "NLP_SUITE_NO_TELEMETRY"):
        if environ.get(name, "").strip().lower() not in ("", "0", "false", "no"):
            return True
    return False


def load_state(path=STATE_PATH):
    """Read the stored state; a missing or corrupt file gives an empty state rather than an error."""
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
        return state if isinstance(state, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(state, path=STATE_PATH):
    """Write the state; returns False (and prints why) when the home folder is not writable."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f)
        return True
    except OSError as e:
        print("NLP Suite usage tracking: could not save " + path + ": " + str(e))  # noqa: T201
        return False


def ensure_install_id(state):
    """Return the install's anonymous ID, creating one in `state` the first time."""
    install_id = state.get("install_id")
    if not isinstance(install_id, str) or not install_id:
        install_id = str(uuid.uuid4())
        state["install_id"] = install_id
    return install_id


def tool_name(script_name):
    """'/x/y/wordclouds_main.py' -> 'wordclouds_main.py': only the file name, never the path."""
    return os.path.basename(str(script_name or "")) or "unknown"


def read_release_version(lib_dir=None):
    """The installed Suite release (lib/release_version.txt), or '' when it cannot be read."""
    if lib_dir is None:
        lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib")
    try:
        with open(os.path.join(lib_dir, "release_version.txt"), encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except OSError:
        return ""


def build_payload(project_key, install_id, event, properties=None):
    """The JSON body for PostHog's /capture/ endpoint.

    $process_person_profile=False keeps events anonymous (no person profile is built), and
    $geoip_disable=True stops PostHog from turning the request's IP address into a location.
    Unique-user counts still work, because they are counted from distinct_id.
    """
    props = {
        "release": read_release_version(),
        "os": platform.system(),
        "python": platform.python_version(),
        "frozen": bool(getattr(sys, "frozen", False)),  # True in the PyInstaller app
        "$process_person_profile": False,
        "$geoip_disable": True,
    }
    props.update(properties or {})
    return {"api_key": project_key, "event": event, "distinct_id": install_id, "properties": props}


def post_payload(payload, host=POSTHOG_HOST, timeout=5):
    """Send one event. Raises on failure; callers decide how quietly to handle it."""
    request = urllib.request.Request(
        host.rstrip("/") + "/capture/",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status


def ask_consent_tk():
    """The one-time yes/no question, shown with tkinter (imported here so tests never need a display)."""
    import tkinter.messagebox as mb

    return bool(mb.askyesno(title=CONSENT_TITLE, message=CONSENT_MESSAGE, default="no"))  # opt-in: Enter means No


def track(
    event,
    properties=None,
    *,
    environ=None,
    state_path=STATE_PATH,
    ask=ask_consent_tk,
    post=post_payload,
    background=True,
):
    """Record one event if tracking is allowed. Returns the payload it sent (or queued), else None.

    The keyword arguments exist so tests can substitute the environment, storage, question and network.
    """
    key = get_project_key(environ)
    if not key or opted_out_by_env(environ):
        return None

    state = load_state(state_path)
    changed = False
    if "consent" not in state:
        state["consent"] = bool(ask())
        changed = True
    if state.get("consent") is not True:
        if changed:
            save_state(state, state_path)  # remember the "no" so the question is not asked again
        return None

    # An ID is created only once someone has said yes.
    changed = changed or "install_id" not in state
    install_id = ensure_install_id(state)
    if changed:
        save_state(state, state_path)

    payload = build_payload(key, install_id, event, properties)

    def send():
        try:
            post(payload)
        except Exception as e:
            print("NLP Suite usage tracking: event not sent (" + type(e).__name__ + ": " + str(e) + ")")  # noqa: T201

    if background:
        threading.Thread(target=send, daemon=True).start()
    else:
        send()
    return payload


def track_gui_opened(script_name):
    """Called from GUI_util.GUI_top, which every GUI goes through once when it is built."""
    return track("gui_opened", {"tool": tool_name(script_name)})


def track_run_clicked(script_name):
    """Called when an enabled RUN button is clicked."""
    return track("run_clicked", {"tool": tool_name(script_name)})
