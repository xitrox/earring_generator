import numpy as np
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union

def generate_mandala_vector(seed, diameter_mm=12.0):
    """
    Generate mandala pattern as 2D vector polygons using shapely.
    This replaces the raster heightmap approach with clean vector geometry.

    Args:
        seed: Random seed for reproducibility
        diameter_mm: Physical diameter in millimeters

    Returns:
        shapely.geometry.Polygon or MultiPolygon: The mandala pattern in mm coordinates
    """
    # Initialize random state (same as raster version)
    if seed:
        np.random.seed(abs(hash(seed)) % (2**32))

    # Work in millimeter space from the start
    radius_mm = diameter_mm / 2.0
    center = Point(0, 0)

    # Adaptive quality based on diameter (user decision)
    quad_segs = max(16, min(32, int(diameter_mm * 1.5)))

    # Generate boundary circle
    boundary = center.buffer(radius_mm, quad_segs=quad_segs)

    # Generative parameters - OPTIMIZED FOR 0.2MM NOZZLE PRINTING
    # Removed 16-fold symmetry (too fine), reduced component count for cleaner prints
    symmetry = np.random.choice([6, 8, 12])  # Max 12-fold instead of 16
    num_components = np.random.randint(3, 6)  # 3-5 components instead of 4-8 (less busy)

    # Collect all pattern polygons
    pattern_parts = []

    # Add rim (border ring) - slightly thicker for better printability
    rim_thickness = diameter_mm * 0.04  # Increased from 0.03 for stronger rim
    outer_ring = center.buffer(radius_mm, quad_segs=quad_segs)
    inner_ring = center.buffer(radius_mm - rim_thickness, quad_segs=quad_segs)
    rim = outer_ring.difference(inner_ring)
    pattern_parts.append(rim)

    # Generate components - with print-friendly thickness
    for _ in range(num_components):
        shape_type = np.random.choice(['ring', 'ray', 'petal_curve', 'dot_ring'])
        # CRITICAL: Minimum 0.25mm thickness for 0.2mm nozzle (was 0.015 * 12mm = 0.18mm, too thin!)
        # New range: 0.25mm to 0.5mm for a 12mm earring (safer for printing)
        min_thickness = max(0.25, diameter_mm * 0.02)  # At least 0.25mm
        max_thickness = diameter_mm * 0.04  # Up to 0.04 * diameter
        thickness = np.random.uniform(min_thickness, max_thickness)

        component = None
        if shape_type == 'ring':
            component = _create_ring(center, radius_mm, thickness, quad_segs)
        elif shape_type == 'ray':
            component = _create_rays(center, radius_mm, symmetry, thickness, quad_segs)
        elif shape_type == 'petal_curve':
            component = _create_petals(center, radius_mm, symmetry, thickness, quad_segs)
        elif shape_type == 'dot_ring':
            component = _create_dot_ring(center, radius_mm, symmetry, thickness, quad_segs)

        if component is not None and component.is_valid:
            pattern_parts.append(component)

    # Union all parts
    if not pattern_parts:
        # Fallback: just return the rim if nothing else was created
        return rim.intersection(boundary)

    combined_pattern = unary_union(pattern_parts)

    # Fix any self-intersections or invalid geometry
    if not combined_pattern.is_valid:
        combined_pattern = combined_pattern.buffer(0)

    # Clip to circular boundary (matches line 128-135 in generator.py)
    final_pattern = combined_pattern.intersection(boundary)

    return final_pattern


def _create_ring(center, radius_mm, thickness, quad_segs):
    """
    Create a concentric ring as an annulus polygon.
    Matches the 'ring' shape type from generator.py line 47-53.
    """
    r_ratio = np.random.uniform(0.1, 0.9)
    r = r_ratio * radius_mm

    # Create annulus (ring)
    outer = center.buffer(r + thickness/2, quad_segs=quad_segs)
    inner = center.buffer(max(0, r - thickness/2), quad_segs=quad_segs)

    if inner.area > 0:
        return outer.difference(inner)
    else:
        return outer


