#!/bin/bash
echo "Building React frontend..."
cd frontend
npm install
npm run build
echo "Build complete! React app is in static/react/"

