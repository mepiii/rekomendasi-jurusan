# Purpose: Generate synthetic training dataset for major recommendation model.
# Callers: Manual CLI execution before model training.
# Deps: numpy, pandas.
# API: python ml/dataset_generator.py --rows N --output path.
# Side effects: Writes CSV dataset to disk.

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import json

import numpy as np
import pandas as pd

SUBJECTS = [
    "math",
    "physics",
    "chemistry",
    "biology",
    "economics",
    "indonesian",
    "english",
]

INTERESTS = [
    "Teknologi",
    "Data & AI",
    "Rekayasa",
    "Sosial/Manusia",
    "Komunikasi",
    "Hukum/Politik",
    "Alam/Kesehatan",
    "Bisnis/Manajemen",
    "Seni/Kreatif",
    "Pendidikan/Bahasa",
]

SMA_TRACKS = ["IPA", "IPS", "Bahasa", "Merdeka"]
SEMESTERS = range(1, 7)
PERSONAS = {
    "steady_high": {"offset": 5, "drift": 0.6, "noise": 4},
    "late_bloomer": {"offset": -2, "drift": 1.8, "noise": 5},
    "early_peak": {"offset": 4, "drift": -0.8, "noise": 5},
    "spiky_specialist": {"offset": 0, "drift": 0.4, "noise": 8},
    "adversarial_interest": {"offset": 1, "drift": 0.1, "noise": 7},
}

MAJOR_LABELS = [
    "Teknik Informatika",
    "Sistem Informasi",
    "Teknik Sipil",
    "Teknik Elektro",
    "Kedokteran",
    "Farmasi",
    "Biologi",
    "Matematika",
    "Psikologi",
    "Ilmu Komunikasi",
    "Hukum",
    "Pendidikan Bahasa Inggris",
    "Manajemen",
    "Akuntansi",
    "Desain Komunikasi Visual",
]

MAJOR_CLUSTER = {
    "Teknik Informatika": "STEM",
    "Sistem Informasi": "STEM",
    "Teknik Sipil": "STEM",
    "Teknik Elektro": "STEM",
    "Kedokteran": "Health",
    "Farmasi": "Health",
    "Biologi": "Health",
    "Matematika": "STEM",
    "Psikologi": "Social",
    "Ilmu Komunikasi": "Social",
    "Hukum": "Social",
    "Pendidikan Bahasa Inggris": "Social",
    "Manajemen": "Business",
    "Akuntansi": "Business",
    "Desain Komunikasi Visual": "Arts",
}


@dataclass(frozen=True)
class MajorRule:
    base: Dict[str, int]
    primary_interests: List[str]
    secondary_interests: List[str]
    preferred_track: str


