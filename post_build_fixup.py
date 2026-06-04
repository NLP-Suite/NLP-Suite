"""Post-build fixup for PyInstaller NLP Suite bundle.

PyInstaller places bundled Python packages in dist/NLP_Suite/_internal/,
but the NLP Suite code resolves paths relative to the exe root (dist/NLP_Suite/).
This script copies data directories and DLLs to the correct locations.

Usage:
    python post_build_fixup.py

Run this AFTER: python -m PyInstaller NLP_Suite.spec --noconfirm
"""

import os
import sys
import shutil
import glob

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'NLP_Suite')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def copy_tree(src, dst):
    """Copy a directory tree, creating dst if needed."""
    if not os.path.isdir(src):
        print(f"  SKIP (not found): {src}")
        return
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"  Copied: {src} -> {dst}")

def copy_files(src_pattern, dst_dir):
    """Copy files matching a glob pattern to dst_dir."""
    os.makedirs(dst_dir, exist_ok=True)
    files = glob.glob(src_pattern)
    for f in files:
        shutil.copy2(f, dst_dir)
    print(f"  Copied {len(files)} files to {dst_dir}")

def main():
    if not os.path.isdir(DIST_DIR):
        print(f"ERROR: dist directory not found: {DIST_DIR}")
        print("Run PyInstaller first: python -m PyInstaller NLP_Suite.spec --noconfirm")
        sys.exit(1)

    print(f"Post-build fixup for: {DIST_DIR}")
    print()

    # 1. Copy data directories to exe root
    print("=== Copying data directories ===")
    for dirname in ['lib', 'config', 'TIPS', 'reminders', 'src']:
        src = os.path.join(PROJECT_ROOT, dirname)
        dst = os.path.join(DIST_DIR, dirname)
        if dirname == 'src':
            # Only copy .py files for src
            os.makedirs(dst, exist_ok=True)
            py_files = glob.glob(os.path.join(src, '*.py'))
            for f in py_files:
                shutil.copy2(f, dst)
            print(f"  Copied {len(py_files)} .py files to {dst}")
        else:
            copy_tree(src, dst)

    # 2. Copy DLLs that PyInstaller misses (Windows only)
    if sys.platform == 'win32':
        print()
        print("=== Copying missing DLLs (Windows) ===")
        python_dir = os.path.dirname(sys.executable)
        dll_names = ['tk86t.dll', 'tcl86t.dll', 'sqlite3.dll', 'liblzma.dll']
        for dll in dll_names:
            for root, dirs, files in os.walk(python_dir):
                if dll in files:
                    src = os.path.join(root, dll)
                    shutil.copy2(src, DIST_DIR)
                    print(f"  Copied: {dll}")
                    break

        # Copy tcl/tk library directories
        print()
        print("=== Copying tcl/tk libraries ===")
        tcl_base = os.path.join(python_dir, 'tcl')
        for subdir in ['tcl8.6', 'tk8.6']:
            src = os.path.join(tcl_base, subdir)
            if os.path.isdir(src):
                dst = os.path.join(DIST_DIR, subdir.split('8')[0], subdir)
                copy_tree(src, dst)

    print()
    total_mb = sum(os.path.getsize(os.path.join(dp, f))
                   for dp, dn, fn in os.walk(DIST_DIR) for f in fn) / (1024*1024)
    print(f"=== Done! Total bundle size: {total_mb:.0f} MB ===")
    print(f"Executable: {os.path.join(DIST_DIR, 'NLP_Suite.exe')}")

if __name__ == '__main__':
    main()
