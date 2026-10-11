from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.jagapasien.analysis import (
    build_patient_timeline,
    candidate_summary,
    classify_findings,
    filter_candidates,
    find_case_by_id,
    get_priority_order,
    priority_distribution,
    summarize_kpis,
)
from src.jagapasien.data_loader import load_datasets
from src.jagapasien.visualization import (
    build_distance_chart,
    build_facility_chart,
    build_percentile_chart,
    build_priority_chart,
    build_patient_timeline as build_timeline_chart,
)

ROOT_DIR = Path(__file__).resolve().parent


st.set_page_config(page_title="JagaPasien AI", page_icon="🩺", layout="wide")

def render_overview(candidates: pd.DataFrame, pairs: pd.DataFrame, patients: pd.DataFrame, visits: pd.DataFrame) -> None:
    kpis = summarize_kpis(candidates, pairs, patients)
    st.subheader("Ringkasan eksekutif")
    col1, col2, col3, col4, col5 = st.columns(5)
    info_cards = [
        ("Total pasien sintetis", kpis["total_pasien"]),
        ("Total kunjungan", len(visits)),
        ("Total pasangan dianalisis", kpis["total_pasangan_dianalisis"]),
        ("Total kandidat review", kpis["total_kandidat_review"]),
        ("Total pasangan dengan pengecualian klinis", kpis["pasangan_dengan_pengecualian"]),
    ]
    for col, (label, value) in zip([col1, col2, col3, col4, col5], info_cards):
        col.metric(label, f"{value:,}")

    st.write(
        "JagaPasien AI membantu memprioritaskan pasangan kunjungan yang perlu diperiksa. Jumlah kandidat bukan jumlah fraud terkonfirmasi."
    )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        priority_chart = build_priority_chart(candidates)
        if priority_chart is not None:
            st.plotly_chart(priority_chart, use_container_width=True)
    with chart_col2:
        facility_chart = build_facility_chart(candidates)
        if facility_chart is not None:
            st.plotly_chart(facility_chart, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        distance_chart = build_distance_chart(candidates)
        if distance_chart is not None:
            st.plotly_chart(distance_chart, use_container_width=True)
    with chart_col4:
        percentile_chart = build_percentile_chart(candidates)
        if percentile_chart is not None:
            st.plotly_chart(percentile_chart, use_container_width=True)


def render_candidates(candidates: pd.DataFrame) -> None:
    st.subheader("Daftar kandidat review")
    priority_options = ["Semua"] + sorted(candidates["prioritas"].dropna().unique().tolist(), key=lambda x: ["Tinggi", "Sedang", "Rendah"].index(x) if x in ["Tinggi", "Sedang", "Rendah"] else 99)
    faskes_options = ["Semua"] + sorted(candidates["faskes"].dropna().unique().tolist())

    with st.sidebar:
        st.markdown("### Filter kandidat")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_priority = st.selectbox("Prioritas", priority_options)
    with col2:
        selected_faskes = st.selectbox("Faskes", faskes_options)
    with col3:
        patient_filter = st.text_input("ID pasien")
    with col4:
        case_filter = st.text_input("ID kasus")

    range_col1, range_col2 = st.columns(2)
    with range_col1:
        date_from = st.date_input("Tanggal mulai", value=None)
    with range_col2:
        date_to = st.date_input("Tanggal akhir", value=None)

    search_term = st.text_input("Pencarian")

    filtered = filter_candidates(
        candidates,
        priority=None if selected_priority == "Semua" else selected_priority,
        faskes=None if selected_faskes == "Semua" else selected_faskes,
        patient_id=patient_filter or None,
        case_id=case_filter or None,
        date_from=date_from.isoformat() if date_from else None,
        date_to=date_to.isoformat() if date_to else None,
        search=search_term or None,
    )

    st.caption(f"Menampilkan {len(filtered):,} dari {len(candidates):,} kandidat setelah filter.")
    if len(filtered) > 500:
        st.warning("Tabel hanya menampilkan sebagian hasil karena jumlah data lebih besar dari batas render yang dipilih untuk menjaga performa.")

    columns = [
        "case_id",
        "patient_id",
        "faskes",
        "tanggal_1",
        "tanggal_2",
        "jarak_hari",
        "prioritas",
        "skor_prioritas",
        "persentil_anomali",
        "status_review",
    ]
    display = filtered[columns].copy() if all(col in filtered.columns for col in columns) else filtered.copy()
    st.dataframe(display.head(500), use_container_width=True)

    csv = display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV hasil filter",
        data=csv,
        file_name="kandidat_review_terfilter.csv",
        mime="text/csv",
    )


