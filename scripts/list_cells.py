"""Print cell indices, tags, and first line for each base notebook.

Helper for authoring persona override files.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

for f in [
    ROOT / "notebooks" / "01_simple_regression.ipynb",
    ROOT / "notebooks" / "02_deep_learning_regression.ipynb",
]:
    print(f"\n=== {f.name} ===")
    nb = json.loads(f.read_text(encoding="utf-8"))
    for i, c in enumerate(nb["cells"]):
        tags = c.get("metadata", {}).get("tags", [])
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        first = src.lstrip().split("\n", 1)[0][:70]
        print(f"  [{i:2d}] {str(tags):42s} {first}")