MAJOR_RULES: Dict[str, MajorRule] = {
    "Teknik Informatika": MajorRule(
        base={"math": 88, "physics": 84, "chemistry": 74, "biology": 62, "economics": 66, "indonesian": 74, "english": 81},
        primary_interests=["Teknologi", "Data & AI"],
        secondary_interests=["Rekayasa", "Bisnis/Manajemen"],
        preferred_track="IPA",
    ),
    "Sistem Informasi": MajorRule(
        base={"math": 83, "physics": 74, "chemistry": 68, "biology": 60, "economics": 80, "indonesian": 76, "english": 82},
        primary_interests=["Teknologi", "Bisnis/Manajemen"],
        secondary_interests=["Data & AI", "Komunikasi"],
        preferred_track="IPA",
    ),
    "Teknik Sipil": MajorRule(
        base={"math": 86, "physics": 85, "chemistry": 73, "biology": 58, "economics": 62, "indonesian": 72, "english": 74},
        primary_interests=["Rekayasa", "Teknologi"],
        secondary_interests=["Alam/Kesehatan", "Data & AI"],
        preferred_track="IPA",
    ),
    "Teknik Elektro": MajorRule(
        base={"math": 89, "physics": 88, "chemistry": 76, "biology": 56, "economics": 60, "indonesian": 70, "english": 78},
        primary_interests=["Rekayasa", "Teknologi"],
        secondary_interests=["Data & AI", "Alam/Kesehatan"],
        preferred_track="IPA",
    ),
    "Kedokteran": MajorRule(
        base={"math": 80, "physics": 75, "chemistry": 88, "biology": 92, "economics": 58, "indonesian": 74, "english": 78},
        primary_interests=["Alam/Kesehatan"],
        secondary_interests=["Sosial/Manusia", "Pendidikan/Bahasa"],
        preferred_track="IPA",
    ),
    "Farmasi": MajorRule(
        base={"math": 79, "physics": 72, "chemistry": 90, "biology": 87, "economics": 60, "indonesian": 73, "english": 77},
        primary_interests=["Alam/Kesehatan"],
        secondary_interests=["Teknologi", "Data & AI"],
        preferred_track="IPA",
    ),
    "Biologi": MajorRule(
        base={"math": 74, "physics": 70, "chemistry": 82, "biology": 91, "economics": 57, "indonesian": 75, "english": 74},
        primary_interests=["Alam/Kesehatan"],
        secondary_interests=["Pendidikan/Bahasa", "Sosial/Manusia"],
        preferred_track="IPA",
    ),
    "Matematika": MajorRule(
        base={"math": 94, "physics": 82, "chemistry": 72, "biology": 58, "economics": 66, "indonesian": 70, "english": 76},
        primary_interests=["Data & AI", "Teknologi"],
        secondary_interests=["Rekayasa", "Pendidikan/Bahasa"],
        preferred_track="IPA",
    ),
    "Psikologi": MajorRule(
        base={"math": 68, "physics": 60, "chemistry": 64, "biology": 72, "economics": 78, "indonesian": 84, "english": 79},
        primary_interests=["Sosial/Manusia"],
        secondary_interests=["Komunikasi", "Alam/Kesehatan"],
        preferred_track="IPS",
    ),
    "Ilmu Komunikasi": MajorRule(
        base={"math": 62, "physics": 54, "chemistry": 58, "biology": 63, "economics": 77, "indonesian": 89, "english": 84},
        primary_interests=["Komunikasi"],
        secondary_interests=["Sosial/Manusia", "Seni/Kreatif"],
        preferred_track="IPS",
    ),
    "Hukum": MajorRule(
        base={"math": 66, "physics": 55, "chemistry": 57, "biology": 60, "economics": 82, "indonesian": 88, "english": 80},
        primary_interests=["Hukum/Politik"],
        secondary_interests=["Sosial/Manusia", "Komunikasi"],
        preferred_track="IPS",
    ),
    "Pendidikan Bahasa Inggris": MajorRule(
        base={"math": 61, "physics": 52, "chemistry": 56, "biology": 60, "economics": 72, "indonesian": 82, "english": 92},
        primary_interests=["Pendidikan/Bahasa"],
        secondary_interests=["Komunikasi", "Sosial/Manusia"],
        preferred_track="Bahasa",
    ),
    "Manajemen": MajorRule(
        base={"math": 74, "physics": 60, "chemistry": 61, "biology": 58, "economics": 90, "indonesian": 78, "english": 83},
        primary_interests=["Bisnis/Manajemen"],
        secondary_interests=["Komunikasi", "Data & AI"],
        preferred_track="IPS",
    ),
    "Akuntansi": MajorRule(
        base={"math": 82, "physics": 62, "chemistry": 60, "biology": 57, "economics": 92, "indonesian": 76, "english": 80},
        primary_interests=["Bisnis/Manajemen", "Data & AI"],
        secondary_interests=["Hukum/Politik", "Sosial/Manusia"],
        preferred_track="IPS",
    ),
    "Desain Komunikasi Visual": MajorRule(
        base={"math": 58, "physics": 51, "chemistry": 55, "biology": 61, "economics": 70, "indonesian": 85, "english": 81},
        primary_interests=["Seni/Kreatif"],
        secondary_interests=["Komunikasi", "Pendidikan/Bahasa"],
        preferred_track="Bahasa",
    ),
}

INTEREST_COLUMN_MAP = {
    "Teknologi": "interest_tech",
    "Data & AI": "interest_data_ai",
    "Rekayasa": "interest_engineering",
    "Sosial/Manusia": "interest_social",
    "Komunikasi": "interest_communication",
    "Hukum/Politik": "interest_law_politics",
    "Alam/Kesehatan": "interest_nature_health",
    "Bisnis/Manajemen": "interest_business",
    "Seni/Kreatif": "interest_arts",
    "Pendidikan/Bahasa": "interest_education_language",
}


def _sample_track(preferred_track: str, rng: np.random.Generator) -> str:
    pool = [preferred_track] * 7 + [t for t in SMA_TRACKS if t != preferred_track] * 2
    return rng.choice(pool)


def _sample_persona(rng: np.random.Generator) -> str:
    return str(rng.choice(list(PERSONAS), p=[0.24, 0.24, 0.18, 0.24, 0.10]))


