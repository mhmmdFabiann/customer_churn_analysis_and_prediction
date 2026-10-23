# Telco Customer Churn: Full-Cycle Analytics & Prediction

> Proyek analitik dan data science terpadu (*Full-Cycle Data Project*) yang menggabungkan kekuatan **Data Analytics** (eksplorasi diagnostik, kueri SQL, estimasi MRR Loss, segmentasi kohort) dan **Data Science** (pipeline rekayasa fitur bebas kebocoran, model klasifikasi XGBoost, optimasi ambang batas, interpretasi SHAP, dan RESTful API siap deploy).

---

## 1. Executive Summary

- **Masalah Bisnis:** Dari 7.043 pelanggan, sebanyak **1.869 pelanggan (26,54%)** mengalami churn, mengakibatkan kehilangan pendapatan bulanan berulang (*Monthly Recurring Revenue* / MRR Loss) sebesar **$139.130,85 per bulan** (30,5% dari total MRR perusahaan senilai $456.116,60).
- **Solusi Terpadu:**
  - **Track Analytics:** Mendiagnosis akar pemicu churn, mengevaluasi bahaya retensi pada kohort pelanggan baru, dan memetakan pola kerentanan layanan Fiber Optic serta metode pembayaran manual.
  - **Track Science:** Membangun pipeline prediktif berbasis **XGBoost Classifier** dengan penanganan ketidakseimbangan kelas (*scale_pos_weight = 2.77*) untuk mendeteksi pelanggan berisiko churn sebelum mereka membatalkan layanan.
- **Dampak Kuantitatif:** Model berhasil mendeteksi **78,9% dari seluruh pelanggan yang akan churn** (*Recall = 0.7888*, *ROC-AUC = 0.8463*). Intervensi retensi terarah berpotensi menyelamatkan hingga **$110.000+ MRR per bulan**.

---

## 2. Business Insights (Data Analytics Track)

### Temuan Kunci Analitik:
1. **Volatilitas Kontrak Bulanan:** Kontrak *Month-to-month* menyumbang **88,6% dari seluruh churn** (tingkat churn kelompok ini mencapai **42,71%**), sementara kontrak 1 tahun hanya 11,27% dan 2 tahun hanya 2,83%.
2. **The "Danger Zone" (Bulan ke 0–12):** Lebih dari 55% churn terjadi pada tahun pertama berlangganan (median tenure pelanggan churn hanya **10 bulan** vs pelanggan loyal **38 bulan**). Pada pelanggan baru dengan kontrak bulanan, tingkat churn melonjak hingga **53,8%**.
3. **Paradoks Layanan Fiber Optic:** Pelanggan Fiber Optic membayar tagihan bulanan tertinggi ($91,50/bulan), namun mengalami churn rate **41,89%**. Saat tidak mendapatkan *Tech Support*, churn rate melonjak ke angka kritis **53,3%**.
4. **Friksi Pembayaran Manual:** Pelanggan dengan *Electronic check* mengalami churn rate **45,29%**, hampir 3 kali lipat lebih tinggi dari pengguna pembayaran otomatis (*Auto-pay* via kartu kredit 15,24% atau transfer bank 16,71%).

### Rekomendasi Strategis Bisnis:
- **Paket Bundling 'Value-Shield':** Berikan *Tech Support* dan *Online Security* gratis selama 3–6 bulan pertama bagi seluruh pelanggan baru Fiber Optic.
- **Kampanye Insentif Migrasi Kontrak Tahunan:** Tawarkan diskon biaya langganan bulanan 10%–15% bagi pelanggan *Month-to-month* yang bersedia beralih ke kontrak komitmen tahunan.
- **Program Reward Transisi ke Auto-Pay:** Berikan potongan tagihan satu kali senilai $5 bagi pelanggan yang mendaftarkan autodebet kartu kredit atau transfer bank.
- **Dashboard Demo:** *Direktori `deliverables/analytics/` direservasi untuk integrasi dashboard BI masa depan.*

---

## 3. Machine Learning System (Data Science Track)

