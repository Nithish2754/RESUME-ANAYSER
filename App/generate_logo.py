from PIL import Image, ImageDraw, ImageFont

# Create a white image
width, height = 800, 400
image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(image)

# Try to load a font, otherwise use default
try:
    # Arial or similar standard font
    font_small = ImageFont.truetype("arial.ttf", 24)
    font_large = ImageFont.truetype("arialbd.ttf", 72)
    font_medium = ImageFont.truetype("arialbd.ttf", 28)
except IOError:
    font_small = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()

# Define text
text_top = "LOGIC BEHIND THE MAGIC PRESENTS"
text_mid = "AI RESUME\nANALYZER"
text_bot = "A NITHISH QUICKIE"

# Colors
blue = (31, 78, 121)

# Helper for drawing centered text
def draw_centered_text(draw, text, font, y_pos, fill):
    # Use textbbox instead of textsize (deprecated in Pillow 10)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except AttributeError:
        text_width, _ = draw.textsize(text, font=font)
    
    x_pos = (width - text_width) / 2
    
    # Draw drop shadow for the middle text
    if "RESUME" in text:
        draw.multiline_text((x_pos+4, y_pos+4), text, font=font, fill=(180, 200, 220), align="center")
    
    draw.multiline_text((x_pos, y_pos), text, font=font, fill=fill, align="center")

# Draw the text
draw_centered_text(draw, text_top, font_small, 50, blue)
draw_centered_text(draw, text_mid, font_large, 120, blue)
draw_centered_text(draw, text_bot, font_medium, 300, blue)

# Save the image
image.save("Logo/RESUM.png")
print("Image generated successfully")
