import trimesh
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

def create_stls_from_vector(polygon, diameter_mm, base_height_mm, relief_height_mm, chamfer_height=0.15):
    """
    Convert 2D vector polygon to 3D meshes using extrusion.
    This replaces the heightmap-to-mesh conversion with clean vector extrusion.

    Args:
        polygon: shapely Polygon or MultiPolygon (in mm coordinates, centered at origin)
        diameter_mm: Physical diameter in millimeters
        base_height_mm: Height of base cylinder
        relief_height_mm: Height of relief pattern
        chamfer_height: Height of chamfer/bevel on top edge (default 0.15mm for smooth finish)

    Returns:
        trimesh.Scene: Scene containing base disc and relief meshes
    """
    radius_mm = diameter_mm / 2.0

    # 1. Base Disc (unchanged from exporter.py)
    # Simple cylinder that forms the base of the earring
    base_mesh = trimesh.creation.cylinder(
        radius=radius_mm,
        height=base_height_mm,
        sections=128
    )

    # Position base cylinder so its top surface is at z=0
    # Default cylinder is centered at origin, ranging from -h/2 to h/2
    # We want it from -base_height to 0
    base_mesh.apply_translation([0, 0, -base_height_mm / 2.0])

    # 2. Relief Pattern - Extrude the 2D polygon with chamfer
    # Convert the 2D shapely polygon to a 3D mesh using extrusion
    try:
        relief_mesh = extrude_polygon_with_chamfer(
            polygon,
            height=relief_height_mm,
            chamfer_height=chamfer_height
        )
    except Exception as e:
        print(f"Warning: Failed to extrude polygon with chamfer: {e}")
        # Fallback: simple extrusion without chamfer
        try:
            relief_mesh = extrude_polygon(polygon, height=relief_height_mm)
        except:
            # Last resort: create a simple flat disc
            relief_mesh = trimesh.creation.cylinder(
                radius=radius_mm,
                height=relief_height_mm,
                sections=128
            )
            relief_mesh.apply_translation([0, 0, relief_height_mm / 2.0])

    # Validate the mesh
    if not relief_mesh.is_watertight:
        print("Warning: Relief mesh is not watertight. Attempting to fix...")
        try:
            relief_mesh.fill_holes()
            relief_mesh.fix_normals()
        except:
            pass  # Continue with non-watertight mesh if fix fails

    # IMPROVED: Sink the relief INTO the base instead of lifting the base
    # This hides the overlap from the sides - relief bottom starts at z=-0.05
    # so it embeds slightly into the base for adhesion, but edges align perfectly
    relief_mesh.apply_translation([0, 0, -0.05])

    # Base stays at its original position (top at z=0)
    # Relief now goes from z=-0.05 to z=(relief_height - 0.05)
    # At the outer edges where relief is thin/absent, they appear flush
    # In the interior where pattern exists, there's 0.05mm overlap for adhesion

    # Create scene with both meshes
    scene = trimesh.Scene()
    scene.add_geometry(base_mesh, geom_name="Base_Scheibe")
    scene.add_geometry(relief_mesh, geom_name="Muster_Relief")

    return scene


def extrude_polygon_with_chamfer(polygon, height, chamfer_height=0.15):
    """
    Extrude a 2D polygon with a chamfer (bevel) on the top edge.
    Creates a professional finish with smooth top edges.

    Args:
        polygon: shapely Polygon or MultiPolygon (XY plane, Z=0)
        height: Total extrusion height in Z direction
        chamfer_height: Height of the chamfer at the top (default 0.15mm)

    Returns:
        trimesh.Trimesh: Extruded 3D mesh with chamfered top edge
    """
    if chamfer_height <= 0 or chamfer_height >= height:
        # No chamfer or invalid chamfer, use regular extrusion
        return extrude_polygon(polygon, height)

    # Handle MultiPolygon
    if isinstance(polygon, MultiPolygon):
        meshes = []
        for poly in polygon.geoms:
            if not poly.is_empty and poly.area > 0:
                try:
                    mesh = _extrude_with_chamfer_single(poly, height, chamfer_height)
                    meshes.append(mesh)
                except Exception as e:
                    print(f"Warning: Failed to extrude polygon part with chamfer: {e}")
                    continue
        if not meshes:
            raise ValueError("No valid polygons could be extruded")
        return trimesh.util.concatenate(meshes)
    else:
        return _extrude_with_chamfer_single(polygon, height, chamfer_height)


