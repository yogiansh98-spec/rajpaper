"""Conservative starter: validate existing catalog; do not publish unverified PDFs."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"data"/"papers.json"
data=json.loads(p.read_text(encoding="utf-8"))
assert isinstance(data,list)
for item in data:
    assert item.get("name") and item.get("pdf_url","").startswith("https://")
print(f"Validated {len(data)} paper entries. Official-source discovery pending.")
