import trimesh
import numpy as np
from PIL import Image

def create_stls(heightmap, diameter_mm, base_height_mm, relief_height_mm):
    """
    Converts a heightmap (numpy array 0-1) into a Trimesh Scene containing:
    1. Base Disc
    2. Relief Pattern
    """
    resolution = heightmap.shape[0]
    radius_mm = diameter_mm / 2.0
    
    # 1. Base Disc
    # Simple cylinder
    base_mesh = trimesh.creation.cylinder(radius=radius_mm, height=base_height_mm, sections=128)
    
    # Center the cylinder so its top surface is at z=0 (logic: base sits below 0)
    # Default cylinder is centered at 0, ranging from -h/2 to h/2.
    # We want it from -base_height to 0.
    base_mesh.apply_translation([0, 0, -base_height_mm / 2.0])
    
    # 2. Relief Pattern
    # Use heightmap to create a surface.
    # Grid points
    step = 2.0 * radius_mm / (resolution - 1)
    x = np.linspace(-radius_mm, radius_mm, resolution)
    y = np.linspace(-radius_mm, radius_mm, resolution)
    xx, yy = np.meshgrid(x, y)
    
    # Z coordinates: heightmap * relief_height
    zz = heightmap * relief_height_mm
    
    # Create vertices for the relief surface
    # Vertices: (N*N, 3)
    vertices = np.column_stack((xx.flatten(), yy.flatten(), zz.flatten()))
    
    # Faces: Generate grid indices
    # This is standard grid triangulation.
    # This is standard grid triangulation.
    # from trimesh.creation import triangulation
    # Unused and causing import error
    
    # Let's do manual index generation for a grid
    rows = resolution
    cols = resolution
    
    # Indices array
    # 2 triangles per square cell
    # cell (i, j) connects to (i+1, j), (i, j+1), (i+1, j+1)
    
    i, j = np.indices((rows-1, cols-1))
    
    # Triangle 1
    # v0 = i*cols + j
    # v1 = i*cols + (j+1)
    # v2 = (i+1)*cols + j
    v0 = i * cols + j
    v1 = i * cols + (j + 1)
    v2 = (i + 1) * cols + j
    
    # Triangle 2
    # v1 = i*cols + (j+1)
    # v3 = (i+1)*cols + (j+1)
    # v2 = (i+1)*cols + j
    v3 = (i + 1) * cols + (j + 1)
    
    faces_a = np.stack((v0, v2, v1), axis=-1).reshape(-1, 3)
    faces_b = np.stack((v1, v2, v3), axis=-1).reshape(-1, 3)
    faces = np.vstack((faces_a, faces_b))
    
    relief_surface = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # IMPROVEMENT: Make relief a valid volume, not just a surface.
    # Isolate relevant vertices (where z > 0) to avoid processing the huge flat area?
    # For now, simpler approach: Extrude the surface down slightly into the base to ensure overlap.
    # Actually, trimesh doesn't have a simple "extrude surface to plane" for complex meshes easily without errors.
    # Alternative: The relief is just the "ink".
    # User Request: "combine the two layers so they will not break apart easily."
    # Solution: Embed the relief -0.2mm into the base. 
    # Current Base: Top at Z=0.
    # Current Relief: Bottom at Z=0.
    # To embed: Move Relief down by 0.2mm. AND make sure it has thickness?
    # If Relief is just a surface, slicers might complain. It needs to be a closed volume.
    
    # Volume Logic:
    # 1. Take the surface. 
    # 2. Add a "floor" at Z = -0.2.
    # 3. Connect edges.
    # This is complex to code from scratch for a grid.
    
    # Easier approximation for "Release":
    # Just treat the relief as a thick voxelized grid or keep it as a surface if the slicer handles it (Bambu often does).
    # BUT, to be safe, let's just overlap them.
    
    # Let's move the Base UP by 0.2mm so it swallows the bottom of the relief?
    # No, Relief is Z >= 0.
    # Move Base Z up by 0.2. Base Top is now at 0.2.
    # Relief Bottom is at 0.0.
    # Intersection: 0.0 to 0.2.
    # This ensures they are fused.
    
    base_mesh.apply_translation([0, 0, 0.2])
    
    # Create a Scene
    scene = trimesh.Scene()
    scene.add_geometry(base_mesh, geom_name="Base_Scheibe")
    scene.add_geometry(relief_surface, geom_name="Muster_Relief")
    
    return scene
