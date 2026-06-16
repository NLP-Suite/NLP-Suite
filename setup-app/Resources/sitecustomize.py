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
