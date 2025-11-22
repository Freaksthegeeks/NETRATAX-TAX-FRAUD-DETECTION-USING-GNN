"""
CSV Upload and Processing Service for NETRA TAX
Handles file validation, transformation, and graph building
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
import hashlib
from datetime import datetime
import torch
from torch_geometric.data import Data
import networkx as nx

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class UploadResult:
    """Result of file upload"""
    success: bool
    file_id: str
    filename: str
    rows_processed: int
    rows_valid: int
    rows_errors: int
    validation_report: Dict
    data_hash: str
    timestamp: datetime
    message: str


@dataclass
class ValidationReport:
    """CSV validation report"""
    total_rows: int
    valid_rows: int
    error_rows: int
    errors: List[str]
    warnings: List[str]
    columns_found: List[str]
    columns_missing: List[str]
    data_quality: Dict


# ============================================================================
# File Upload Service
# ============================================================================

class CSVUploadService:
    """Handle CSV file uploads and processing"""
    
    # Expected columns for different file types
    INVOICE_COLUMNS = {
        'required': ['supplier_gstin', 'buyer_gstin', 'invoice_no', 'amount', 'date'],
        'optional': ['cgst', 'sgst', 'igst', 'itc_claimed', 'description']
    }
    
    COMPANY_COLUMNS = {
        'required': ['gstin', 'company_name', 'director_name', 'location'],
        'optional': ['turnover', 'incorporation_date', 'industry']
    }
    
    def __init__(self, upload_dir: str):
        """Initialize upload service"""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_and_validate(
        self,
        file_path: str,
        file_type: str  # 'invoice' or 'company'
    ) -> UploadResult:
        """Upload and validate CSV file"""
        try:
            # Read CSV
            df = pd.read_csv(file_path, low_memory=False)
            
            # Validate columns
            file_id = self._generate_file_id()
            validation_report = self._validate_columns(df, file_type)
            
            # Clean data
            df_clean = self._clean_data(df)
            
            # Validate data
            validation_report = self._validate_data(df_clean, file_type, validation_report)
            
            # Save processed file
            processed_path = self.upload_dir / f"{file_id}_{file_type}.csv"
            df_clean.to_csv(processed_path, index=False)
            
            # Generate data hash
            data_hash = self._compute_hash(df_clean)
            
            return UploadResult(
                success=validation_report['columns_missing'] == [],
                file_id=file_id,
                filename=Path(file_path).name,
                rows_processed=len(df),
                rows_valid=len(df_clean),
                rows_errors=len(df) - len(df_clean),
                validation_report=validation_report,
                data_hash=data_hash,
                timestamp=datetime.now(),
                message=f"Successfully processed {len(df_clean)} rows"
            )
        
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return UploadResult(
                success=False,
                file_id="",
                filename=Path(file_path).name,
                rows_processed=0,
                rows_valid=0,
                rows_errors=0,
                validation_report={'errors': [str(e)]},
                data_hash="",
                timestamp=datetime.now(),
                message=f"Error: {str(e)}"
            )
    
    def _validate_columns(self, df: pd.DataFrame, file_type: str) -> Dict:
        """Validate CSV columns"""
        config = self.INVOICE_COLUMNS if file_type == 'invoice' else self.COMPANY_COLUMNS
        
        df_columns_lower = [col.lower().strip() for col in df.columns]
        required_cols = [c.lower() for c in config['required']]
        optional_cols = [c.lower() for c in config['optional']]
        
        found_required = [c for c in required_cols if c in df_columns_lower]
        missing_required = [c for c in required_cols if c not in df_columns_lower]
        
        return {
            'columns_found': df.columns.tolist(),
            'columns_missing': missing_required,
            'columns_required': config['required'],
            'columns_optional': config['optional'],
            'validation_status': 'PASS' if not missing_required else 'FAIL'
        }
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize data"""
        df = df.copy()
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing values
        df = df.dropna(subset=[col for col in df.columns if col.lower() in ['supplier_gstin', 'buyer_gstin', 'gstin', 'invoice_no']])
        
        # Standardize column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Convert amount columns to numeric
        for col in ['amount', 'cgst', 'sgst', 'igst', 'itc_claimed', 'turnover']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Standardize GSTIN format
        for col in ['supplier_gstin', 'buyer_gstin', 'gstin']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.upper().str.strip()
        
        return df
    
    def _validate_data(self, df: pd.DataFrame, file_type: str, validation_report: Dict) -> Dict:
        """Validate data quality"""
        errors = []
        warnings = []
        
        # Check for null values in critical columns
        critical_cols = ['supplier_gstin', 'buyer_gstin', 'invoice_no', 'amount'] if file_type == 'invoice' else ['gstin', 'company_name']
        
        for col in critical_cols:
            if col in df.columns and df[col].isnull().any():
                null_count = df[col].isnull().sum()
                warnings.append(f"{null_count} null values in {col}")
        
        # Check GSTIN format (Indian GSTIN format: 15 characters)
        for col in ['supplier_gstin', 'buyer_gstin', 'gstin']:
            if col in df.columns:
                invalid = df[df[col].str.len() != 15].shape[0]
                if invalid > 0:
                    warnings.append(f"{invalid} rows with invalid GSTIN format in {col}")
        
        # Check amount values
        if 'amount' in df.columns:
            negative = (df['amount'] < 0).sum()
            if negative > 0:
                warnings.append(f"{negative} rows with negative amounts")
        
        validation_report.update({
            'errors': errors,
            'warnings': warnings,
            'data_quality': {
                'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
                'duplicate_percentage': 0,  # Already removed
                'invalid_format_percentage': len(warnings) / len(df) * 100
            }
        })
        
        return validation_report
    
    def _generate_file_id(self) -> str:
        """Generate unique file ID"""
        return hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]
    
    def _compute_hash(self, df: pd.DataFrame) -> str:
        """Compute hash of data for versioning"""
        data_str = pd.util.hash_pandas_object(df, index=True).values.tobytes()
        return hashlib.sha256(data_str).hexdigest()[:16]


