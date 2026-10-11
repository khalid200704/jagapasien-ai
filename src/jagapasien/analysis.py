from __future__ import annotations

import warnings
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


def _normalize_boolean_value(value: Any) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    if isinstance(value, (bool, pd.BooleanDtype)):
        return bool(value)
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return False
        if value in (0, 0.0):
            return False
        if value in (1, 1.0):
            return True
        raise ValueError(f"Nilai boolean tidak valid: {value!r}")
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in {"", "na", "n/a", "null", "none"}:
            return False
        mapping = {
            "true": True,
            "false": False,
            "ya": True,
            "tidak": False,
            "yes": True,
            "no": False,
            "1": True,
            "0": False,
            "y": True,
            "n": False,
        }
        if cleaned in mapping:
            return mapping[cleaned]
        warnings.warn(f"Nilai boolean tidak dikenal diubah menjadi False: {value!r}", UserWarning)
        return False
    if pd.isna(value):
        return False
    warnings.warn(f"Nilai boolean tidak dikenal diubah menjadi False: {value!r}", UserWarning)
    return False


def safe_bool(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype=bool)
    values = []
    for value in series:
        try:
            values.append(_normalize_boolean_value(value))
        except ValueError as exc:
            warnings.warn(str(exc), UserWarning)
            values.append(False)
    return pd.Series(values, index=series.index, dtype=bool)


def get_priority_order(priority_values: Iterable[str]) -> List[str]:
    order = ["Tinggi", "Sedang", "Rendah"]
    ordered = [value for value in order if value in set(priority_values)]
    for value in priority_values:
        if value not in ordered:
            ordered.append(value)
    return ordered


