# Earring Generator

A web-based generative earring designer that creates unique mandala patterns for 3D printing. Features vector-based pattern generation for sharp edges and small file sizes (~100KB vs 20MB).

## Features

- **Vector-Based Generation**: Sharp, clean edges perfect for 3D printing (99.5% file size reduction)
- **Real-Time 3D Preview**: View actual mesh geometry with interactive rotation
- **Pattern Controls**: Customize symmetry, complexity, and pattern types while maintaining seed-based randomization
- **Optimized for FDM Printing**: Minimum 0.25mm features for 0.2mm nozzles
- **Professional Finish**: Chamfered edges for comfort and aesthetic appeal
- **Multiple Export Formats**: 3MF and GLB file export

## Pattern Options

- **Symmetry**: 6-fold, 8-fold, 12-fold, or random
- **Complexity**: 1-5 elements per pattern
- **Pattern Types**: Rings, Rays, Petals, Dots (toggle individually)
- **Dimensions**: 8-25mm diameter, 1-4mm height, 0.2-2mm relief depth

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- (Optional) SWAG for SSL/reverse proxy

### Deploy

```bash
# Clone the repository
git clone <repository-url>
cd earring_generator

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f
```

Access at `http://localhost:8080`

For integration with SWAG and SSL setup, see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

## Local Development

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for running without Docker.

### Backend (Python/Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:5000`

### Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## Project Structure

```
earring_generator/
├── backend/
│   ├── app.py                  # Flask API server
│   ├── vector_generator.py     # Pattern generation (Shapely)
│   ├── vector_exporter.py      # 3D mesh creation (Trimesh)
│   ├── vector_rasterizer.py    # PNG preview conversion
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main application
│   │   ├── components/
│   │   │   ├── Viewer.jsx     # 3D viewer (React Three Fiber)
│   │   │   └── Controls.jsx   # Pattern controls UI
│   │   └── main.jsx
│   └── package.json
├── deployment/
│   ├── docker-nginx.conf      # Nginx config for container
│   └── supervisord.conf       # Process manager config
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Technology Stack

### Backend
- **Flask**: Web framework with CORS support
- **Shapely**: 2D polygon operations and boolean geometry
- **Trimesh**: 3D mesh creation and extrusion
- **Pillow**: Image processing for 2D previews
- **NumPy**: Numerical operations

### Frontend
- **React**: UI framework
- **Vite**: Build tool and dev server
- **React Three Fiber**: 3D rendering with Three.js
- **@react-three/drei**: 3D helpers and controls
- **Tailwind CSS**: Styling

## API Endpoints

### GET /api/preview
Returns PNG preview of the 2D pattern.

**Query Parameters:**
- `seed`: Pattern seed (string)
- `diameter`: Diameter in mm (float)
- `symmetry`: 6, 8, 12, or "random" (optional)
- `complexity`: 1-5 (optional)
- `pattern_types`: Comma-separated list (optional)
- `line_thickness`: "min,max" in mm (optional)

### GET /api/preview3d
Returns GLB (binary glTF) 3D mesh for real-time preview.

**Query Parameters:** Same as `/api/preview` plus:
- `height`: Total height in mm (float)
- `relief_depth`: Relief depth in mm (float)

### POST /api/export
Exports 3MF file for 3D printing.

**Request Body (JSON):**
```json
{
  "seed": "abc123",
  "diameter": 12.0,
  "height": 2.0,
  "relief_depth": 0.8,
  "symmetry": 8,
  "complexity": 4,
  "pattern_types": ["ring", "ray", "petal_curve"],
  "line_thickness": [0.25, 0.5]
}
```

## Architecture Highlights

### Vector-Based Approach
- Generates 2D polygons using Shapely (not raster heightmaps)
- Extrudes polygons to 3D using Trimesh
- Results: 98%+ vertex reduction, perfectly sharp edges
- File sizes: <100KB (down from ~20MB)

### Pattern Generation
- Seed-based randomization for reproducibility
- User constraints (symmetry, complexity, types)
- Adaptive quality based on diameter (quad_segs)
- Radial symmetry with component layering

### 3D Mesh Creation
- Base cylinder + relief pattern extrusion
- 0.15mm chamfer on relief edges
- 0.05mm overlap for print adhesion (hidden internally)
- Watertight mesh validation

## Deployment Options

- **Docker + SWAG**: See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Raspberry Pi**: See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - works with SWAG
- **Local Development**: See [LOCAL_SETUP.md](LOCAL_SETUP.md)

## Development

### Environment Variables
- `USE_VECTOR_GENERATOR=true`: Enable vector mode (default)
- `PYTHONUNBUFFERED=1`: Better logging

### Testing Pattern Generation
```bash
cd backend
python vector_generator.py  # Test vector generation
python vector_rasterizer.py # Test PNG conversion
```

## Performance

- Pattern generation: 0.5-2 seconds
- 3D mesh creation: 1-3 seconds
- File sizes: 50-100KB (3MF format)
- Vertices: 5,000-20,000 (vs 1M+ with raster)

## Print Settings Recommendations

- **Layer height**: 0.1-0.2mm
- **Nozzle**: 0.2mm or larger
- **Material**: PLA, PETG, or resin
- **Infill**: 100% (small part)
- **Supports**: None needed
- **Bed adhesion**: Brim recommended for small contact area

## Contributing

Feel free to open issues or submit pull requests.

## License

MIT License