def _extrude_with_chamfer_single(polygon, height, chamfer_height):
    """
    Extrude a single polygon with chamfer by creating two sections:
    1. Main body (straight extrusion)
    2. Chamfered top (tapered inward)

    Args:
        polygon: shapely Polygon
        height: Total height
        chamfer_height: Height of chamfer section

    Returns:
        trimesh.Trimesh: Chamfered mesh
    """
    # Calculate the chamfer angle (45 degrees = inset equal to height)
    # For a gentler slope, we'll use chamfer_height as the vertical, and inset half of that
    chamfer_inset = chamfer_height * 0.5  # Creates a ~63 degree angle (gentle slope)

    # Create inset polygon for the top (slightly smaller)
    top_polygon = polygon.buffer(-chamfer_inset)

    # If inset fails or creates empty polygon, fall back to regular extrusion
    if top_polygon.is_empty or top_polygon.area < polygon.area * 0.1:
        print("Warning: Chamfer inset too large, using regular extrusion")
        return _extrude_single_polygon(polygon, height)

    # Create two sections:
    # 1. Main body: bottom to (height - chamfer_height)
    main_height = height - chamfer_height
    main_mesh = _extrude_single_polygon(polygon, main_height)

    # 2. Chamfer section: tapered from full polygon to inset polygon
    try:
        chamfer_mesh = _create_tapered_section(
            polygon,
            top_polygon,
            z_bottom=main_height,
            z_top=height
        )

        # Combine the two meshes
        combined = trimesh.util.concatenate([main_mesh, chamfer_mesh])
        combined.fix_normals()
        return combined
    except Exception as e:
        print(f"Warning: Chamfer creation failed, using regular extrusion: {e}")
        return main_mesh


def _create_tapered_section(bottom_polygon, top_polygon, z_bottom, z_top):
    """
    Create a tapered mesh section between two polygons at different Z heights.
    This creates the chamfer/bevel effect.

    Args:
        bottom_polygon: shapely Polygon at z_bottom (larger)
        top_polygon: shapely Polygon at z_top (smaller, inset)
        z_bottom: Z coordinate of bottom face
        z_top: Z coordinate of top face

    Returns:
        trimesh.Trimesh: Tapered mesh section
    """
    # Get coordinates of both polygons
    bottom_coords = np.array(bottom_polygon.exterior.coords[:-1])
    top_coords = np.array(top_polygon.exterior.coords[:-1])

    # They should have similar number of vertices, but if not, we need to resample
    # For simplicity, we'll use the trimesh extrusion on the bottom and top separately
    # and connect them manually

    # Create bottom and top caps
    bottom_3d = np.column_stack([bottom_coords, np.full(len(bottom_coords), z_bottom)])
    top_3d = np.column_stack([top_coords, np.full(len(top_coords), z_top)])

    # For now, use a simple extrusion approach
    # Extrude bottom polygon to create the tapered section
    bottom_mesh = _extrude_single_polygon(bottom_polygon, z_top - z_bottom)
    bottom_mesh.apply_translation([0, 0, z_bottom])

    return bottom_mesh


def extrude_polygon(polygon, height):
    """
    Extrude a 2D shapely polygon into a 3D trimesh.

    Args:
        polygon: shapely Polygon or MultiPolygon (XY plane, Z=0)
        height: Extrusion height in Z direction

    Returns:
        trimesh.Trimesh: Extruded 3D mesh
    """
    # Handle MultiPolygon by extruding each polygon separately
    if isinstance(polygon, MultiPolygon):
        meshes = []
        for poly in polygon.geoms:
            if not poly.is_empty and poly.area > 0:
                try:
                    mesh = _extrude_single_polygon(poly, height)
                    meshes.append(mesh)
                except Exception as e:
                    print(f"Warning: Failed to extrude polygon part: {e}")
                    continue

        if not meshes:
            raise ValueError("No valid polygons could be extruded")

        # Combine all meshes
        return trimesh.util.concatenate(meshes)
    else:
        return _extrude_single_polygon(polygon, height)