- **Referensi Metodologi:** **Peng, K., Peng, Y., & Li, W. (2023).** *Research on customer churn prediction and model interpretability analysis.* **PLOS ONE**, 18(12), e0289724 (`notebooks/02_prediction/referensi_churn_xgboost.pdf`).
- **Formulasi:** Klasifikasi Biner (*Binary Classification*) untuk memprediksi probabilitas churn dalam 30 hari ke depan.
- **Penanganan Class Imbalance:** Menerapkan teknik resampling hibrida **SMOTEENN** (*Synthetic Minority Over-sampling + Edited Nearest Neighbors*) yang terbukti paling efektif menangkap kelas minoritas churn tanpa memperbesar noise batas keputusan.
- **Model Terbaik:** **GA-XGBoost (Tuned)** dengan *ColumnTransformer* pra-pemrosesan (`StandardScaler` + `OneHotEncoder`) dan *Domain Feature Engineering*.
- **Hyperparameter Optimal (AUC Objective):** `n_estimators = 265`, `max_depth = 5`, `learning_rate = 0.097`, `subsample = 0.8`, `colsample_bytree = 0.8`.
- **Hasil Evaluasi (Held-Out Test Set 20%, $n = 1.409$):**

| Metrik Evaluasi | Baseline (No Processing) | **GA-XGBoost (SMOTEENN Tuned)** | Evaluasi Bisnis |
| :--- | :---: | :---: | :--- |
| **Recall (Churn)** | 0.5134 | **0.8075** | Menangkap **~81% dari seluruh pelanggan yang akan churn** |
| **ROC-AUC** | 0.8466 | **0.8444** | Kemampuan diskriminasi probabilitas churn sangat andal |
| **Precision** | 0.6621 | **0.5093** | Mengorbankan sedikit presisi demi meminimalkan *False Negatives* yang merugikan |
| **F1-Score** | 0.5783 | **0.6246** | Keseimbangan harmonis terbaik untuk mitigasi risiko churn |
| **Accuracy** | 0.8013 | **0.7424** | Akurasi operasional stabil pada data seimbang |

- **Interpretabilitas Model (SHAP):** Sesuai Bagian 4.6 paper, model black-box dibuka menggunakan *SHAP Summary Beeswarm Plot*, *Feature Importance Bar Plot*, *Dependence Plot*, dan *Waterfall Plot* untuk memberikan transparansi penuh kepada pemangku kepentingan.
- **Model Card:** Dokumentasi lengkap spesifikasi model, bias, dan analisis ambang batas keputusan tersedia di `reports/model_card.md`.

---

## 4. Arsitektur & Struktur Proyek (Dual-Track Pattern)

