"""
Streamlit Dashboard for Tax Fraud Detection
Interactive visualization and fraud risk analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import torch
import pickle
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gnn_models.train_gnn import GNNFraudDetector

# Page config
st.set_page_config(page_title="Tax Fraud Detection Dashboard", layout="wide")

@st.cache_resource
def load_data_and_model():
    """Load processed data and trained model"""
    data_path = Path(__file__).parent.parent / "data" / "processed"
    models_path = Path(__file__).parent.parent / "models"
    
    try:
        # Load data
        companies = pd.read_csv(data_path / "companies_processed.csv")
        invoices = pd.read_csv(data_path / "invoices_processed.csv")
        
        # Load graph
        graph_data = torch.load(data_path / "graphs" / "graph_data.pt")
        
        # Load model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = GNNFraudDetector(in_channels=3, hidden_channels=64, out_channels=2, model_type="gcn").to(device)
        try:
            model.load_state_dict(torch.load(models_path / "best_model.pt", map_location=device))
        except:
            st.warning("Model weights not found. Using untrained model.")
        
        # Load node mappings
        with open(data_path / "graphs" / "node_mappings.pkl", "rb") as f:
            mappings = pickle.load(f)
        
        return companies, invoices, graph_data, model, device, mappings
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.exception(e)
        # Return empty dataframes to prevent crashes
        return pd.DataFrame(), pd.DataFrame(), None, None, None, {}


def get_fraud_predictions(model, graph_data, device):
    """Get fraud predictions from model"""
    if model is None or graph_data is None or device is None:
        return np.array([])
    try:
        model.eval()
        with torch.no_grad():
            out = model(graph_data.x.to(device), graph_data.edge_index.to(device))
            predictions = torch.softmax(out, dim=1)
            fraud_proba = predictions[:, 1].cpu().numpy()
        return fraud_proba
    except Exception as e:
        st.error(f"Error getting fraud predictions: {e}")
        return np.array([])


# ============================================================================
# MAIN APP
# ============================================================================

st.title("Tax Fraud Detection Dashboard")
st.markdown("Graph Neural Network-based fraud detection for invoice networks")

# Load data
companies, invoices, graph_data, model, device, mappings = load_data_and_model()
fraud_proba = get_fraud_predictions(model, graph_data, device)

# Add predictions to companies dataframe
if len(companies) > 0 and len(fraud_proba) > 0:
    companies["fraud_probability"] = fraud_proba
    companies["predicted_fraud"] = (fraud_proba > 0.5).astype(int)
elif len(companies) > 0:
    companies["fraud_probability"] = 0.0
    companies["predicted_fraud"] = 0

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

with st.sidebar:
    st.header("Filters")
    
    risk_threshold = st.slider(
        "Fraud Risk Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Companies with fraud probability above this are flagged as high-risk"
    )
    
    location_filter = st.multiselect(
        "Filter by Location",
        options=companies["location"].unique(),
        default=companies["location"].unique()
    )
    
    st.divider()
    st.markdown("**Model Info**")
    st.metric("Total Companies", len(companies))
    st.metric("High-Risk Companies", (fraud_proba > risk_threshold).sum())
    st.metric("Flagged as Fraud", (companies["predicted_fraud"] == 1).sum())

# ============================================================================
# MAIN CONTENT
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([" Overview", "Detailed Analysis", " Risk Scoring", "Network Insights"])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    filtered_companies = companies[companies["location"].isin(location_filter)]
    
    with col1:
        st.metric(
            "Total Companies",
            len(filtered_companies),
            delta=None,
            delta_color="normal"
        )
    
    with col2:
        high_risk_count = (filtered_companies["fraud_probability"] > risk_threshold).sum()
        st.metric(
            "High-Risk Companies",
            high_risk_count,
            delta=f"{100*high_risk_count/len(filtered_companies):.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        fraud_count = (filtered_companies["predicted_fraud"] == 1).sum()
        st.metric(
            "Predicted Fraud",
            fraud_count,
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        avg_risk = filtered_companies["fraud_probability"].mean()
        st.metric(
            "Avg Risk Score",
            f"{avg_risk:.2%}",
            delta=None
        )
    
    st.divider()
    
    # Fraud distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        fraud_dist = filtered_companies["predicted_fraud"].value_counts()
        fig = go.Figure(data=[
            go.Bar(
                x=["Normal", "Fraud"],
                y=fraud_dist.values,
                marker=dict(color=["green", "red"])
            )
        ])
        fig.update_layout(
            title="Predicted Fraud Distribution",
            xaxis_title="Status",
            yaxis_title="Count",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk score distribution
        fig = go.Figure(data=[
            go.Histogram(
                x=filtered_companies["fraud_probability"],
                nbinsx=30,
                marker=dict(color="blue")
            )
        ])
        fig.update_layout(
            title="Fraud Probability Distribution",
            xaxis_title="Fraud Probability",
            yaxis_title="Count",
            height=400
        )
        fig.add_vline(x=risk_threshold, line_dash="dash", line_color="red",
                     annotation_text=f"Threshold: {risk_threshold:.2f}")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2: DETAILED ANALYSIS
# ============================================================================

with tab2:
    st.header("Company-Level Fraud Analysis")
    
    # Company search
    search_company = st.text_input("Search by Company ID", "")
    
    filtered_companies_detail = companies[companies["location"].isin(location_filter)]
    filtered_companies_detail = filtered_companies_detail[
        filtered_companies_detail["fraud_probability"] > risk_threshold
    ]
    
    if search_company:
        try:
            company_id = int(search_company)
            filtered_companies_detail = filtered_companies_detail[
                filtered_companies_detail["company_id"] == company_id
            ]
        except ValueError:
            st.warning("Please enter a valid company ID")
    
    # Sort by fraud probability
    filtered_companies_detail = filtered_companies_detail.sort_values(
        "fraud_probability",
        ascending=False
    )
    
    # Display table
    st.subheader("High-Risk Companies (Sorted by Risk)")
    
    display_cols = ["company_id", "location", "turnover", "fraud_probability", "predicted_fraud"]
    display_df = filtered_companies_detail[display_cols].copy()
    display_df["fraud_probability"] = display_df["fraud_probability"].apply(lambda x: f"{x:.2%}")
    display_df["turnover"] = display_df["turnover"].apply(lambda x: f"₹{x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)
    
    # Company detail view
    st.subheader("Detailed Company Information")
    
    if len(filtered_companies_detail) > 0:
        selected_company_idx = st.selectbox(
            "Select a company to view details",
            range(len(filtered_companies_detail)),
            format_func=lambda i: f"Company {filtered_companies_detail.iloc[i]['company_id']}"
        )
        
        company = filtered_companies_detail.iloc[selected_company_idx]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Company ID", int(company["company_id"]))
            st.metric("Location", company["location"])
        
        with col2:
            st.metric("Fraud Probability", f"{company['fraud_probability']:.2%}")
            st.metric("Predicted Status", " FRAUD" if company["predicted_fraud"] == 1 else "Normal")
        
        with col3:
            st.metric("Turnover", f"₹{company['turnover']:.2f}")
            st.metric("Invoice Frequency", int(company["invoice_frequency"]))
        
        # Transaction network
        st.subheader("Transaction Partners")
        company_id = int(company["company_id"])
        
        # Outgoing invoices
        outgoing = invoices[invoices["seller_id"] == company_id]
        # Incoming invoices
        incoming = invoices[invoices["buyer_id"] == company_id]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Invoices Sent", len(outgoing))
            st.metric("Total Amount Sent", f"₹{outgoing['amount'].sum():.2f}")
        
        with col2:
            st.metric("Invoices Received", len(incoming))
            st.metric("Total Amount Received", f"₹{incoming['amount'].sum():.2f}")

# ============================================================================
# TAB 3: RISK SCORING
# ============================================================================

with tab3:
    st.header("Risk Scoring Model")
    
    st.markdown("""
    ### Fraud Risk Calculation
    
    The GNN model computes a fraud probability for each company based on:
    
    **Node Features:**
    - Company Turnover
    - Invoice Sent Count
    - Invoice Received Count
    
    **Graph Structure:**
    - Connected company networks (invoice relationships)
    - Invoice amounts and ITC values
    - Subgraph patterns (shell companies)
    
    **Model Architecture:**
    - Graph Convolutional Networks (GCN)
    - 3-layer architecture for learning patterns
    - Classification into Normal (0) or Fraud (1)
    """)
    
    # Risk distribution by location
    fig = px.box(
        companies,
        x="location",
        y="fraud_probability",
        title="Fraud Probability Distribution by Location",
        labels={"fraud_probability": "Fraud Probability", "location": "Location"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Turnover vs Risk
    fig = px.scatter(
        companies[companies["location"].isin(location_filter)],
        x="turnover",
        y="fraud_probability",
        color="predicted_fraud",
        title="Company Turnover vs Fraud Risk",
        labels={"turnover": "Turnover (₹)", "fraud_probability": "Fraud Probability"},
        hover_data=["company_id", "location"]
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 4: NETWORK INSIGHTS
# ============================================================================

with tab4:
    st.header("🌐 Network Analysis")
    
    st.markdown("""
    ### Graph-Level Insights
    
    These metrics are calculated from the transaction network structure.
    """)
    
    # Debug: Show data status
    with st.expander("🔍 Debug Information", expanded=False):
        st.write(f"Invoices shape: {invoices.shape if invoices is not None else 'None'}")
        st.write(f"Invoices columns: {list(invoices.columns) if invoices is not None and len(invoices) > 0 else 'No data'}")
        st.write(f"Graph data nodes: {graph_data.num_nodes if graph_data is not None else 'None'}")
        st.write(f"Graph data edges: {graph_data.num_edges if graph_data is not None else 'None'}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Load graph stats if available
    try:
        with col1:
            st.metric("Total Nodes", graph_data.num_nodes)
        
        with col2:
            st.metric("Total Edges", graph_data.num_edges)
        
        with col3:
            if graph_data.num_nodes > 1:
                density = (2 * graph_data.num_edges) / (graph_data.num_nodes * (graph_data.num_nodes - 1))
            else:
                density = 0.0
            st.metric("Network Density", f"{density:.4f}")
        
        with col4:
            avg_degree = (2 * graph_data.num_edges) / graph_data.num_nodes if graph_data.num_nodes > 0 else 0
            st.metric("Avg. Degree", f"{avg_degree:.2f}")
    except Exception as e:
        st.error(f"Error loading graph statistics: {e}")
        st.exception(e)
    
    st.divider()
    
    # Invoice pattern analysis
    st.subheader("📊 Invoice Pattern Analysis")
    
    # Check if invoices data is available
    if invoices is None or len(invoices) == 0:
        st.error("❌ No invoice data available. Please check data loading.")
    elif "seller_id" not in invoices.columns or "buyer_id" not in invoices.columns:
        st.error(f"❌ Missing required columns. Available columns: {list(invoices.columns)}")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top 10 Invoice Senders**")
            try:
                # Group by seller_id and get counts
                sender_counts = invoices.groupby("seller_id").size().sort_values(ascending=False)
                top_senders = sender_counts.head(10)
                
                if len(top_senders) > 0:
                    # Convert to lists for Plotly
                    sender_ids = [str(x) for x in top_senders.index.tolist()]
                    counts = top_senders.values.tolist()
                    
                    # Create bar chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=sender_ids,
                        y=counts,
                        marker=dict(
                            color="steelblue",
                            line=dict(color="darkblue", width=1)
                        ),
                        text=counts,
                        textposition='outside',
                        textfont=dict(size=10)
                    ))
                    fig.update_layout(
                        title="Top 10 Invoice Senders",
                        xaxis_title="Company ID",
                        yaxis_title="Invoice Count",
                        height=400,
                        showlegend=False,
                        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                        yaxis=dict(range=[0, max(counts) * 1.15] if counts else [0, 10]),
                        margin=dict(b=100, l=60, r=20, t=60)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ No sender data found after grouping")
                    st.info(f"Total invoices: {len(invoices)}, Unique sellers: {invoices['seller_id'].nunique()}")
            except Exception as e:
                st.error(f"❌ Error creating top senders chart: {e}")
                st.exception(e)
        
        with col2:
            st.write("**Top 10 Invoice Recipients**")
            try:
                # Group by buyer_id and get counts
                recipient_counts = invoices.groupby("buyer_id").size().sort_values(ascending=False)
                top_recipients = recipient_counts.head(10)
                
                if len(top_recipients) > 0:
                    # Convert to lists for Plotly
                    recipient_ids = [str(x) for x in top_recipients.index.tolist()]
                    counts = top_recipients.values.tolist()
                    
                    # Create bar chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=recipient_ids,
                        y=counts,
                        marker=dict(
                            color="coral",
                            line=dict(color="darkred", width=1)
                        ),
                        text=counts,
                        textposition='outside',
                        textfont=dict(size=10)
                    ))
                    fig.update_layout(
                        title="Top 10 Invoice Recipients",
                        xaxis_title="Company ID",
                        yaxis_title="Invoice Count",
                        height=400,
                        showlegend=False,
                        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                        yaxis=dict(range=[0, max(counts) * 1.15] if counts else [0, 10]),
                        margin=dict(b=100, l=60, r=20, t=60)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ No recipient data found after grouping")
                    st.info(f"Total invoices: {len(invoices)}, Unique buyers: {invoices['buyer_id'].nunique()}")
            except Exception as e:
                st.error(f"❌ Error creating top recipients chart: {e}")
                st.exception(e)
        
        st.divider()
        
        # Additional network insights
        st.subheader("🔍 Network Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                # Transaction amount analysis
                if "amount" in invoices.columns and len(invoices) > 0:
                    amount_stats = invoices["amount"].describe()
                    fig = go.Figure(data=[
                        go.Box(
                            y=invoices["amount"],
                            name="Transaction Amounts",
                            marker=dict(color="lightblue")
                        )
                    ])
                    fig.update_layout(
                        title="Transaction Amount Distribution",
                        yaxis_title="Amount (₹)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Amount data not available")
            except Exception as e:
                st.error(f"Error creating amount distribution chart: {e}")
        
        with col2:
            try:
                # Invoice count over time (if date column exists)
                if "date" in invoices.columns and len(invoices) > 0:
                    invoices["date"] = pd.to_datetime(invoices["date"], errors='coerce')
                    invoices_by_date = invoices.groupby(invoices["date"].dt.to_period("M")).size()
                    fig = go.Figure(data=[
                        go.Scatter(
                            x=invoices_by_date.index.astype(str),
                            y=invoices_by_date.values,
                            mode='lines+markers',
                            marker=dict(color="green", size=8),
                            line=dict(width=2)
                        )
                    ])
                    fig.update_layout(
                        title="Invoice Count Over Time",
                        xaxis_title="Month",
                        yaxis_title="Number of Invoices",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Show fraud risk distribution in network
                    if len(companies) > 0 and "fraud_probability" in companies.columns:
                        fig = go.Figure(data=[
                            go.Histogram(
                                x=companies["fraud_probability"],
                                nbinsx=20,
                                marker=dict(color="red", opacity=0.7)
                            )
                        ])
                        fig.update_layout(
                            title="Fraud Risk Distribution in Network",
                            xaxis_title="Fraud Probability",
                            yaxis_title="Number of Companies",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Time series or risk data not available")
            except Exception as e:
                st.error(f"Error creating time series chart: {e}")
        
        st.divider()
        
        # Network statistics table
        st.subheader("📈 Network Statistics Summary")
        
        try:
            stats_data = {
                "Metric": [
                    "Total Companies (Nodes)",
                    "Total Transactions (Edges)",
                    "Network Density",
                    "Average Connections per Node",
                    "Total Invoices",
                    "Average Invoice Amount",
                    "High-Risk Companies",
                    "Fraud Detection Rate"
                ],
                "Value": [
                    f"{graph_data.num_nodes:,}",
                    f"{graph_data.num_edges:,}",
                    f"{(2 * graph_data.num_edges) / (graph_data.num_nodes * (graph_data.num_nodes - 1)):.4f}" if graph_data.num_nodes > 1 else "0.0000",
                    f"{(2 * graph_data.num_edges) / graph_data.num_nodes:.2f}" if graph_data.num_nodes > 0 else "0.00",
                    f"{len(invoices):,}" if len(invoices) > 0 else "0",
                    f"₹{invoices['amount'].mean():,.2f}" if "amount" in invoices.columns and len(invoices) > 0 else "N/A",
                    f"{(companies['fraud_probability'] > 0.5).sum():,}" if "fraud_probability" in companies.columns else "N/A",
                    f"{((companies['fraud_probability'] > 0.5).sum() / len(companies) * 100):.2f}%" if "fraud_probability" in companies.columns and len(companies) > 0 else "N/A"
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error creating statistics table: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Tax Fraud Detection System** | Powered by Graph Neural Networks  
*SIH 2024 Project* | For demonstration and research purposes only
""")