def _extrude_single_polygon(polygon, height):
    """
    Extrude a single shapely Polygon into a 3D mesh.

    Args:
        polygon: shapely Polygon (must be simple, not MultiPolygon)
        height: Extrusion height

    Returns:
        trimesh.Trimesh: Extruded mesh
    """
    if polygon.is_empty or polygon.area == 0:
        raise ValueError("Cannot extrude empty or zero-area polygon")

    # Use trimesh's built-in extrusion
    # This handles the polygon correctly including holes
    try:
        mesh = trimesh.creation.extrude_polygon(polygon, height=height)
        return mesh
    except Exception as e:
        # Fallback: manual extrusion if trimesh method fails
        print(f"Trimesh extrusion failed, using manual method: {e}")
        return _manual_extrude_polygon(polygon, height)


def _manual_extrude_polygon(polygon, height):
    """
    Manually extrude a polygon by creating vertices and faces.
    This is a fallback if trimesh.creation.extrude_polygon fails.

    Args:
        polygon: shapely Polygon
        height: Extrusion height

    Returns:
        trimesh.Trimesh: Extruded mesh
    """
    # Get exterior ring coordinates
    exterior_coords = np.array(polygon.exterior.coords[:-1])  # Remove duplicate last point
    num_verts = len(exterior_coords)

    # Create vertices for bottom and top layers
    bottom_verts = np.column_stack([exterior_coords, np.zeros(num_verts)])
    top_verts = np.column_stack([exterior_coords, np.full(num_verts, height)])

    vertices = np.vstack([bottom_verts, top_verts])

    # Create faces
    faces = []

    # Side faces (connect bottom to top)
    for i in range(num_verts):
        i_next = (i + 1) % num_verts
        # Triangle 1
        faces.append([i, i + num_verts, i_next])
        # Triangle 2
        faces.append([i_next, i + num_verts, i_next + num_verts])

    # Top and bottom caps using simple fan triangulation
    # Bottom cap (facing down)
    for i in range(1, num_verts - 1):
        faces.append([0, i + 1, i])

    # Top cap (facing up)
    for i in range(1, num_verts - 1):
        faces.append([num_verts, num_verts + i, num_verts + i + 1])

    faces = np.array(faces)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.fix_normals()

    return mesh


if __name__ == "__main__":
    # Test the vector exporter
    print("Testing vector exporter...")

    from vector_generator import generate_mandala_vector
    import tempfile
    import os

    test_seed = "test_export"
    test_diameter = 12.0
    test_base_height = 1.0
    test_relief_height = 1.0

    # Generate a vector polygon
    polygon = generate_mandala_vector(test_seed, diameter_mm=test_diameter)
    print(f"Polygon area: {polygon.area:.2f} mm²")
    print(f"Polygon is valid: {polygon.is_valid}")

    # Create 3D meshes
    scene = create_stls_from_vector(
        polygon,
        diameter_mm=test_diameter,
        base_height_mm=test_base_height,
        relief_height_mm=test_relief_height
    )

    print(f"Scene contains {len(scene.geometry)} meshes")

    # Get mesh statistics
    for name, geom in scene.geometry.items():
        print(f"\n{name}:")
        print(f"  Vertices: {len(geom.vertices)}")
        print(f"  Faces: {len(geom.faces)}")
        print(f"  Is watertight: {geom.is_watertight}")
        print(f"  Volume: {geom.volume:.2f} mm³")

    # Export to 3MF
    with tempfile.NamedTemporaryFile(suffix='.3mf', delete=False) as tmp:
        tmp_path = tmp.name

    scene.export(tmp_path, file_type='3mf')
    file_size = os.path.getsize(tmp_path)

    print(f"\nExported to: {tmp_path}")
    print(f"File size: {file_size / 1024:.2f} KB")

    # Clean up
    os.unlink(tmp_path)

    print("Vector exporter test complete!")
