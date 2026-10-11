
from pathlib import Path
from datetime import date, timedelta
import random
import json

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="JagaPasien AI",
    page_icon="💚",
    layout="wide",
)

FOLDER = Path(__file__).resolve().parent / "data_jagapasien"
KODE = {
    "J06.9": ("Infeksi saluran napas atas", "Poli Umum"),
    "I10": ("Hipertensi", "Poli Penyakit Dalam"),
    "E11.9": ("Diabetes tipe 2", "Poli Penyakit Dalam"),
    "K29.7": ("Gastritis", "Poli Umum"),
    "J45.9": ("Asma", "Poli Paru"),
    "N39.0": ("Infeksi saluran kemih", "Poli Umum"),
    "M54.5": ("Nyeri punggung bawah", "Poli Saraf"),
    "Z00.0": ("Pemeriksaan kesehatan", "Poli Umum"),
}


def buat_data(jumlah_pasien=10000, seed=20261010):
    r = random.Random(seed)
    pasien, kunjungan, kandidat = [], [], []
    pengecualian = 0
    nomor_encounter = 0
    tanggal_awal = date(2026, 5, 1)

    for nomor_pasien in range(1, jumlah_pasien + 1):
        pid = f"SYN-P{nomor_pasien:06d}"
        kronis = r.random() < 0.22
        pasien.append({
            "patient_id": pid,
            "umur": r.randint(1, 85),
            "jenis_kelamin": r.choice(["L", "P"]),
            "penyakit_kronis": "Ya" if kronis else "Tidak",
            "tipe_data": "SINTETIS",
        })

        jumlah_kunjungan = r.randint(2, 5)
        hari = r.randint(0, 50)
        faskes_awal = f"FASKES-SYN-{r.randint(1, 12):02d}"
        riwayat = []

        for urutan in range(jumlah_kunjungan):
            sebelumnya = riwayat[-1] if riwayat else None

            if sebelumnya:
                hari += (
                    r.randint(0, 7)
                    if r.random() < 0.45
                    else r.randint(9, 24)
                )

            kode = (
                sebelumnya["diagnosis_kode"]
                if sebelumnya and r.random() < 0.63
                else r.choice(list(KODE))
            )

            faskes = (
                sebelumnya["faskes"]
                if sebelumnya and r.random() < 0.85
                else faskes_awal
            )

            poli = (
                sebelumnya["poli"]
                if sebelumnya and r.random() < 0.67
                else KODE[kode][1]
            )

            dokter = (
                sebelumnya["dokter"]
                if sebelumnya and r.random() < 0.75
                else f"DOK-SYN-{r.randint(1, 30):02d}"
            )

            jam = f"{r.randint(8, 14):02d}:{r.choice(['00', '15', '30', '45'])}"
            kontrol = bool(sebelumnya and r.random() < 0.18)
            monitoring = bool(kronis and sebelumnya and r.random() < 0.26)
            igd = r.random() < 0.065
            status = "finished" if r.random() < 0.96 else "arrived"

            duplikasi = bool(
                sebelumnya
                and hari - sebelumnya["hari_index"] <= 1
                and r.random() < 0.11
            )

            if duplikasi:
                hari = sebelumnya["hari_index"]
                kode = sebelumnya["diagnosis_kode"]
                faskes = sebelumnya["faskes"]
                poli = sebelumnya["poli"]
                dokter = sebelumnya["dokter"]
                jam = sebelumnya["jam"]
                kontrol = monitoring = igd = False
                status = "finished"

            nomor_encounter += 1
            item = {
                "encounter_id": f"SYN-E{nomor_encounter:07d}",
                "patient_id": pid,
                "faskes": faskes,
                "tanggal": str(tanggal_awal + timedelta(days=hari)),
                "jam": jam,
                "hari_index": hari,
                "diagnosis_kode": kode,
                "diagnosis_nama": KODE[kode][0],
                "poli": poli,
                "dokter": dokter,
                "jenis_layanan": "IGD" if igd else "Rawat Jalan",
                "status": status,
                "kontrol_terjadwal": "Ya" if kontrol else "Tidak",
                "monitoring_kronis": "Ya" if monitoring else "Tidak",
                "tipe_data": "SINTETIS",
            }
            riwayat.append(item)
            kunjungan.append(item)

        # Analisis semua pasangan kunjungan dalam rentang 7 hari.
        for i, awal in enumerate(riwayat):
            for akhir in riwayat[i + 1:]:
                jarak = akhir["hari_index"] - awal["hari_index"]
                if jarak > 7:
                    break

                if awal["faskes"] != akhir["faskes"]:
                    continue

                alasan_pengecualian = (
                    awal["status"] != "finished"
                    or akhir["status"] != "finished"
                    or awal["jenis_layanan"] == "IGD"
                    or akhir["jenis_layanan"] == "IGD"
                    or akhir["kontrol_terjadwal"] == "Ya"
                    or akhir["monitoring_kronis"] == "Ya"
                )
                if alasan_pengecualian:
                    pengecualian += 1
                    continue

                sama_diagnosis = (
                    awal["diagnosis_kode"] == akhir["diagnosis_kode"]
                )
                sama_dokter = awal["dokter"] == akhir["dokter"]

                kemungkinan_duplikasi = (
                    jarak == 0
                    and awal["jam"] == akhir["jam"]
                    and sama_diagnosis
                    and sama_dokter
                    and awal["poli"] == akhir["poli"]
                )

                if kemungkinan_duplikasi:
                    skor = 88
                    sinyal = "Kemungkinan duplikasi dokumentasi"
                    alasan = (
                        "Tanggal, jam, dokter, poli, dan diagnosis sama "
                        "pada dua Encounter berbeda. Periksa dokumentasi."
                    )
                elif sama_diagnosis:
                    skor = 49 + (20 if jarak <= 2 else 8)
                    skor += 5 if sama_dokter else 0
                    sinyal = "Diagnosis sama, kunjungan berdekatan"
                    alasan = (
                        f"Kunjungan berjarak {jarak} hari pada faskes "
                        "yang sama dengan diagnosis simulasi sama. "
                        "Periksa indikasi klinis dan rencana kontrol."
                    )
                elif jarak <= 1:
                    skor = 36
                    sinyal = "Kunjungan sangat berdekatan"
                    alasan = (
                        "Kunjungan sangat berdekatan, tetapi diagnosis "
                        "berbeda. Bukti masih lemah; perlu telaah klinis."
                    )
                else:
                    continue

                prioritas = (
                    "Tinggi" if skor >= 70
                    else "Sedang" if skor >= 50
                    else "Rendah"
                )

                kandidat.append({
                    "case_id": f"JP-C{len(kandidat) + 1:06d}",
                    "patient_id": pid,
                    "faskes": awal["faskes"],
                    "encounter_1": awal["encounter_id"],
                    "encounter_2": akhir["encounter_id"],
                    "tanggal_1": awal["tanggal"],
                    "tanggal_2": akhir["tanggal"],
                    "jarak_hari": jarak,
                    "diagnosis_1": awal["diagnosis_kode"],
                    "diagnosis_2": akhir["diagnosis_kode"],
                    "prioritas": prioritas,
                    "skor_prioritas": skor,
                    "sinyal": sinyal,
                    "alasan": alasan,
                    "status_review": "PERLU_REVIEW_MANUAL",
                    "tipe_data": "SINTETIS",
                })

    FOLDER.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(pasien).to_csv(
        FOLDER / "pasien_sintetis.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(kunjungan).to_csv(
        FOLDER / "kunjungan_sintetis.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(kandidat).to_csv(
        FOLDER / "kandidat_review.csv", index=False, encoding="utf-8-sig"
    )

    metadata = {
        "jumlah_pasien": len(pasien),
        "jumlah_kunjungan": len(kunjungan),
        "jumlah_kandidat": len(kandidat),
        "pasangan_dikecualikan": pengecualian,
        "seed": seed,
        "tipe_data": "SINTETIS",
    }
    (FOLDER / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )


