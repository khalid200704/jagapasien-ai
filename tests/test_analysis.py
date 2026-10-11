import pandas as pd
import pytest

from src.jagapasien.analysis import classify_findings, filter_candidates, safe_bool, summarize_kpis


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


def test_safe_bool_handles_known_variants():
    series = pd.Series([True, False, 1, 0, "True", "FALSE", "Ya", "Tidak", "yes", "no", " ", None, "1", "0"])
    normalized = safe_bool(series)
    expected = pd.Series([True, False, True, False, True, False, True, False, True, False, False, False, True, False], dtype=bool)
    pd.testing.assert_series_equal(normalized.reset_index(drop=True), expected)


def test_summarize_kpis_uses_visit_and_unique_encounters():
    patients = pd.DataFrame({"patient_id": ["P1", "P2"]})
    visits = pd.DataFrame({"encounter_id": ["E1", "E2", "E1"]})
    pairs = pd.DataFrame(
        {
            "encounter_1": ["E1", "E2", "E3"],
            "encounter_2": ["E2", "E1", "E2"],
            "pengecualian_klinis": [True, False, True],
        }
    )
    candidates = pd.DataFrame({"patient_id": ["P1", "P2", "P2"], "prioritas": ["Tinggi", "Sedang", "Rendah"]})
    summary = summarize_kpis(candidates, pairs, patients, visits)
    assert summary["total_pasien"] == 2
    assert summary["total_kunjungan"] == 3
    assert summary["total_pasangan_dianalisis"] == 3
    assert summary["total_kandidat_review"] == 3
    assert summary["pasangan_dengan_pengecualian"] == 2
    assert summary["pasien_unik_kandidat"] == 2
    assert summary["encounter_unik_total"] == 3


def test_filter_candidates_handles_special_regex_characters_and_date_ranges():
    df = pd.DataFrame(
        [
            {"case_id": "CASE(1)", "patient_id": "P1", "faskes": "Faskes A", "prioritas": "Tinggi", "tanggal_1": "2026-05-03", "tanggal_2": "2026-05-06", "alasan": "Alpha"},
            {"case_id": "CASE[2]", "patient_id": "P2", "faskes": "Faskes B", "prioritas": "Rendah", "tanggal_1": "2026-05-10", "tanggal_2": "2026-05-12", "alasan": "Beta"},
        ]
    )
    searched = filter_candidates(df, search="CASE(1)")
    assert len(searched) == 1
    date_filtered = filter_candidates(df, date_from="2026-05-04", date_to="2026-05-11")
    assert len(date_filtered) == 1
    assert date_filtered.iloc[0]["case_id"] == "CASE[2]"

    with pytest.raises(ValueError):
        filter_candidates(df, date_from="2026-05-20", date_to="2026-05-10")


def test_classify_findings_is_exclusive():
    df = pd.DataFrame(
        [
            {"case_id": "A", "kemungkinan_duplikasi": True, "pengecualian_klinis": False, "diagnosis_sama": 1, "jarak_hari": 0},
            {"case_id": "B", "kemungkinan_duplikasi": False, "pengecualian_klinis": False, "diagnosis_sama": 1, "jarak_hari": 5},
            {"case_id": "C", "kemungkinan_duplikasi": False, "pengecualian_klinis": False, "diagnosis_sama": 0, "jarak_hari": 3},
            {"case_id": "D", "kemungkinan_duplikasi": False, "pengecualian_klinis": True, "diagnosis_sama": 0, "jarak_hari": 9},
        ]
    )
    findings = classify_findings(df)
    total = sum(findings.values())
    assert total == len(df)
    assert findings["potensi_duplikasi_dokumentasi"] == 1
    assert findings["pengecualian_klinis"] == 1
    assert findings["kesinambungan_episode_perlu_telaah"] == 1
    assert findings["kunjungan_berdekatan_bukti_terbatas"] == 1
