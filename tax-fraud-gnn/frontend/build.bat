@echo off
echo Building React frontend...
cd frontend
call npm install
call npm run build
echo Build complete! React app is in static/react/
pause

