# Metodologi JagaPasien AI

## Pengantar
Prototipe JagaPasien AI dirancang sebagai alat pendukung telaah pola kunjungan pasien JKN berbasis data sintetis. Fokus utama adalah memprioritaskan pasangan kunjungan yang memerlukan pemeriksaan lebih lanjut, bukan menilai fraud secara otomatis.

## Data yang digunakan
Dataset yang digunakan dalam prototipe berasal dari data sintetis dengan total pasien 10.000 dan total kunjungan 35.009. File utama yang dipakai mencakup:

- hasil_jagapasien_ai.csv
- pasangan_kunjungan.csv
- pasien_sintetis.csv
- kunjungan_sintetis.csv

## Isolation Forest
Isolation Forest adalah algoritma unsupervised yang membangun pohon isolasi dan mengukur seberapa mudah sebuah titik dapat diisolasi dari data lain. Semakin mudah terisolasi, semakin tidak biasa pola tersebut dalam distribusi data.

Dalam konteks prototipe ini, model digunakan untuk mengidentifikasi pasangan kunjungan yang relatif jarang terjadi dibanding pola umum yang muncul pada data sintetis. Hasilnya adalah skor anomali dan prioritas review, bukan probabilitas fraud.

## Fitur yang menjadi pertimbangan
Fitur yang tersedia dalam dataset mencakup:

- jarak hari antarkunjungan
- kesamaan diagnosis
- kesamaan dokter
- kesamaan poli
- tanggal dan jam identik
- status lengkap
- ada_igd
- kontrol_terjadwal
- monitoring_kronis
- pasien_kronis
- pengecualian klinis

## Pasangan kunjungan
Pasangan kunjungan dibentuk dari kombinasi encounter yang dianalisis secara terstruktur. Setiap baris pada pasangan_kunjungan.csv merepresentasikan dua encounter yang dibandingkan untuk melihat pola kunjungan, jarak waktu, kesesuaian diagnosis, dan sinyal lain yang relevan.

## Pengecualian klinis
Pengecualian klinis diambil dari variabel yang tersedia dalam dataset pasangan. Variabel ini tidak dimaksudkan sebagai diagnosis klinis, melainkan sebagai indikator awal untuk membatasi atau menandai kasus yang membutuhkan konteks klinis yang lebih jelas.

## Prioritas review
Prioritas review diperoleh dari kombinasi pemeringkatan sinyal yang tersedia pada artefak hasil model, seperti skor anomali, persentil anomali, status review, dan indikator kesamaan temuan. Nilai tersebut termasuk Tinggi, Sedang, dan Rendah, yang digunakan untuk menghasilkan daftar prioritas dalam dashboard.

## Batasan ilmiah
- Dataset sintetis hanya merepresentasikan pola simulasi.
- Tidak tersedia label fraud aktual.
- Tidak ada validasi klinis pada data nyata.
- Skor anomali bukan probabilitas fraud.
- Kesimpulan final tetap memerlukan review rekam medis dan konteks pelayanan.

## Kesimpulan
Metodologi yang digunakan masih bersifat proof of concept dan tidak dimaksudkan sebagai produksi analitik klinis. Kebermanfaatannya terletak pada kemampuan menyorot pola yang memerlukan telaah lebih lanjut dengan cara yang transparan dan terukur.