@st.cache_data
def baca_data():
    return (
        pd.read_csv(FOLDER / "pasien_sintetis.csv"),
        pd.read_csv(FOLDER / "kunjungan_sintetis.csv"),
        pd.read_csv(FOLDER / "kandidat_review.csv"),
        json.loads((FOLDER / "metadata.json").read_text(encoding="utf-8")),
    )


if not (FOLDER / "metadata.json").exists():
    with st.spinner("Membuat dataset sintetis awal..."):
        buat_data()

st.title("💚 JagaPasien AI")
st.caption("Deteksi dini pola fragmentasi episode pelayanan JKN — demo sintetis")

st.warning(
    "SEMUA DATA SINTETIS. Sistem tidak membuktikan fraud, "
    "tidak memiliki klaim BPJS asli, dan tidak menggantikan "
    "penilaian auditor atau tenaga medis."
)

with st.sidebar:
    st.header("Pengaturan dataset")
    jumlah = st.selectbox(
        "Jumlah pasien", [1000, 5000, 10000, 20000], index=2
    )
    seed = st.number_input(
        "Random seed", min_value=1, value=20261010, step=1
    )
    if st.button("🔄 Bangkitkan ulang", use_container_width=True):
        with st.spinner("Membuat data dan menganalisis kunjungan..."):
            buat_data(jumlah, int(seed))
            baca_data.clear()
        st.rerun()

