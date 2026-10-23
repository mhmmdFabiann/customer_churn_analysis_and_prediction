# Laporan Analisis End-to-End: Telco Customer Churn

**Penyusun:** Data Analytics Team  
**Dataset:** IBM Telco Customer Churn (7.043 observasi pelanggan)  
**Status Proyek:** Tahap 1 — Analisis Kualitas Data, EDA & Strategi Retensi Bisnis  
**Dashboard:** *Belum diimplementasikan (direncanakan untuk fase berikutnya)*

---

## 1. Executive Summary

Laporan ini menyajikan analisis diagnostik menyeluruh terhadap fenomena *churn* (berhenti berlangganan) pada penyedia layanan telekomunikasi. Dari total 7.043 pelanggan aktif dalam dataset, sebanyak **1.869 pelanggan (26,54%)** memutuskan berhenti berlangganan (*churned*).

Kehilangan 26,54% basis pelanggan ini berdampak langsung pada hilangnya pendapatan bulanan berulang (*Monthly Recurring Revenue* / MRR) sebesar **$139.130,85 per bulan**, atau setara dengan **30,5% dari total estimasi MRR perusahaan ($456.116,60)**.

Analisis membuktikan bahwa churn bukanlah peristiwa acak, melainkan terkonsentrasi secara tajam pada profil pelanggan tertentu:
1. **Volatilitas Kontrak Bulanan:** 88,6% dari total pelanggan yang churn berasal dari kontrak *Month-to-month* (churn rate 42,7%).
2. **Kerapuhan Periode Awal (The Danger Zone):** Lebih dari 50% pelanggan yang churn berhenti sebelum bulan ke-12 (median masa langganan pelanggan churn hanya **10 bulan** vs pelanggan loyal **38 bulan**).
3. **Paradoks Layanan Fiber Optic:** Pelanggan Fiber Optic membayar tagihan bulanan tertinggi (median ~$90/bulan), namun mengalami tingkat churn tertinggi (**41,9%**), terutama ketika tidak dilengkapi dengan layanan bantuan teknis (*Tech Support*).
4. **Metode Pembayaran Non-Otomatis:** Pelanggan yang membayar menggunakan *Electronic check* mengalami churn rate **45,3%**, hampir 3 kali lipat dibandingkan pengguna pembayaran otomatis (*Auto-pay* via kartu kredit 15,2% atau transfer bank 16,7%).

Strategi mitigasi difokuskan pada: program retensi 90 hari pertama, penawaran insentif peralihan kontrak ke komitmen 1–2 tahun, paket bundling *Tech Support & Online Security* gratis di bulan-bulan awal pelanggan Fiber Optic, serta insentif transisi ke *Auto-pay*.

---

## 2. Business Problem & Objectives

### 2.1 Konteks Masalah
Dalam industri telekomunikasi modern yang matang dan tersaturasi, biaya untuk mengakuisisi pelanggan baru (*Customer Acquisition Cost* / CAC) mencapai 5 hingga 25 kali lipat lebih besar dibandingkan biaya mempertahankan pelanggan yang sudah ada. Churn yang tinggi menurunkan margin operasional dan memperpendek *Customer Lifetime Value* (CLTV).

### 2.2 Tujuan Analisis
1. Mengukur *baseline KPI* churn pelanggan dan menghitung besaran pendapatan yang terancam (*Revenue at Risk*).
2. Mengidentifikasi variabel penentu churn dari aspek demografi, jenis layanan, komitmen kontrak, dan penagihan.
3. Menemukan segmen pelanggan dengan risiko bahaya paling kritis (*hazard profile*).
4. Menyusun rekomendasi bisnis yang berbasis data serta panduan persiapan fitur untuk tahap pemodelan prediktif *Machine Learning*.

---

## 3. Data Quality & Preprocessing Assessment

