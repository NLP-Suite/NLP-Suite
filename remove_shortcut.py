from add_shortcut import remove, get_env, set_env
import os

paths = get_env('Path').split(';')
remove(paths, '')
remove(paths, os.path.dirname(os.path.abspath(__file__)))
set_env('Path', ';'.join(paths))
