from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import plotly.express as px


def _safe_numeric(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype=float)
    return pd.to_numeric(series, errors="coerce")


def build_priority_chart(df: pd.DataFrame):
    if "prioritas" not in df.columns:
        return None
    values = df["prioritas"].fillna("Tidak diketahui").astype(str)
    counts = values.value_counts().reindex(["Tinggi", "Sedang", "Rendah", "Tidak diketahui"], fill_value=0)
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        color=counts.index,
        color_discrete_sequence=["#1f4e79", "#2a9d8f", "#e9c46a", "#adb5bd"],
        labels={"x": "Prioritas", "y": "Jumlah kandidat"},
        title="Distribusi prioritas review",
    )
    fig.update_layout(template="plotly_white", title_x=0.05, height=350)
    return fig


def build_facility_chart(df: pd.DataFrame):
    if "faskes" not in df.columns:
        return None
    counts = df["faskes"].fillna("Tidak diketahui").astype(str).value_counts().head(10)
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        labels={"x": "Fasilitas kesehatan", "y": "Jumlah kandidat"},
        title="Jumlah kandidat berdasarkan fasilitas kesehatan",
    )
    fig.update_layout(template="plotly_white", title_x=0.05, height=350, xaxis_tickangle=-45)
    return fig


def build_distance_chart(df: pd.DataFrame):
    if "jarak_hari" not in df.columns:
        return None
    distances = _safe_numeric(df["jarak_hari"]).dropna()
    if distances.empty:
        return None
    fig = px.histogram(
        distances,
        nbins=20,
        labels={"value": "Jarak hari", "count": "Jumlah pasangan"},
        title="Distribusi jarak hari antarkunjungan",
    )
    fig.update_layout(template="plotly_white", title_x=0.05, height=350)
    return fig


def build_percentile_chart(df: pd.DataFrame):
    if "persentil_anomali" not in df.columns:
        return None
    values = _safe_numeric(df["persentil_anomali"]).dropna()
    if values.empty:
        return None
    fig = px.histogram(
        values,
        nbins=20,
        labels={"value": "Persentil anomali", "count": "Jumlah pasangan"},
        title="Distribusi persentil anomali",
    )
    fig.update_layout(template="plotly_white", title_x=0.05, height=350)
    return fig


def build_patient_timeline(df: pd.DataFrame):
    if df.empty:
        return None
    timeline = df.copy()
    if "tanggal" in timeline.columns:
        timeline["tanggal_dt"] = pd.to_datetime(timeline["tanggal"], errors="coerce")
    if "jam" in timeline.columns:
        timeline["jam"] = timeline["jam"].fillna("00:00")
        timeline["tanggal_dt"] = pd.to_datetime(
            timeline["tanggal"].astype(str).fillna("") + " " + timeline["jam"].astype(str).fillna("00:00"),
            errors="coerce",
        )
    timeline = timeline.dropna(subset=["tanggal_dt"]).sort_values("tanggal_dt", na_position="last").reset_index(drop=True)
    if timeline.empty:
        return None
    timeline["y"] = 0
    fig = px.scatter(
        timeline,
        x="tanggal_dt",
        y="y",
        hover_data={
            "encounter_id": True,
            "tanggal": True,
            "jam": True,
            "diagnosis_nama": True,
            "poli": True,
            "faskes": True,
            "dokter": True,
            "y": False,
        },
        labels={"tanggal_dt": "Tanggal & jam", "encounter_id": "Encounter", "diagnosis_nama": "Diagnosis", "poli": "Poli", "faskes": "Faskes", "dokter": "Dokter"},
        title="Timeline kunjungan pasien",
    )
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_layout(template="plotly_white", title_x=0.05, height=350)
    return fig
