import pandas as pd

from src.jagapasien.analysis import classify_findings, filter_candidates


def build_candidate_df():
    return pd.DataFrame(
        [
            {
                "case_id": "C1",
                "patient_id": "P1",
                "faskes": "FASKES-SYN-01",
                "tanggal_1": "2026-05-10",
                "tanggal_2": "2026-05-10",
                "jarak_hari": 0,
                "diagnosis_sama": 1,
                "prioritas": "Tinggi",
                "skor_prioritas": 100,
                "persentil_anomali": 95.0,
                "kemungkinan_duplikasi": True,
                "pengecualian_klinis": False,
            },
            {
                "case_id": "C2",
                "patient_id": "P2",
                "faskes": "FASKES-SYN-02",
                "tanggal_1": "2026-05-12",
                "tanggal_2": "2026-05-15",
                "jarak_hari": 3,
                "diagnosis_sama": 1,
                "prioritas": "Sedang",
                "skor_prioritas": 60,
                "persentil_anomali": 70.0,
                "kemungkinan_duplikasi": False,
                "pengecualian_klinis": False,
            },
            {
                "case_id": "C3",
                "patient_id": "P3",
                "faskes": "FASKES-SYN-03",
                "tanggal_1": "2026-05-16",
                "tanggal_2": "2026-05-18",
                "jarak_hari": 2,
                "diagnosis_sama": 0,
                "prioritas": "Rendah",
                "skor_prioritas": 30,
                "persentil_anomali": 40.0,
                "kemungkinan_duplikasi": False,
                "pengecualian_klinis": True,
            },
        ]
    )


def test_filter_candidates_by_priority_and_faskes():
    df = build_candidate_df()
    filtered = filter_candidates(df, priority="Tinggi", faskes="FASKES-SYN-01")
    assert len(filtered) == 1
    assert filtered.iloc[0]["case_id"] == "C1"


def test_filter_candidates_by_patient_id_and_search():
    df = build_candidate_df()
    filtered = filter_candidates(df, patient_id="P2")
    assert len(filtered) == 1
    assert filtered.iloc[0]["case_id"] == "C2"

    searched = filter_candidates(df, search="dokumen")
    assert len(searched) == 0


def test_classify_findings_counts_unclassified_cases():
    df = build_candidate_df()
    findings = classify_findings(df)
    assert findings["potensi_duplikasi_dokumentasi"] >= 1
    assert findings["pengecualian_klinis"] >= 1
    assert findings["belum_dapat_diklasifikasikan"] >= 0
