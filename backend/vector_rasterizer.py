from shapely.geometry import Polygon, MultiPolygon
from PIL import Image, ImageDraw
import numpy as np

def rasterize_polygon_to_png(polygon, diameter_mm, resolution=1024):
    """
    Rasterize a shapely polygon to a PIL Image for preview.
    This allows the vector-based generator to output PNG previews
    compatible with the existing /api/preview endpoint.

    Args:
        polygon: shapely Polygon or MultiPolygon (in mm coordinates)
        diameter_mm: Physical diameter in millimeters
        resolution: Output image resolution (default 1024x1024)

    Returns:
        PIL.Image: Grayscale image (mode 'L'), 0=background, 255=pattern
    """
    # Create blank image
    image = Image.new("L", (resolution, resolution), 0)
    draw = ImageDraw.Draw(image)

    # Scale factor: mm to pixels
    # The polygon is centered at (0, 0) with radius = diameter_mm/2
    radius_mm = diameter_mm / 2.0
    scale = (resolution / 2.0) / radius_mm  # pixels per mm
    offset = resolution / 2.0  # center of image

    def transform_coords(coords):
        """Convert from mm-centered coords to pixel coords."""
        return [(x * scale + offset, y * scale + offset) for x, y in coords]

    # Handle both Polygon and MultiPolygon
    polygons = []
    if isinstance(polygon, Polygon):
        polygons = [polygon]
    elif isinstance(polygon, MultiPolygon):
        polygons = list(polygon.geoms)
    else:
        # Handle empty or invalid geometry
        return image

    # Draw each polygon
    for poly in polygons:
        if poly.is_empty:
            continue

        # Draw exterior (the main shape)
        try:
            exterior_coords = list(poly.exterior.coords)
            pixel_coords = transform_coords(exterior_coords)
            draw.polygon(pixel_coords, fill=255, outline=255)

            # Draw holes (interiors) - these should be "cut out" (black)
            for interior in poly.interiors:
                interior_coords = list(interior.coords)
                pixel_coords = transform_coords(interior_coords)
                draw.polygon(pixel_coords, fill=0, outline=0)
        except Exception as e:
            # Skip invalid polygons
            print(f"Warning: Could not rasterize polygon: {e}")
            continue

    return image


def rasterize_polygon_to_array(polygon, diameter_mm, resolution=1024):
    """
    Rasterize a shapely polygon to a numpy array (0.0 to 1.0).
    This is useful for compatibility with code expecting heightmap arrays.

    Args:
        polygon: shapely Polygon or MultiPolygon (in mm coordinates)
        diameter_mm: Physical diameter in millimeters
        resolution: Output array resolution (default 1024x1024)

    Returns:
        numpy.ndarray: 2D array with values 0.0 (background) to 1.0 (pattern)
    """
    img = rasterize_polygon_to_png(polygon, diameter_mm, resolution)
    arr = np.array(img).astype(np.float32) / 255.0
    return arr


if __name__ == "__main__":
    # Test the rasterizer
    print("Testing vector rasterizer...")

    from vector_generator import generate_mandala_vector

    test_seed = "test_rasterizer"
    test_diameter = 12.0

    # Generate a vector polygon
    polygon = generate_mandala_vector(test_seed, diameter_mm=test_diameter)
    print(f"Polygon area: {polygon.area:.2f} mm²")

    # Rasterize to PNG
    img = rasterize_polygon_to_png(polygon, diameter_mm=test_diameter, resolution=512)
    print(f"Image size: {img.size}")
    print(f"Image mode: {img.mode}")

    # Save for visual inspection
    img.save("test_vector_rasterized.png")
    print("Saved test_vector_rasterized.png")

    # Test array conversion
    arr = rasterize_polygon_to_array(polygon, diameter_mm=test_diameter, resolution=512)
    print(f"Array shape: {arr.shape}")
    print(f"Array range: {arr.min():.2f} to {arr.max():.2f}")
    print(f"Non-zero pixels: {np.count_nonzero(arr)}")

    print("Vector rasterizer test complete!")