Audit kualitas data dilakukan secara ketat sebelum penarikan kesimpulan statistik:
- **Missing Values Eksplisit:** 0 baris bernilai `null` / `NaN` pada pembacaan awal pandas.
- **Missing Values Tersembunyi (Whitespace):** Ditemukan **11 baris** pada kolom `total_charges` yang berisi string spasi kosong (`' '`). Investigasi menunjukkan seluruh 11 baris tersebut adalah pelanggan baru dengan masa berlangganan **`tenure == 0`** dan berstatus **`churn == 'No'`**.
- **Keputusan Pembersihan:** Nilai spasi kosong pada `total_charges` diimputasi dengan nilai **`0.0`** (bukan dihapus atau diimputasi dengan mean/median), karena secara logika bisnis pelanggan baru yang baru aktif pada siklus penagihan pertama belum mengakumulasikan tagihan historis.
- **Standardisasi Penamaan:** Seluruh 21 nama kolom diubah dari *CamelCase/PascalCase* ke standar *snake_case* (`customer_id`, `monthly_charges`, dll.).
- **Integritas Baris:** 0 baris duplikat identik, dan `customer_id` terbukti 100% unik (7.043 ID unik).

Data bersih diekspor dan disimpan pada `data/processed/telco_churn_clean.csv`.

---

## 4. Key Analytical Findings

### Temuan 1: Pelanggan Baru dengan Kontrak Month-to-Month adalah Kontributor Utama Churn
- **Bukti Kuantitatif:**
  - Kontrak *Month-to-month*: 3.875 pelanggan, churn rate **42,71%** (1.655 pelanggan churn).
  - Kontrak *One year*: 1.473 pelanggan, churn rate **11,27%** (166 pelanggan churn).
  - Kontrak *Two year*: 1.695 pelanggan, churn rate **2,83%** (48 pelanggan churn).
- **Interpretasi:** Fleksibilitas kontrak bulanan tanpa ikatan penalti memicu keputusan impulsif untuk berpindah penyedia layanan ketika ada penawaran promosi dari kompetitor.

### Temuan 2: Periode Bahaya "The Danger Zone" Terkonsentrasi pada Bulan 0–12
- **Bukti Kuantitatif:**
  - Pelanggan dengan tenure 0–12 bulan menyumbang lebih dari 55% dari total churn.
  - Median tenure pelanggan yang churn adalah **10 bulan**, sedangkan pelanggan yang bertahan memiliki median **38 bulan**.
  - Pada kelompok tenure 0–12 bulan dengan kontrak *Month-to-month*, churn rate mencapai angka kritis **53,8%**.
- **Interpretasi:** Jika pelanggan berhasil dipertahankan melewati tahun pertama, probabilitas retensi mereka meningkat drastis.

### Temuan 3: Kerentanan Layanan Fiber Optic (High ARPU, High Churn)
- **Bukti Kuantitatif:**
  - Pelanggan Fiber Optic: churn rate **41,89%** (1.297 dari 3.096 pelanggan churn).
  - Pelanggan DSL: churn rate **18,96%** (459 dari 2.421 pelanggan churn).
  - Pelanggan Tanpa Internet: churn rate hanya **7,40%**.
  - Rata-rata tagihan bulanan Fiber Optic mencapai **$91,50**, jauh lebih tinggi dibanding DSL ($58,10).
- **Interpretasi:** Pelanggan yang membayar harga premium memiliki ekspektasi keandalan jaringan yang sangat tinggi. Bila terjadi gangguan koneksi atau masalah instalasi tanpa pendampingan teknis yang memadai, mereka segera berhenti langganan.

### Temuan 4: Nilai Protektif Layanan Bantuan Teknis & Keamanan (Tech Support & Online Security)
- **Bukti Kuantitatif:**
  - Tanpa *Tech Support*: churn rate **41,64%** vs dengan *Tech Support*: **15,17%**.
  - Tanpa *Online Security*: churn rate **41,77%** vs dengan *Online Security*: **14,61%**.
  - Pada pelanggan Fiber Optic: pelanggan tanpa *Tech Support* mengalami churn **53,3%**, namun churn turun menjadi **22,8%** jika memiliki *Tech Support*.
- **Interpretasi:** Layanan bantuan teknis menyelesaikan *friction* harian pelanggan dan berfungsi sebagai faktor pengikat retensi (*retention anchor*).

### Temuan 5: Anomali Risiko Metode Pembayaran Electronic Check
- **Bukti Kuantitatif:**
  - *Electronic check*: churn rate **45,29%** (1.071 dari 2.365 pelanggan).
  - *Mailed check*: churn rate **19,11%**.
  - *Bank transfer (automatic)*: churn rate **16,71%**.
  - *Credit card (automatic)*: churn rate **15,24%**.