def render_detail(candidates: pd.DataFrame, visits: pd.DataFrame) -> None:
    st.subheader("Detail kasus")
    case_options = candidates["case_id"].astype(str).tolist()
    selected_id = st.selectbox("Pilih Case ID", case_options)
    case = find_case_by_id(candidates, selected_id)
    if case is None:
        st.warning("Case ID tidak ditemukan.")
        return

    detail_cols = [
        "case_id",
        "patient_id",
        "faskes",
        "tanggal_1",
        "tanggal_2",
        "jarak_hari",
        "diagnosis_1",
        "diagnosis_2",
        "dokter_sama",
        "poli_sama",
        "prioritas",
        "skor_prioritas",
        "persentil_anomali",
        "status_review",
    ]
    info_row = {key: case.get(key, "-") for key in detail_cols if key in case}
    st.write(info_row)

    st.markdown("### Mengapa kasus ini perlu ditinjau?")
    st.write(case.get("alasan", "Tidak tersedia penjelasan yang cukup untuk kasus ini."))

    st.info(
        "Skor dan persentil anomali bukan probabilitas fraud. Kesimpulan akhir memerlukan telaah rekam medis, konteks klinis, dan dokumen klaim."
    )

    timeline_df = build_patient_timeline(visits, case.get("patient_id", ""))
    if timeline_df.empty:
        st.warning("Timeline terbatas karena file kunjungan lengkap tidak tersedia atau pasien tidak ditemukan.")
    else:
        st.markdown("### Timeline kunjungan pasien")
        timeline_chart = build_timeline_chart(timeline_df)
        if timeline_chart is not None:
            st.plotly_chart(timeline_chart, use_container_width=True)
        st.dataframe(timeline_df[["encounter_id", "tanggal", "jam", "diagnosis_nama", "poli", "dokter"]], use_container_width=True)


def render_analysis(candidates: pd.DataFrame, pairs: pd.DataFrame) -> None:
    st.subheader("Analisis temuan")
    findings = classify_findings(candidates)
    labels = [
        ("Potensi duplikasi dokumentasi", findings["potensi_duplikasi_dokumentasi"]),
        ("Kesinambungan episode perlu telaah", findings["kesinambungan_episode_perlu_telaah"]),
        ("Kunjungan berdekatan dengan bukti terbatas", findings["kunjungan_berdekatan_bukti_terbatas"]),
        ("Pengecualian klinis", findings["pengecualian_klinis"]),
        ("Belum dapat diklasifikasikan", findings["belum_dapat_diklasifikasikan"]),
    ]

    cols = st.columns(5)
    for col, (label, value) in zip(cols, labels):
        col.metric(label, f"{value:,}")

    st.caption(
        "Klasifikasi di atas hanya menampilkan pola indikatif berdasarkan kolom yang tersedia di dataset. Tidak otomatis menegaskan diagnosis atau audit klinis."
    )

    if "pengecualian_klinis" in pairs.columns:
        st.write(f"Jumlah kasus dengan pengecualian klinis di data pasangan: {pairs['pengecualian_klinis'].fillna(False).astype(bool).sum():,}")
    else:
        st.write("Kategori pengecualian klinis belum tersedia dalam CSV kandidat.")


