# Powershell helper to start Neo4j with GDS and verify installation
# Usage: run_local_gds.ps1

# Start Neo4j with docker-compose
docker-compose up -d

Write-Host "Waiting for Neo4j to start and GDS to initialize (this may take 30-90s)..."

# Poll for gds.version() via Python one-liner until it succeeds or timeout
$timeout = 300  # seconds
$start = Get-Date
while ((Get-Date) - $start).TotalSeconds -lt $timeout {
    try {
        & "D:\NetraTax\big\Scripts\python.exe" - <<'PY'
from neo4j import GraphDatabase
import os, sys
uri = os.environ.get('NEO4J_URI','bolt://localhost:7687')
user = os.environ.get('NEO4J_USER','neo4j')
password = os.environ.get('NEO4J_PASSWORD','neo4j')
try:
    driver = GraphDatabase.driver(uri, auth=(user,password))
    with driver.session() as session:
        res = session.run('RETURN gds.version() AS v')
        v = res.single()
        if v:
            print('GDS_VERSION:'+str(v['v']))
            sys.exit(0)
except Exception as e:
    # print(e)
    sys.exit(2)
PY
        if ($LASTEXITCODE -eq 0) {
            Write-Host "GDS is available."
            break
        }
    } catch {
        # ignore
    }
    Start-Sleep -Seconds 5
}

if ((Get-Date) - $start).TotalSeconds -ge $timeout {
    Write-Host "Timed out waiting for GDS to become available. Check docker logs: docker logs <container> --tail 200"
    exit 1
}

Write-Host "Tip: update environment variables for local run (examples):"
Write-Host "  $env:NEO4J_URI='bolt://localhost:7687'"
Write-Host "  $env:NEO4J_USER='neo4j'"
Write-Host "  $env:NEO4J_PASSWORD='neo4j'"
Write-Host "Then run: python .\\gds_analytics.py"