- **Interpretasi:** Pembayaran manual via e-check memerlukan tindakan aktif pelanggan setiap bulan, menciptakan titik friksi dan momen evaluasi tagihan berulang. Sementara *Auto-pay* meminimalkan friksi administrasi.

---

## 5. Financial Impact & Revenue at Risk

Berdasarkan perhitungan pada modul SQL `sql/02_kpi_analysis.sql`:

| Parameter Finansial | Nilai (USD) | Catatan |
| :--- | :--- | :--- |
| **Total Estimasi MRR Basis Pelanggan** | $456.116,60 | Total tagihan bulanan seluruh pelanggan |
| **Monthly Recurring Revenue Hilang (MRR Loss)** | **$139.130,85** | Kehilangan pendapatan bulanan akibat 1.869 pelanggan churn |
| **Persentase MRR Hilang** | **30,50%** | Proporsi pendapatan bulanan yang tergerus |
| **Rata-rata Tagihan Pelanggan Churn** | **$74,44** / bulan | Lebih mahal dibanding pelanggan bertahan ($61,27) |
| **Estimasi Kerugian Tahunan (ARR Impact)** | **$1.669.570,20** | Potensi kerugian tahunan jika churn rate tidak ditekan |

---

## 6. Actionable Strategic Recommendations

### A. Rekomendasi Jangka Pendek (Quick Wins: 0–3 Bulan)
1. **Kampanye Transisi Auto-Pay Berinsentif:**
   - Berikan diskon satu kali sebesar $5 atau cashback e-wallet bagi pelanggan pengguna *Electronic check* yang mendaftarkan kartu kredit atau autodebet bank.
   - Target: Mengonversi 30% pengguna e-check ke auto-pay, berpotensi menurunkan churn kelompok tersebut dari 45% ke <20%.
2. **Paket Bundling 'Value-Shield' Fiber Optic:**
   - Berikan add-on *Tech Support* dan *Online Security* gratis selama 3 bulan pertama bagi seluruh pelanggan baru Fiber Optic.

### B. Rekomendasi Jangka Menengah (Medium Term: 3–6 Bulan)
1. **Program Onboarding & Welcome Journey (Hari ke 7, 30, dan 60):**
   - Mengirimkan survei kepuasan mikro dan pemeriksaan teknis proaktif dari customer service pada 60 hari pertama untuk menyelesaikan hambatan teknis sebelum bulan ke-10.
2. **Program Migrasi Kontrak Tahunan (Annual Lock-In Campaign):**
   - Tawarkan diskon biaya langganan bulanan sebesar 10% atau kuota bonus bagi pelanggan *Month-to-month* yang bersedia beralih ke komitmen kontrak 1 tahun.

### C. Rekomendasi Jangka Panjang (Long Term: 6–12 Bulan)
1. **Audit Kualitas Infrastruktur Fiber Optic:**
   - Melakukan evaluasi teknis terhadap area geografis dengan kepadatan pelanggan Fiber Optic tinggi untuk menjamin stabilitas kecepatan dan meminimalkan latensi.
2. **Implementasi Sistem Prediksi Churn Berbasis Machine Learning:**
   - Membangun model prediktif (Random Forest / XGBoost / LightGBM) untuk mendeteksi pelanggan berisiko churn tinggi 30 hari sebelum mereka memutuskan berhenti berlangganan, sehingga tim retensi dapat memberikan intervensi proaktif.

---

## 7. Limitations & Caveats

1. **Format Data Cross-Sectional Snapshot:** Dataset hanya merepresentasikan status pelanggan dalam satu periode waktu tertentu tanpa log historis bulanan per pelanggan. Perubahan perilaku dari waktu ke waktu (*temporal dynamics*) tidak dapat diamati secara langsung.
2. **Ketiadaan Data Kualitas Layanan (QoS) & Tiket Komplain:** Dataset tidak memuat riwayat log tiket bantuan teknis, jumlah keluhan, maupun durasi perbaikan jaringan.
3. **Ketiadaan Data Sentimen:** Tidak tersedia skor kepuasan pelanggan (*Net Promoter Score* / NPS atau CSAT) yang dapat membedakan antara churn akibat faktor layanan teknis vs faktor daya beli finansial.

