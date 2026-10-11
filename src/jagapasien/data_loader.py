from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]


@dataclass
class DatasetBundle:
    candidates: pd.DataFrame
    pairs: pd.DataFrame
    patients: pd.DataFrame
    visits: pd.DataFrame
    files: Dict[str, Path]


def _iter_csv_files(directory: Path) -> Iterable[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".csv")


def _resolve_first_existing(directory: Path, names: List[str]) -> Optional[Path]:
    for name in names:
        path = directory / name
        if path.exists():
            return path
    return None


def choose_dataset_files(directory: Path = ROOT_DIR) -> Dict[str, Path]:
    files: Dict[str, Path] = {}
    alias_map = {
        "candidate": [
            "hasil_jagapasien_ai.csv",
            "hasil_jagapasien_ai(1).csv",
            "kandidat_review.csv",
            "kandidat_review(1).csv",
        ],
        "pairs": [
            "pasangan_kunjungan.csv",
            "pasangan_kunjungan(1).csv",
        ],
        "patients": [
            "pasien_sintetis.csv",
            "pasien_sintetis(1).csv",
        ],
        "visits": [
            "kunjungan_sintetis.csv",
            "kunjungan_sintetis(1).csv",
        ],
        "metadata": ["metadata.json"],
        "training_summary": ["ringkasan_training.json"],
    }

    for key, candidates in alias_map.items():
        resolved = _resolve_first_existing(directory, candidates)
        if resolved is not None:
            files[key] = resolved
    return files


def load_datasets(directory: Path = ROOT_DIR) -> DatasetBundle:
    files = choose_dataset_files(directory)
    missing = []
    for key in ["candidate", "pairs", "patients", "visits"]:
        if key not in files:
            missing.append(key)

    if missing:
        raise FileNotFoundError(
            "File data tidak lengkap. Pastikan file CSV berikut tersedia di workspace: "
            + ", ".join(missing)
        )

    candidates = pd.read_csv(files["candidate"])
    pairs = pd.read_csv(files["pairs"])
    patients = pd.read_csv(files["patients"])
    visits = pd.read_csv(files["visits"])

    return DatasetBundle(candidates=candidates, pairs=pairs, patients=patients, visits=visits, files=files)


def load_candidate_data(directory: Path = ROOT_DIR) -> pd.DataFrame:
    return load_datasets(directory).candidates


def load_pair_data(directory: Path = ROOT_DIR) -> pd.DataFrame:
    return load_datasets(directory).pairs


def load_patient_data(directory: Path = ROOT_DIR) -> pd.DataFrame:
    return load_datasets(directory).patients


def load_visit_data(directory: Path = ROOT_DIR) -> pd.DataFrame:
    return load_datasets(directory).visits


def get_available_files(directory: Path = ROOT_DIR) -> List[str]:
    return [p.name for p in _iter_csv_files(directory)]


def get_dataset_summary(directory: Path = ROOT_DIR) -> Dict[str, Any]:
    files = choose_dataset_files(directory)
    summary: Dict[str, Any] = {"available_files": sorted(p.name for p in directory.iterdir() if p.is_file())}
    if "candidate" in files:
        summary["candidate_rows"] = len(pd.read_csv(files["candidate"]))
    if "pairs" in files:
        summary["pair_rows"] = len(pd.read_csv(files["pairs"]))
    if "patients" in files:
        summary["patient_rows"] = len(pd.read_csv(files["patients"]))
    if "visits" in files:
        summary["visit_rows"] = len(pd.read_csv(files["visits"]))
    return summary
