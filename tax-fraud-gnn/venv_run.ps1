<#
Run a Python script using the project's virtualenv Python (big).

Usage examples:
  # Run a python script with arguments
  .\venv_run.ps1 prepare_real_data.py

  # Forward arbitrary args to the script
  .\venv_run.ps1 train_gnn_model.py --epochs 50

This script simply forwards arguments to the venv python executable so you
do not need to call Activate.ps1 or change shells.
#>

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$VENV_PY = "C:/BIG HACK/big/Scripts/python.exe"

if (-not (Test-Path $VENV_PY)) {
    Write-Error "Virtualenv python not found at $VENV_PY"
    exit 1
}

if ($Args.Count -eq 0) {
    # If no args provided, open interactive REPL with venv python
    & $VENV_PY
} else {
    & $VENV_PY @Args
}
