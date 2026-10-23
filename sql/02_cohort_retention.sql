-- ==============================================================================
-- 02_cohort_retention.sql
-- Proyek: Full-Cycle Telco Churn Analysis & Prediction
-- Track: Analytics (Cohort & Retention Analysis)
-- Deskripsi: Analisis masa retensi pelanggan, kohort tenure, kurva churn per kuartil,
--            dan matriks bahaya retensi (Tenure x Kontrak).
-- ==============================================================================

-- 1. Analisis Kohort Siklus Hidup Pelanggan (Tenure Cohorts)
SELECT
    CASE 
        WHEN tenure <= 12 THEN '01. 0-12 Bulan (Baru)'
        WHEN tenure <= 24 THEN '02. 13-24 Bulan'
        WHEN tenure <= 48 THEN '03. 25-48 Bulan'
        ELSE '04. 49-72 Bulan (Loyal)'
    END AS tenure_cohort,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) AS lost_mrr_cohort
FROM telco_churn_clean
GROUP BY 1
ORDER BY 1;

-- 2. Matriks Bahaya Retensi: Interaksi Kelompok Tenure x Tipe Kontrak
SELECT
    CASE 
        WHEN tenure <= 12 THEN '0-12 Bulan'
        WHEN tenure <= 24 THEN '13-24 Bulan'
        WHEN tenure <= 48 THEN '25-48 Bulan'
        ELSE '49-72 Bulan'
    END AS tenure_group,
    contract,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_count,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS churn_rate_pct
FROM telco_churn_clean
GROUP BY 1, contract
ORDER BY 1, churn_rate_pct DESC;

-- 3. Deteksi Titik Churn Awal (Critical First Year Milestones: Bulan 1 - 6)
SELECT
    tenure AS tenure_month,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS churn_rate_pct
FROM telco_churn_clean
WHERE tenure <= 6
GROUP BY tenure
ORDER BY tenure ASC;
