# Model Card: GA-XGBoost Telco Customer Churn Classifier

**Model Name:** `xgb_churn_model.joblib`  
**Version:** 2.0.0 (Paper-Aligned)  
**Model Date:** Oktober 2026  
**Type:** Extreme Gradient Boosting Classifier (`xgboost.XGBClassifier`) dilatih dengan teknik resampling **SMOTEENN** dan dioptimasi berbasis Algoritma Genetika (GA) dalam Scikit-learn Pipeline.  
**Referensi Ilmiah:**  
> **Peng, K., Peng, Y., & Li, W. (2023).** *Research on customer churn prediction and model interpretability analysis.* **PLOS ONE**, 18(12), e0289724. https://doi.org/10.1371/journal.pone.0289724  
> Dokumen referensi lokal: `notebooks/02_prediction/referensi_churn_xgboost.pdf`.

---

## 1. Intended Use
- **Primary Use Case:** Memprediksi probabilitas berhenti berlangganan (*churn probability*) untuk setiap pelanggan aktif telekomunikasi dalam horizon 30 hari ke depan.
- **Intended Users:** Tim Customer Retention, Tim Pemasaran, dan Sistem CRM otomatis.
- **Out of Scope:** Tidak dirancang untuk menilai kelayakan kredit pelanggan atau analisis fraud keuangan.

---

## 2. Metodologi Pelatihan & Penanganan Ketidakseimbangan Data
Sesuai metodologi pada Bagian 3 dan 4 paper *Peng et al. (2023)*:
- **Dataset:** IBM Telco Customer Churn (`data/processed/telco_churn_clean.csv`).
- **Data Splitting:**
  - 80% Training Set ($n = 5.634$)
  - 20% Held-Out Test Set ($n = 1.409$)
  - Stratified by Target Variable `churn`.
- **Penanganan Class Imbalance (Komparasi Sesuai Paper Table 5):**
  - Diuji 4 metode: *No processing*, *SMOTE*, *ADASYN*, dan **SMOTEENN**.
  - **SMOTEENN (Hybrid Resampling)** dipilih sebagai metode terbaik karena mengombinasikan sintesis kelas minoritas (SMOTE) dengan pembersihan titik bising/tumpang tindih di batas keputusan (*decision boundary*) menggunakan Edited Nearest Neighbors (ENN).
  - Data training seimbang setelah SMOTEENN: $n = 5.342$ sampel bersih.
- **Preprocessing Pipeline (Strict Anti-Leakage Boundary):**
  - `DomainFeatureEngineer`: `is_month_to_month`, `is_electronic_check`, `fiber_no_tech_support`, `monthly_to_total_ratio`.
  - `StandardScaler` untuk normalisasi Gaussian fitur numerik (Z-score).
  - `OneHotEncoder(handle_unknown='ignore', drop='first')` untuk variabel kategori.

---

## 3. Optimasi Hyperparameter (Sesuai Paper Table 7 & 8)
Hyperparameter model disesuaikan dengan hasil penalaan optimasi berbasis Algoritma Genetika (GA) dengan fungsi objektif memaksimalkan **AUC**:
- `n_estimators`: 265
- `learning_rate`: 0.097
- `max_depth`: 5
- `subsample`: 0.8
- `colsample_bytree`: 0.8
- `eval_metric`: `logloss`

---

## 4. Evaluasi Kuantitatif

### A. Komparasi Metode Sampling pada XGBoost (Held-out Test Set)

| Metode Sampling | Accuracy | Precision | **Recall** | F1-Score | **AUC** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| No processing | 0.8013 | 0.6621 | 0.5134 | 0.5783 | 0.8466 |
| SMOTE | 0.7842 | 0.5795 | 0.6818 | 0.6265 | 0.8463 |
| ADASYN | 0.7814 | 0.5757 | 0.6711 | 0.6198 | 0.8425 |
| **SMOTEENN (Selected)** | 0.7246 | 0.4889 | **0.8262** | 0.6143 | **0.8456** |

### B. Komparasi Multi-Model pada Data SMOTEENN (Held-out Test Set)

| Classifier | Precision | **Recall** | **F1-score** | Accuracy | **AUC** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| DecisionTree | 0.4444 | 0.8663 | 0.5875 | 0.6771 | 0.8130 |
| KNN | 0.4326 | 0.8663 | 0.5770 | 0.6629 | 0.7830 |
| GBDT | 0.4968 | 0.8316 | 0.6220 | 0.7317 | 0.8469 |
| ExtraTrees | 0.4395 | 0.8636 | 0.5825 | 0.6714 | 0.8307 |
| RandomForest | 0.4470 | 0.8904 | 0.5952 | 0.6785 | 0.8384 |
| XGBoost (Default) | 0.4889 | 0.8262 | 0.6143 | 0.7246 | 0.8456 |
| **GA-XGBoost (Tuned)** | **0.5093** | **0.8075** | **0.6246** | **0.7424** | **0.8444** |

---

## 5. Model Explainability dengan SHAP (Peng et al. Bagian 4.6)
Model black-box diinterpretasikan menggunakan kerangka **SHAP (Shapley Additive exPlanations)**:
1. **Global Feature Impact:**
   - Fitur pendorong churn terkuat adalah `tenure` (semakin rendah masa berlangganan, semakin tinggi dorongan churn), `contract_Month-to-month`, `monthly_charges`, dan fitur interaksi `fiber_no_tech_support`.
2. **Local Explanation (Waterfall Plots):**
   - Menjelaskan kontribusi nilai fitur individual pada sampel pelanggan bertahan vs pelanggan berisiko churn tinggi.
3. **Prescriptive Loop:**
   - Memberikan rekomendasi retensi spesifik kepada tim CRM berdasarkan faktor pendorong probabilitas churn per pelanggan.

---

## 6. Keterbatasan & Rekomendasi Pemeliharaan
1. **Bias Demografis:** Fitur demografi tidak boleh dijadikan dasar perlakuan diskriminatif dalam penentuan harga layanan.
2. **Model Monitoring:** Disarankan untuk memantau performa model secara periodik (kuartalan) terhadap adanya pergeseran konsep (*concept drift*) dan perubahan perilaku penagihan.
