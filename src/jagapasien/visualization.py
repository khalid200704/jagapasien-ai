from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import plotly.express as px


def build_priority_chart(df: pd.DataFrame):
    if "prioritas" not in df.columns:
        return None
    values = df["prioritas"].value_counts().reindex(["Tinggi", "Sedang", "Rendah"], fill_value=0)
    fig = px.bar(
        x=values.index,
        y=values.values,
        color=values.index,
        color_discrete_sequence=["#1f4e79", "#2a9d8f", "#e9c46a"],
        labels={"x": "Prioritas", "y": "Jumlah kandidat"},
        title="Distribusi prioritas review",
    )
    fig.update_layout(template="plotly_white", title_x=0.05, height=350)
    return fig


def build_facility_chart(df: pd.DataFrame):
    if "faskes" not in df.columns:
        return None
    counts = df["faskes"].value_counts().head(10)
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
    distances = df["jarak_hari"].dropna().astype(float)
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
    values = df["persentil_anomali"].dropna().astype(float)
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
    fig = px.line(
        df,
        x="tanggal",
        y="hari_index",
        color="encounter_id",
        markers=True,
        title="Timeline kunjungan pasien",
        labels={"tanggal": "Tanggal", "hari_index": "Hari indeks", "encounter_id": "Encounter"},
    )
    fig.update_layout(template="plotly_white", title_x=0.05, height=350)
    return fig