def summarize_kpis(candidates: pd.DataFrame, pairs: pd.DataFrame, patients: pd.DataFrame, visits: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    candidate_count = len(candidates) if isinstance(candidates, pd.DataFrame) else 0
    pair_count = len(pairs) if isinstance(pairs, pd.DataFrame) else 0
    patient_count = len(patients) if isinstance(patients, pd.DataFrame) else 0
    visit_count = len(visits) if isinstance(visits, pd.DataFrame) else 0

    candidate_unique_patients = 0
    if isinstance(candidates, pd.DataFrame) and "patient_id" in candidates.columns:
        candidate_unique_patients = int(candidates["patient_id"].dropna().astype(str).nunique())

    encounter_values: List[str] = []
    if isinstance(pairs, pd.DataFrame):
        for col in ["encounter_1", "encounter_2"]:
            if col in pairs.columns:
                encounter_values.append(pairs[col].dropna().astype(str))
    if encounter_values:
        encounter_unique = pd.concat(encounter_values, ignore_index=True).dropna().astype(str).unique()
        encounter_unique_count = len(encounter_unique)
    else:
        encounter_unique_count = 0

    if isinstance(pairs, pd.DataFrame) and "pengecualian_klinis" in pairs.columns:
        pengecualian_count = int(safe_bool(pairs["pengecualian_klinis"]).sum())
    else:
        pengecualian_count = 0

    return {
        "total_pasien": patient_count,
        "total_kunjungan": visit_count,
        "total_pasangan_dianalisis": pair_count,
        "total_kandidat_review": candidate_count,
        "pasangan_dengan_pengecualian": pengecualian_count,
        "pasien_unik_kandidat": candidate_unique_patients,
        "encounter_unik_total": encounter_unique_count,
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
    return pd.Series(pd.to_numeric(df["jarak_hari"], errors="coerce").dropna())


def percentile_distribution(df: pd.DataFrame) -> pd.Series:
    if "persentil_anomali" not in df.columns:
        return pd.Series(dtype=float)
    return pd.Series(pd.to_numeric(df["persentil_anomali"], errors="coerce").dropna())


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
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if isinstance(df, pd.DataFrame) else [])

    result = df.copy()

    if priority is not None:
        priority_value = str(priority).strip().lower()
        if "prioritas" in result.columns:
            result = result[result["prioritas"].fillna("").astype(str).str.strip().str.lower().eq(priority_value)]
        else:
            return result.iloc[0:0].copy()

    if faskes is not None:
        faskes_value = str(faskes).strip().lower()
        if "faskes" in result.columns:
            result = result[result["faskes"].fillna("").astype(str).str.strip().str.lower().eq(faskes_value)]
        else:
            return result.iloc[0:0].copy()

    if patient_id is not None:
        patient_value = str(patient_id).strip().lower()
        if "patient_id" in result.columns:
            result = result[result["patient_id"].fillna("").astype(str).str.strip().str.lower().eq(patient_value)]
        else:
            return result.iloc[0:0].copy()

    if case_id is not None:
        case_value = str(case_id).strip().lower()
        if "case_id" in result.columns:
            result = result[result["case_id"].fillna("").astype(str).str.strip().str.lower().eq(case_value)]
        else:
            return result.iloc[0:0].copy()

    if search is not None:
        token = str(search).strip().lower()
        if token:
            fields = [col for col in ["case_id", "patient_id", "faskes", "alasan", "status_review"] if col in result.columns]
            mask = pd.Series(False, index=result.index)
            for field in fields:
                mask |= result[field].fillna("").astype(str).str.lower().str.contains(token, regex=False, na=False)
            result = result[mask]

    if date_from is not None or date_to is not None:
        if "tanggal_1" not in result.columns and "tanggal_2" not in result.columns:
            return result.iloc[0:0].copy()

        start_dt = pd.to_datetime(date_from, errors="coerce") if date_from else pd.NaT
        end_dt = pd.to_datetime(date_to, errors="coerce") if date_to else pd.NaT
        if date_from is not None and pd.isna(start_dt):
            raise ValueError(f"Tanggal mulai tidak valid: {date_from!r}")
        if date_to is not None and pd.isna(end_dt):
            raise ValueError(f"Tanggal akhir tidak valid: {date_to!r}")
        if pd.notna(start_dt) and pd.notna(end_dt) and start_dt > end_dt:
            raise ValueError("Tanggal mulai tidak boleh lebih besar daripada tanggal akhir.")

        start_series = pd.to_datetime(result["tanggal_1"], errors="coerce") if "tanggal_1" in result.columns else pd.Series(pd.NaT, index=result.index)
        end_series = pd.to_datetime(result["tanggal_2"], errors="coerce") if "tanggal_2" in result.columns else pd.Series(pd.NaT, index=result.index)
        pair_start = start_series.combine(end_series, min)

        mask = pd.Series(True, index=result.index)
        if pd.notna(start_dt):
            mask &= pair_start >= start_dt
        if pd.notna(end_dt):
            mask &= pair_start <= end_dt
        result = result[mask]

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
    diag_same_mask = safe_bool(df["diagnosis_sama"]) if "diagnosis_sama" in df.columns else pd.Series(False, index=df.index)

    if "jarak_hari" in df.columns:
        distance_values = pd.to_numeric(df["jarak_hari"], errors="coerce")
    else:
        distance_values = pd.Series(pd.NaN, index=df.index)

    continuity_mask = pd.Series(False, index=df.index)
    nearby_mask = pd.Series(False, index=df.index)
    if len(df) > 0:
        continuity_mask = diag_same_mask & distance_values.notna() & (distance_values > 0) & (distance_values <= 14)
        nearby_mask = distance_values.notna() & (distance_values > 0) & (distance_values <= 7) & (~dup_mask)

    for idx in range(len(df)):
        if except_mask.iloc[idx]:
            category = "pengecualian_klinis"
        elif dup_mask.iloc[idx]:
            category = "potensi_duplikasi_dokumentasi"
        elif continuity_mask.iloc[idx]:
            category = "kesinambungan_episode_perlu_telaah"
        elif nearby_mask.iloc[idx]:
            category = "kunjungan_berdekatan_bukti_terbatas"
        else:
            category = "belum_dapat_diklasifikasikan"
        counts[category] += 1

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
