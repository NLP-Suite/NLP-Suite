"""Phase 0 bundle smoke test for the CustomTkinter migration (docs/CustomTkinter-Migration-Plan.md).

GO / NO-GO gate: does CustomTkinter -- and specifically the PIL.ImageTk path used by CTkImage --
actually work under the interpreter that ships in the NLP Suite installer (python-build-standalone)?
That interpreter has historically broken Tk-adjacent image handling: it is the reason
GUI_util.tk_image_from_pil exists, and it is what crashed the matplotlib 'TkAgg' backend (fixed by
falling back to 'Agg').

RESULT (2026-07-15, macOS aarch64, cpython-3.10.15 python-build-standalone): raw CTkImage FAILS
under the bundle exactly as predicted -- `TypeError: bad argument type for built-in operation` from
PIL.ImageTk. The fix is ctk_bundle_util.patch_ctk_image_for_bundle(), which routes CTkImage's Tk
image construction through the same base64-PNG path as GUI_util.tk_image_from_pil. This test applies
that patch and verifies CTkImage then works, so the gate now checks the SHIPPING approach (patched).
Without the patch the CTkImage check fails -- see docs/CustomTkinter-Migration-Plan.md §5.1.

IMPORTANT: run this INSIDE the frozen bundle / with the BUNDLED interpreter (python-build-standalone),
not just a dev Anaconda env -- a dev env passing tells you nothing about the bundle. It needs a real
display (a GUI session), so it is NOT a headless pytest unit test (the filename has no test_ prefix /
_test suffix on purpose, so pytest won't collect it).

Usage:  <bundled-python> tests/ctk_bundle_smoke.py
Exit code 0 = PASS (all checks), non-zero = FAIL. Prints a per-check report.
"""
# Standalone runtime probe: customtkinter/ctk_bundle_util are optional and loaded via a runtime
# sys.path insert, and _ctk is a deliberately None-initialised module global. None of that is
# statically resolvable, so scope off the two Pyright rules it trips.
# pyright: reportMissingImports=false, reportOptionalMemberAccess=false
import os
import sys

# Import the production shim from src/ without importing GUI_util (which builds a Tk root at import).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

_results = []
_root = None
_ctk = None


def _check(name, fn):
    try:
        fn()
        _results.append((name, True, ''))
        print('PASS  ' + name)
    except BaseException as e:   # BaseException: a Tcl/Tk failure can surface oddly
        _results.append((name, False, repr(e)))
        print('FAIL  ' + name + '  ->  ' + repr(e))


def _import_and_root():
    global _root, _ctk
    import customtkinter as ctk
    from ctk_bundle_util import patch_ctk_image_for_bundle
    if not patch_ctk_image_for_bundle():   # apply the bundle ImageTk workaround before any CTkImage
        raise RuntimeError('patch_ctk_image_for_bundle() reported CustomTkinter not importable')
    _ctk = ctk
    ctk.set_appearance_mode('light')
    _root = ctk.CTk()
    _root.geometry('320x220')
    _root.update()   # force the first render pass


def _basic_widgets():
    _ctk.CTkLabel(_root, text='smoke').pack()
    _ctk.CTkButton(_root, text='button').pack()
    om = _ctk.CTkOptionMenu(_root, values=['alpha', 'beta'])
    om.pack()
    om.set('beta')                       # OptionMenu repopulation path (a known migration gotcha)
    _ctk.CTkFrame(_root).pack()
    _root.update()


def _ctk_image():
    # THE risk: CTkImage -> PIL.ImageTk, which python-build-standalone breaks. Passes only because
    # patch_ctk_image_for_bundle() (applied in _import_and_root) reroutes it through base64 PNG.
    from PIL import Image
    img = Image.new('RGB', (16, 16), (200, 30, 30))
    cimg = _ctk.CTkImage(light_image=img, dark_image=img, size=(16, 16))
    _ctk.CTkLabel(_root, text='', image=cimg).pack()
    _root.update()


def _appearance_toggle():
    _ctk.set_appearance_mode('dark')
    _root.update()
    _ctk.set_appearance_mode('light')
    _root.update()


def _teardown():
    if _root is not None:
        _root.destroy()


def main():
    print('CustomTkinter bundle smoke test — interpreter: ' + sys.version.split()[0])
    _check('import customtkinter + create CTk root', _import_and_root)
    if _root is not None:
        _check('basic CTk widgets render (Label/Button/OptionMenu/Frame)', _basic_widgets)
        _check('CTkImage (patched: base64-PNG path, the python-build-standalone risk)', _ctk_image)
        _check('appearance mode light<->dark toggle', _appearance_toggle)
        _check('teardown (destroy root)', _teardown)
    ok = bool(_results) and all(p for _, p, _ in _results)
    print('\n=== Phase 0 CustomTkinter bundle smoke test: ' + ('PASS' if ok else 'FAIL') + ' ===')
    if not ok:
        print('Failing checks:')
        for name, passed, err in _results:
            if not passed:
                print('  - ' + name + ': ' + err)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
