# Purpose: Evaluate Apti v2 model artifacts and write reports.
# Callers: Manual evaluation and retrain pipeline.
# Deps: argparse, joblib, pandas, sklearn, fairness/topn helpers.
# API: evaluate_model.
# Side effects: Writes evaluation and fairness report JSON files.

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

from fairness_checks import build_fairness_report
from topn_metrics import mean_reciprocal_rank, top_n_accuracy

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = REPO_ROOT / "backend" / "ml" / "data" / "processed" / "apti_training_v2.csv"
MODEL_PATH = REPO_ROOT / "backend" / "ml" / "models" / "apti_group_model_v2.pkl"
ENCODER_PATH = REPO_ROOT / "backend" / "ml" / "models" / "apti_label_encoder_group_v2.pkl"
EVAL_REPORT_PATH = REPO_ROOT / "backend" / "ml" / "experiments" / "apti_eval_report_v2.json"
FAIRNESS_REPORT_PATH = REPO_ROOT / "backend" / "ml" / "experiments" / "apti_fairness_report_v2.json"
TARGET = "target_kelompok_prodi"
DROP_COLUMNS = {"sample_id", "target_prodi", "target_prodi_id", "target_cluster", TARGET}


def evaluate_model(dataset: Path = DEFAULT_DATASET) -> dict[str, object]:
    df = pd.read_csv(dataset)
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    y = label_encoder.transform(df[TARGET])
    x = df.drop(columns=[TARGET])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
    del x_train, y_train
    pred = model.predict(x_test)
    proba = model.predict_proba(x_test)
    y_true_labels = label_encoder.inverse_transform(y_test).tolist()
    pred_labels = label_encoder.inverse_transform(pred).tolist()
    classes = label_encoder.classes_.tolist()
    report = {
        "rows_evaluated": len(x_test),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "macro_f1": round(float(f1_score(y_test, pred, average="macro", zero_division=0)), 4),
        "top3_kelompok_accuracy": top_n_accuracy(y_true_labels, classes, proba, 3),
        "top5_kelompok_accuracy": top_n_accuracy(y_true_labels, classes, proba, 5),
        "mean_reciprocal_rank": mean_reciprocal_rank(y_true_labels, classes, proba),
        "classes": classes,
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "specific_prodi_metrics": {
            "top3_prodi_accuracy": None,
            "top5_prodi_accuracy": None,
            "top10_prodi_accuracy": None,
            "note": "Specific prodi ranking is deterministic hybrid scoring, not this group classifier output.",
        },
    }
    fairness = build_fairness_report(x_test.assign(**{TARGET: y_true_labels}).to_dict("records"), pred_labels)
    EVAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    FAIRNESS_REPORT_PATH.write_text(json.dumps(fairness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"eval_report": str(EVAL_REPORT_PATH), "fairness_report": str(FAIRNESS_REPORT_PATH), "metrics": report, "fairness": fairness}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-version", default="apti_v2")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    print(json.dumps(evaluate_model(args.dataset), ensure_ascii=False, indent=2))
