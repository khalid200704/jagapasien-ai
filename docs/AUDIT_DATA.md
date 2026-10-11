# Audit Dataset JagaPasien AI

## 1. File yang tersedia

- .gitignore
- README.md
- app.py
- hasil_jagapasien_ai.csv
- kandidat_review.csv
- kesehatan2.py
- kunjungan_sintetis.csv
- metadata.json
- model_jagapasien.joblib
- output.txt
- pasangan_kunjungan.csv
- pasien_sintetis.csv
- requirements.txt
- ringkasan_training.json

## 2. Ringkasan jumlah baris per CSV

- hasil_jagapasien_ai.csv: 6,114 baris
- pasangan_kunjungan.csv: 13,149 baris
- pasien_sintetis.csv: 10,000 baris
- kunjungan_sintetis.csv: 35,009 baris

## 3. Pemeriksaan kolom dan tipe data

### hasil_jagapasien_ai.csv
Jumlah kolom: 29
- case_id: str
- patient_id: str
- faskes: str
- encounter_1: str
- encounter_2: str
- tanggal_1: str
- tanggal_2: str
- jarak_hari: int64
- diagnosis_1: str
- diagnosis_2: str
- diagnosis_sama: int64
- dokter_sama: int64
- poli_sama: int64
- waktu_identik: int64
- status_lengkap: int64
- ada_igd: int64
- kontrol_terjadwal: int64
- monitoring_kronis: int64
- pasien_kronis: int64
- skor_anomali_raw: float64
- persentil_anomali: float64
- pengecualian_klinis: bool
- kemungkinan_duplikasi: bool
- sinyal_review: bool
- skor_prioritas: int64
- prioritas: str
- alasan: str
- status_review: str
- tipe_data: str

### pasangan_kunjungan.csv
Jumlah kolom: 23
- patient_id: str
- faskes: str
- encounter_1: str
- encounter_2: str
- tanggal_1: str
- tanggal_2: str
- jarak_hari: int64
- diagnosis_1: str
- diagnosis_2: str
- diagnosis_sama: int64
- dokter_sama: int64
- poli_sama: int64
- waktu_identik: int64
- status_lengkap: int64
- ada_igd: int64
- kontrol_terjadwal: int64
- monitoring_kronis: int64
- pasien_kronis: int64
- skor_anomali_raw: float64
- persentil_anomali: float64
- pengecualian_klinis: bool
- kemungkinan_duplikasi: bool
- sinyal_review: bool

### pasien_sintetis.csv
Jumlah kolom: 5
- patient_id: str
- umur: int64
- jenis_kelamin: str
- penyakit_kronis: str
- tipe_data: str

### kunjungan_sintetis.csv
Jumlah kolom: 15
- encounter_id: str
- patient_id: str
- faskes: str
- tanggal: str
- jam: str
- hari_index: int64
- diagnosis_kode: str
- diagnosis_nama: str
- poli: str
- dokter: str
- jenis_layanan: str
- status: str
- kontrol_terjadwal: str
- monitoring_kronis: str
- tipe_data: str

## 4. Jumlah pasien unik, encounter unik, dan kandidat

- Pasien unik di pasien_sintetis.csv: 10,000
- Encounter unik di kunjungan_sintetis.csv: 35,009
- Pasangan kunjungan di pasangan_kunjungan.csv: 13,149
- Candidate review di hasil_jagapasien_ai.csv: 6,114

## 5. Distribusi prioritas

- {'Sedang': 5210, 'Rendah': 609, 'Tinggi': 295}

## 6. Jumlah kasus per fasilitas kesehatan

- {'FASKES-SYN-10': 551, 'FASKES-SYN-04': 546, 'FASKES-SYN-08': 533, 'FASKES-SYN-05': 532, 'FASKES-SYN-01': 515, 'FASKES-SYN-09': 515, 'FASKES-SYN-02': 509, 'FASKES-SYN-12': 505, 'FASKES-SYN-07': 498, 'FASKES-SYN-03': 477}

## 7. Nilai kosong dan duplikasi ID

- Nilai kosong total pada candidate: 0
- Nilai kosong total pada pasangan: 0
- Duplikasi case_id pada candidate: 0
- Duplikasi patient_id pada candidate: 1,786
- Duplikasi encounter_id pada kunjungan: 0

## 8. Tanggal tidak valid

- Tanggal tidak valid pada candidate tanggal_1: 0
- Tanggal tidak valid pada candidate tanggal_2: 0
- Tanggal tidak valid pada pasangan tanggal_1: 0
- Tanggal tidak valid pada pasangan tanggal_2: 0

## 9. Pasangan dengan tanggal dan jam identik

- Pasangan data pasangan_kunjungan.csv dengan tanggal dan jam identik: 360
- Candidate review dengan tanggal dan jam identik: 310

## 10. Kasus dengan skor prioritas identik

- Jumlah baris kandidat dengan skor_prioritas yang sama persis dengan baris lain: 6,104 dari 6,114

## 11. Persentil anomali berulang

- Persentil anomali yang berulang di candidate: 6,027

## 12. Kesesuaian ringkasan CSV dan JSON

- metadata.json: jumlah_kandidat=6052, pasangan_dikecualikan=4811
- ringkasan_training.json: kandidat_review=6114, pasangan_dengan_pengecualian=4749
- Selisih kandidat: 62
- Selisih pasangan dengan pengecualian: -62

Berdasarkan bukti yang tersedia, selisih 62 kandidat tidak dapat dijelaskan secara definitif dari kolom yang ada. Hal ini tampak sebagai perbedaan antara ringkasan tahap pembangkitan data dan ringkasan tahap analisis model yang belum direkonsiliasi.

## 13. Keterbatasan interpretasi

Kolom yang tersedia mencakup atribut seperti diagnosis, dokter, poli, tanggal, jam, dan indikator hasil model. Namun, tanpa rekam medis lengkap, nomor klaim, atau bukti audit manual yang terstruktur, belum dapat dibedakan secara meyakinkan antara duplikasi dokumentasi dan fragmentasi pelayanan. Oleh karena itu, interpretasi harus tetap bersifat indikatif dan memerlukan telaah manusia.
