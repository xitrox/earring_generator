# 🏠 Local Setup Guide

Complete guide to running the Earring Generator locally on your machine.

## Prerequisites

- **Python 3.10+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/)

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/earring_generator.git
cd earring_generator
```

### 2. Set Up Backend (Python/Flask)

```bash
# Navigate to backend folder
cd backend

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python app.py
```

✅ Backend should now be running at `http://localhost:5000`

You should see:
```
✓ Using VECTOR-BASED generator (sharp edges, small files)
* Running on http://127.0.0.1:5000
```

### 3. Set Up Frontend (React/Vite)

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

✅ Frontend should now be running at `http://localhost:5173`

You should see:
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### 4. Open in Browser

Visit **http://localhost:5173** in your browser!

## 🎨 Using the Application

### Controls
- **Diameter** - Size of the earring (8-25mm)
- **Total Height** - Overall thickness (1-4mm)
- **Relief Depth** - Height of the pattern (0.2-2mm)
- **Seed** - Random pattern identifier (same seed = same pattern)

### Buttons
- **← →** - Navigate between patterns
- **2D Pattern / 3D Preview** - Toggle view modes
- **Export STL** - Download 3MF file for printing

### Pattern Generation
Currently patterns are generated randomly based on the seed:
- **Symmetry**: 6, 8, or 12-fold (random)
- **Components**: 3-5 elements (random)
- **Types**: Rings, rays, petals, dots (random combination)
- **Thickness**: 0.25-0.5mm (optimized for 0.2mm nozzle)

## 📁 Project Structure

```
earring_generator/
├── backend/
│   ├── app.py              # Flask API server
│   ├── generator.py        # Legacy raster generator
│   ├── vector_generator.py # Vector pattern generation ✨
│   ├── vector_exporter.py  # 3D mesh extrusion
│   ├── vector_rasterizer.py# 2D preview rendering
│   ├── exporter.py         # Legacy exporter
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main app component
│   │   ├── components/
│   │   │   ├── Viewer.jsx    # 3D viewer
│   │   │   └── Controls.jsx  # UI controls
│   │   └── main.jsx
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Build configuration
└── specs.md               # Original specifications
```

## 🔧 Development Tips

### Backend Development
- Backend runs on port **5000**
- Auto-reloads on code changes (Flask debug mode)
- Check logs in terminal for errors
- API endpoints:
  - `GET /api/preview` - 2D PNG preview
  - `GET /api/preview3d` - 3D GLB model
  - `POST /api/export` - 3MF file export

### Frontend Development
- Frontend runs on port **5173**
- Hot-reloads on code changes (Vite HMR)
- API calls proxy to backend automatically
- Check browser console for errors

### Switching Between Vector/Raster Mode

You can toggle between vector and raster generation:

```bash
# In backend terminal:
export USE_VECTOR_GENERATOR=false  # Use legacy raster mode
export USE_VECTOR_GENERATOR=true   # Use vector mode (default)

# Then restart: python app.py
```

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Backend: Reinstall dependencies
cd backend
pip install -r requirements.txt

# Frontend: Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Activate virtual environment
- Check port 5000 isn't already in use

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Clear npm cache: `npm cache clean --force`
- Check port 5173 isn't already in use

### 3D Preview shows "Generating..."
- Check backend is running
- Check browser console for errors
- Try refreshing the page

### Export button doesn't work
- Check backend terminal for errors
- Verify all dependencies installed (especially `scipy`, `networkx`, `lxml`)
- Check browser downloads folder

## 📦 Dependencies Explained

### Backend (Python)
- **flask** - Web server
- **shapely** - 2D geometry operations
- **trimesh** - 3D mesh operations
- **numpy** - Numerical computing
- **pillow** - Image processing
- **scipy** - Scientific computing
- **networkx** - Graph operations (for 3MF export)
- **lxml** - XML processing (for 3MF export)

### Frontend (JavaScript)
- **react** - UI framework
- **three.js** - 3D rendering
- **@react-three/fiber** - React wrapper for Three.js
- **@react-three/drei** - Three.js helpers
- **vite** - Build tool
- **tailwindcss** - Styling

## 🚀 Next Steps

1. **Explore Patterns** - Try different seeds, adjust parameters
2. **Export & Print** - Download 3MF, slice, and print!
3. **Customize** - Edit code to create custom pattern types
4. **Share** - Deploy to hosting service when ready

## 💡 Tips for Best Results

### For 3D Printing
- Use **0.2mm nozzle** or smaller
- Layer height: **0.1-0.2mm**
- Print speed: **30-50 mm/s** for best detail
- Materials: **PLA, PETG, ABS** (dual-color setup)

### Pattern Selection
- Small earrings (8-12mm): Keep relief depth low (0.5-0.8mm)
- Large earrings (20-25mm): Can use deeper relief (1.0-1.5mm)
- High symmetry = more detail (12-fold vs 6-fold)

### Performance
- 3D preview generation: **1-3 seconds**
- Export generation: **2-5 seconds**
- File sizes: **~100-200 KB** (vector mode)

## 🤝 Need Help?

- Check the main [README.md](README.md)
- Review [specs.md](specs.md) for technical details
- Check browser/terminal console for errors

Happy earring making! 💎✨
