from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


def safe_bool(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(bool)


def get_priority_order(priority_values: Iterable[str]) -> List[str]:
    order = ["Tinggi", "Sedang", "Rendah"]
    ordered = [value for value in order if value in set(priority_values)]
    for value in priority_values:
        if value not in ordered:
            ordered.append(value)
    return ordered


def summarize_kpis(candidates: pd.DataFrame, pairs: pd.DataFrame, patients: pd.DataFrame) -> Dict[str, Any]:
    candidate_count = len(candidates)
    pair_count = len(pairs)
    patient_count = len(patients)
    candidate_unique_patients = candidates["patient_id"].nunique() if "patient_id" in candidates.columns else 0
    visit_unique_encounters = pairs["encounter_1"].nunique() + pairs["encounter_2"].nunique() if {"encounter_1", "encounter_2"}.issubset(pairs.columns) else 0
    return {
        "total_pasien": patient_count,
        "total_kunjungan": len(patients) if "patient_id" in patients.columns else 0,
        "total_pasangan_dianalisis": pair_count,
        "total_kandidat_review": candidate_count,
        "pasangan_dengan_pengecualian": int(pairs["pengecualian_klinis"].fillna(False).astype(bool).sum()) if "pengecualian_klinis" in pairs.columns else 0,
        "pasien_unik_kandidat": candidate_unique_patients,
        "encounter_unik_total": visit_unique_encounters,
    }


def priority_distribution(df: pd.DataFrame) -> pd.Series:
    if "prioritas" not in df.columns:
        return pd.Series(dtype=int)
    return df["prioritas"].fillna("Tidak diketahui").value_counts().sort_index()


def facility_distribution(df: pd.DataFrame) -> pd.Series:
    if "faskes" not in df.columns:
        return pd.Series(dtype=int)
    return df["faskes"].value_counts()


def distance_distribution(df: pd.DataFrame) -> pd.Series:
    if "jarak_hari" not in df.columns:
        return pd.Series(dtype=float)
    return pd.Series(df["jarak_hari"].dropna().astype(float))


def percentile_distribution(df: pd.DataFrame) -> pd.Series:
    if "persentil_anomali" not in df.columns:
        return pd.Series(dtype=float)
    return pd.Series(df["persentil_anomali"].dropna().astype(float))


def filter_candidates(
    df: pd.DataFrame,
    priority: Optional[str] = None,
    faskes: Optional[str] = None,
    patient_id: Optional[str] = None,
    case_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
) -> pd.DataFrame:
    result = df.copy()
    if priority:
        result = result[result["prioritas"].astype(str).str.lower() == str(priority).lower()]
    if faskes:
        result = result[result["faskes"].astype(str).str.lower() == str(faskes).lower()]
    if patient_id:
        result = result[result["patient_id"].astype(str).str.lower() == str(patient_id).lower()]
    if case_id:
        result = result[result["case_id"].astype(str).str.lower() == str(case_id).lower()]
    if search:
        token = str(search).lower()
        fields = [col for col in ["case_id", "patient_id", "faskes", "alasan", "status_review"] if col in result.columns]
        mask = pd.Series(False, index=result.index)
        for field in fields:
            mask |= result[field].fillna("").astype(str).str.lower().str.contains(token, na=False)
        result = result[mask]
    if date_from and "tanggal_1" in result.columns:
        date_from = pd.to_datetime(date_from, errors="coerce")
        if pd.notna(date_from):
            result = result[pd.to_datetime(result["tanggal_1"], errors="coerce") >= date_from]
    if date_to and "tanggal_2" in result.columns:
        date_to = pd.to_datetime(date_to, errors="coerce")
        if pd.notna(date_to):
            result = result[pd.to_datetime(result["tanggal_2"], errors="coerce") <= date_to]
    return result.reset_index(drop=True)


def find_case_by_id(df: pd.DataFrame, case_id: str) -> Optional[pd.Series]:
    if df.empty or "case_id" not in df.columns:
        return None
    match = df[df["case_id"].astype(str).str.lower() == str(case_id).lower()]
    return match.iloc[0].copy() if not match.empty else None


def build_patient_timeline(visits: pd.DataFrame, patient_id: str) -> pd.DataFrame:
    if "patient_id" not in visits.columns:
        return pd.DataFrame()
    timeline = visits[visits["patient_id"].astype(str).str.lower() == str(patient_id).lower()].copy()
    if timeline.empty:
        return timeline
    timeline = timeline.sort_values(["tanggal", "jam"], na_position="last").reset_index(drop=True)
    return timeline


def classify_findings(df: pd.DataFrame) -> Dict[str, int]:
    counts = {
        "potensi_duplikasi_dokumentasi": 0,
        "kesinambungan_episode_perlu_telaah": 0,
        "kunjungan_berdekatan_bukti_terbatas": 0,
        "pengecualian_klinis": 0,
        "belum_dapat_diklasifikasikan": 0,
    }
    if df.empty:
        return counts

    dup_mask = safe_bool(df["kemungkinan_duplikasi"]) if "kemungkinan_duplikasi" in df.columns else pd.Series(False, index=df.index)
    except_mask = safe_bool(df["pengecualian_klinis"]) if "pengecualian_klinis" in df.columns else pd.Series(False, index=df.index)
    diag_same_mask = df["diagnosis_sama"].fillna(0).astype(int).eq(1) if "diagnosis_sama" in df.columns else pd.Series(False, index=df.index)
    same_faskes_mask = pd.Series(True, index=df.index)
    if "faskes" in df.columns:
        same_faskes_mask = df["faskes"].notna()
    continuity_mask = diag_same_mask & (df["jarak_hari"].fillna(0).astype(int) <= 14) if "jarak_hari" in df.columns else pd.Series(False, index=df.index)
    adjacent_limit_mask = (df["jarak_hari"].fillna(0).astype(int) <= 7) & (~dup_mask) if "jarak_hari" in df.columns else pd.Series(False, index=df.index)

    counts["potensi_duplikasi_dokumentasi"] = int(dup_mask.sum())
    counts["pengecualian_klinis"] = int(except_mask.sum())
    counts["kesinambungan_episode_perlu_telaah"] = int(continuity_mask.sum())
    counts["kunjungan_berdekatan_bukti_terbatas"] = int(adjacent_limit_mask.sum())
    counts["belum_dapat_diklasifikasikan"] = int((~dup_mask & ~except_mask & ~continuity_mask & ~adjacent_limit_mask).sum())
    return counts


def candidate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "total": len(df),
        "prioritas": {},
        "faskes": {},
        "pasien_unik": 0,
    }
    if "prioritas" in df.columns:
        result["prioritas"] = df["prioritas"].value_counts().to_dict()
    if "faskes" in df.columns:
        result["faskes"] = df["faskes"].value_counts().to_dict()
    if "patient_id" in df.columns:
        result["pasien_unik"] = int(df["patient_id"].nunique())
    return result
