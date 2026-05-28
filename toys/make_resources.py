from PIL import Image, ImageDraw, ImageFont
import os

# placeholders
BASE = os.path.join(os.path.dirname(__file__), "resources")
os.makedirs(BASE, exist_ok=True)

PALETTE = [
    (245, 222, 179), (222, 184, 135), (255, 222, 173), (210, 180, 140),
    (188, 143, 143), (244, 164, 96),  (218, 165, 32),  (205, 133, 63),
    (160, 82, 45),   (139, 69, 19),
]


def font(size):
    # arial
    for p in ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def stub(path, text, w, h, bg):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    f = font(max(12, min(w, h) // 5))
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((w - tw) / 2, (h - th) / 2), text, fill=(60, 40, 20), font=f)
    img.save(path)


# products
for i in range(1, 11):
    stub(os.path.join(BASE, f"{i}.jpg"), f"Игрушка {i}", 300, 200, PALETTE[i - 1])

# fallback
stub(os.path.join(BASE, "picture.png"), "Нет фото", 300, 200, (245, 222, 179))

# logo
logo = Image.new("RGB", (220, 60), (255, 255, 255))
d = ImageDraw.Draw(logo)
d.rectangle([0, 0, 219, 59], outline=(222, 184, 135), width=2)
d.text((12, 14), "МирИгрушек", fill=(139, 69, 19), font=font(26))
logo.save(os.path.join(BASE, "logo.png"))

# icon
icon = Image.new("RGB", (64, 64), (222, 184, 135))
d = ImageDraw.Draw(icon)
d.ellipse([8, 8, 56, 56], fill=(255, 222, 173), outline=(139, 69, 19), width=3)
d.text((20, 18), "МИ", fill=(139, 69, 19), font=font(22))
icon.save(os.path.join(BASE, "icon.png"))
icon.save(os.path.join(BASE, "icon.jpg"))
icon.save(os.path.join(BASE, "icon.ico"), sizes=[(64, 64), (32, 32), (16, 16)])

print("done")
