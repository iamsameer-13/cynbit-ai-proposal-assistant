"""Evaluate extraction + scoring on labelled sample inquiries.
Usage: python eval.py            (auto: LLM if key set)
       python eval.py --offline  (force heuristic baseline)"""
import json, sys
from pathlib import Path
import core

use_llm = False if "--offline" in sys.argv else None
data = json.loads((Path(__file__).parent / "data/sample_inquiries.json").read_text())
keys = {"service": 0, "urgency": 0, "band": 0, "budget_inr": 0}
for d in data:
    a = core.analyze(d["text"], use_llm)
    ok = {k: a.get(k) == d[k] for k in keys}
    for k, v in ok.items():
        keys[k] += v
    if not all(ok.values()):
        print(f"#{d['id']} miss:", {k: (a.get(k), d[k]) for k, v in ok.items() if not v})
print(f"\nExtractor: {a['source']}  (n={len(data)})")
for k, v in keys.items():
    print(f"{k:>10}: {v}/{len(data)} = {v/len(data):.0%}")
