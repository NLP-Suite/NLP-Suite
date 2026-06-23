import importlib.abc
import importlib.machinery
import os
import sys


class PackageCheckLoader(importlib.abc.Loader):
    def __init__(self, loader):
        self.loader = loader

    def create_module(self, spec):
        create = getattr(self.loader, "create_module", None)
        return create(spec) if create else None

    def exec_module(self, module):
        self.loader.exec_module(module)
        module.install_all_Python_packages = lambda window, calling_script, modules: True


class PackageCheckFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name != "IO_libraries_util":
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec and spec.loader:
            spec.loader = PackageCheckLoader(spec.loader)
        return spec


if os.environ.get("NLP_SUITE_SKIP_PACKAGE_CHECKS") == "1":
    sys.meta_path.insert(0, PackageCheckFinder())

    # The old frozen binary calls subprocess.check_output(["pip", "freeze"]) with no
    # try/except to detect TensorFlow. When launched from the Setup app, pip finds no
    # tensorflow-macos/metal, shows an outdated "reinstall Anaconda" warning, and then
    # opens a browser tab — burying the NLP Suite window behind the browser so it
    # appears to have closed. Intercept that specific call and report
    # tensorflow-macos as present so the check passes silently.
    # (This mirrors what the pip shim in Launch NLP Suite (Mac).command does.)
    import subprocess as _subprocess
    _real_check_output = _subprocess.check_output

    def _check_output_shim(cmd, *args, **kwargs):
        try:
            cmd_list = list(cmd) if not isinstance(cmd, str) else cmd.split()
            if (any("pip" in str(c) for c in cmd_list)
                    and any(c == "freeze" for c in cmd_list)):
                return b"tensorflow-macos==2.12.0\n"
        except Exception:
            pass
        return _real_check_output(cmd, *args, **kwargs)

    _subprocess.check_output = _check_output_shim
