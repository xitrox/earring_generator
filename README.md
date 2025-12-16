# 💎 Earring Generator

A web-based tool for generating dual-color mandala earring designs optimized for multi-material 3D printing (AMS-compatible).

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **🎨 Vector-Based Generation** - Sharp, precise geometry (99.5% smaller files than raster)
- **⚡ Real-time 3D Preview** - See exactly what you'll print
- **🖨️ Print-Optimized** - Designed for 0.2mm nozzles and FDM printing
- **🎯 Chamfered Edges** - Professional finish, comfortable to wear
- **🔄 Infinite Variations** - Reproducible with seed-based generation
- **📦 Multi-Material Ready** - Exports separate base and relief for AMS/MMU

## 🚀 Quick Start

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`

### Deploy to Render.com (Free)

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions.

Quick deploy:
1. Push to GitHub
2. Go to https://render.com
3. Click "New Blueprint Instance"
4. Connect your repo - done! ✨

## 📐 Technical Details

### Architecture
- **Frontend:** React + Vite + Three.js
- **Backend:** Python Flask + Shapely + Trimesh
- **Generation:** Vector-based 2D polygon → 3D extrusion

### File Sizes
- **Raster approach:** ~20MB per earring ❌
- **Vector approach:** ~100KB per earring ✅

### Print Settings
- **Nozzle:** 0.2mm
- **Min line width:** 0.25mm
- **Layer height:** 0.1-0.2mm
- **Material:** PLA, PETG, ABS (dual-color)

## 🎯 Pattern Optimization

Patterns are optimized for FDM printing:
- Minimum feature size: 0.25mm (safe for 0.2mm nozzles)
- Line thickness: 0.25-0.5mm
- Chamfered top edges: 0.15mm bevel
- Hidden overlap: 0.05mm embedded adhesion

## 📝 Parameters

- **Diameter:** 8-25mm
- **Height:** 1-4mm
- **Relief Depth:** 0.2-2mm
- **Seed:** Any string (for reproducibility)

## 🔧 Technology Stack

**Backend:**
- Flask 3.0
- Shapely 2.0 (2D geometry)
- Trimesh 4.0 (3D mesh operations)
- NumPy, Pillow, SciPy

**Frontend:**
- React 19
- Vite 7
- Three.js + React Three Fiber
- Tailwind CSS

## 📦 Export Formats

- **3MF:** Multi-material 3D printing (recommended)
- **GLB:** Web preview format

## 🎨 Pattern Types

- **Rings:** Concentric circles
- **Rays:** Radial lines
- **Petals:** Circular patterns
- **Dots:** Ring arrangements
- **Custom combinations** with 6, 8, or 12-fold symmetry

## 🤝 Contributing

Contributions welcome! This is a personal project but feel free to fork and adapt.

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🙏 Acknowledgments

Built with modern web technologies and optimized for real-world 3D printing.

---

**Happy Printing! 🎨✨**
