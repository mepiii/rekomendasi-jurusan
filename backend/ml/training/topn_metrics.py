# Purpose: Compute top-N and ranking metrics for Apti model evaluation.
# Callers: evaluate_model.py and train_model.py.
# Deps: numpy.
# API: top_n_accuracy, mean_reciprocal_rank.
# Side effects: None.

from __future__ import annotations

import numpy as np


def top_n_accuracy(y_true: list[str], classes: list[str], probabilities: np.ndarray, n: int) -> float:
    top_indices = np.argsort(probabilities, axis=1)[:, -n:]
    hits = sum(label in {classes[index] for index in row} for label, row in zip(y_true, top_indices))
    return round(hits / len(y_true), 4) if y_true else 0.0


def mean_reciprocal_rank(y_true: list[str], classes: list[str], probabilities: np.ndarray) -> float:
    rankings = np.argsort(probabilities, axis=1)[:, ::-1]
    scores = []
    for label, row in zip(y_true, rankings):
        ordered = [classes[index] for index in row]
        scores.append(1 / (ordered.index(label) + 1) if label in ordered else 0)
    return round(float(np.mean(scores)), 4) if scores else 0.0
