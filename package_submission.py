"""
Packages the clean MechEval submission zip file.
Excludes .venv, .git, cache files, and builds mecheval_submission.zip.
"""

import os
import zipfile

def package_submission(source_dir: str, zip_path: str):
    ignore_dirs = {".venv", ".git", "__pycache__", ".pytest_cache"}
    ignore_exts = {".pyc", ".pyo", ".log"}

    total_files = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ignore_exts:
                    continue
                if file.endswith("_submission.zip"):
                    continue

                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.dirname(source_dir))
                zf.write(abs_path, rel_path)
                total_files += 1

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"[+] Successfully created: {zip_path}")
    print(f"    - Included files: {total_files}")
    print(f"    - Archive size:   {size_mb:.2f} MB (Limit: 50.00 MB)")


if __name__ == "__main__":
    src = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    dest = os.path.abspath(os.path.join(src, "..", "mecheval_submission.zip"))
    package_submission(src, dest)
