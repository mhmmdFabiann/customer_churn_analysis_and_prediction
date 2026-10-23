# Data Dictionary: Telco Customer Churn

Dataset ini berisi informasi profil 7.043 pelanggan penyedia layanan telekomunikasi di California pada kuartal ketiga. Setiap baris merepresentasikan **satu pelanggan unik** (*unit of observation*).

---

## Tabel Metadata Kolom

| Nama Kolom | Tipe Data Asli | Tipe Data Bersih | Kategori | Deskripsi Bisnis | Contoh Nilai |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_id` | `object` | `object` | Identifier | ID unik pengenal pelanggan | `7590-VHVEG`, `5575-GNVDE` |
| `gender` | `object` | `object` | Demografi | Jenis kelamin pelanggan | `Female`, `Male` |
| `senior_citizen` | `int64` | `int64` | Demografi | Indikator apakah pelanggan adalah lansia (1: Ya, 0: Tidak) | `0`, `1` |
| `partner` | `object` | `object` | Demografi | Status pernikahan/memiliki pasangan | `Yes`, `No` |
| `dependents` | `object` | `object` | Demografi | Status memiliki tanggungan (anak/keluarga) | `Yes`, `No` |
| `tenure` | `int64` | `int64` | Akun | Jumlah bulan pelanggan telah berlangganan (0 – 72 bulan) | `1`, `34`, `72` |
| `phone_service` | `object` | `object` | Layanan | Apakah berlangganan telepon rumah | `Yes`, `No` |
| `multiple_lines` | `object` | `object` | Layanan | Apakah memiliki beberapa saluran telepon | `Yes`, `No`, `No phone service` |
| `internet_service` | `object` | `object` | Layanan | Jenis penyedia koneksi internet | `DSL`, `Fiber optic`, `No` |
| `online_security` | `object` | `object` | Layanan (VAS)| Layanan keamanan daring tambahan | `Yes`, `No`, `No internet service` |
| `online_backup` | `object` | `object` | Layanan (VAS)| Layanan pencadangan cloud tambahan | `Yes`, `No`, `No internet service` |
| `device_protection` | `object` | `object` | Layanan (VAS)| Perlindungan asuransi perangkat keras | `Yes`, `No`, `No internet service` |
| `tech_support` | `object` | `object` | Layanan (VAS)| Layanan bantuan teknis prioritas | `Yes`, `No`, `No internet service` |
| `streaming_tv` | `object` | `object` | Layanan | Layanan streaming TV dari penyedia | `Yes`, `No`, `No internet service` |
| `streaming_movies` | `object` | `object` | Layanan | Layanan streaming film dari penyedia | `Yes`, `No`, `No internet service` |
| `contract` | `object` | `object` | Akun | Ketentuan komitmen kontrak berlangganan | `Month-to-month`, `One year`, `Two year` |
| `paperless_billing` | `object` | `object` | Penagihan | Apakah menggunakan tagihan digital tanpa kertas | `Yes`, `No` |
| `payment_method` | `object` | `object` | Penagihan | Metode pembayaran tagihan bulanan | `Electronic check`, `Mailed check`, `Bank transfer`, `Credit card` |
| `monthly_charges` | `float64` | `float64` | Finansial | Biaya tagihan bulanan pelanggan dalam USD ($18.25 – $118.75) | `29.85`, `70.70`, `108.15` |
| `total_charges` | `object` | `float64` | Finansial | Total akumulasi biaya yang telah dibayarkan ($0.0 – $8,684.80) | `29.85`, `1889.5` (11 spasi `' '` diimputasi `0.0` karena `tenure=0`) |
| `churn` | `object` | `object` | Target | Status penghentian langganan dalam bulan terakhir | `Yes` (26,5%), `No` (73,5%) |

---

## Catatan Aturan Bisnis & Validitas Data
1. **Total Charges vs Tenure:** Pelanggan dengan `tenure == 0` belum melalui siklus penagihan pertama sehingga `total_charges` bernilai `0.0`.
2. **Ketergantungan Layanan:** Pelanggan tanpa `phone_service` otomatis memiliki `multiple_lines == 'No phone service'`. Pelanggan tanpa `internet_service` otomatis memiliki nilai `'No internet service'` pada seluruh layanan pendukung (VAS).