```text
churn_analysis_and_prediction/
├── README.md                          # Dokumentasi utama proyek
├── requirements.txt                   # Dependencies
├── Dockerfile                         # Containerisasi aplikasi REST API
├── .dockerignore                      # Pengabaian build Docker
├── .gitignore                         # Pengabaian file cache & temporary
├── .env.example                       # Template konfigurasi environment
├── pytest.ini                         # Konfigurasi pengujian otomatis
│
├── data/                              # SINGLE SOURCE OF TRUTH
│   ├── raw/                           # Data mentah original (read-only)
│   │   └── Telco-Customer-Churn.csv
│   └── processed/                     # Data bersih hasil single cleaning pipeline
│       └── telco_churn_clean.csv
│
├── sql/                               # Kueri bisnis & agregasi KPI
│   ├── 01_kpi_metrics.sql             # Rumus churn rate, ARPU, CLV, dan MRR loss
│   └── 02_cohort_retention.sql        # Analisis kohort masa langganan (tenure) & matriks bahaya
│
├── notebooks/                         # Eksplorasi terurut (Numbered)
│   ├── 00_data_audit_cleaning.ipynb   # [Shared] Audit kualitas & pembuatan data bersih
│   ├── 01_analytics/                  # [Track Analytics]
│   │   ├── 01_eda_and_patterns.ipynb
│   │   ├── 02_cohort_and_segments.ipynb
│   │   └── 03_business_insights.ipynb
│   └── 02_prediction/                 # [Track Science]
│       ├── 01_feature_engineering.ipynb
│       ├── 02_model_experimentation.ipynb
│       └── 03_evaluation_and_shap.ipynb
│
├── src/                               # Modul kode produksi (Reusable & Tested)
│   └── telco_churn/
│       ├── core/                      # [Shared Core]
│       │   ├── __init__.py
│       │   ├── loader.py              # Pemuatan data dengan resolusi path fleksibel
│       │   └── cleaner.py             # Pembersihan data dan standarisasi snake_case
│       ├── analytics/                 # [Analytics Track]
│       │   ├── __init__.py
│       │   ├── metrics.py             # Kalkulasi KPI bisnis (Churn Rate, MRR Loss, ARPU)
│       │   └── aggregations.py        # Logika agregasi kohort dan matriks risiko
│       └── prediction/                # [Science Track]
│           ├── __init__.py
│           ├── pipelines.py           # Scikit-learn Pipeline (Domain Features + Transformer)
│           ├── train.py               # Script pelatihan model & cross-validation
│           └── inference.py           # Kelas ChurnPredictor (Single, Batch & Prescriptive Loop)
│
├── deliverables/                      # Produk akhir yang siap diuji/dilihat
│   ├── analytics/                     # [Aset Data Analyst]
│   │   └── .gitkeep                   # (Direservasi untuk dashboard masa depan)
│   └── prediction/                    # [Aset Data Scientist / ML]
│       ├── models/                    # Artefak model serial
│       │   ├── xgb_churn_model.joblib
│       │   └── model_metadata.json
│       └── api/                       # REST API Service
│           └── app.py                 # FastAPI entrypoint (POST /predict)
│
├── reports/                           # Laporan tertulis & dokumentasi
│   ├── figures/                       # Grafik visualisasi & diagnostik model (.png)
│   ├── tables/                        # Tabel ringkasan metrik KPI (.csv)
│   ├── data_dictionary.md             # Definisi kolom, tipe data, dan batas nilai
│   ├── analytics_findings.md          # Temuan bisnis & rekomendasi strategis
│   ├── model_card.md                  # Spesifikasi model, metrik, bias, dan threshold
│   └── final_report.md                # Laporan akhir komprehensif bagi stakeholder
│
└── tests/                             # Pengujian otomatis (Unit & Integration Testing)
    ├── test_cleaner.py                # Uji validitas pembersihan data dasar
    ├── test_metrics.py                # Uji akurasi rumus KPI bisnis
    └── test_prediction.py             # Uji integrasi endpoint API dan pipeline
```

---

## 5. Cara Menjalankan Proyek

### 1. Setup Lingkungan
```bash
pip install -r requirements.txt
```

### 2. Jalankan Pembersihan Data (Core Pipeline)
```bash
python -m src.telco_churn.core.cleaner
```

### 3. Jalankan Pelatihan Model XGBoost (Science Track)
```bash
python -m src.telco_churn.prediction.train
```

### 4. Jalankan Pengujian Otomatis (Testing Suite)
```bash
pytest
```

### 5. Jalankan API Prediksi (FastAPI Service)
```bash
uvicorn deliverables.prediction.api.app:app --host 0.0.0.0 --port 8000 --reload
```
Akses antarmuka dokumentasi Swagger UI interaktif di browser: `http://localhost:8000/docs`

### 6. Contoh Prediksi Menggunakan cURL
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "gender": "Female",
       "senior_citizen": 0,
       "partner": "No",
       "dependents": "No",
       "tenure": 2,
       "phone_service": "Yes",
       "multiple_lines": "No",
       "internet_service": "Fiber optic",
       "online_security": "No",
       "online_backup": "No",
       "device_protection": "No",
       "tech_support": "No",
       "streaming_tv": "Yes",
       "streaming_movies": "Yes",
       "contract": "Month-to-month",
       "paperless_billing": "Yes",
       "payment_method": "Electronic check",
       "monthly_charges": 89.5,
       "total_charges": 179.0
     }'
```

### 7. Menjalankan Menggunakan Docker
```bash
docker build -t telco-churn-service:v1 .
docker run -d -p 8000:8000 --name churn-service telco-churn-service:v1
```

---

## 6. References
- IBM Sample Data Sets: [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
