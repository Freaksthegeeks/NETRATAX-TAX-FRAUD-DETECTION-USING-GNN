# Incremental Learning Implementation

This document describes the implementation of incremental learning functionality for the Tax Fraud GNN system.

## Overview

The incremental learning system allows the model to be updated with new data without requiring a full retraining from scratch. When new CSV files are uploaded through the web interface, the system:

1. Updates the graph with new nodes/edges
2. Identifies affected subgraphs
3. Retrains only those subgraphs
4. Updates global embeddings and model weights

## Key Functions

### 1. `update_graph(new_companies_df, new_invoices_df)`
Updates the existing NetworkX graph with new nodes and edges from uploaded data.

- **Parameters:**
  - `new_companies_df`: DataFrame with new company data
  - `new_invoices_df`: DataFrame with new invoice data
- **Returns:** Updated NetworkX graph and mappings

### 2. `identify_affected_nodes(new_companies_df, new_invoices_df, k_hop=2)`
Identifies nodes that are affected by new data (new nodes + neighbors within k-hop).

- **Parameters:**
  - `new_companies_df`: DataFrame with new company data
  - `new_invoices_df`: DataFrame with new invoice data
  - `k_hop`: Number of hops to consider for neighborhood (default: 2)
- **Returns:** List of affected node IDs

### 3. `extract_subgraph(affected_nodes, k_hop=2)`
Extracts a k-hop subgraph around affected nodes.

- **Parameters:**
  - `affected_nodes`: List of affected node IDs
  - `k_hop`: Number of hops to extract (default: 2)
- **Returns:** NetworkX subgraph

### 4. `networkx_to_pytorch_geometric_subgraph(G, full_node_to_idx)`
Converts a NetworkX subgraph to PyTorch Geometric Data object.

- **Parameters:**
  - `G`: NetworkX graph
  - `full_node_to_idx`: Full node to index mapping
- **Returns:** PyTorch Geometric Data object, node list, node to index mapping

### 5. `incremental_retrain(subgraph_data, epochs=50, lr=0.001)`
Retrains the model on subgraph data.

- **Parameters:**
  - `subgraph_data`: PyTorch Geometric Data object
  - `epochs`: Number of training epochs (default: 50)
  - `lr`: Learning rate (default: 0.001)
- **Returns:** Updated model state dict

### 6. `update_global_embeddings()`
Updates global fraud probabilities for all nodes after incremental training.

### 7. `save_updated_graph_and_model()`
Saves updated graph, mappings, and model weights to disk.

### 8. `process_incremental_learning(file_path, filename)`
Main function that orchestrates the entire incremental learning process.

- **Parameters:**
  - `file_path`: Path to uploaded CSV file
  - `filename`: Name of uploaded file

## Integration

The incremental learning functionality is integrated into the upload pipeline:

1. When a CSV file is uploaded via `/api/upload_data`
2. The `process_incremental_learning()` function is called
3. The system automatically determines if it's companies or invoices data
4. Appropriate feature engineering is applied
5. The graph is updated with new data
6. Affected subgraphs are identified and extracted
7. The model is incrementally retrained on the subgraph
8. Global embeddings are updated
9. Updated graph and model are saved to disk

## Benefits

1. **Efficiency**: Only retrain affected portions of the graph instead of the entire model
2. **Scalability**: Handle large graphs by focusing on local updates
3. **Real-time Updates**: Process new data as it arrives without downtime
4. **Resource Conservation**: Use less computational resources than full retraining

## Usage

The system works automatically when new CSV files are uploaded through the web interface. No additional API calls are needed.

For programmatic access, you can call the `/api/upload_data` endpoint with a CSV file.

## Error Handling

The system includes comprehensive error handling:

- Graceful degradation if incremental learning fails
- Detailed logging of all operations
- Fallback mechanisms for data processing
- Validation of input data formats

## Future Improvements

1. Add support for batch processing of multiple files
2. Implement more sophisticated subgraph selection algorithms
3. Add performance monitoring and metrics
4. Implement rollback mechanisms for failed updates