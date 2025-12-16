from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import numpy as np
from PIL import Image
import io
import zipfile
import tempfile
import os

# Feature flag: Use vector-based generation (default: True)
USE_VECTOR_GENERATOR = os.environ.get('USE_VECTOR_GENERATOR', 'true').lower() == 'true'

# Import modules based on feature flag
if USE_VECTOR_GENERATOR:
    import vector_generator
    import vector_rasterizer
    import vector_exporter
    print("✓ Using VECTOR-BASED generator (sharp edges, small files)")
else:
    print("✓ Using RASTER-BASED generator (legacy mode)")

# Always import for fallback
import generator
import exporter

app = Flask(__name__)

# Enable CORS for production (allow frontend to call backend API)
CORS(app)

# In-memory cache for simple "save" (in a real app, use DB)
SAVED_PATTERNS = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/', methods=['GET'])
def index():
    mode = "VECTOR" if USE_VECTOR_GENERATOR else "RASTER"
    return f"Earring Generator Backend is Running ({mode} mode). Use /api/preview or frontend to interact."

@app.route('/api/preview', methods=['GET'])
def preview():
    seed = request.args.get('seed', 'default')
    diameter = float(request.args.get('diameter', 12.0))

    if USE_VECTOR_GENERATOR:
        # Vector approach: generate polygon, then rasterize for preview
        polygon = vector_generator.generate_mandala_vector(seed, diameter_mm=diameter)
        img = vector_rasterizer.rasterize_polygon_to_png(polygon, diameter_mm=diameter)
    else:
        # Raster approach (legacy)
        hmap = generator.generate_mandala(seed)
        img = Image.fromarray((hmap * 255).astype(np.uint8))

    # Return as PNG
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/api/preview3d', methods=['GET'])
def preview3d():
    """
    Generate and return actual 3D mesh for real-time preview.
    Returns GLB format (compact binary glTF) instead of PNG.
    This shows the actual vector geometry with sharp edges!
    """
    seed = request.args.get('seed', 'default')
    diameter = float(request.args.get('diameter', 12.0))
    height = float(request.args.get('height', 2.0))
    relief_depth = float(request.args.get('relief_depth', 0.8))

    base_height = height - relief_depth

    if USE_VECTOR_GENERATOR:
        # Vector approach: generate polygon, extrude to 3D
        polygon = vector_generator.generate_mandala_vector(seed, diameter_mm=diameter)
        scene = vector_exporter.create_stls_from_vector(
            polygon, diameter, base_height, relief_depth
        )
    else:
        # Raster approach (legacy)
        hmap = generator.generate_mandala(seed)
        scene = exporter.create_stls(hmap, diameter, base_height, relief_depth)

    # Export as GLB (binary glTF - compact and web-friendly)
    with tempfile.NamedTemporaryFile(suffix='.glb', delete=False) as tmp:
        scene.export(tmp.name, file_type='glb')
        tmp_path = tmp.name

    # Return GLB
    with open(tmp_path, 'rb') as f:
        data_io = io.BytesIO(f.read())

    os.unlink(tmp_path)

    return send_file(
        data_io,
        mimetype='model/gltf-binary',
        as_attachment=False  # Not a download, just for preview
    )

@app.route('/api/export', methods=['POST'])
def export_stls():
    data = request.json
    seed = data.get('seed')
    diameter = float(data.get('diameter', 12.0))
    height = float(data.get('height', 2.0)) # Total height
    relief_depth = float(data.get('relief_depth', 1.0))

    base_height = height - relief_depth

    if USE_VECTOR_GENERATOR:
        # Vector approach: generate polygon, extrude to 3D
        polygon = vector_generator.generate_mandala_vector(seed, diameter_mm=diameter)
        scene = vector_exporter.create_stls_from_vector(
            polygon, diameter, base_height, relief_depth
        )
    else:
        # Raster approach (legacy)
        hmap = generator.generate_mandala(seed)
        scene = exporter.create_stls(hmap, diameter, base_height, relief_depth)

    # Export as 3MF
    # 3MF supports multiple meshes in one file.
    with tempfile.NamedTemporaryFile(suffix='.3mf', delete=False) as tmp:
        scene.export(tmp.name, file_type='3mf')
        tmp_path = tmp.name

    # Return 3mf
    with open(tmp_path, 'rb') as f:
        data_io = io.BytesIO(f.read())

    os.unlink(tmp_path)

    return send_file(
        data_io,
        mimetype='model/3mf',
        as_attachment=True,
        download_name=f'earring_{seed}.3mf'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
