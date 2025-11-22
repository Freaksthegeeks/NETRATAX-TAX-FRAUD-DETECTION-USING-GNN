"""
Comprehensive Dataset Analysis for Tax Fraud Detection Project
Analyzes companies.csv and invoices.csv for suitability
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("TAX FRAUD DETECTION - DATASET ANALYSIS")
print("=" * 80)

# ============================================================================
# 1. LOAD DATASETS
# ============================================================================

print("\n📂 LOADING DATASETS...")
companies = pd.read_csv("c:\\BIG HACK\\companies.csv")
invoices = pd.read_csv("c:\\BIG HACK\\invoices.csv")

print(f"✅ Companies dataset loaded: {companies.shape[0]} rows, {companies.shape[1]} columns")
print(f"✅ Invoices dataset loaded: {invoices.shape[0]} rows, {invoices.shape[1]} columns")

# ============================================================================
# 2. COMPANIES DATASET ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("COMPANIES DATASET ANALYSIS")
print("=" * 80)

print("\n📋 Column Names and Types:")
print(companies.dtypes)

print("\n📊 Dataset Statistics:")
print(companies.describe())

print("\n🔍 Missing Values:")
print(companies.isnull().sum())

print("\n📍 Locations Distribution:")
print(companies['location'].value_counts())

print("\n🚨 Fraud Distribution:")
fraud_dist = companies['is_fraud'].value_counts()
fraud_pct = (fraud_dist / len(companies) * 100).round(2)
print(f"Non-Fraudulent: {fraud_dist.get(0, 0)} ({fraud_pct.get(0, 0)}%)")
print(f"Fraudulent: {fraud_dist.get(1, 0)} ({fraud_pct.get(1, 0)}%)")

print("\n💰 Turnover Analysis:")
print(f"  Min: ₹{companies['turnover'].min():,.2f}")
print(f"  Max: ₹{companies['turnover'].max():,.2f}")
print(f"  Mean: ₹{companies['turnover'].mean():,.2f}")
print(f"  Median: ₹{companies['turnover'].median():,.2f}")
print(f"  Std Dev: ₹{companies['turnover'].std():,.2f}")

# ============================================================================
# 3. INVOICES DATASET ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("INVOICES DATASET ANALYSIS")
print("=" * 80)

print("\n📋 Column Names and Types:")
print(invoices.dtypes)

print("\n📊 Dataset Statistics:")
print(invoices.describe())

print("\n🔍 Missing Values:")
print(invoices.isnull().sum())

print("\n📅 Date Range:")
invoices['date'] = pd.to_datetime(invoices['date'])
print(f"  From: {invoices['date'].min()}")
print(f"  To: {invoices['date'].max()}")
print(f"  Duration: {(invoices['date'].max() - invoices['date'].min()).days} days")

print("\n🏛️ ITC Claimed Distribution:")
itc_dist = invoices['itc_claimed'].value_counts()
itc_pct = (itc_dist / len(invoices) * 100).round(2)
print(f"ITC Not Claimed (0): {itc_dist.get(0, 0)} ({itc_pct.get(0, 0)}%)")
print(f"ITC Claimed (1): {itc_dist.get(1, 0)} ({itc_pct.get(1, 0)}%)")

print("\n💰 Invoice Amount Analysis:")
print(f"  Min: ₹{invoices['amount'].min():,.2f}")
print(f"  Max: ₹{invoices['amount'].max():,.2f}")
print(f"  Mean: ₹{invoices['amount'].mean():,.2f}")
print(f"  Median: ₹{invoices['amount'].median():,.2f}")
print(f"  Std Dev: ₹{invoices['amount'].std():,.2f}")

# ============================================================================
# 4. DATA INTEGRATION & VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("DATA INTEGRATION & VALIDATION")
print("=" * 80)

print("\n🔗 Company ID Validation:")
invoice_sellers = set(invoices['seller_id'].unique())
invoice_buyers = set(invoices['buyer_id'].unique())
company_ids = set(companies['company_id'].unique())

sellers_in_companies = invoice_sellers.intersection(company_ids)
buyers_in_companies = invoice_buyers.intersection(company_ids)

print(f"  Total companies: {len(company_ids)}")
print(f"  Unique sellers in invoices: {len(invoice_sellers)}")
print(f"  Sellers in companies dataset: {len(sellers_in_companies)} ({len(sellers_in_companies)/len(invoice_sellers)*100:.1f}%)")
print(f"  Unique buyers in invoices: {len(invoice_buyers)}")
print(f"  Buyers in companies dataset: {len(buyers_in_companies)} ({len(buyers_in_companies)/len(invoice_buyers)*100:.1f}%)")

# ============================================================================
# 5. SUITABILITY ASSESSMENT
# ============================================================================

print("\n" + "=" * 80)
print("SUITABILITY ASSESSMENT FOR GNN FRAUD DETECTION")
print("=" * 80)

criteria = {}

# Criterion 1: Fraud Labels
print("\n✓ Criterion 1: FRAUD LABELS")
has_fraud_labels = 'is_fraud' in companies.columns
criteria['fraud_labels'] = has_fraud_labels
print(f"  Status: {'✅ PASS' if has_fraud_labels else '❌ FAIL'}")
if has_fraud_labels:
    print(f"  Reason: 'is_fraud' column present with {fraud_dist.get(1, 0)} positive samples")

# Criterion 2: Network Structure
print("\n✓ Criterion 2: NETWORK STRUCTURE")
has_network = 'seller_id' in invoices.columns and 'buyer_id' in invoices.columns
criteria['network'] = has_network
print(f"  Status: {'✅ PASS' if has_network else '❌ FAIL'}")
if has_network:
    edge_count = len(invoices)
    print(f"  Reason: {len(company_ids)} nodes (companies) and {edge_count} edges (transactions)")

# Criterion 3: Sufficient Data
print("\n✓ Criterion 3: SUFFICIENT DATA")
has_sufficient_data = len(companies) >= 100 and len(invoices) >= 100
criteria['sufficient_data'] = has_sufficient_data
print(f"  Status: {'✅ PASS' if has_sufficient_data else '❌ FAIL'}")
print(f"  Reason: {len(companies)} companies, {len(invoices)} invoices")

# Criterion 4: Balanced Labels
print("\n✓ Criterion 4: LABEL BALANCE")
fraud_ratio = fraud_dist.get(1, 0) / len(companies)
is_balanced = 0.05 <= fraud_ratio <= 0.95
criteria['balanced'] = is_balanced
print(f"  Status: {'✅ PASS' if is_balanced else '⚠️  WARNING'}")
print(f"  Reason: Fraud ratio is {fraud_ratio:.1%} (ideal: 5-95%)")

# Criterion 5: Features
print("\n✓ Criterion 5: RELEVANT FEATURES")
has_features = 'turnover' in companies.columns and 'amount' in invoices.columns
criteria['features'] = has_features
print(f"  Status: {'✅ PASS' if has_features else '❌ FAIL'}")
features_list = list(companies.columns) + list(invoices.columns)
print(f"  Available features: {', '.join(features_list)}")

# Criterion 6: Data Quality
print("\n✓ Criterion 6: DATA QUALITY")
no_nulls = companies.isnull().sum().sum() == 0 and invoices.isnull().sum().sum() == 0
criteria['quality'] = no_nulls
print(f"  Status: {'✅ PASS' if no_nulls else '⚠️  WARNING'}")
print(f"  Companies nulls: {companies.isnull().sum().sum()}")
print(f"  Invoices nulls: {invoices.isnull().sum().sum()}")

# ============================================================================
# 6. FINAL VERDICT
# ============================================================================

print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

passed = sum(criteria.values())
total = len(criteria)

if passed >= 5:
    verdict = "✅ HIGHLY SUITABLE"
    recommendation = "PROCEED with model training using this dataset"
elif passed >= 4:
    verdict = "🟢 SUITABLE"
    recommendation = "PROCEED with minor data preprocessing"
else:
    verdict = "🔴 NOT SUITABLE"
    recommendation = "NEEDS SIGNIFICANT DATA PREPARATION"

print(f"\n{verdict}")
print(f"Passed: {passed}/{total} criteria")
print(f"\n📌 Recommendation: {recommendation}")

# ============================================================================
# 7. DETAILED SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)

summary_data = {
    'Metric': [
        'Total Companies',
        'Total Invoices',
        'Fraudulent Companies',
        'Fraud Ratio',
        'Locations',
        'Date Range (days)',
        'Avg Turnover',
        'Avg Invoice Amount',
        'Network Density',
        'Complete Mappings'
    ],
    'Value': [
        f"{len(companies):,}",
        f"{len(invoices):,}",
        f"{fraud_dist.get(1, 0):,}",
        f"{fraud_ratio:.2%}",
        f"{companies['location'].nunique()}",
        f"{(invoices['date'].max() - invoices['date'].min()).days}",
        f"₹{companies['turnover'].mean():,.0f}",
        f"₹{invoices['amount'].mean():,.0f}",
        f"{len(sellers_in_companies)/len(invoice_sellers):.1%}",
        f"{len(buyers_in_companies)/len(invoice_buyers):.1%}"
    ]
}

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE!")
print("=" * 80)
