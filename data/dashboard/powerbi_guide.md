# Power BI Dashboard Guide

Build the churn dashboard from `data/customers_scored.csv` (created by the notebook).
When it's done, save it here as `churn_dashboard.pbix` and add a screenshot to `images/dashboard.png`.

## 1. Load the data
Home → Get Data → Text/CSV → `customers_scored.csv` → Transform Data:
- Set `total_charges`, `monthly_charges`, `churn_risk` to Decimal Number
- Set `tenure_months`, `support_calls` to Whole Number
- Close & Apply

## 2. DAX measures
```dax
Total Customers = COUNTROWS(customers_scored)

Churned Customers = CALCULATE([Total Customers], customers_scored[churn] = "Yes")

Churn Rate = DIVIDE([Churned Customers], [Total Customers])

Monthly Revenue Lost =
CALCULATE(SUM(customers_scored[monthly_charges]), customers_scored[churn] = "Yes")

High Risk Customers =
CALCULATE([Total Customers], customers_scored[risk_level] = "High", customers_scored[churn] = "No")

Revenue at Risk =
CALCULATE(SUM(customers_scored[monthly_charges]),
          customers_scored[risk_level] = "High", customers_scored[churn] = "No")
```

## 3. Page layout
| Area | Visual | Fields |
| --- | --- | --- |
| Top row | 4 cards | Total Customers, Churn Rate, Monthly Revenue Lost, High Risk Customers |
| Middle left | Clustered bar | Churn Rate by `contract` |
| Middle centre | Line chart | Churn Rate by `tenure_band` |
| Middle right | Clustered bar | Churn Rate by `payment_method` |
| Bottom | Table | `customer_id`, `contract`, `tenure_months`, `monthly_charges`, `churn_risk` — filtered to High risk, not yet churned, sorted by `churn_risk` |
| Side | Slicers | `internet_service`, `senior_citizen`, `risk_level` |

The bottom table is the retention team's call list.
