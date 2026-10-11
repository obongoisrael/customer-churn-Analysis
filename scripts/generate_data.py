"""
Generate a synthetic telecom customer dataset for churn analysis.

The data is simulated (no real customers) but follows realistic patterns:
month-to-month contracts, short tenure, high monthly charges, electronic-check
payments and frequent support calls all raise the chance of churn.

Usage:
    python scripts/generate_data.py
Output:
    data/telco_customers.csv  (7,000 rows)
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 7_000
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "telco_customers.csv"


def main() -> None:
    rng = np.random.default_rng(SEED)

    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"], N_CUSTOMERS, p=[0.55, 0.24, 0.21]
    )
    # Longer contracts tend to belong to longer-tenure customers
    tenure_mean = np.select(
        [contract == "Month-to-month", contract == "One year"], [18, 36], default=52
    )
    tenure = np.clip(rng.normal(tenure_mean, 14), 1, 72).round().astype(int)

    internet = rng.choice(
        ["Fiber optic", "DSL", "No internet"], N_CUSTOMERS, p=[0.44, 0.34, 0.22]
    )
    base_charge = np.select(
        [internet == "Fiber optic", internet == "DSL"], [80, 55], default=22
    )
    monthly = np.clip(rng.normal(base_charge, 12), 18, 120).round(2)
    total = (monthly * tenure * rng.uniform(0.95, 1.02, N_CUSTOMERS)).round(2)

    payment = rng.choice(
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        N_CUSTOMERS,
        p=[0.34, 0.23, 0.22, 0.21],
    )
    gender = rng.choice(["Male", "Female"], N_CUSTOMERS)
    senior = rng.choice([0, 1], N_CUSTOMERS, p=[0.84, 0.16])
    partner = rng.choice(["Yes", "No"], N_CUSTOMERS, p=[0.48, 0.52])
    tech_support = np.where(
        internet == "No internet",
        "No internet service",
        rng.choice(["Yes", "No"], N_CUSTOMERS, p=[0.35, 0.65]),
    )
    paperless = rng.choice(["Yes", "No"], N_CUSTOMERS, p=[0.59, 0.41])
    support_calls = rng.poisson(1.6, N_CUSTOMERS)

    # Churn probability via a logistic model of the drivers
    logit = (
        -1.9
        + 1.35 * (contract == "Month-to-month")
        - 0.9 * (contract == "Two year")
        - 0.035 * tenure
        + 0.018 * (monthly - 65)
        + 0.55 * (payment == "Electronic check")
        + 0.45 * (internet == "Fiber optic")
        - 0.45 * (tech_support == "Yes")
        + 0.30 * senior
        + 0.28 * support_calls
        + 0.15 * (paperless == "Yes")
    )
    prob = 1 / (1 + np.exp(-logit))
    churn = np.where(rng.random(N_CUSTOMERS) < prob, "Yes", "No")

    df = pd.DataFrame(
        {
            "customer_id": [f"CUST-{i:05d}" for i in range(1, N_CUSTOMERS + 1)],
            "gender": gender,
            "senior_citizen": senior,
            "partner": partner,
            "tenure_months": tenure,
            "contract": contract,
            "internet_service": internet,
            "tech_support": tech_support,
            "paperless_billing": paperless,
            "payment_method": payment,
            "monthly_charges": monthly,
            "total_charges": total,
            "support_calls": support_calls,
            "churn": churn,
        }
    )

    # Add a little real-world mess for the cleaning step
    blank_idx = rng.choice(N_CUSTOMERS, 11, replace=False)
    df["total_charges"] = df["total_charges"].astype(object)
    df.loc[blank_idx, "total_charges"] = " "

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df):,} rows to {OUT_PATH} (churn rate {np.mean(churn == 'Yes'):.1%})")


if __name__ == "__main__":
    main()
