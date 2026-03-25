# Local Neo4j + Graph Data Science (GDS) setup

This guide helps you run a local Neo4j instance with the Graph Data Science library enabled and then run the repository's GDS analytics script.

Files added:
- `docker-compose.yml` : launches Neo4j 5.x with the `graph-data-science` labs plugin enabled
- `run_local_gds.ps1` : PowerShell helper to start the container and wait for GDS
- `gds_analytics.py` : already present; it now reads `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` from the environment

Quick start (Windows / PowerShell)
1. Start the local Neo4j container:

```powershell
cd D:\NetraTax\tax-fraud-gnn
# start Neo4j with GDS
docker-compose up -d
# or use the helper
.\run_local_gds.ps1
```

2. Set environment variables for the local DB (in the same PowerShell session):

```powershell
$env:NEO4J_URI = 'bolt://localhost:7687'
$env:NEO4J_USER = 'neo4j'
$env:NEO4J_PASSWORD = 'neo4j'
```

3. (Optional) If you need to load sample CSV data into Neo4j, run your loader:

```powershell
# ensure neo4j_client.py points to the local DB or set env vars used by your loader
python load_to_neo4j.py
```

4. Run the analytics script (this will project and run PageRank/Louvain/WCC and write properties back to nodes):

```powershell
python D:\NetraTax\tax-fraud-gnn\gds_analytics.py
```

Notes
- The `docker-compose.yml` sets `NEO4JLABS_PLUGINS` to `graph-data-science`. The image will download the plugin on startup.
- If you prefer a different admin password, set `NEO4J_AUTH` in `docker-compose.yml` before starting the container.
- For production or large graphs, tune Neo4j memory settings and ensure disk space for the GDS plugin.

If you want, I can also:
- Add a script to automatically import CSV files into the running local Neo4j instance
- Add a convenience script that sets environment variables and runs `gds_analytics.py` end-to-end
