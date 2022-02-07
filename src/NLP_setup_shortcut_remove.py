from NLP_setup_shortcut_add import remove, get_env, set_env
import os
from pathlib import Path

paths = get_env('Path').split(';')
remove(paths, '')
path = Path(os.path.dirname(os.path.abspath(__file__))).parent
path_setup = path / 'setup_Windows'
print("\n\nUPDATED SYSTEM ENVIRONMENT VARIABLES:\n\n",path,"\n\n")
remove(paths, os.path.abspath(path))
remove(paths, os.path.abspath(path_setup))
print(get_env('Path'),"\n\n")
set_env('Path', ';'.join(paths))
