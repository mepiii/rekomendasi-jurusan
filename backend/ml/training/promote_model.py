# Purpose: Promote Apti v2 model only when evaluation and fairness thresholds pass.
# Callers: Retrain pipeline and manual release flow.
# Deps: json, pathlib.
# API: can_promote.
# Side effects: Prints promotion decision when run as script.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EVAL_REPORT_PATH = REPO_ROOT / "backend" / "ml" / "experiments" / "apti_eval_report_v2.json"
FAIRNESS_REPORT_PATH = REPO_ROOT / "backend" / "ml" / "experiments" / "apti_fairness_report_v2.json"


def can_promote() -> dict[str, object]:
    eval_report = json.loads(EVAL_REPORT_PATH.read_text(encoding="utf-8"))
    fairness = json.loads(FAIRNESS_REPORT_PATH.read_text(encoding="utf-8"))
    passed = eval_report["top3_kelompok_accuracy"] >= 0.75 and eval_report["macro_f1"] >= 0.45 and fairness["passed"]
    return {"promote": passed, "criteria": {"top3_kelompok_accuracy_min": 0.75, "macro_f1_min": 0.45, "fairness_passed": True}, "observed": {"top3_kelompok_accuracy": eval_report["top3_kelompok_accuracy"], "macro_f1": eval_report["macro_f1"], "fairness_passed": fairness["passed"]}}


if __name__ == "__main__":
    print(json.dumps(can_promote(), ensure_ascii=False, indent=2))
