"""
Sample Data Generator
Creates synthetic tax fraud dataset for demonstration and testing
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_sample_data(num_companies=500, num_invoices=2000, fraud_ratio=0.15):
    """
    Generate synthetic companies and invoice data
    
    Parameters:
    - num_companies: Number of company records
    - num_invoices: Number of invoice records
    - fraud_ratio: Proportion of fraudulent companies (0-1)
    """
    logger.info(f"Generating sample data: {num_companies} companies, {num_invoices} invoices")
    
    # Generate companies
    np.random.seed(42)
    company_ids = np.arange(1, num_companies + 1)
    
    # Assign fraud labels
    num_fraud = int(num_companies * fraud_ratio)
    is_fraud = np.zeros(num_companies, dtype=int)
    fraud_indices = np.random.choice(num_companies, num_fraud, replace=False)
    is_fraud[fraud_indices] = 1
    
    locations = np.random.choice(
        ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata"],
        num_companies
    )
    
    # Turnover distribution (log-normal to simulate realistic distribution)
    turnover = np.random.lognormal(mean=10, sigma=1.5, size=num_companies)
    
    companies_df = pd.DataFrame({
        "company_id": company_ids,
        "turnover": turnover,
        "location": locations,
        "is_fraud": is_fraud
    })
    
    logger.info(f"Generated {len(companies_df)} companies ({is_fraud.sum()} fraudulent)")
    
    # Generate invoices
    np.random.seed(43)
    seller_ids = np.random.choice(company_ids, num_invoices)
    buyer_ids = np.random.choice(company_ids, num_invoices)
    
    # Ensure no self-loops
    for i in range(num_invoices):
        while seller_ids[i] == buyer_ids[i]:
            buyer_ids[i] = np.random.choice(company_ids)
    
    # Invoice amounts (realistic range)
    amounts = np.random.lognormal(mean=9, sigma=2, size=num_invoices)
    
    # ITC claimed (typically 5-18% of invoice amount)
    itc_rates = np.random.uniform(0.05, 0.18, num_invoices)
    itc_claimed = amounts * itc_rates
    
    invoices_df = pd.DataFrame({
        "invoice_id": np.arange(1, num_invoices + 1),
        "seller_id": seller_ids,
        "buyer_id": buyer_ids,
        "amount": amounts,
        "itc_claimed": itc_claimed
    })
    
    logger.info(f"Generated {len(invoices_df)} invoices")
    logger.info(f"  Average invoice amount: ₹{amounts.mean():.2f}")
    logger.info(f"  Average ITC claimed: ₹{itc_claimed.mean():.2f}")
    
    return companies_df, invoices_df


def save_sample_data(companies_df, invoices_df, output_path="../../data/raw"):
    """Save dataframes to CSV"""
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    companies_df.to_csv(output_path / "companies.csv", index=False)
    invoices_df.to_csv(output_path / "invoices.csv", index=False)
    
    logger.info(f"✓ Saved companies.csv ({len(companies_df)} rows)")
    logger.info(f"✓ Saved invoices.csv ({len(invoices_df)} rows)")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("GENERATING SAMPLE DATA")
    logger.info("=" * 60)
    
    companies, invoices = generate_sample_data(
        num_companies=500,
        num_invoices=2000,
        fraud_ratio=0.15
    )
    
    save_sample_data(companies, invoices)
    
    logger.info("=" * 60)
    logger.info("✅ SAMPLE DATA GENERATION COMPLETE")
    logger.info("=" * 60)
    print("\nGenerated datasets:")
    print(f"\nCompanies ({len(companies)} rows):")
    print(companies.head())
    print(f"\nInvoices ({len(invoices)} rows):")
    print(invoices.head())
