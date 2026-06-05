#!/usr/bin/env python3
"""
Anniversary Animated GIF Generator

This script creates a cinematic, romantic animated GIF for an anniversary.
Features:
- Beating red heart in the center
- Girlfriend's photo placed inside the heart
- Main anniversary text
- Multiple romantic messages with fade transitions
- Floating hearts drifting across the screen
- Elegant fonts and soft romantic colors

Requirements:
pip install pillow numpy
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================================
# CONFIGURATION - EASILY CHANGE THESE
# ============================================================================
# Set the path to your girlfriend's photo (change this to your own image file)
GIRLFRIEND_PHOTO_PATH = "girlfriend.jpg"

# Output GIF file name
OUTPUT_GIF = "anniversary_gift.gif"

# Animation settings
WIDTH = 640           # Width of GIF in pixels
HEIGHT = 640          # Height of GIF in pixels
FPS = 15              # Frames per second (smooth animation)
DURATION = 12         # Duration in seconds (10-15 seconds recommended)
TOTAL_FRAMES = FPS * DURATION
PULSE_PERIOD = 1.0    # Heart beats once per second

# Color palette (soft romantic colors)
BG_TOP_COLOR = (255, 240, 245)     # Soft pinkish white
BG_BOTTOM_COLOR = (255, 200, 210)  # Soft rose
HEART_COLOR = (220, 50, 60)        # Rich red
HEART_OUTLINE = (255, 215, 0)      # Gold outline
GOLD_ACCENT = (255, 215, 0)
TEXT_COLOR = (80, 40, 50)          # Deep romantic burgundy
SHADOW_COLOR = (0, 0, 0, 80)       # Semi-transparent black for shadows

# ============================================================================
# FONT SETUP - Use elegant fonts if available, fallback to default
# ============================================================================
def get_font(size, bold=False):
    """Load an elegant font, fallback to default if not available."""
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "C:/Windows/Fonts/Georgia.ttf",
        "C:/Windows/Fonts/GreatVibes-Regular.ttf",
        "/System/Library/Fonts/Georgia.ttf",
        "/System/Library/Fonts/AppleGothic.ttf",
    ]
    if bold:
        bold_paths = [p.replace("Regular", "Bold") for p in font_paths]
        font_paths = bold_paths + font_paths
    
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    # Fallback to default PIL font
    return ImageFont.load_default()

# ============================================================================
# HEART SHAPE GENERATION (Parametric heart curve)
# ============================================================================
def generate_heart_points(center_x, center_y, scale, num_points=60):
    """
    Generate points for a classic heart shape using parametric equations.
    The heart points downward (cleft at top), suitable for upright display.
    """
    points = []
    # Heart parametric equation: x = 16*sin(t)^3, y = 13cos(t)-5cos(2t)-2cos(3t)-cos(4t)
    # Normalized to range approximately [-16,16] in x and [-17,15] in y
    for i in range(num_points + 1):
        t = 2 * math.pi * i / num_points
        # Calculate raw heart coordinates
        x_raw = 16 * math.sin(t) ** 3
        y_raw = 13 * math.cos(t) - 5 * math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t)
        # Flip Y because image Y increases downward (heart point should be at bottom)
        y_raw = -y_raw
        # Scale and translate to center
        x = center_x + (x_raw * scale)
        y = center_y + (y_raw * scale)
        points.append((x, y))
    return points

# ============================================================================
# CIRCULAR PHOTO MASK (for placing photo inside the heart)
# ============================================================================
def create_circular_photo(photo_path, size):
    """
    Load a photo, crop it into a circle, and resize.
    Returns an RGBA image with circular transparency.
    """
    try:
        photo = Image.open(photo_path).convert("RGBA")
    except FileNotFoundError:
        # Create a placeholder if photo not found
        print(f"Warning: Photo not found at '{photo_path}'. Using placeholder.")
        photo = Image.new("RGBA", (size, size), (200, 150, 180, 255))
        draw = ImageDraw.Draw(photo)
        draw.ellipse((0, 0, size, size), outline=GOLD_ACCENT, width=3)
        return photo
    
    # Resize photo to fit desired size (square)
    photo = photo.resize((size, size), Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size, size), fill=255)
    
    # Apply mask to make photo circular
    circular_photo = Image.new("RGBA", (size, size))
    circular_photo.paste(photo, (0, 0), mask)
    
    # Add a soft gold border
    border = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_draw.ellipse((0, 0, size-1, size-1), outline=GOLD_ACCENT, width=3)
    circular_photo = Image.alpha_composite(circular_photo, border)
    
    return circular_photo

# ============================================================================
# FLOATING HEART PARTICLE SYSTEM
# ============================================================================
class FloatingHeart:
    """A single floating heart that drifts across the screen."""
    def __init__(self, x, y, size, speed_x, speed_y, color, alpha):
        self.x = x
        self.y = y
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color
        self.alpha = alpha  # Transparency 0-255
    
    def update(self):
        """Update position for next frame."""
        self.x += self.speed_x
        self.y += self.speed_y
    
    def is_alive(self):
        """Check if heart is still on screen."""
        return -50 < self.x < WIDTH + 50 and -50 < self.y < HEIGHT + 50

def draw_small_heart(draw, x, y, size, color, alpha=255):
    """Draw a small heart shape at given position."""
    # Scale a tiny heart polygon
    scale = size / 30.0  # Base size reference
    points = generate_heart_points(x, y, scale, num_points=20)
    draw.polygon(points, fill=color + (alpha,))

def generate_floating_hearts(current_hearts, frame_idx):
    """Update and generate new floating hearts each frame."""
    # Update existing hearts
    for heart in current_hearts[:]:
        heart.update()
        if not heart.is_alive():
            current_hearts.remove(heart)
    
    # Occasionally add new hearts
    if random.random() < 0.3:  # 30% chance per frame
        x = random.randint(-50, WIDTH + 50)
        y = random.randint(-50, HEIGHT + 50)
        size = random.randint(10, 35)
        speed_x = random.uniform(-1.5, 1.5)
        speed_y = random.uniform(-1.0, 1.0)
        color_choice = random.choice([
            (255, 100, 120),   # Light red
            (255, 140, 160),   # Soft pink
            (255, 180, 190),   # Pale pink
            (255, 215, 0)      # Gold accent
        ])
        alpha = random.randint(100, 200)
        current_hearts.append(FloatingHeart(x, y, size, speed_x, speed_y, color_choice, alpha))
    
    return current_hearts

# ============================================================================
# ROMANTIC MESSAGES WITH TIMING
# ============================================================================
MESSAGES = [
    ("Happy One Year Anniversary To Us, Baby ❤️", 0, DURATION, 32, "center", HEIGHT - 60),
    ("Thank you for a year filled with love, laughter, and unforgettable memories.", 1.5, 4.0, 18, "center", HEIGHT // 2 + 80),
    ("You are my safe place, my happiness, and my favorite person.", 4.0, 6.5, 18, "center", HEIGHT // 2 + 80),
    ("Every day with you feels like a blessing.", 6.5, 9.0, 18, "center", HEIGHT // 2 + 80),
    ("No matter where life takes us, my heart will always choose you.", 9.0, 11.5, 18, "center", HEIGHT // 2 + 80),
    ("I love you more today than yesterday and less than tomorrow.", 11.0, DURATION, 18, "center", HEIGHT // 2 + 80),
]

def get_text_alpha(frame_sec, start_sec, end_sec, fade_duration=1.0):
    """
    Calculate alpha (opacity) for a message based on current time.
    Fades in and out smoothly.
    """
    if frame_sec < start_sec:
        return 0
    if frame_sec > end_sec:
        return 0
    # Fade in
    if frame_sec - start_sec < fade_duration:
        return int(255 * ((frame_sec - start_sec) / fade_duration))
    # Fade out
    if end_sec - frame_sec < fade_duration:
        return int(255 * ((end_sec - frame_sec) / fade_duration))
    # Fully visible
    return 255

# ============================================================================
# BACKGROUND GRADIENT
# ============================================================================
def create_gradient_background(width, height, top_color, bottom_color):
    """Create a vertical gradient background."""
    gradient = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(gradient)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line((0, y, width, y), fill=(r, g, b))
    return gradient

# ============================================================================
# MAIN ANIMATION GENERATION
# ============================================================================
def generate_anniversary_gif():
    """Generate the full animated GIF."""
    print("🎨 Generating anniversary GIF...")
    
    # Pre-create gradient background (static)
    gradient_bg = create_gradient_background(WIDTH, HEIGHT, BG_TOP_COLOR, BG_BOTTOM_COLOR)
    
    # Load girlfriend's photo (size will be about 35% of heart size)
    photo_size = int(WIDTH * 0.2)  # 20% of width, fits nicely inside heart
    girlfriend_photo = create_circular_photo(GIRLFRIEND_PHOTO_PATH, photo_size)
    
    # Pre-load fonts
    title_font = get_font(36, bold=True)
    message_font = get_font(22)
    small_font = get_font(18)
    
    # Floating hearts list (persists across frames)
    floating_hearts = []
    
    # List to store all frames for GIF
    frames = []
    
    # Heart beat parameters
    heart_base_scale = WIDTH * 0.28  # Base size of heart (radius-like)
    heart_center_x = WIDTH // 2
    heart_center_y = HEIGHT // 2 + 10  # Slightly below center for visual balance
    
    # Pre-calculate heart center for photo placement (geometric center of heart shape)
    # We'll use the same center as the heart for placing photo inside it
    photo_center_x = heart_center_x
    photo_center_y = heart_center_y
    
    # Generate each frame
    for frame_idx in range(TOTAL_FRAMES):
        # Current time in seconds
        frame_sec = frame_idx / FPS
        
        # Calculate heart pulse scale factor (sinusoidal beating)
        pulse_factor = 1 + 0.12 * math.sin(2 * math.pi * frame_sec / PULSE_PERIOD)
        current_heart_scale = heart_base_scale * pulse_factor
        
        # Start with background
        frame = gradient_bg.copy()
        
        # Draw floating hearts (behind the main heart)
        floating_hearts = generate_floating_hearts(floating_hearts, frame_idx)
        draw_floating = ImageDraw.Draw(frame, "RGBA")
        for heart in floating_hearts:
            draw_small_heart(draw_floating, heart.x, heart.y, heart.size, heart.color, heart.alpha)
        
        # Draw the main beating heart
        heart_polygon = generate_heart_points(heart_center_x, heart_center_y, current_heart_scale)
        # Create a temporary layer for heart with shadow
        heart_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        heart_draw = ImageDraw.Draw(heart_layer)
        
        # Draw drop shadow (offset slightly)
        shadow_offset = 8
        shadow_polygon = [(x + shadow_offset, y + shadow_offset) for x, y in heart_polygon]
        heart_draw.polygon(shadow_polygon, fill=SHADOW_COLOR)
        
        # Draw main heart with gradient-like fill (solid red with inner glow effect)
        heart_draw.polygon(heart_polygon, fill=HEART_COLOR)
        
        # Add gold outline
        heart_draw.polygon(heart_polygon, outline=HEART_OUTLINE, width=3)
        
        # Add subtle inner glow (a smaller heart with softer color)
        inner_scale_factor = 0.85
        inner_heart = generate_heart_points(heart_center_x, heart_center_y, current_heart_scale * inner_scale_factor)
        heart_draw.polygon(inner_heart, outline=(255, 100, 120), width=2)
        
        # Composite heart onto frame
        frame = Image.alpha_composite(frame.convert("RGBA"), heart_layer).convert("RGB")
        
        # Place girlfriend's photo inside the heart
        # Calculate photo position so it's centered within the heart's interior
        photo_x = photo_center_x - photo_size // 2
        photo_y = photo_center_y - photo_size // 2
        # Slight vertical adjustment for better aesthetic (heart's center is a bit high)
        photo_y += int(current_heart_scale * 0.08)
        
        # Paste photo (respecting its circular transparency)
        frame.paste(girlfriend_photo, (photo_x, photo_y), girlfriend_photo)
        
        # Add a soft glow around the photo (small gold ring effect)
        glow_draw = ImageDraw.Draw(frame)
        glow_radius = photo_size // 2 + 5
        glow_center = (photo_x + photo_size // 2, photo_y + photo_size // 2)
        for r in range(3):
            alpha = 100 - r * 30
            glow_draw.ellipse(
                (glow_center[0] - glow_radius + r, glow_center[1] - glow_radius + r,
                 glow_center[0] + glow_radius - r, glow_center[1] + glow_radius - r),
                outline=(255, 215, 0, alpha)
            )
        
        # Draw text messages with fade transitions
        # Use a separate transparent layer for text to handle alpha blending
        text_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        for msg_text, start_sec, end_sec, font_size, align, y_pos in MESSAGES:
            alpha = get_text_alpha(frame_sec, start_sec, end_sec, fade_duration=0.8)
            if alpha == 0:
                continue
            
            # Select font based on size
            if font_size >= 32:
                font = title_font
            else:
                font = message_font
            
            # Calculate text size and position
            bbox = text_draw.textbbox((0, 0), msg_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if align == "center":
                x_pos = (WIDTH - text_width) // 2
            else:
                x_pos = 20
            
            # Add shadow for better readability
            shadow_offset = 2
            text_draw.text((x_pos + shadow_offset, y_pos + shadow_offset), msg_text,
                          fill=(0, 0, 0, int(alpha * 0.5)), font=font)
            # Draw main text with romantic color and current alpha
            text_draw.text((x_pos, y_pos), msg_text,
                          fill=(TEXT_COLOR[0], TEXT_COLOR[1], TEXT_COLOR[2], alpha), font=font)
        
        # Composite text layer onto frame
        frame = Image.alpha_composite(frame.convert("RGBA"), text_layer).convert("RGB")
        
        # Add small gold corner accents for cinematic feel
        accent_draw = ImageDraw.Draw(frame)
        corner_length = 30
        corner_width = 3
        # Top-left
        accent_draw.line((10, 10, 10 + corner_length, 10), fill=GOLD_ACCENT, width=corner_width)
        accent_draw.line((10, 10, 10, 10 + corner_length), fill=GOLD_ACCENT, width=corner_width)
        # Top-right
        accent_draw.line((WIDTH - 10, 10, WIDTH - 10 - corner_length, 10), fill=GOLD_ACCENT, width=corner_width)
        accent_draw.line((WIDTH - 10, 10, WIDTH - 10, 10 + corner_length), fill=GOLD_ACCENT, width=corner_width)
        # Bottom-left
        accent_draw.line((10, HEIGHT - 10, 10 + corner_length, HEIGHT - 10), fill=GOLD_ACCENT, width=corner_width)
        accent_draw.line((10, HEIGHT - 10, 10, HEIGHT - 10 - corner_length), fill=GOLD_ACCENT, width=corner_width)
        # Bottom-right
        accent_draw.line((WIDTH - 10, HEIGHT - 10, WIDTH - 10 - corner_length, HEIGHT - 10), fill=GOLD_ACCENT, width=corner_width)
        accent_draw.line((WIDTH - 10, HEIGHT - 10, WIDTH - 10, HEIGHT - 10 - corner_length), fill=GOLD_ACCENT, width=corner_width)
        
        # Add a subtle vignette effect (darkened edges)
        vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        vignette_draw = ImageDraw.Draw(vignette)
        for i in range(40):
            alpha = 15 - i // 3
            vignette_draw.rectangle((i, i, WIDTH - i, HEIGHT - i), outline=(0, 0, 0, alpha), width=1)
        frame = Image.alpha_composite(frame.convert("RGBA"), vignette).convert("RGB")
        
        # Append frame to list
        frames.append(frame)
        
        # Progress indicator
        if frame_idx % (TOTAL_FRAMES // 10) == 0:
            print(f"  Rendering frame {frame_idx}/{TOTAL_FRAMES} ({int(100*frame_idx/TOTAL_FRAMES)}%)")
    
    # Save as animated GIF
    print("💾 Saving GIF... This may take a moment.")
    frame_duration = int(1000 / FPS)  # milliseconds per frame
    
    # Save with optimization settings
    frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0,
        optimize=True,
        quality=85
    )
    
    print(f"✅ Done! Anniversary GIF saved as '{OUTPUT_GIF}'")
    print(f"   Duration: {DURATION} seconds, {FPS} fps, {TOTAL_FRAMES} frames")
    print(f"   File size: {os.path.getsize(OUTPUT_GIF) / 1024:.1f} KB")

# ============================================================================
# RUN THE SCRIPT
# ============================================================================
if __name__ == "__main__":
    # Check if Pillow and numpy are available
    try:
        from PIL import __version__ as pil_version
        print(f"✓ Pillow version {pil_version}")
    except ImportError:
        print("✗ Please install Pillow: pip install pillow")
        exit(1)
    
    # Verify girlfriend's photo exists (warning only)
    if not os.path.exists(GIRLFRIEND_PHOTO_PATH):
        print(f"⚠️ Warning: Photo not found at '{GIRLFRIEND_PHOTO_PATH}'")
        print("   A placeholder will be used. Please update the path to your girlfriend's photo.")
    
    generate_anniversary_gif()
