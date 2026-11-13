"""Package the research app without local credentials, databases or environments."""
from pathlib import Path
import os
import zipfile

root = Path(__file__).resolve().parent.parent
target = root.parent / "Candidate-Lab-Source.zip"
excluded = {".venv", "node_modules", "data", "models", "tmp", "__pycache__", ".pytest_cache", ".test-tmp", "test-results", "playwright-report", ".git"}
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in excluded]
        for name in files:
            path = Path(folder) / name
            if name == ".env" or name.endswith((".log", ".pyc", ".db", ".zip")):
                continue
            archive.write(path, Path("candidate-lab") / path.relative_to(root))
print(target)
print(f"{target.stat().st_size:,} bytes")
