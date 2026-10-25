"""Retrieval evaluation.

Ingests data/sample into a clean database, runs every question in
eval/cases.json through retrieve(), and reports hit@1, hit@3 and MRR
(did the expected document appear, and how high?).

    python -m eval.run                 # prints a report
    python -m eval.run --min-hit3 0.9  # exits 1 if hit@3 is below the bar (used in CI)
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import config  # noqa: E402
import db  # noqa: E402
import rag  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-hit3", type=float, default=0.0)
    args = parser.parse_args()

    db.open_pool()
    try:
        with db.get_pool().connection() as conn:
            conn.execute("TRUNCATE chunks, documents RESTART IDENTITY CASCADE")
        for path in sorted((ROOT / "data" / "sample").glob("*.md")):
            rag.ingest_document(path.name, path.read_text(encoding="utf-8"))

        cases = json.loads((ROOT / "eval" / "cases.json").read_text())
        hit1 = hit3 = 0
        rr_sum = 0.0
        misses = []
        for case in cases:
            titles = [p["title"] for p in rag.retrieve(case["question"], args.top_k)]
            rank = next(
                (i for i, t in enumerate(titles, 1) if t == case["expected_title"]), None
            )
            if rank:
                rr_sum += 1 / rank
                hit3 += 1
                hit1 += rank == 1
            else:
                misses.append(case["question"])

        n = len(cases)
        print(f"provider={config.EMBEDDING_PROVIDER} cases={n}")
        print(f"hit@1={hit1 / n:.2f}  hit@3={hit3 / n:.2f}  MRR={rr_sum / n:.2f}")
        for q in misses:
            print(f"  MISS: {q}")
        return 0 if hit3 / n >= args.min_hit3 else 1
    finally:
        db.close_pool()


if __name__ == "__main__":
    raise SystemExit(main())