# ============================================================================
# Graph Building Service
# ============================================================================

class GraphBuildingService:
    """Build knowledge graph from CSV data"""
    
    def __init__(self):
        """Initialize graph builder"""
        self.entity_to_id = {}
        self.id_to_entity = {}
        self.next_id = 0
    
    def build_graph(
        self,
        invoices_df: pd.DataFrame,
        companies_df: Optional[pd.DataFrame] = None
    ) -> Data:
        """Build PyTorch Geometric graph from data"""
        try:
            # Build entity mapping
            self._build_entity_mapping(invoices_df, companies_df)
            
            # Build edges from invoices
            edge_list = []
            edge_attrs = []
            
            for _, row in invoices_df.iterrows():
                supplier_id = self._get_or_create_entity(row['supplier_gstin'], 'company')
                buyer_id = self._get_or_create_entity(row['buyer_gstin'], 'company')
                
                edge_list.append([supplier_id, buyer_id])
                
                # Edge attributes
                edge_attrs.append({
                    'amount': float(row.get('amount', 0)),
                    'cgst': float(row.get('cgst', 0)),
                    'sgst': float(row.get('sgst', 0)),
                    'igst': float(row.get('igst', 0)),
                    'itc_claimed': float(row.get('itc_claimed', 0))
                })
            
            # Create edge index
            if edge_list:
                edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
            else:
                edge_index = torch.zeros((2, 0), dtype=torch.long)
            
            # Create node features
            num_nodes = len(self.entity_to_id)
            x = self._create_node_features(num_nodes, companies_df)
            
            # Create edge attributes
            edge_attr = None
            if edge_attrs:
                edge_attr = torch.tensor(
                    [[attr['amount'], attr['cgst'], attr['sgst'], attr['igst'], attr['itc_claimed']] 
                     for attr in edge_attrs],
                    dtype=torch.float
                )
            
            # Create PyG Data object
            graph_data = Data(
                x=x,
                edge_index=edge_index,
                edge_attr=edge_attr,
                num_nodes=num_nodes
            )
            
            logger.info(f"Built graph with {num_nodes} nodes and {edge_index.shape[1]} edges")
            
            return graph_data
        
        except Exception as e:
            logger.error(f"Error building graph: {e}")
            raise
    
    def _build_entity_mapping(self, invoices_df: pd.DataFrame, companies_df: Optional[pd.DataFrame] = None):
        """Build mapping of entities to node IDs"""
        # Get all unique GSTINs from invoices
        suppliers = set(invoices_df['supplier_gstin'].unique())
        buyers = set(invoices_df['buyer_gstin'].unique())
        all_gstins = suppliers.union(buyers)
        
        # Add from companies if available
        if companies_df is not None:
            all_gstins.update(companies_df['gstin'].unique())
        
        # Create mapping
        for gstin in sorted(all_gstins):
            self.entity_to_id[gstin] = self.next_id
            self.id_to_entity[self.next_id] = gstin
            self.next_id += 1
    
    def _get_or_create_entity(self, gstin: str, entity_type: str) -> int:
        """Get or create entity ID"""
        if gstin not in self.entity_to_id:
            self.entity_to_id[gstin] = self.next_id
            self.id_to_entity[self.next_id] = gstin
            self.next_id += 1
        return self.entity_to_id[gstin]
    
    def _create_node_features(self, num_nodes: int, companies_df: Optional[pd.DataFrame] = None) -> torch.Tensor:
        """Create node feature matrix"""
        features = np.zeros((num_nodes, 10))  # 10 features per node
        
        if companies_df is not None:
            for idx, (gstin, node_id) in enumerate(self.entity_to_id.items()):
                company = companies_df[companies_df['gstin'] == gstin]
                
                if not company.empty:
                    # Feature 0: Turnover (normalized)
                    if 'turnover' in company.columns:
                        turnover = float(company['turnover'].iloc[0]) if pd.notna(company['turnover'].iloc[0]) else 0
                        features[node_id, 0] = min(turnover / 10000000, 1.0)  # Normalize
                    
                    # Feature 1: Company age
                    if 'incorporation_date' in company.columns:
                        try:
                            date = pd.to_datetime(company['incorporation_date'].iloc[0])
                            age_days = (pd.Timestamp.now() - date).days
                            features[node_id, 1] = min(age_days / 7300, 1.0)  # 20 years normalized
                        except:
                            pass
        
        # Add degree-based features (computed later from edges)
        features_tensor = torch.tensor(features, dtype=torch.float32)
        
        return features_tensor
    
    def get_entity_mapping(self) -> Tuple[Dict, Dict]:
        """Get entity to ID and ID to entity mappings"""
        return self.entity_to_id, self.id_to_entity
    
    def build_networkx_graph(self, graph_data: Data) -> nx.DiGraph:
        """Build NetworkX graph from PyG Data"""
        G = nx.DiGraph()
        
        # Add all nodes
        G.add_nodes_from(range(graph_data.num_nodes))
        
        # Add edges
        edge_index = graph_data.edge_index
        for i in range(edge_index.shape[1]):
            src = int(edge_index[0, i])
            dst = int(edge_index[1, i])
            G.add_edge(src, dst)
        
        return G
