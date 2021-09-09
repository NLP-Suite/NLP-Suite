from add_shortcut import remove, get_env, set_env
import os
from pathlib import Path

paths = get_env('Path').split(';')
remove(paths, '')
path = Path(os.path.dirname(os.path.abspath(__file__))).parent
path_setup = path / 'setup_Windows'
print(path)
remove(paths, os.path.abspath(path))
remove(paths, os.path.abspath(path_setup))
print(get_env('Path'))
set_env('Path', ';'.join(paths))
