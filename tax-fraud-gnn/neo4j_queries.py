"""
Neo4j query helper functions for tax fraud detection
Provides functions to query company, invoice, and fraud data from Neo4j
"""

from neo4j_client import driver
import logging

logger = logging.getLogger(__name__)


def get_top_risky_companies(limit=10):
    """
    Get top companies with high fraud probability
    Returns list of dicts with company details
    """
    try:
        query = """
        MATCH (c:Company)
        WHERE c.is_fraud = 1 OR c.fraud_probability > 0.7
        RETURN 
            c.gstin AS gstin,
            c.name AS name,
            c.state AS state,
            c.is_fraud AS is_fraud,
            c.suspicious_flags AS suspicious_flags
        ORDER BY c.is_fraud DESC
        LIMIT $limit
        """
        with driver.session() as session:
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching top risky companies: {e}")
        return []


def get_company_stats():
    """
    Get overall company statistics from Neo4j
    Returns dict with counts and aggregates
    """
    try:
        query = """
        MATCH (c:Company)
        RETURN 
            COUNT(c) AS total_companies,
            SUM(CASE WHEN c.is_fraud = 1 THEN 1 ELSE 0 END) AS fraud_count,
            AVG(c.fraud_probability) AS avg_fraud_probability,
            COUNT(DISTINCT c.state) AS unique_locations
        """
        with driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {
                    "total_companies": record.get("total_companies", 0),
                    "fraud_count": record.get("fraud_count", 0),
                    "avg_fraud_probability": record.get("avg_fraud_probability", 0),
                    "unique_locations": record.get("unique_locations", 0)
                }
            return {}
    except Exception as e:
        logger.error(f"Error fetching company stats: {e}")
        return {}


def get_invoice_stats():
    """
    Get overall invoice statistics from Neo4j
    Returns dict with counts and aggregates
    """
    try:
        query = """
        MATCH (inv:Invoice)
        RETURN 
            COUNT(inv) AS total_invoices,
            SUM(inv.amount) AS total_amount,
            AVG(inv.amount) AS avg_amount,
            SUM(inv.itc_claimed) AS total_itc
        """
        with driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {
                    "total_invoices": record.get("total_invoices", 0),
                    "total_amount": record.get("total_amount", 0),
                    "avg_amount": record.get("avg_amount", 0),
                    "total_itc": record.get("total_itc", 0)
                }
            return {}
    except Exception as e:
        logger.error(f"Error fetching invoice stats: {e}")
        return {}


def get_company_by_id(company_id):
    """
    Get detailed information about a specific company
    """
    try:
        query = """
        MATCH (c:Company {gstin: $gstin})
        OPTIONAL MATCH (c)-[s:SUPPLIES_TO]->(inv:Invoice)
        OPTIONAL MATCH (inv2:Invoice)-[b:BILLED_TO]->(c)
        RETURN 
            c.gstin AS gstin,
            c.name AS name,
            c.state AS state,
            c.address AS address,
            c.is_fraud AS is_fraud,
            c.suspicious_flags AS suspicious_flags,
            COUNT(DISTINCT inv) AS invoices_sent,
            COUNT(DISTINCT inv2) AS invoices_received,
            SUM(inv.amount) AS total_sent,
            SUM(inv2.amount) AS total_received
        """
        with driver.session() as session:
            result = session.run(query, gstin=company_id)
            record = result.single()
            if record:
                return dict(record)
            return None
    except Exception as e:
        logger.error(f"Error fetching company {company_id}: {e}")
        return None


def get_top_senders(limit=10):
    """
    Get top invoice senders by invoice count
    """
    try:
        query = """
        MATCH (seller:Company)-[s:SUPPLIES_TO]->(inv:Invoice)
        RETURN 
            seller.gstin AS gstin,
            seller.name AS name,
            COUNT(inv) AS invoice_count,
            SUM(inv.amount) AS total_amount,
            seller.is_fraud AS is_fraud
        ORDER BY COUNT(inv) DESC
        LIMIT $limit
        """
        with driver.session() as session:
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching top senders: {e}")
        return []


