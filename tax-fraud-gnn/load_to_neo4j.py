import pandas as pd
from neo4j_client import driver

COMP_CSV = "data/processed/companies_processed.csv"
INV_CSV = "data/processed/invoices_processed.csv"

def load_companies():
    df = pd.read_csv(COMP_CSV)
    # normalize possible gstin column names to 'Supplier_GSTIN'
    for cand in ('Supplier_GSTIN', 'gstin', 'company_id', 'seller_id', 'seller_id_x'):
        if cand in df.columns:
            df['Supplier_GSTIN'] = df[cand]
            break
    if 'Supplier_GSTIN' not in df.columns:
        raise KeyError("Expected a GSTIN column (e.g. 'Supplier_GSTIN' or 'company_id') not found in companies CSV")
    # filter out rows without a valid Supplier_GSTIN to avoid MERGE on null
    df = df[df['Supplier_GSTIN'].notnull()]
    df = df[df['Supplier_GSTIN'].astype(str).str.strip() != '']
    query = """
    UNWIND $rows AS row
    MERGE (c:Company {gstin: row.Supplier_GSTIN})
      SET c.name = row.Supplier_Name,
          c.state = row.Supplier_State,
          c.address = row.Supplier_Address,
          c.is_fraud = row.Fraud_Label,
          c.suspicious_flags = row.Suspicious_Pattern_Flags
    """
    rows = df.to_dict("records")
    with driver.session() as session:
        session.run(query, rows=rows)

def load_invoices():
    df = pd.read_csv(INV_CSV)
    # normalize invoice columns to expected names used in Cypher
    # supplier/buyer gstin
    if 'Supplier_GSTIN' not in df.columns:
        for cand in ('seller_id', 'seller', 'seller_id_x', 'Supplier_GSTIN'):
            if cand in df.columns:
                df['Supplier_GSTIN'] = df[cand]
                break
    if 'Buyer_GSTIN' not in df.columns:
        for cand in ('buyer_id', 'buyer', 'buyer_id_x', 'Buyer_GSTIN'):
            if cand in df.columns:
                df['Buyer_GSTIN'] = df[cand]
                break
    # invoice number / date / amount
    if 'Invoice_Number' not in df.columns and 'invoice_id' in df.columns:
        df['Invoice_Number'] = df['invoice_id']
    if 'Invoice_Date' not in df.columns and 'date' in df.columns:
        df['Invoice_Date'] = df['date']
    if 'Total_Invoice_Value_with_GST' not in df.columns and 'amount' in df.columns:
        df['Total_Invoice_Value_with_GST'] = df['amount']
    # require supplier and buyer GSTIN and invoice number for relationship creation
    missing_cols = [c for c in ('Supplier_GSTIN', 'Buyer_GSTIN', 'Invoice_Number') if c not in df.columns]
    if missing_cols:
        raise KeyError(f"Expected columns missing from invoices CSV after normalization: {missing_cols}")
    df = df[df['Supplier_GSTIN'].notnull() & df['Buyer_GSTIN'].notnull() & df['Invoice_Number'].notnull()]
    df = df[df['Supplier_GSTIN'].astype(str).str.strip() != '']
    df = df[df['Buyer_GSTIN'].astype(str).str.strip() != '']
    query = """
    UNWIND $rows AS row
    MERGE (s:Company {gstin: row.Supplier_GSTIN})
    MERGE (b:Company {gstin: row.Buyer_GSTIN})
    MERGE (inv:Invoice {invoice_no: row.Invoice_Number, date: row.Invoice_Date})
      SET inv.amount = row.Total_Invoice_Value_with_GST,
          inv.taxable_value = row.Taxable_Value,
          inv.itc_claimed = row.ITC_Claimed,
          inv.payment_type = row.Payment_Type,
          inv.transaction_id = row.Transaction_ID,
          inv.fraud_label = row.Fraud_Label,
          inv.suspicious_flags = row.Suspicious_Pattern_Flags
    MERGE (s)-[:SUPPLIES_TO]->(inv)
    MERGE (inv)-[:BILLED_TO]->(b)
    """
    rows = df.to_dict("records")
    with driver.session() as session:
        session.run(query, rows=rows)

if __name__ == "__main__":
    load_companies()
    load_invoices()
    driver.close()
