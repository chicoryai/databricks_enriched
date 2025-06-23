{{ config(materialized = 'view') }}   -- dbt model: high_risk_customers.sql

WITH recent_txns AS (               -- 30-day transaction slice
    SELECT
        a.customer_id,
        t.id              AS transaction_id,
        CAST(t.amount AS DECIMAL(18,2)) AS amount
    FROM transactions t                                     -- [Doc-145]
    JOIN accounts      a ON a.id = t.account_id             -- [Doc-142]
    WHERE t.timestamp >= CURRENT_DATE - INTERVAL '30' DAY
),

avg_txn AS (                        -- average amount per customer
    SELECT
        customer_id,
        AVG(amount) AS avg_amount_30d
    FROM recent_txns
    GROUP BY customer_id
),

fraud_customers AS (                -- customers with ≥1 fraud flag in 30 days
    SELECT DISTINCT
        a.customer_id
    FROM fraud_flags f                                   -- [Doc-143 “fraud_flags”]
    JOIN transactions t  ON t.id = f.transaction_id
    JOIN accounts     a  ON a.id = t.account_id
    WHERE t.timestamp >= CURRENT_DATE - INTERVAL '30' DAY
),

kyc AS (                             -- latest / only KYC record
    SELECT
        customer_id,
        status AS kyc_status
    FROM kyc_info                                          -- [Doc-Updated_financial_schema p.3]
)

SELECT
    fc.id           AS customer_id,
    fc.name,
    fc.email,
    at.avg_amount_30d,
    k.kyc_status
FROM fixed_customers  fc                                   -- [Doc-142]
JOIN avg_txn          at ON fc.id = at.customer_id
JOIN fraud_customers  f  ON fc.id = f.customer_id
JOIN kyc              k  ON fc.id = k.customer_id
WHERE at.avg_amount_30d > 1000      -- risk threshold
  AND k.kyc_status != 'verified';