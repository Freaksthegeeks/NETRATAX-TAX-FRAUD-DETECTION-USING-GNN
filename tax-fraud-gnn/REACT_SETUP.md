# React Frontend Setup Guide

This project now includes a modern React.js frontend with beautiful animations and the custom color palette.

## Quick Start

### 1. Install Node.js Dependencies

```bash
cd tax-fraud-gnn/frontend
npm install
```

### 2. Development Mode (Recommended)

**Terminal 1 - Start Flask Backend:**
```bash
cd tax-fraud-gnn
python app.py
```

**Terminal 2 - Start React Dev Server:**
```bash
cd tax-fraud-gnn/frontend
npm run dev
```

- React frontend: http://localhost:3000
- Flask API: http://localhost:5000

### 3. Production Build

Build the React app for production:

**Windows:**
```bash
cd tax-fraud-gnn/frontend
build.bat
```

**Linux/Mac:**
```bash
cd tax-fraud-gnn/frontend
chmod +x build.sh
./build.sh
```

Or manually:
```bash
cd tax-fraud-gnn/frontend
npm install
npm run build
```

After building, Flask will automatically serve the React app from `static/react/`.

## Features

### 🎨 Color Palette Applied
- **Arctic Powder** (#F1F6F4) - Backgrounds
- **Forsythia** (#FFC801) - Primary accents
- **Nocturnal Expedition** (#114C5A) - Dark elements
- **Mystic Mint** (#D9E8E2) - Secondary backgrounds
- **Deep Saffron** (#FF9932) - Warnings/High risk
- **Oceanic Noir** (#172B36) - Text

### ✨ Animations & Interactions
- Smooth page transitions
- Hover effects on cards and buttons
- Loading animations
- Interactive charts
- Modal animations
- Staggered list animations

### 📱 Responsive Design
- Mobile-friendly layout
- Adaptive grid systems
- Touch-friendly interactions

## Troubleshooting

### Port Already in Use
If port 3000 is busy:
- Change it in `vite.config.js`: `server: { port: 3001 }`

### CORS Errors
- Flask CORS is enabled, but if issues persist, check Flask is running on port 5000

### Build Errors
- Make sure Node.js version is 16+ (`node --version`)
- Delete `node_modules` and `package-lock.json`, then `npm install` again

## File Structure

```
tax-fraud-gnn/
├── frontend/              # React app
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── static/
│   └── react/            # Production build (after npm run build)
└── app.py                # Flask backend (serves React)
```

## Next Steps

1. Install dependencies: `cd frontend && npm install`
2. Start dev server: `npm run dev`
3. Open http://localhost:3000
4. Enjoy the beautiful, animated interface! 🎉

