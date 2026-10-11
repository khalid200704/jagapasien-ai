from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.jagapasien.data_loader import choose_dataset_files, load_datasets


def count_invalid_dates(series: pd.Series) -> int:
    return int(pd.to_datetime(series, errors="coerce").isna().sum())


def build_report() -> str:
    available_files = sorted(p.name for p in ROOT_DIR.iterdir() if p.is_file())
    files = choose_dataset_files(ROOT_DIR)
    dataset = load_datasets(ROOT_DIR)

    rows = []
    rows.append("# Audit Dataset JagaPasien AI")
    rows.append("")
    rows.append("## 1. File yang tersedia")
    rows.append("")
    for name in available_files:
        rows.append(f"- {name}")
    rows.append("")

    rows.append("## 2. Ringkasan jumlah baris per CSV")
    rows.append("")
    for key in ["candidate", "pairs", "patients", "visits"]:
        if key in files:
            df = pd.read_csv(files[key])
            rows.append(f"- {files[key].name}: {len(df):,} baris")
    rows.append("")

    rows.append("## 3. Pemeriksaan kolom dan tipe data")
    rows.append("")
    for key in ["candidate", "pairs", "patients", "visits"]:
        if key in files:
            df = pd.read_csv(files[key])
            rows.append(f"### {files[key].name}")
            rows.append(f"Jumlah kolom: {len(df.columns)}")
            for col, dtype in df.dtypes.items():
                rows.append(f"- {col}: {dtype}")
            rows.append("")

    rows.append("## 4. Jumlah pasien unik, encounter unik, dan kandidat")
    rows.append("")
    patients = dataset.patients
    visits = dataset.visits
    candidates = dataset.candidates
    pairs = dataset.pairs
    rows.append(f"- Pasien unik di pasien_sintetis.csv: {patients['patient_id'].nunique():,}")
    rows.append(f"- Encounter unik di kunjungan_sintetis.csv: {visits['encounter_id'].nunique():,}")
    rows.append(f"- Pasangan kunjungan di pasangan_kunjungan.csv: {len(pairs):,}")
    rows.append(f"- Candidate review di hasil_jagapasien_ai.csv: {len(candidates):,}")
    rows.append("")

    rows.append("## 5. Distribusi prioritas")
    rows.append("")
    priority_counts = candidates["prioritas"].value_counts().to_dict()
    rows.append(f"- {priority_counts}")
    rows.append("")

    rows.append("## 6. Jumlah kasus per fasilitas kesehatan")
    rows.append("")
    facility_counts = candidates["faskes"].value_counts().head(10).to_dict()
    rows.append(f"- {facility_counts}")
    rows.append("")

    rows.append("## 7. Nilai kosong dan duplikasi ID")
    rows.append("")
    rows.append(f"- Nilai kosong total pada candidate: {int(candidates.isna().sum().sum()):,}")
    rows.append(f"- Nilai kosong total pada pasangan: {int(pairs.isna().sum().sum()):,}")
    rows.append(f"- Duplikasi case_id pada candidate: {int(candidates['case_id'].duplicated().sum()):,}")
    rows.append(f"- Duplikasi patient_id pada candidate: {int(candidates['patient_id'].duplicated().sum()):,}")
    rows.append(f"- Duplikasi encounter_id pada kunjungan: {int(visits['encounter_id'].duplicated().sum()):,}")
    rows.append("")

    rows.append("## 8. Tanggal tidak valid")
    rows.append("")
    rows.append(f"- Tanggal tidak valid pada candidate tanggal_1: {count_invalid_dates(candidates['tanggal_1'])}")
    rows.append(f"- Tanggal tidak valid pada candidate tanggal_2: {count_invalid_dates(candidates['tanggal_2'])}")
    rows.append(f"- Tanggal tidak valid pada pasangan tanggal_1: {count_invalid_dates(pairs['tanggal_1'])}")
    rows.append(f"- Tanggal tidak valid pada pasangan tanggal_2: {count_invalid_dates(pairs['tanggal_2'])}")
    rows.append("")

    rows.append("## 9. Pasangan dengan tanggal dan jam identik")
    rows.append("")
    same_datetime = ((pairs['tanggal_1'] == pairs['tanggal_2']) & (pairs['waktu_identik'] == 1)).sum()
    rows.append(f"- Pasangan data pasangan_kunjungan.csv dengan tanggal dan jam identik: {int(same_datetime):,}")
    rows.append(f"- Candidate review dengan tanggal dan jam identik: {int(((candidates['tanggal_1'] == candidates['tanggal_2']) & (candidates['waktu_identik'] == 1)).sum()):,}")
    rows.append("")

    rows.append("## 10. Kasus dengan skor prioritas identik")
    rows.append("")
    same_priority_score = int(candidates.duplicated(subset=['skor_prioritas']).sum())
    rows.append(f"- Jumlah baris kandidat dengan skor_prioritas yang sama persis dengan baris lain: {same_priority_score:,} dari {len(candidates):,}")
    rows.append("")

    rows.append("## 11. Persentil anomali berulang")
    rows.append("")
    repeated_pct = int(candidates['persentil_anomali'].duplicated().sum())
    rows.append(f"- Persentil anomali yang berulang di candidate: {repeated_pct:,}")
    rows.append("")

    rows.append("## 12. Kesesuaian ringkasan CSV dan JSON")
    rows.append("")
    metadata_path = ROOT_DIR / 'metadata.json'
    training_path = ROOT_DIR / 'ringkasan_training.json'
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    training = json.loads(training_path.read_text(encoding='utf-8'))
    rows.append(f"- metadata.json: jumlah_kandidat={metadata.get('jumlah_kandidat')}, pasangan_dikecualikan={metadata.get('pasangan_dikecualikan')}")
    rows.append(f"- ringkasan_training.json: kandidat_review={training.get('kandidat_review')}, pasangan_dengan_pengecualian={training.get('pasangan_dengan_pengecualian')}")
    diff_candidate = training.get('kandidat_review', 0) - metadata.get('jumlah_kandidat', 0)
    diff_exclusion = training.get('pasangan_dengan_pengecualian', 0) - metadata.get('pasangan_dikecualikan', 0)
    rows.append(f"- Selisih kandidat: {diff_candidate}")
    rows.append(f"- Selisih pasangan dengan pengecualian: {diff_exclusion}")
    rows.append("")
    rows.append("Berdasarkan bukti yang tersedia, selisih 62 kandidat tidak dapat dijelaskan secara definitif dari kolom yang ada. Hal ini tampak sebagai perbedaan antara ringkasan tahap pembangkitan data dan ringkasan tahap analisis model yang belum direkonsiliasi.")
    rows.append("")
    rows.append("## 13. Keterbatasan interpretasi")
    rows.append("")
    rows.append("Kolom yang tersedia mencakup atribut seperti diagnosis, dokter, poli, tanggal, jam, dan indikator hasil model. Namun, tanpa rekam medis lengkap, nomor klaim, atau bukti audit manual yang terstruktur, belum dapat dibedakan secara meyakinkan antara duplikasi dokumentasi dan fragmentasi pelayanan. Oleh karena itu, interpretasi harus tetap bersifat indikatif dan memerlukan telaah manusia.")

    return "\n".join(rows) + "\n"


def main() -> None:
    report = build_report()
    output_path = ROOT_DIR / 'docs' / 'AUDIT_DATA.md'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')
    print(report)


if __name__ == "__main__":
    main()
