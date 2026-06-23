#!/usr/bin/env python3

import argparse
import ast
import importlib.util
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


CRITICAL_MODULES = [
    "tkinter",
    "numpy",
    "pandas",
    "matplotlib",
    "openpyxl",
    "plotly",
    "seaborn",
    "requests",
    "psutil",
]

IGNORED_DECLARATIONS = {"__main__"}

# Top-level imports across src/ that are intentionally NOT present in the bundled
# environment, so the scan must not report them as missing:
#   - Legacy Python 2 / Windows-only modules.
#   - The SRL stack (transformer_srl + allennlp): SRL runs in its own isolated Python
#     3.8 conda env set up via setup_SRL.py (transformer-srl pins torch 1.7 / allennlp /
#     spaCy 2.x). transformer_srl is imported only by SRL_worker.py, which runs in that
#     separate env - never in the bundled python-env.
IGNORED_SOURCE_IMPORTS = {
    "urllib2",  # Legacy Python 2 script.
    "win32con",
    "win32gui",
    "winreg",
    "transformer_srl",  # SRL: separate Python 3.8 env via setup_SRL.py
    "allennlp",         # SRL dependency, same separate env
}


def declared_modules(source_directory):
    modules = set()
    parse_errors = []
    if not source_directory.is_dir():
        return modules, ["Source directory is missing."]

    for source_file in source_directory.glob("*.py"):
        try:
            tree = ast.parse(source_file.read_text(encoding="utf-8-sig"), filename=str(source_file))
        except Exception as error:
            parse_errors.append(f"{source_file.name}: {error}")
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function_name = ""
            if isinstance(node.func, ast.Name):
                function_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                function_name = node.func.attr
            if function_name != "install_all_Python_packages":
                continue
            for argument in node.args:
                if not isinstance(argument, (ast.List, ast.Tuple)):
                    continue
                values = []
                for element in argument.elts:
                    if isinstance(element, ast.Constant) and isinstance(element.value, str):
                        values.append(element.value)
                if values:
                    modules.update(values)

    return modules, parse_errors


def imported_modules(source_directory):
    modules = set()
    parse_errors = []
    local_modules = {path.stem for path in source_directory.glob("*.py")}
    standard_modules = set(getattr(sys, "stdlib_module_names", ()))

    for source_file in source_directory.glob("*.py"):
        try:
            tree = ast.parse(source_file.read_text(encoding="utf-8-sig"), filename=str(source_file))
        except Exception as error:
            parse_errors.append(f"{source_file.name}: {error}")
            continue

        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module.split(".", 1)[0]]

            for name in names:
                if (
                    name not in local_modules
                    and name not in standard_modules
                    and name not in IGNORED_SOURCE_IMPORTS
                ):
                    modules.add(name)

    return modules, parse_errors


def module_available(module):
    try:
        return importlib.util.find_spec(module) is not None, ""
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"


def import_check(module):
    code = """
import importlib
import json
import sys
import traceback

module_name = sys.argv[1]
try:
    imported = importlib.import_module(module_name)
    version = getattr(imported, "__version__", "")
    print(json.dumps({"ok": True, "version": str(version), "error": ""}))
except Exception:
    lines = traceback.format_exc().strip().splitlines()
    print(json.dumps({"ok": False, "version": "", "error": lines[-1] if lines else "Import failed"}))
"""
    environment = os.environ.copy()
    environment["PYTHONNOUSERSITE"] = "1"
    environment.setdefault("MPLCONFIGDIR", f"/tmp/nlp-suite-launcher-mpl-{os.getuid()}")
    try:
        completed = subprocess.run(
            [sys.executable, "-c", code, module],
            capture_output=True,
            text=True,
            timeout=30,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return {"module": module, "ok": False, "version": "", "error": "Import timed out after 30 seconds"}

    output_lines = completed.stdout.strip().splitlines()
    if output_lines:
        try:
            result = json.loads(output_lines[-1])
            return {"module": module, **result}
        except json.JSONDecodeError:
            pass

    error = completed.stderr.strip().splitlines()
    message = error[-1] if error else f"Import process exited with status {completed.returncode}"
    return {"module": module, "ok": False, "version": "", "error": message}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    arguments = parser.parse_args()

    suite_directory = Path(arguments.suite).expanduser().resolve()
    source_directory = suite_directory / "src"
    checks = [import_check(module) for module in CRITICAL_MODULES]

    declared = set()
    parse_errors = []
    missing = []
    lookup_errors = {}
    declared, parse_errors = declared_modules(source_directory)
    imported, import_parse_errors = imported_modules(source_directory)
    declared.update(imported)
    parse_errors.extend(import_parse_errors)
    declared.difference_update(IGNORED_DECLARATIONS)
    for module in sorted(declared):
        available, error = module_available(module)
        if not available:
            missing.append(module)
            if error:
                lookup_errors[module] = error

    report = {
        "python": sys.executable,
        "pythonVersion": platform.python_version(),
        "architecture": platform.machine(),
        "suite": str(suite_directory),
        "checks": checks,
        "declaredCount": len(declared),
        "declaredMissing": missing,
        "lookupErrors": lookup_errors,
        "parseErrors": parse_errors,
    }
    print(json.dumps(report))


if __name__ == "__main__":
    main()
