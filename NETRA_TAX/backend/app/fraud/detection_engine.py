"""
Fraud Detection Engine for NETRA TAX
GNN inference, pattern detection, risk scoring
"""

import torch
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class FraudResult:
    """Fraud detection result"""
    entity_id: str
    fraud_score: float  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH
    reasons: List[str]
    connected_entities: List[Dict]
    pattern_flags: List[str]
    confidence: float
    evidence: Dict


@dataclass
class RiskScore:
    """Risk score for entity"""
    entity_id: str
    risk_score: float  # 0-1
    risk_level: str  # LOW, MEDIUM, HIGH
    factors: List[str]


# ============================================================================
# Fraud Detection Engine
# ============================================================================

class FraudDetectionEngine:
    """Core fraud detection using GNN and pattern analysis"""
    
    def __init__(
        self,
        gnn_model: torch.nn.Module,
        graph_data: dict,
        device: str = "cpu"
    ):
        """Initialize fraud detection engine"""
        self.model = gnn_model
        self.graph_data = graph_data
        self.device = device
        self.model.to(device)
        self.model.eval()
        
        # Build NetworkX graph for pattern detection
        self.nx_graph = self._build_networkx_graph()
    
    def _build_networkx_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from PyG graph data"""
        G = nx.DiGraph()
        
        edge_index = self.graph_data.get("edge_index")
        if edge_index is not None:
            for i in range(edge_index.shape[1]):
                src = int(edge_index[0, i])
                dst = int(edge_index[1, i])
                G.add_edge(src, dst)
        
        return G
    
    # ========================================================================
    # Core Risk Functions
    # ========================================================================
    
    def node_risk(self, node_id: int) -> RiskScore:
        """Calculate risk score for a single node (company/entity)"""
        with torch.no_grad():
            # Get GNN prediction
            x = self.graph_data.get("x")
            edge_index = self.graph_data.get("edge_index")
            
            if x is None or edge_index is None:
                return RiskScore(
                    entity_id=str(node_id),
                    risk_score=0.5,
                    risk_level="MEDIUM",
                    factors=["Insufficient data"]
                )
            
            x_tensor = x.to(self.device)
            edge_index_tensor = edge_index.to(self.device)
            
            # Get model predictions
            logits = self.model(x_tensor, edge_index_tensor)
            probs = torch.sigmoid(logits)
            
            # Get specific node prediction
            node_prob = float(probs[node_id, 0]) if node_id < len(probs) else 0.5
            
            # Determine risk level
            if node_prob > 0.7:
                risk_level = "HIGH"
            elif node_prob > 0.3:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Get contributing factors
            factors = self._get_risk_factors(node_id, node_prob)
            
            return RiskScore(
                entity_id=str(node_id),
                risk_score=node_prob,
                risk_level=risk_level,
                factors=factors
            )
    
    def invoice_risk(self, invoice_id: str) -> FraudResult:
        """Calculate fraud risk for a specific invoice"""
        # Parse invoice to get sender and receiver
        sender_id, receiver_id = self._parse_invoice_id(invoice_id)
        
        sender_risk = self.node_risk(sender_id)
        receiver_risk = self.node_risk(receiver_id)
        
        # Combined risk
        combined_risk = max(sender_risk.risk_score, receiver_risk.risk_score)
        fraud_score = combined_risk * 100
        
        # Determine risk level
        if combined_risk > 0.7:
            risk_level = "HIGH"
        elif combined_risk > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Reasons
        reasons = []
        if sender_risk.risk_level == "HIGH":
            reasons.append(f"Sender has HIGH fraud risk ({sender_risk.risk_score:.1%})")
        if receiver_risk.risk_level == "HIGH":
            reasons.append(f"Receiver has HIGH fraud risk ({receiver_risk.risk_score:.1%})")
        if not reasons:
            reasons.append("Normal transaction pattern detected")
        
        return FraudResult(
            entity_id=invoice_id,
            fraud_score=fraud_score,
            risk_level=risk_level,
            reasons=reasons,
            connected_entities=[
                {"id": str(sender_id), "type": "sender", "risk": sender_risk.risk_score},
                {"id": str(receiver_id), "type": "receiver", "risk": receiver_risk.risk_score}
            ],
            pattern_flags=self._get_invoice_patterns(sender_id, receiver_id),
            confidence=0.85,
            evidence={"sender_risk": sender_risk.risk_score, "receiver_risk": receiver_risk.risk_score}
        )
    
    def network_analysis(self, node_id: int) -> Dict:
        """Analyze network around a node"""
        node_risk = self.node_risk(node_id)
        
        # Get neighbors
        predecessors = list(self.nx_graph.predecessors(node_id))
        successors = list(self.nx_graph.successors(node_id))
        
        # Analyze patterns
        patterns = {
            "circular_trades": self._detect_circular_trades(node_id),
            "high_degree_nodes": self._detect_high_degree_nodes(node_id),
            "fraud_rings": self._detect_fraud_rings(node_id),
            "chain_analysis": self._analyze_chain_depth(node_id),
            "clustering_coefficient": nx.clustering(self.nx_graph, node_id)
        }
        
        return {
            "node_id": node_id,
            "node_risk": {
                "score": node_risk.risk_score,
                "level": node_risk.risk_level,
                "factors": node_risk.factors
            },
            "network_metrics": {
                "in_degree": self.nx_graph.in_degree(node_id),
                "out_degree": self.nx_graph.out_degree(node_id),
                "predecessors_count": len(predecessors),
                "successors_count": len(successors),
            },
            "patterns": patterns,
            "connected_entities": {
                "predecessors": predecessors[:10],  # Top 10
                "successors": successors[:10]
            }
        }
    
    def fraud_explanation(self, node_id: int) -> Dict:
        """Explain fraud prediction for a node"""
        risk_score = self.node_risk(node_id)
        
        # Get connected nodes
        neighbors = list(self.nx_graph.neighbors(node_id))
        neighbor_risks = [self.node_risk(n).risk_score for n in neighbors if n < 1000]  # Avoid error
        
        explanation = {
            "entity_id": str(node_id),
            "fraud_probability": risk_score.risk_score,
            "risk_level": risk_score.risk_level,
            "primary_reasons": risk_score.factors,
            "network_context": {
                "connected_high_risk_entities": sum(1 for r in neighbor_risks if r > 0.7),
                "connected_medium_risk_entities": sum(1 for r in neighbor_risks if 0.3 < r <= 0.7),
                "avg_neighbor_risk": np.mean(neighbor_risks) if neighbor_risks else 0,
            },
            "pattern_analysis": {
                "circular_trades": len(self._detect_circular_trades(node_id)) > 0,
                "unusual_transaction_patterns": self._detect_unusual_patterns(node_id),
                "clustering_anomaly": self._is_clustering_anomaly(node_id),
            },
            "confidence_score": 0.85,
            "recommendations": self._get_recommendations(risk_score.risk_level)
        }
        
        return explanation
    
    # ========================================================================
    # Pattern Detection Algorithms
    # ========================================================================
    
    def _detect_circular_trades(self, node_id: int) -> List[List[int]]:
        """Detect circular trading loops involving a node"""
        try:
            # Find cycles containing this node
            cycles = []
            for cycle in nx.simple_cycles(self.nx_graph):
                if node_id in cycle:
                    cycles.append(cycle)
            return cycles[:5]  # Return first 5
        except Exception as e:
            logger.warning(f"Error detecting circular trades: {e}")
            return []
    
    def _detect_high_degree_nodes(self, node_id: int) -> Dict:
        """Detect high-degree nodes in network around a node"""
        high_degree = {}
        in_degree = self.nx_graph.in_degree()
        out_degree = self.nx_graph.out_degree()
        
        # Get neighbors and their degrees
        neighbors = set(list(self.nx_graph.predecessors(node_id)) + list(self.nx_graph.successors(node_id)))
        
        for neighbor in neighbors:
            total_degree = in_degree[neighbor] + out_degree[neighbor]
            if total_degree > 10:  # High-degree threshold
                high_degree[neighbor] = total_degree
        
        return high_degree
    
    def _detect_fraud_rings(self, node_id: int) -> List[List[int]]:
        """Detect potential fraud rings (cliques of suspicious nodes)"""
        try:
            # Get neighborhood
            neighbors = set([node_id])
            neighbors.update(self.nx_graph.predecessors(node_id))
            neighbors.update(self.nx_graph.successors(node_id))
            
            # Find cliques in subgraph
            subgraph = self.nx_graph.subgraph(neighbors).to_undirected()
            cliques = list(nx.find_cliques(subgraph))
            
            # Filter to meaningful cliques (size >= 3)
            return [c for c in cliques if len(c) >= 3][:5]
        except Exception as e:
            logger.warning(f"Error detecting fraud rings: {e}")
            return []
    
    def _analyze_chain_depth(self, node_id: int) -> Dict:
        """Analyze transaction chain depth"""
        max_depth = 0
        max_chain = []
        
        try:
            for target in self.nx_graph.nodes():
                if target != node_id:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.nx_graph, node_id, target, cutoff=5
                        ))
                        if paths:
                            longest = max(paths, key=len)
                            if len(longest) > max_depth:
                                max_depth = len(longest)
                                max_chain = longest
                    except nx.NetworkXNoPath:
                        continue
        except Exception as e:
            logger.warning(f"Error analyzing chain depth: {e}")
        
        return {
            "max_depth": max_depth,
            "max_chain": max_chain[:5] if max_chain else []
        }
    
    def _detect_unusual_patterns(self, node_id: int) -> List[str]:
        """Detect unusual transaction patterns"""
        patterns = []
        
        in_degree = self.nx_graph.in_degree(node_id)
        out_degree = self.nx_graph.out_degree(node_id)
        
        if out_degree > 15 and in_degree < 2:
            patterns.append("High outflow with low inflow (possible shell company)")
        elif in_degree > 15 and out_degree < 2:
            patterns.append("High inflow with low outflow (possible conduit)")
        elif in_degree > 50 and out_degree > 50:
            patterns.append("Very high volume trader (potential hub)")
        
        return patterns
    
    def _is_clustering_anomaly(self, node_id: int) -> bool:
        """Check if clustering coefficient is anomalous"""
        try:
            coef = nx.clustering(self.nx_graph, node_id)
            return coef > 0.8
        except:
            return False
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _get_risk_factors(self, node_id: int, risk_score: float) -> List[str]:
        """Get factors contributing to risk score"""
        factors = []
        
        # Check degree
        in_degree = self.nx_graph.in_degree(node_id)
        out_degree = self.nx_graph.out_degree(node_id)
        total_degree = in_degree + out_degree
        
        if total_degree > 15:
            factors.append(f"High network activity ({total_degree} connections)")
        
        if out_degree > 10 and in_degree < 2:
            factors.append("Suspicious outflow pattern")
        
        if in_degree > 10 and out_degree < 2:
            factors.append("Suspicious inflow pattern")
        
        # Check clustering
        try:
            coef = nx.clustering(self.nx_graph, node_id)
            if coef > 0.8:
                factors.append("High clustering coefficient (isolated group)")
        except:
            pass
        
        if not factors:
            factors.append("GNN model flagged for review")
        
        return factors
    
    def _parse_invoice_id(self, invoice_id: str) -> Tuple[int, int]:
        """Parse invoice ID to get sender and receiver node IDs"""
        # Assume format: "sender_receiver" or use hash mapping
        parts = invoice_id.split("_")
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        return hash(invoice_id) % 1000, (hash(invoice_id) // 1000) % 1000
    
    def _get_invoice_patterns(self, sender_id: int, receiver_id: int) -> List[str]:
        """Get fraud pattern flags for an invoice"""
        patterns = []
        
        # Check if direct connection exists
        if not self.nx_graph.has_edge(sender_id, receiver_id):
            patterns.append("No direct transaction history")
        
        # Check if part of circular trade
        try:
            cycles = list(nx.simple_cycles(self.nx_graph))
            for cycle in cycles:
                if sender_id in cycle and receiver_id in cycle:
                    patterns.append("Part of circular trading pattern")
                    break
        except:
            pass
        
        return patterns
    
    def _get_recommendations(self, risk_level: str) -> List[str]:
        """Get recommendations based on risk level"""
        if risk_level == "HIGH":
            return [
                "Recommend immediate audit",
                "Flag for GST officer review",
                "Verify supplier documentation",
                "Check ITC eligibility"
            ]
        elif risk_level == "MEDIUM":
            return [
                "Schedule routine audit",
                "Verify transaction details",
                "Monitor future transactions"
            ]
        else:
            return [
                "Monitor for patterns",
                "Standard compliance check"
            ]