def render_methodology() -> None:
    st.subheader("Metodologi AI")
    st.markdown(
        """
        JagaPasien AI adalah prototipe berbasis data sintetis untuk memprioritaskan pasangan kunjungan yang layak ditelaah lebih lanjut.

        - Isolation Forest adalah algoritma unsupervised yang mempelajari pola normal pada fitur numerik dan kategorikal yang terwakili dalam data pasangan kunjungan.
        - Dalam konteks ini, model digunakan untuk mengidentifikasi observasi yang relatif tidak biasa dibanding pola umum dalam dataset sintetis.
        - Analisis tanpa label berarti model tidak dibekali label fraud aktual untuk melatih atau mengevaluasi klasifikasi. Hasilnya bersifat indikatif, bukan keputusan klinis.
        - Fitur yang dipertimbangkan mencakup jarak hari, kesamaan diagnosis, kesamaan dokter/poli, apakah tanggal dan jam identik, status lengkap, kondisi kronis, dan variabel pengecualian klinis.
        - Pasangan kunjungan dibentuk dari kombinasi encounter yang muncul dalam kandidat review dan data pasangan analisis.
        - Pengecualian klinis diambil dari atribut yang tersedia di data pasangan dan dikelola secara hati-hati agar tidak disamakan dengan hasil kandidat.
        - Prioritas review ditentukan berdasarkan bobot kombinasi anomali statistik dan sinyal review yang tersedia pada artefak data.
        - Skor anomali dan persentil bukan probabilitas fraud; keduanya memberi ukuran seberapa jarang sebuah pola terjadi dalam data sintetis.
        - Model belum memiliki ukuran akurasi klinis karena tidak ada label validasi pada data nyata maupun data sintetis yang dijadikan ground truth.
        """
    )


def render_about() -> None:
    st.subheader("Tentang JagaPasien AI")
    st.markdown(
        """
        JagaPasien AI adalah prototipe yang dirancang untuk membantu petugas telaah memprioritaskan pasangan kunjungan yang memerlukan perhatian lebih lanjut.

        Latar belakang: pelayanan JKN menghadapi tantangan dalam menjaga kesinambungan episode pelayanan, menilai kunjungan berulang, dan membedakan pola yang wajar dari pola yang membutuhkan pemeriksaan lebih lanjut.

        Tujuan: meningkatkan efisiensi telaah manusia dengan menyorot pasangan kunjungan yang perlu ditinjau, bukan untuk menetapkan fraud secara otomatis.

        Nilai inovasi: kombinasi analisis pola kunjungan, prioritas review, dan interpretasi yang transparan untuk tim pengawas atau pemeriksa.

        Teknologi: Python 3.10+, Streamlit, Pandas, Plotly, scikit-learn, Joblib, pytest.

        Manfaat yang diharapkan: mempercepat pemetaan kandidat review, kesesuaian data, dan penguatan proses telaah manual yang lebih terstruktur.

        Keterbatasan: data bersifat sintetis, label fraud tidak tersedia, dan belum ada validasi klinis pada pelayanan nyata.

        Rencana pengembangan: validasi dengan data nyata, penguatan aturan klinis, dan integrasi kebutuhan operasional yang lebih spesifik.

        Context Healthkathon 2026: prototipe digunakan sebagai alat pendukung observasi dan telaah awal.

        Placeholder pemilik: [NAMA PEMILIK]
        Placeholder tim: [NAMA TIM]
        """
    )


def main() -> None:
    try:
        dataset = load_datasets(ROOT_DIR)
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.info("Pastikan file CSV seperti hasil_jagapasien_ai.csv, pasangan_kunjungan.csv, pasien_sintetis.csv, dan kunjungan_sintetis.csv tersedia di workspace.")
        return

    candidates = dataset.candidates
    pairs = dataset.pairs
    patients = dataset.patients
    visits = dataset.visits

    st.title("JagaPasien AI")
    st.caption("AI untuk Menjaga Kesinambungan Pelayanan Pasien JKN")
    st.warning("DATA SINTETIS — BUKAN DETEKSI FRAUD TERKONFIRMASI")

    with st.sidebar:
        st.sidebar.title("Navigasi")
        page = st.sidebar.radio(
            "Halaman",
            ["Overview", "Daftar Kandidat", "Detail Kasus", "Analisis Temuan", "Metodologi AI", "Tentang JagaPasien AI"],
        )

    if page == "Overview":
        render_overview(candidates, pairs, patients, visits)
    elif page == "Daftar Kandidat":
        render_candidates(candidates)
    elif page == "Detail Kasus":
        render_detail(candidates, visits)
    elif page == "Analisis Temuan":
        render_analysis(candidates, pairs)
    elif page == "Metodologi AI":
        render_methodology()
    else:
        render_about()


if __name__ == "__main__":
    main()
