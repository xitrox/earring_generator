from flask import Flask, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
import numpy as np
from PIL import Image
import io
import zipfile
import generator
import exporter
import tempfile
import os

app = Flask(__name__)

# In-memory cache for simple "save" (in a real app, use DB)
SAVED_PATTERNS = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/', methods=['GET'])
def index():
    return "Earring Generator Backend is Running. Use /api/preview or frontend to interact."

@app.route('/api/preview', methods=['GET'])
def preview():
    seed = request.args.get('seed', 'default')
    # Generate heightmap
    hmap = generator.generate_mandala(seed)
    # Convert to image
    img = Image.fromarray((hmap * 255).astype(np.uint8))
    
    # Return as PNG
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/api/export', methods=['POST'])
def export_stls():
    data = request.json
    seed = data.get('seed')
    diameter = float(data.get('diameter', 12.0))
    height = float(data.get('height', 2.0)) # Total height
    relief_depth = float(data.get('relief_depth', 1.0))
    
    base_height = height - relief_depth
    
    hmap = generator.generate_mandala(seed)
    
    # Generate scene
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
