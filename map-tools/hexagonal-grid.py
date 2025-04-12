from PIL import Image, ImageDraw
import math

def create_hexagon_grid(width, height, hex_size, line_color='black', line_width=2):
    """
    Create a hexagonal grid PNG image.

    Parameters:
    - width, height: Dimensions of the output image
    - hex_size: Radius of the hexagon (distance from center to vertex)
    - line_color: Color of the grid lines
    - line_width: Width of the grid lines
    - bg_color: Background color of the image
    """

    # Calculate hexagon properties
    hex_width = hex_size * 2
    hex_height = math.sqrt(3) * hex_size
    horizontal_spacing = hex_size * math.sqrt(3)/2
    vertical_spacing = hex_height* math.sqrt(3)

    # Create blank image
    img = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # Draw hexagons in a grid pattern
    for row in range(0, int(height // vertical_spacing) + 1):
        for col in range(0, int(width // horizontal_spacing) + 1):
            # Calculate center position
            x = col * horizontal_spacing
            y = row * vertical_spacing

            # Offset every other column
            if col % 2 == 1:
                y += vertical_spacing / 2

            # Generate hexagon vertices
            vertices = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = math.pi / 180 * angle_deg
                vx = x + hex_size * math.cos(angle_rad)
                vy = y + hex_size * math.sin(angle_rad)
                vertices.append((vx, vy))

            # Draw hexagon
            draw.polygon(vertices, outline=line_color, width=line_width)

    return img

# Example usage
if __name__ == "__main__":
    # Parameters
    image_width = 450
    image_height = 450
    hex_radius = 18  # Size of each hexagon

    # Create the grid
    hex_grid = create_hexagon_grid(image_width, image_height, hex_radius)

    # Save to file
    hex_grid.save('hexagon_grid.png', 'png')
    print("Hexagon grid saved as 'hexagon_grid.png'")