def get_top_receivers(limit=10):
    """
    Get top invoice receivers by invoice count
    """
    try:
        query = """
        MATCH (buyer:Company)<-[b:BILLED_TO]-(inv:Invoice)
        RETURN 
            buyer.gstin AS gstin,
            buyer.name AS name,
            COUNT(inv) AS invoice_count,
            SUM(inv.amount) AS total_amount,
            buyer.is_fraud AS is_fraud
        ORDER BY COUNT(inv) DESC
        LIMIT $limit
        """
        with driver.session() as session:
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching top receivers: {e}")
        return []


def get_fraud_patterns():
    """
    Get common fraud patterns from suspicious companies
    """
    try:
        query = """
        MATCH (c:Company)
        WHERE c.is_fraud = 1
        WITH c.suspicious_flags AS pattern, COUNT(c) AS count
        WHERE pattern IS NOT NULL
        RETURN pattern, count
        ORDER BY count DESC
        LIMIT 10
        """
        with driver.session() as session:
            result = session.run(query)
            return [{"pattern": record.get("pattern"), "count": record.get("count")} for record in result]
    except Exception as e:
        logger.error(f"Error fetching fraud patterns: {e}")
        return []


def get_suspicious_networks(min_connections=3):
    """
    Find suspicious transaction networks (companies connected through multiple invoices)
    """
    try:
        query = """
        MATCH (c1:Company)-[s:SUPPLIES_TO]->(inv:Invoice)-[b:BILLED_TO]->(c2:Company)
        WHERE (c1.is_fraud = 1 OR c2.is_fraud = 1)
        WITH c1, c2, COUNT(inv) AS transaction_count
        WHERE transaction_count >= $min_connections
        RETURN 
            c1.gstin AS seller_gstin,
            c1.name AS seller_name,
            c2.gstin AS buyer_gstin,
            c2.name AS buyer_name,
            transaction_count
        ORDER BY transaction_count DESC
        """
        with driver.session() as session:
            result = session.run(query, min_connections=min_connections)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching suspicious networks: {e}")
        return []


def search_companies(search_term, limit=20):
    """
    Search companies by name or GSTIN
    """
    try:
        query = """
        MATCH (c:Company)
        WHERE c.gstin CONTAINS $search OR c.name CONTAINS $search
        RETURN 
            c.gstin AS gstin,
            c.name AS name,
            c.state AS state,
            c.is_fraud AS is_fraud,
            c.suspicious_flags AS suspicious_flags
        LIMIT $limit
        """
        with driver.session() as session:
            result = session.run(query, search=search_term.upper(), limit=limit)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        return []


def get_state_statistics():
    """
    Get fraud statistics by state/location
    """
    try:
        query = """
        MATCH (c:Company)
        RETURN 
            c.state AS state,
            COUNT(c) AS total_companies,
            SUM(CASE WHEN c.is_fraud = 1 THEN 1 ELSE 0 END) AS fraud_count,
            AVG(c.fraud_probability) AS avg_fraud_probability
        ORDER BY fraud_count DESC
        """
        with driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching state statistics: {e}")
        return []


def get_invoice_anomalies(threshold=10000):
    """
    Get invoices with anomalous amounts (high value suspicious transactions)
    """
    try:
        query = """
        MATCH (seller:Company)-[s:SUPPLIES_TO]->(inv:Invoice)-[b:BILLED_TO]->(buyer:Company)
        WHERE inv.amount > $threshold AND (seller.is_fraud = 1 OR buyer.is_fraud = 1)
        RETURN 
            inv.invoice_no AS invoice_no,
            inv.date AS date,
            inv.amount AS amount,
            seller.gstin AS seller_gstin,
            seller.name AS seller_name,
            buyer.gstin AS buyer_gstin,
            buyer.name AS buyer_name,
            seller.is_fraud AS seller_fraud,
            buyer.is_fraud AS buyer_fraud
        ORDER BY inv.amount DESC
        LIMIT 20
        """
        with driver.session() as session:
            result = session.run(query, threshold=threshold)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching invoice anomalies: {e}")
        return []