pasien, kunjungan, kandidat, metadata = baca_data()

a, b, c, d = st.columns(4)
a.metric("Pasien sintetis", f"{len(pasien):,}")
b.metric("Encounter sintetis", f"{len(kunjungan):,}")
c.metric("Kandidat review", f"{len(kandidat):,}")
d.metric(
    "Pasangan dikecualikan",
    f"{metadata['pasangan_dikecualikan']:,}"
)

st.subheader("Distribusi prioritas")
urutan = ["Tinggi", "Sedang", "Rendah"]
distribusi = kandidat["prioritas"].value_counts().reindex(
    urutan, fill_value=0
)
st.bar_chart(distribusi)

st.subheader("Daftar kandidat")
kolom_filter, kolom_cari = st.columns([1, 2])
with kolom_filter:
    prioritas = st.selectbox(
        "Filter prioritas", ["Semua"] + urutan
    )
with kolom_cari:
    cari = st.text_input("Cari ID pasien atau kasus")

tampil = kandidat.copy()
if prioritas != "Semua":
    tampil = tampil[tampil["prioritas"] == prioritas]
if cari:
    cocok = (
        tampil["patient_id"].str.contains(cari, case=False, regex=False)
        | tampil["case_id"].str.contains(cari, case=False, regex=False)
    )
    tampil = tampil[cocok]

tampil = tampil.sort_values(
    "skor_prioritas", ascending=False
)

st.write(f"**{len(tampil):,} kandidat** sesuai filter")
st.dataframe(
    tampil[[
        "case_id", "patient_id", "tanggal_1", "tanggal_2",
        "jarak_hari", "prioritas", "sinyal", "status_review"
    ]],
    use_container_width=True,
    hide_index=True,
    height=320,
)

if not tampil.empty:
    st.subheader("Penjelasan kandidat")
    pilihan = st.selectbox(
        "Pilih kasus untuk diperiksa",
        tampil["case_id"].tolist(),
    )
    kasus = tampil[tampil["case_id"] == pilihan].iloc[0]

    kiri, kanan = st.columns(2)
    with kiri:
        st.write("**Pasien:**", kasus["patient_id"])
        st.write("**Faskes:**", kasus["faskes"])
        st.write("**Jarak:**", f"{kasus['jarak_hari']} hari")
        st.write("**Prioritas:**", kasus["prioritas"])
    with kanan:
        st.write("**Diagnosis 1:**", kasus["diagnosis_1"])
        st.write("**Diagnosis 2:**", kasus["diagnosis_2"])
        st.write("**Skor prioritas:**", kasus["skor_prioritas"])
        st.write("**Status:** PERLU_REVIEW_MANUAL")

    st.info(kasus["alasan"])

    st.subheader("Timeline kunjungan pasien")
    riwayat = kunjungan[
        kunjungan["patient_id"] == kasus["patient_id"]
    ].sort_values(["tanggal", "jam"])

    st.dataframe(
        riwayat[[
            "tanggal", "jam", "encounter_id", "faskes",
            "diagnosis_kode", "poli", "jenis_layanan",
            "kontrol_terjadwal", "monitoring_kronis"
        ]],
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Unduh hasil")
x, y, z = st.columns(3)
for kolom, label, data, nama in [
    (x, "CSV Pasien", pasien, "pasien_sintetis.csv"),
    (y, "CSV Kunjungan", kunjungan, "kunjungan_sintetis.csv"),
    (z, "CSV Kandidat", kandidat, "kandidat_review.csv"),
]:
    with kolom:
        st.download_button(
            label,
            data.to_csv(index=False).encode("utf-8-sig"),
            file_name=nama,
            mime="text/csv",
            use_container_width=True,
        )

st.caption(
    "Skor hanya menentukan prioritas telaah, bukan probabilitas fraud. "
    "Data sintetis ini belum divalidasi secara klinis maupun terhadap "
    "data klaim JKN."
)
