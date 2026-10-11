# Naskah Submission JagaPasien AI

## Judul proyek
JagaPasien AI — AI untuk Menjaga Kesinambungan Pelayanan Pasien JKN

## Ringkasan eksekutif
JagaPasien AI adalah prototipe dashboard berbasis Python dan Streamlit yang membantu menyorot pasangan kunjungan pasien JKN yang memerlukan telaah lebih lanjut. Prototipe ini dirancang untuk mendukung pemeriksaan awal terhadap pola kunjungan tidak biasa, potensi duplikasi dokumentasi, dan kesenjangan kesinambungan episode pelayanan di dalam data sintetis.

## Masalah yang diangkat
Pelayanan JKN memerlukan alat bantu yang mampu menilai kesesuaian pola kunjungan, mengidentifikasi kemungkinan duplikasi dokumentasi, dan menjaga kesinambungan episode pelayanan. Dalam praktiknya, tim pemeriksa perlu memprioritaskan kasus yang membutuhkan perhatian lebih lanjut tanpa membebani mereka dengan seluruh dataset secara bersamaan.

## Solusi yang ditawarkan
Prototipe ini menyediakan dashboard interaktif yang menampilkan ringkasan data, daftar kandidat review, detail kasus, timeline kunjungan, dan analisis temuan yang bersifat indikatif. Dengan pendekatan berbasis data sintetis dan visualisasi yang jelas, pengguna dapat memprioritaskan kasus untuk telaah manual dengan lebih efektif.

## Keunikan dan inovasi
- Fokus pada kesinambungan episode pelayanan dan pasangan kunjungan.
- Penggunaan analisis tanpa label untuk memprioritaskan pola yang relatif tidak biasa.
- Penjelasan yang transparan tentang batasan dan konteks.
- Dashboard yang mudah diakses secara lokal tanpa kebutuhan cloud atau API berbayar.

## Teknologi yang digunakan
- Python 3.10+
- Streamlit
- Pandas
- Plotly
- scikit-learn
- Joblib
- Pytest

## Metodologi
Prototipe menggunakan Isolation Forest untuk mengidentifikasi pasangan kunjungan yang relatif tidak biasa dalam data sintetis. Data kandidat diperiksa secara eksploratif dan disajikan dalam bentuk dashboard, kemudian divalidasi secara umum dengan pemeriksaan data, prioritas review, dan penjelasan temuan yang disusun berdasarkan kolom yang tersedia.

## Hasil eksperimen
Pada dataset yang tersedia, terdapat 10.000 pasien sintetis, 35.009 kunjungan sintetis, 13.149 pasangan kunjungan dianalisis, dan 6.114 kandidat review. Prioritas review yang terverifikasi dari file hasil adalah 295 tinggi, 5.210 sedang, dan 609 rendah.

## Contoh kasus
Kasus kandidat menampilkan pasangan encounter dengan diagnosis sama, jarak hari yang pendek, dan atribut yang menunjukkan pola tidak biasa. Kasus tersebut perlu ditelaah secara manual untuk mengecek konteks klinis dan kemungkinan duplikasi dokumentasi, tanpa menyimpulkan kesalahan yang telah terbukti.

## Manfaat yang diharapkan
- Mempercepat pemetaan kasus yang memerlukan telaah lebih lanjut.
- Meningkatkan konsistensi interpretasi pola kunjungan.
- Menyediakan basis visual yang komunikatif bagi tim audit dan pemeriksa.
- Memfasilitasi perspektif data yang lebih jelas untuk pengujian prototipe.

## Keterbatasan
- Data bersifat sintetis.
- Tidak ada label fraud aktual.
- Tidak ada validasi klinis pada data rumah sakit nyata.
- Skor dan persentil anomali bukan probabilitas fraud.
- Belum ada rekonsiliasi definitif atas selisih 62 kandidat antara ringkasan metadata dan ringkasan model.

## Rencana pengembangan
- Validasi dengan data pelayanan nyata yang memadai.
- Penguatan aturan pengecualian klinis dan interpretasi temuan.
- Integrasi protokol review manual yang lebih rapi untuk tim audit.
- Penguatan dokumentasi untuk pengujian dan pemeliharaan aplikasi.

## Kesimpulan
JagaPasien AI adalah prototipe pendukung telaah pelayanan pasien JKN yang fokus pada pola kunjungan, prioritas review, dan transparansi interpretasi. Prototipe ini tidak dimaksudkan untuk menggantikan penilaian klinis atau keputusan klaim, tetapi menjadi alat bantu analitik yang berguna untuk eksplorasi, telaah, dan kesiapan protokol audit.
