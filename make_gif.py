"""Generate a simple dancing cat GIF for Kicau Mania Detector."""
from PIL import Image, ImageDraw, ImageFont
import math

frames = []
W, H = 160, 160
TOTAL_FRAMES = 12

for i in range(TOTAL_FRAMES):
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    t = i / TOTAL_FRAMES * 2 * math.pi
    bounce = int(10 * math.sin(t * 2))
    tilt = int(5 * math.sin(t))
    
    cx, cy = W // 2, H // 2 + bounce
    
    # Body
    draw.ellipse([cx-30, cy-10, cx+30, cy+40], fill=(255, 165, 0))
    
    # Head
    hx, hy = cx + tilt, cy - 25 + bounce
    draw.ellipse([hx-22, hy-22, hx+22, hy+22], fill=(255, 180, 50))
    
    # Ears
    draw.polygon([(hx-18, hy-18), (hx-25, hy-38), (hx-5, hy-22)], fill=(255, 140, 0))
    draw.polygon([(hx+18, hy-18), (hx+25, hy-38), (hx+5, hy-22)], fill=(255, 140, 0))
    
    # Eyes
    draw.ellipse([hx-10, hy-8, hx-4, hy+2], fill=(0, 0, 0))
    draw.ellipse([hx+4, hy-8, hx+10, hy+2], fill=(0, 0, 0))
    
    # Mouth (smile)
    draw.arc([hx-8, hy+2, hx+8, hy+14], 0, 180, fill=(0, 0, 0), width=2)
    
    # Arms (waving!)
    arm_angle = math.sin(t * 2) * 30
    lax = cx - 30 + int(15 * math.sin(t))
    lay = cy + 5 + int(10 * math.cos(t))
    draw.line([(cx-28, cy+5), (lax, lay)], fill=(255, 140, 0), width=4)
    
    rax = cx + 30 + int(15 * math.cos(t))
    ray = cy + 5 + int(10 * math.sin(t + 1))
    draw.line([(cx+28, cy+5), (rax, ray)], fill=(255, 140, 0), width=4)
    
    # Legs
    draw.line([(cx-15, cy+38), (cx-20, cy+60)], fill=(255, 140, 0), width=4)
    draw.line([(cx+15, cy+38), (cx+20, cy+60)], fill=(255, 140, 0), width=4)
    
    # Text
    try:
        draw.text((W//2-35, H-25), "KICAU!", fill=(0, 255, 136))
    except:
        pass
    
    frames.append(img)

frames[0].save(
    "cat_dance.gif",
    save_all=True,
    append_images=frames[1:],
    duration=100,
    loop=0
)
print("cat_dance.gif berhasil dibuat!")
