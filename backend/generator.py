import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def generate_mandala(seed, resolution=1024):
    """
    Generates a mandala heightmap using vector-style drawing for sharp lines.
    Matches the aesthetic of laser-cut or dual-color filament prints.
    """
    if seed:
        np.random.seed(abs(hash(seed)) % (2**32))
    
    # 1. Create a blank image (Mode 'L' for 8-bit grayscale)
    # We draw typically in white (1.0 height) on black (0.0 height) background?
    # Or vice versa. Let's say Pattern is High (White).
    image = Image.new("L", (resolution, resolution), 0)
    draw = ImageDraw.Draw(image)
    
    center = (resolution // 2, resolution // 2)
    radius = resolution // 2
    
    # Draw Rim (Border)
    # Thickness relative to resolution
    rim_thickness = int(resolution * 0.03) 
    # Draw a ring by drawing two circles? Or stroke.
    # PIL ellipse with outline width (supported in newer PIL)
    # Outer rim
    draw.ellipse(
        [0, 0, resolution, resolution], 
        outline=255, 
        width=rim_thickness
    )
    
    # Generative Parameters
    # Symmetry count (e.g. 6, 8, 12)
    symmetry = np.random.choice([6, 8, 12, 16])
    
    # Number of "components" to draw
    num_components = np.random.randint(4, 9)
    
    for _ in range(num_components):
        # Choose a shape type
        shape_type = np.random.choice(['ring', 'ray', 'petal_curve', 'dot_ring'])
        
        # Line thickness (Thicker for solidity)
        thickness = np.random.randint(int(resolution * 0.015), int(resolution * 0.03))
        
        if shape_type == 'ring':
            # Concentric ring
            r_ratio = np.random.uniform(0.1, 0.9)
            r_px = int(r_ratio * radius)
            # Clip
            box = [center[0] - r_px, center[1] - r_px, center[0] + r_px, center[1] + r_px]
            draw.ellipse(box, outline=255, width=thickness)
            
        elif shape_type == 'ray':
            # Straight lines from radius A to B
            r_start = np.random.uniform(0.0, 0.5) * radius
            r_end = np.random.uniform(r_start/radius + 0.1, 0.95) * radius
            
            for i in range(symmetry):
                angle = (2 * np.pi * i) / symmetry
                # Optional phase shift common to all rays in this layer
                # But rays usually align with symmetry axes.
                
                # Start Point
                x1 = center[0] + r_start * np.cos(angle)
                y1 = center[1] + r_start * np.sin(angle)
                
                # End Point
                x2 = center[0] + r_end * np.cos(angle)
                y2 = center[1] + r_end * np.sin(angle)
                
                draw.line([x1, y1, x2, y2], fill=255, width=thickness)

        elif shape_type == 'petal_curve':
            # Bezier or simple arc style petals? 
            # Easiest: Draw an ellipse at an offset and rotate it?
            
            # Distance of petal center from main center
            d_offset = np.random.uniform(0.2, 0.7) * radius
            # Size of the petal
            p_size = np.random.uniform(0.1, 0.4) * radius
            
            # Draw on a temp layer to rotate?
            # PIL doesn't support complex rotation of arbitrary drawn paths easily without transforming coordinates for every point.
            
            # Analytic approach for "petals" using points:
            # Calculate the "petal" relative to (0,0) then rotate and translate.
            # Petal shape: Ellipse centered at (d_offset, 0).
            
            # Perform rotation manually
            for i in range(symmetry):
                base_angle = (2 * np.pi * i) / symmetry
                
                # Center of this specific petal
                cx = center[0] + d_offset * np.cos(base_angle)
                cy = center[1] + d_offset * np.sin(base_angle)
                
                # Bounding box for the petal ellipse
                # We need to rotate the ellipse itself if we want it pointing out.
                # PIL can't draw rotated ellipses easily directly. 
                # Approximation: Draw a polygon or simple line loop.
                # Or just circles (round petals).
                
                # Let's do diamond shapes or small circles (simple petals)
                rect = [cx - p_size, cy - p_size, cx + p_size, cy + p_size]
                draw.ellipse(rect, outline=255, width=thickness)
                
        elif shape_type == 'dot_ring':
            # Ring of solid dots
            r_dist = np.random.uniform(0.2, 0.9) * radius
            dot_size = np.random.randint(thickness, thickness * 3)
            
            dot_count = symmetry * np.random.randint(1, 3) # Maybe double density
            
            for i in range(dot_count):
                angle = (2 * np.pi * i) / dot_count
                cx = center[0] + r_dist * np.cos(angle)
                cy = center[1] + r_dist * np.sin(angle)
                
                draw.ellipse(
                    [cx - dot_size, cy - dot_size, cx + dot_size, cy + dot_size],
                    fill=255, outline=None
                )
    
    # Post-process
    # Mask outside main circle to be clean
    # Create mask
    mask_img = Image.new("L", (resolution, resolution), 0)
    draw_mask = ImageDraw.Draw(mask_img)
    draw_mask.ellipse([0, 0, resolution, resolution], fill=255)
    
    # Combine
    final_img = Image.new("L", (resolution, resolution), 0)
    final_img.paste(image, (0, 0), mask_img)
    
    # IMPROVEMENT: Apply slight blur to avoid aliasing "fuzziness" in 3D preview
    # and to give the walls a slight slope (better for printing).
    # Reverting blur per user request for "same height allover" / binary look
    # final_img = final_img.filter(ImageFilter.GaussianBlur(radius=2))
    
    # Normalize to 0-1 float array
    # 255 -> 1.0 (Relief Top)
    # 0 -> 0.0 (Base level)
    arr = np.array(final_img).astype(np.float32) / 255.0
    
    return arr

if __name__ == "__main__":
    # Test
    h = generate_mandala("test_seed")
    img = Image.fromarray((h * 255).astype(np.uint8))
    img.save("test_mandala.png")
    print("Generated test_mandala.png")
