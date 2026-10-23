-- ==============================================================================
-- 01_kpi_metrics.sql
-- Proyek: Full-Cycle Telco Churn Analysis & Prediction
-- Track: Analytics (Business Intelligence & Financial KPIs)
-- Deskripsi: Menghitung metrik finansial utama: Baseline Churn Rate, MRR Loss, 
--            ARPU, CLV (Customer Lifetime Value), Breakdown Segmen & Dampak Pendapatan.
-- ==============================================================================

-- 1. Ringkasan Eksekutif Churn & Pendapatan Bulanan yang Berisiko (MRR Loss)
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS baseline_churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_recurring_revenue,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) AS lost_mrr,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END) / SUM(monthly_charges) * 100, 2) AS pct_mrr_loss,
    ROUND(AVG(monthly_charges), 2) AS overall_arpu,
    ROUND(AVG(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE NULL END), 2) AS churned_arpu,
    ROUND(AVG(CASE WHEN churn = 'No' THEN monthly_charges ELSE NULL END), 2) AS retained_arpu
FROM telco_churn_clean;

-- 2. Customer Lifetime Value (CLV) & Revenue Realization
SELECT
    churn,
    COUNT(*) AS customer_count,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge,
    ROUND(AVG(total_charges), 2) AS avg_realized_clv,
    ROUND(SUM(total_charges), 2) AS cumulative_lifetime_revenue
FROM telco_churn_clean
GROUP BY churn;

-- 3. Breakdown MRR Loss berdasarkan Tipe Kontrak
SELECT
    contract,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) AS contract_mrr_loss
FROM telco_churn_clean
GROUP BY contract
ORDER BY contract_mrr_loss DESC;

-- 4. Breakdown MRR Loss berdasarkan Metode Pembayaran
SELECT
    payment_method,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) AS payment_mrr_loss
FROM telco_churn_clean
GROUP BY payment_method
ORDER BY payment_mrr_loss DESC;

-- 5. Segmen Kritis Berisiko Tertinggi (High-Hazard Cluster)
-- Pelanggan Month-to-month, Fiber optic, Tanpa Tech Support, Pembayaran via Electronic Check
SELECT
    'Segmen Kritis (M2M + Fiber + No TechSupport + E-Check)' AS segment_name,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_count,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS monthly_revenue_at_risk
FROM telco_churn_clean
WHERE contract = 'Month-to-month'
  AND internet_service = 'Fiber optic'
  AND tech_support = 'No'
  AND payment_method = 'Electronic check';
