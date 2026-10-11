# Batasan JagaPasien AI

## Data sintetis
Semua data yang dipakai dalam prototipe adalah data sintetis. Dengan demikian, hasil analisis harus dipahami sebagai simulasi pola, bukan representasi praktik pelayanan nyata.

## Bukan keputusan claim
Prototipe ini tidak digunakan untuk menetapkan fraud, melanggar prosedur klaim, atau menggantikan standar kepatuhan dan evaluasi klinis.

## Tidak ada label ground truth
Tidak tersedia label audit klinis atau label fraud aktual pada data. Oleh karena itu, tidak ada ukuran precision, recall, atau F1-score yang dapat dinyatakan sebagai valid untuk dunia nyata.

## Anomali statistik bukan diagnosis
Skor anomali dan persentil anomali hanya menunjukkan bahwa suatu pola relatif jarang terjadi dalam data. Nilai ini tidak sama dengan diagnosis medis atau pembuktian pelanggaran.

## Perbedaan ringkasan belum direkonsiliasi
Terdapat perbedaan antara ringkasan metadata.json dan ringkasan_training.json. Berdasarkan bukti yang tersedia, perbedaan ini belum dapat dijelaskan secara definitif. Karena itu, dokumentasi tetap mencatat adanya perbedaan antar tahap analisis yang belum direkonsiliasi.

## Keterbatasan interpretasi
Tanpa rekam medis, data klaim, atau konteks klinis yang lengkap, tidak dapat dibedakan dengan meyakinkan antara duplikasi dokumentasi dan fragmentasi pelayanan. Dalam keadaan seperti ini, tugas manusia tetap wajib dilaksanakan sebagai review final.