def _create_rays(center, radius_mm, symmetry, thickness, quad_segs):
    """
    Create radial rays as buffered line strings.
    Matches the 'ray' shape type from generator.py line 55-73.
    """
    r_start = np.random.uniform(0.0, 0.5) * radius_mm
    r_end = np.random.uniform(r_start/radius_mm + 0.1, 0.95) * radius_mm

    rays = []
    for i in range(symmetry):
        angle = (2 * np.pi * i) / symmetry

        # Start and end points
        x1 = r_start * np.cos(angle)
        y1 = r_start * np.sin(angle)
        x2 = r_end * np.cos(angle)
        y2 = r_end * np.sin(angle)

        # Create line and buffer it to give thickness
        line = LineString([(x1, y1), (x2, y2)])
        ray = line.buffer(thickness/2, cap_style='round', quad_segs=quad_segs)
        rays.append(ray)

    return unary_union(rays)


def _create_petals(center, radius_mm, symmetry, thickness, quad_segs):
    """
    Create petal shapes as circles positioned radially.
    Matches the 'petal_curve' shape type from generator.py line 75-107.
    """
    d_offset = np.random.uniform(0.2, 0.7) * radius_mm
    p_size = np.random.uniform(0.1, 0.4) * radius_mm

    petals = []
    for i in range(symmetry):
        angle = (2 * np.pi * i) / symmetry

        # Center of this specific petal
        cx = d_offset * np.cos(angle)
        cy = d_offset * np.sin(angle)

        # Create petal as an outlined circle (annulus)
        petal_center = Point(cx, cy)
        outer = petal_center.buffer(p_size + thickness/2, quad_segs=quad_segs)
        inner = petal_center.buffer(max(0, p_size - thickness/2), quad_segs=quad_segs)

        if inner.area > 0:
            petal = outer.difference(inner)
        else:
            petal = outer

        petals.append(petal)

    return unary_union(petals)


def _create_dot_ring(center, radius_mm, symmetry, thickness, quad_segs):
    """
    Create solid dots arranged in a ring.
    Matches the 'dot_ring' shape type from generator.py line 109-124.
    OPTIMIZED: Larger dots, less density for better printing.
    """
    r_dist = np.random.uniform(0.3, 0.8) * radius_mm  # Keep away from edges
    # Ensure dots are at least 0.3mm diameter for printability
    dot_size = np.random.uniform(max(0.15, thickness), max(0.25, thickness * 2))
    # Reduce dot density - was symmetry * 1-3, now just symmetry (one dot per sector)
    dot_count = symmetry * np.random.randint(1, 2)  # 1x or 2x symmetry count (less dense)

    dots = []
    for i in range(dot_count):
        angle = (2 * np.pi * i) / dot_count

        # Position of this dot
        cx = r_dist * np.cos(angle)
        cy = r_dist * np.sin(angle)

        # Create solid dot (filled circle)
        dot = Point(cx, cy).buffer(dot_size, quad_segs=quad_segs)
        dots.append(dot)

    return unary_union(dots)


if __name__ == "__main__":
    # Test the vector generator
    print("Testing vector generator...")

    test_seed = "test_seed_123"
    test_diameter = 12.0

    polygon = generate_mandala_vector(test_seed, diameter_mm=test_diameter)

    print(f"Generated polygon type: {type(polygon).__name__}")
    print(f"Is valid: {polygon.is_valid}")
    print(f"Area: {polygon.area:.2f} mm²")
    print(f"Bounds: {polygon.bounds}")

    # Test reproducibility
    polygon2 = generate_mandala_vector(test_seed, diameter_mm=test_diameter)
    print(f"Reproducible: {polygon.equals(polygon2)}")

    print("Vector generator test complete!")