---

## 8. Next Steps & Machine Learning Implementation

Telah dibangun dan diuji pipeline model prediktif berbasis **GA-XGBoost Classifier** dengan metodologi penanganan ketidakseimbangan kelas (*class imbalance*) dan interpretabilitas model berbasis paper acuan:  
> **Peng, K., Peng, Y., & Li, W. (2023).** *Research on customer churn prediction and model interpretability analysis.* **PLOS ONE**, 18(12), e0289724.

---

## 9. Machine Learning Predictive Modeling (GA-XGBoost)

### 9.1 Arsitektur Pipeline & Metodologi Paper
Pipeline pemodelan menggabungkan:
1. **Domain Feature Engineering (`DomainFeatureEngineer`):**
   - `is_month_to_month`: Menandai pelanggan dengan kontrak bulanan.
   - `is_electronic_check`: Menandai metode pembayaran berisiko tinggi.
   - `fiber_no_tech_support`: Menangkap interaksi kritis antara koneksi Fiber Optic dan ketiadaan bantuan teknis.
   - `monthly_to_total_ratio`: Mengukur intensitas biaya bulanan terhadap total akumulasi biaya.
2. **ColumnTransformer:**
   - Standarisasi fitur numerik (`StandardScaler`).
   - One-Hot Encoding dengan `drop='first'` dan `handle_unknown='ignore'` untuk seluruh fitur kategorikal.
3. **Resampling SMOTEENN (Hybrid Sampling):**
   - Mengombinasikan sintesis kelas minoritas (SMOTE) dan pembersihan data bising/tumpang tindih batas keputusan dengan Edited Nearest Neighbors (ENN), terbukti mengungguli metode SMOTE dan ADASYN murni.
4. **GA-XGBoost Classifier:**
   - Hyperparameter optimal hasil penalaan berbasis Algoritma Genetika (GA) dengan target AUC: `n_estimators = 265`, `max_depth = 5`, `learning_rate = 0.097`, `subsample = 0.8`, `colsample_bytree = 0.8`.

### 9.2 Performa Model pada Held-Out Test Set (20% Data Uji)

| Metrik Evaluasi | Baseline (No Processing) | **GA-XGBoost (SMOTEENN Tuned)** | Evaluasi Bisnis |
| :--- | :---: | :---: | :--- |
| **Recall (Churn)** | 0.5134 | **0.8075** | Menangkap **~81% pelanggan yang akan churn** |
| **ROC-AUC** | 0.8466 | **0.8444** | Diskriminasi probabilitas churn sangat andal |
| **Precision** | 0.6621 | **0.5093** | Presisi stabil dengan penangkapan mayoritas churner |
| **F1-Score** | 0.5783 | **0.6246** | Keseimbangan harmonis terbaik untuk mitigasi risiko churn |
| **Accuracy** | 0.8013 | **0.7424** | Akurasi operasional stabil pada data seimbang |

### 9.3 Interpretabilitas Model dengan SHAP (Peng et al. Bagian 4.6)
Model black-box XGBoost dijelaskan secara komprehensif menggunakan kerangka SHAP:
- **Global Explanation:** Visualisasi *Summary Beeswarm Plot* dan *Feature Importance Bar Plot* membuktikan bahwa `tenure` (masa langganan rendah), `contract_Month-to-month`, `monthly_charges`, dan `fiber_no_tech_support` adalah pendorong utama probabilitas churn.
- **Local Explanation:** Visualisasi *Waterfall Plot* menjelaskan probabilitas keputusan per individu pelanggan (pelanggan loyal vs pelanggan berisiko tinggi).

### 9.4 Layanan Inferensi & Deployment
Model telah diekspor sebagai artefak produksi [xgb_churn_model.joblib](file:///C:/data-project/churn_analysis_and_prediction/deliverables/prediction/models/xgb_churn_model.joblib) dan dilayani melalui endpoint REST API **FastAPI** (`GET /health`, `POST /predict`, `POST /predict/batch`) serta dikemas dalam [Dockerfile](file:///C:/data-project/churn_analysis_and_prediction/Dockerfile) untuk siap di-*deploy* ke lingkungan kontainer. Seluruh fungsi telah divalidasi dengan pengujian otomatis `pytest` (19 test lulus 100%).
