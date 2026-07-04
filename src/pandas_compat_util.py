# pandas_compat_util.py
#
# Compatibility shim for the pandas.read_csv / read_table "bad lines" keyword.
#
# The kwarg that tells pandas to skip malformed csv rows changed across versions:
#     pandas <  1.3  ->  error_bad_lines=False, warn_bad_lines=False
#     pandas >= 1.3  ->  on_bad_lines='skip'      (error_bad_lines / warn_bad_lines removed in pandas 2.0)
#
# The NLP Suite source uses on_bad_lines='skip' in ~150 places across ~49 files. On an older
# pandas (e.g. the 1.2.x that ships in some Anaconda environments) every one of those calls raises
# "read_csv() got an unexpected keyword argument 'on_bad_lines'", which silently breaks csv reading.
#
# Importing this module ONCE, early in start-up, transparently rewrites on_bad_lines to the legacy
# keywords so every read_csv call keeps working regardless of the installed pandas version.
# On pandas >= 1.3 this module does nothing (on_bad_lines is native). The patch is idempotent and
# tolerates pandas not being importable yet (e.g. a fresh install before packages are installed).


def _install():
    try:
        import pandas as pd
    except Exception:
        # pandas not importable yet (fresh install, before install_all_Python_packages runs)
        return

    if getattr(pd, '_nlp_on_bad_lines_shim', False):
        return  # already handled this session

    try:
        ver = tuple(int(x) for x in pd.__version__.split('.')[:2])
    except Exception:
        return

    if ver >= (1, 3):
        pd._nlp_on_bad_lines_shim = True  # native support, nothing to patch
        return

    def _translate(kwargs):
        if 'on_bad_lines' in kwargs:
            val = kwargs.pop('on_bad_lines')
            if val == 'skip':
                kwargs.setdefault('error_bad_lines', False)
                kwargs.setdefault('warn_bad_lines', False)
            elif val == 'warn':
                kwargs.setdefault('error_bad_lines', False)
                kwargs.setdefault('warn_bad_lines', True)
            elif val == 'error':
                kwargs.setdefault('error_bad_lines', True)
        return kwargs

    def _make(orig, name):
        def _wrapped(*args, **kwargs):
            return orig(*args, **_translate(kwargs))
        _wrapped.__name__ = getattr(orig, '__name__', name)
        _wrapped.__doc__ = getattr(orig, '__doc__', None)
        return _wrapped

    for _name in ('read_csv', 'read_table'):
        _orig = getattr(pd, _name, None)
        if _orig is not None:
            setattr(pd, _name, _make(_orig, _name))

    pd._nlp_on_bad_lines_shim = True


_install()
