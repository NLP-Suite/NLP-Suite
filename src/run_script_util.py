import os
import sys
import shutil
from subprocess import call


def _is_frozen():
    return getattr(sys, 'frozen', False)


def _find_python():
    """Find a usable Python interpreter, even inside a PyInstaller bundle."""
    if not _is_frozen():
        return sys.executable

    # 1. Check for bundled portable Python (shipped with the PyInstaller dist)
    bundle_dir = os.path.dirname(sys.executable)
    if sys.platform == 'win32':
        bundled = os.path.join(bundle_dir, 'python-env', 'Scripts', 'python.exe')
    else:
        bundled = os.path.join(bundle_dir, 'python-env', 'bin', 'python3')
    if os.path.isfile(bundled):
        return bundled

    # 2. Check CONDA_PREFIX (set by the Mac Setup app or conda activate)
    conda_prefix = os.environ.get('CONDA_PREFIX', '')
    if conda_prefix:
        if sys.platform == 'win32':
            cp = os.path.join(conda_prefix, 'python.exe')
        else:
            cp = os.path.join(conda_prefix, 'bin', 'python3')
        if os.path.isfile(cp):
            return cp

    # 3. Check PATH (skip Windows Store alias)
    for name in ('python3', 'python'):
        found = shutil.which(name)
        if found:
            if 'WindowsApps' in found:
                continue
            return found

    # 4. Check common Anaconda/Miniconda locations
    home = os.path.expanduser('~')
    conda_candidates = [
        os.path.join(home, 'AppData', 'Local', 'anaconda3', 'envs', 'NLP', 'python.exe'),
        os.path.join(home, 'AppData', 'Local', 'anaconda3', 'python.exe'),
        os.path.join(home, 'anaconda3', 'envs', 'NLP', 'python.exe'),
        os.path.join(home, 'anaconda3', 'python.exe'),
        os.path.join(home, 'miniconda3', 'envs', 'NLP', 'python.exe'),
        os.path.join(home, 'miniconda3', 'python.exe'),
    ]
    if sys.platform != 'win32':
        conda_candidates.extend([
            os.path.join(home, 'anaconda3', 'envs', 'NLP', 'bin', 'python3'),
            os.path.join(home, 'anaconda3', 'bin', 'python3'),
            os.path.join(home, 'miniconda3', 'envs', 'NLP', 'bin', 'python3'),
            os.path.join(home, 'miniconda3', 'bin', 'python3'),
        ])
    for candidate in conda_candidates:
        if os.path.isfile(candidate):
            return candidate

    return None


def _script_dir():
    """Return the directory containing the NLP Suite .py scripts."""
    if _is_frozen():
        bundle_dir = os.path.dirname(sys.executable)
        src = os.path.join(bundle_dir, 'src')
        if os.path.isdir(src):
            return src
        internal_src = os.path.join(bundle_dir, '_internal', 'src')
        if os.path.isdir(internal_src):
            return internal_src
    return os.path.dirname(os.path.abspath(__file__))


def run_script(script_name, *extra_args):
    """Launch an NLP Suite .py script as a subprocess.

    In normal Python: uses sys.executable (the interpreter).
    In a PyInstaller bundle: locates system Python and the bundled .py files.

    script_name: bare filename like "NLP_menu_main.py"
    extra_args:  additional command-line arguments passed to the script
    """
    python = _find_python()
    src_dir = _script_dir()
    script_path = os.path.join(src_dir, script_name)

    if python is None:
        import tkinter.messagebox as mb
        mb.showerror(title='Python not found',
                     message='Could not find a Python interpreter on this system.\n\n'
                             'Please install Python 3.10+ and make sure it is on your PATH.')
        return 1

    if not os.path.isfile(script_path):
        import tkinter.messagebox as mb
        mb.showerror(title='Script not found',
                     message=f'Could not find the script:\n{script_path}\n\n'
                             'The NLP Suite installation may be incomplete.')
        return 1

    cmd = [python, script_path] + list(extra_args)
    return call(cmd)
