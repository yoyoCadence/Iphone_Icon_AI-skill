#!/usr/bin/env python3
"""Fail if any held-out test term (evals/heldout.txt) appears in what a run of the skill can read.

Validation runs on real projects are only a test while the skill has never seen their answers.
Run before every validation round:  python3 evals/check_heldout.py
"""
import re, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
terms = [t.strip().lower() for t in (root / "evals/heldout.txt").read_text(encoding="utf-8").splitlines()
         if t.strip() and not t.startswith("#")]
files = [root / "SKILL.md", *sorted((root / "references").glob("*.md")),
         root / "assets/examples/README.md", *sorted((root / "scripts").glob("*.*"))]
hits = []
for f in files:
    for n, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        low = line.lower()
        for t in terms:
            if re.search(r"(?<![a-z])" + re.escape(t) if t[0].isalpha() else re.escape(t), low):
                hits.append(f"{f.relative_to(root)}:{n}: '{t}' — {line.strip()[:90]}")
print("\n".join(hits) if hits else "clean: no held-out terms in the skill")
sys.exit(1 if hits else 0)
