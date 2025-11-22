@echo off
REM Run commands using the project's virtualenv Python (big)
SET VENV_PY="C:\BIG HACK\big\Scripts\python.exe"
IF NOT EXIST %~dp0\..\big\Scripts\python.exe (
  REM fallback to exact path as set above
  %VENV_PY% %*
) ELSE (
  %VENV_PY% %*
)
