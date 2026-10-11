-- =============================================================
-- Customer Churn Analysis — SQL queries
-- Table: customers (loaded from data/telco_customers.csv)
-- Written for SQLite, and runs on PostgreSQL / MySQL with minor changes.
-- =============================================================

-- 1. Overall churn rate
SELECT
    COUNT(*)                                                  AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END)            AS churned,
    ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END), 1) AS churn_rate_pct
FROM customers;

-- 2. Churn rate by contract type
SELECT
    contract,
    COUNT(*)                                                  AS customers,
    ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END), 1) AS churn_rate_pct
FROM customers
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- 3. Churn rate by tenure band
SELECT
    CASE
        WHEN tenure_months <= 12 THEN '0-12 months'
        WHEN tenure_months <= 24 THEN '13-24 months'
        WHEN tenure_months <= 48 THEN '25-48 months'
        ELSE '49-72 months'
    END                                                       AS tenure_band,
    COUNT(*)                                                  AS customers,
    ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END), 1) AS churn_rate_pct
FROM customers
GROUP BY tenure_band
ORDER BY tenure_band;

-- 4. Churn rate by payment method
SELECT
    payment_method,
    COUNT(*)                                                  AS customers,
    ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END), 1) AS churn_rate_pct
FROM customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;

-- 5. Monthly revenue lost to churn, by internet service
SELECT
    internet_service,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 0) AS monthly_revenue_lost,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END)
          / SUM(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END)) OVER (), 1)
                                                              AS share_of_loss_pct
FROM customers
GROUP BY internet_service
ORDER BY monthly_revenue_lost DESC;

-- 6. High-risk segment: month-to-month, tenure <= 12, electronic check
WITH segment AS (
    SELECT *
    FROM customers
    WHERE contract = 'Month-to-month'
      AND tenure_months <= 12
      AND payment_method = 'Electronic check'
)
SELECT
    COUNT(*)                                                  AS customers,
    ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END), 1) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2)                            AS avg_monthly_charges
FROM segment;

-- 7. Support calls vs churn (window function: running share of customers)
SELECT
    support_calls,
    COUNT(*)                                                  AS customers,
    ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END), 1) AS churn_rate_pct,
    ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY support_calls)
          / SUM(COUNT(*)) OVER (), 1)                         AS cumulative_pct_customers
FROM customers
GROUP BY support_calls
ORDER BY support_calls;
