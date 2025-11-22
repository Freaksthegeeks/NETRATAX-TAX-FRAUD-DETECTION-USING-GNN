"""
Data Cleaning and Feature Engineering Module
Handles loading, validating, and processing raw tax data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and preprocess raw tax and invoice data"""
    
    def __init__(self, raw_data_path="../../data/raw"):
        self.raw_path = Path(raw_data_path)
        self.processed_path = self.raw_path.parent / "processed"
        self.processed_path.mkdir(exist_ok=True)
        logger.info(f"DataCleaner initialized. Raw path: {self.raw_path}, Processed path: {self.processed_path}")
    
    def load_data(self):
        """Load raw CSV files"""
        try:
            companies = pd.read_csv(self.raw_path / "companies.csv")
            invoices = pd.read_csv(self.raw_path / "invoices.csv")
            logger.info(f"Loaded {len(companies)} companies and {len(invoices)} invoices")
            return companies, invoices
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
    
    def clean_companies(self, df):
        """
        Clean company data:
        - Handle missing values
        - Remove duplicates
        - Fix data types
        - Validate ranges
        """
        df = df.copy()
        logger.info(f"Cleaning {len(df)} company records...")
        
        # Handle missing values
        if "turnover" in df.columns:
            median_turnover = df["turnover"].median()
            df["turnover"] = df["turnover"].fillna(median_turnover)
            logger.info(f"Filled {df['turnover'].isna().sum()} missing turnover values with median: {median_turnover}")
        
        if "location" in df.columns:
            df["location"] = df["location"].fillna("Unknown")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=["company_id"])
        logger.info(f"Removed {initial_count - len(df)} duplicate companies")
        
        # Ensure correct data types
        if "company_id" in df.columns:
            df["company_id"] = df["company_id"].astype(int)
        if "is_fraud" in df.columns:
            df["is_fraud"] = df["is_fraud"].astype(int)
        if "turnover" in df.columns:
            df["turnover"] = df["turnover"].astype(float)
        
        logger.info(f"Cleaned {len(df)} company records ✓")
        return df
    
    def clean_invoices(self, df):
        """
        Clean invoice data:
        - Handle missing values
        - Fix data types
        - Remove invalid transactions
        """
        df = df.copy()
        logger.info(f"Cleaning {len(df)} invoice records...")
        
        # Handle missing values
        if "amount" in df.columns:
            df["amount"] = df["amount"].fillna(0)
        if "itc_claimed" in df.columns:
            df["itc_claimed"] = df["itc_claimed"].fillna(0)
        
        # Ensure correct data types
        if "seller_id" in df.columns:
            df["seller_id"] = df["seller_id"].astype(int)
        if "buyer_id" in df.columns:
            df["buyer_id"] = df["buyer_id"].astype(int)
        if "amount" in df.columns:
            df["amount"] = df["amount"].astype(float)
        
        # Remove self-loops (seller = buyer)
        if "seller_id" in df.columns and "buyer_id" in df.columns:
            initial_count = len(df)
            df = df[df["seller_id"] != df["buyer_id"]]
            logger.info(f"Removed {initial_count - len(df)} self-loop invoices")
        
        logger.info(f"Cleaned {len(df)} invoice records ✓")
        return df
    
    def engineer_features(self, companies, invoices):
        """
        Engineer new features from transaction patterns:
        - Invoice counts per company
        - Total transaction volumes
        - ITC claimed ratios
        """
        logger.info("Engineering features...")
        
        # Count invoices sent (seller perspective)
        seller_counts = invoices.groupby("seller_id").agg({
            "amount": "sum",
            "invoice_id": "count"
        }).reset_index()
        seller_counts.columns = ["company_id", "total_sent_amount", "sent_invoice_count"]
        
        # Count invoices received (buyer perspective)
        buyer_counts = invoices.groupby("buyer_id").agg({
            "amount": "sum",
            "invoice_id": "count"
        }).reset_index()
        buyer_counts.columns = ["company_id", "total_received_amount", "received_invoice_count"]
        
        # Merge features back
        companies = companies.merge(seller_counts, on="company_id", how="left")
        companies = companies.merge(buyer_counts, on="company_id", how="left")
        
        # Fill NaN with 0
        companies.fillna(0, inplace=True)
        
        # Calculate additional features
        companies["total_transaction_volume"] = companies["total_sent_amount"] + companies["total_received_amount"]
        companies["invoice_frequency"] = companies["sent_invoice_count"] + companies["received_invoice_count"]
        
        logger.info(f"Engineered {companies.shape[1]} features for {len(companies)} companies ✓")
        return companies
    
    def process_all(self):
        """Execute complete data cleaning and feature engineering pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("STARTING DATA PROCESSING PIPELINE")
            logger.info("=" * 60)
            
            # Step 1: Load
            companies, invoices = self.load_data()
            
            # Step 2: Clean
            companies = self.clean_companies(companies)
            invoices = self.clean_invoices(invoices)
            
            # Step 3: Engineer features
            companies = self.engineer_features(companies, invoices)
            
            # Step 4: Save
            logger.info("Saving processed data...")
            companies.to_csv(self.processed_path / "companies_processed.csv", index=False)
            invoices.to_csv(self.processed_path / "invoices_processed.csv", index=False)
            
            logger.info("=" * 60)
            logger.info("✅ DATA PROCESSING COMPLETE")
            logger.info(f"Companies: {self.processed_path / 'companies_processed.csv'}")
            logger.info(f"Invoices: {self.processed_path / 'invoices_processed.csv'}")
            logger.info("=" * 60)
            
            return companies, invoices
            
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            raise


if __name__ == "__main__":
    cleaner = DataCleaner()
    companies, invoices = cleaner.process_all()
    print(f"\nCompanies shape: {companies.shape}")
    print(f"Invoices shape: {invoices.shape}")
    print("\nCompanies columns:", companies.columns.tolist())
    print("Invoices columns:", invoices.columns.tolist())