def _subject_trend(values: List[float]) -> float:
    xs = np.array(list(SEMESTERS), dtype=float)
    ys = np.array(values, dtype=float)
    denominator = float(((xs - xs.mean()) ** 2).sum())
    if denominator == 0:
        return 0.0
    slope = float(((xs - xs.mean()) * (ys - ys.mean())).sum() / denominator)
    return round(float(np.clip(slope / 10, -1, 1)), 3)


def _sample_semester_scores(base: Dict[str, int], persona: str, rng: np.random.Generator) -> Dict[str, float]:
    config = PERSONAS[persona]
    record: Dict[str, float] = {}
    for subject, center in base.items():
        anchor = center + config["offset"] + rng.normal(0, config["noise"])
        semester_values = []
        for semester in SEMESTERS:
            drift = (semester - 3.5) * config["drift"]
            value = float(np.clip(anchor + drift + rng.normal(0, config["noise"] / 2), 25, 100))
            record[f"s{semester}_{subject}"] = round(value, 2)
            semester_values.append(value)
        record[f"{subject}_trend"] = _subject_trend(semester_values)
        record[subject] = round(float(np.mean(semester_values)), 2)
    record["kelas_10_avg"] = round(float(np.mean([record[f"s{semester}_{subject}"] for semester in [1, 2] for subject in SUBJECTS])), 2)
    record["kelas_11_avg"] = round(float(np.mean([record[f"s{semester}_{subject}"] for semester in [3, 4] for subject in SUBJECTS])), 2)
    record["kelas_12_avg"] = round(float(np.mean([record[f"s{semester}_{subject}"] for semester in [5, 6] for subject in SUBJECTS])), 2)
    record["overall_gpa"] = round(record["kelas_10_avg"] * 0.2 + record["kelas_11_avg"] * 0.3 + record["kelas_12_avg"] * 0.5, 2)
    return record


def _sample_interests(rule: MajorRule, rng: np.random.Generator, persona: str = "steady_high") -> Dict[str, int]:
    flags = {column: 0 for column in INTEREST_COLUMN_MAP.values()}

    selected: List[str] = []
    selected.append(rng.choice(rule.primary_interests))

    if rng.random() < 0.7:
        selected.append(rng.choice(rule.secondary_interests))
    if rng.random() < 0.2:
        selected.append(rng.choice(rule.primary_interests))
    if rng.random() < 0.15:
        selected.append(rng.choice(INTERESTS))

    if rng.random() < 0.08 or persona == "adversarial_interest":
        selected = [rng.choice([interest for interest in INTERESTS if interest not in rule.primary_interests])]

    selected = list(dict.fromkeys(selected))[:4]

    for name in selected:
        flags[INTEREST_COLUMN_MAP[name]] = 1
    return flags


def _sample_scores(base: Dict[str, int], rng: np.random.Generator) -> Dict[str, float]:
    sampled: Dict[str, float] = {}
    for subject, center in base.items():
        noise = rng.normal(0, 8)
        sampled[subject] = float(np.clip(center + noise, 35, 100))

    if rng.random() < 0.15:
        dip_subject = rng.choice(SUBJECTS)
        sampled[dip_subject] = float(np.clip(sampled[dip_subject] - rng.uniform(8, 18), 25, 100))

    return sampled


def build_dataset(rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    per_label = rows // len(MAJOR_LABELS)
    remainder = rows % len(MAJOR_LABELS)

    records: List[Dict[str, object]] = []

    for index, major in enumerate(MAJOR_LABELS):
        count = per_label + (1 if index < remainder else 0)
        rule = MAJOR_RULES[major]

        for _ in range(count):
            persona = _sample_persona(rng)
            scores = _sample_semester_scores(rule.base, persona, rng)
            interest_flags = _sample_interests(rule, rng, persona)
            track = _sample_track(rule.preferred_track, rng)

            record: Dict[str, object] = {
                **scores,
                **interest_flags,
                "sma_track": track,
                "persona": persona,
                "major": major,
                "kelompok_prodi": major,
                "cluster": MAJOR_CLUSTER[major],
            }
            records.append(record)

    df = pd.DataFrame(records)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic dataset for major recommendation")
    parser.add_argument("--rows", type=int, default=20000, help="Number of rows to generate")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "data" / "training_dataset.csv",
        help="Output CSV path",
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = build_dataset(args.rows, args.seed)
    df.to_csv(args.output, index=False)
    metadata = {"rows": len(df), "labels": int(df["major"].nunique()), "personas": sorted(df["persona"].unique()), "has_semester_features": True}
    (args.output.parent / "training_dataset_v2_report.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"dataset_rows={len(df)}")
    print(f"output={args.output}")
    print(df["major"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
