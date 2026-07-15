"""CustomTkinter bundle compatibility shim (CTk migration — docs/CustomTkinter-Migration-Plan.md §5.1).

CTk's ``CTkImage`` builds its Tk image with ``PIL.ImageTk.PhotoImage``. Under the portable
python-build-standalone interpreter that ships in the NLP Suite installer, Tcl/Tk is *statically
embedded*, so the ``_imagingtk`` C bridge cannot attach and every ``PIL.ImageTk`` call crashes
(``TypeError: bad argument type for built-in operation`` / ``invalid command name "PyImagingPhoto"``).
This is the same root cause that ``GUI_util.tk_image_from_pil`` was written to solve for the plain
``tk.Label`` logo path, and the reason the matplotlib ``TkAgg`` backend had to fall back to ``Agg``.

``patch_ctk_image_for_bundle()`` monkeypatches the two ``CTkImage`` methods that touch ImageTk so
they hand Tk base64-encoded PNG bytes through the plain ``tk.PhotoImage(data=…)`` API instead —
Tk 8.6 decodes PNG natively, and PIL is used only to resize/encode, never touching ``_imagingtk``.
With the patch applied, ``CTkImage`` works under the bundle, so Phase 1+ can use CTk's native image
idiom instead of banning ``CTkImage`` outright.

Kept deliberately free of import-time side effects (no Tk root, no heavy imports) so the Phase 0
bundle smoke test can import it under the standalone interpreter. Call ``patch_ctk_image_for_bundle()``
once at startup, before any ``CTkImage`` is created.
"""
import base64
import io
import tkinter as tk

_patched = False


def _tk_photoimage_from_pil(pil_image):
    """Build a plain ``tk.PhotoImage`` from a PIL image via base64 PNG, bypassing ``PIL.ImageTk``.

    Mirror of ``GUI_util.tk_image_from_pil`` (kept local so this module imports without pulling in
    GUI_util's Tk-root import side effects; see module docstring). Keep a reference to the returned
    image — Tk does not.
    """
    if pil_image.mode not in ("RGB", "RGBA", "L", "LA", "P"):
        pil_image = pil_image.convert("RGBA")
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return tk.PhotoImage(data=base64.b64encode(buffer.getvalue()))


def patch_ctk_image_for_bundle():
    """Route ``CTkImage``'s Tk-image construction through the base64-PNG path (see module docstring).

    Idempotent. Returns True if the patch is in place, False if CustomTkinter is not importable.
    Raises RuntimeError if CTkImage is present but its internals differ from what we patch (so a
    CustomTkinter upgrade that moves these methods fails loudly at startup rather than crashing
    later inside the bundle).
    """
    global _patched
    if _patched:
        return True

    try:
        from customtkinter.windows.widgets.image.ctk_image import CTkImage
    except ImportError:
        return False

    if not (hasattr(CTkImage, "_get_scaled_light_photo_image")
            and hasattr(CTkImage, "_get_scaled_dark_photo_image")):
        raise RuntimeError(
            "ctk_bundle_util: CTkImage internals changed; the bundle ImageTk workaround needs "
            "updating (see docs/CustomTkinter-Migration-Plan.md §5.1)."
        )

    def _get_scaled_light_photo_image(self, scaled_size):
        if scaled_size not in self._scaled_light_photo_images:
            self._scaled_light_photo_images[scaled_size] = _tk_photoimage_from_pil(
                self._light_image.resize(scaled_size)
            )
        return self._scaled_light_photo_images[scaled_size]

    def _get_scaled_dark_photo_image(self, scaled_size):
        if scaled_size not in self._scaled_dark_photo_images:
            self._scaled_dark_photo_images[scaled_size] = _tk_photoimage_from_pil(
                self._dark_image.resize(scaled_size)
            )
        return self._scaled_dark_photo_images[scaled_size]

    CTkImage._get_scaled_light_photo_image = _get_scaled_light_photo_image
    CTkImage._get_scaled_dark_photo_image = _get_scaled_dark_photo_image
    _patched = True
    return True
