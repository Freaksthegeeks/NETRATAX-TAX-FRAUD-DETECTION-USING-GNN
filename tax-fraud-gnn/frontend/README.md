# Tax Fraud Detection - React Frontend

Modern, interactive React.js frontend with beautiful animations and the custom color palette.

## Color Palette

- **Arctic Powder**: #F1F6F4 (Background)
- **Forsythia**: #FFC801 (Primary Accent)
- **Nocturnal Expedition**: #114C5A (Primary Dark)
- **Mystic Mint**: #D9E8E2 (Secondary Background)
- **Deep Saffron**: #FF9932 (Warning/High Risk)
- **Oceanic Noir**: #172B36 (Text/Dark)

## Setup

1. **Install Node.js** (if not already installed)
   - Download from https://nodejs.org/
   - Verify: `node --version` and `npm --version`

2. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Development Mode**
   ```bash
   npm run dev
   ```
   - Frontend runs on http://localhost:3000
   - Make sure Flask backend is running on http://localhost:5000

4. **Build for Production**
   ```bash
   npm run build
   ```
   - Builds to `../static/react/`
   - Flask will serve this automatically

## Features

- ✨ Smooth animations with Framer Motion
- 🎨 Beautiful color palette throughout
- 📊 Interactive charts with Plotly
- 🔍 Advanced filtering and search
- 📱 Responsive design
- ⚡ Fast and optimized

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── pages/          # Page components
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── package.json        # Dependencies
└── vite.config.js      # Vite configuration
```

