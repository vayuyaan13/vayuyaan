#!/usr/bin/env python3
"""Generate unique raster Open Graph cards from the site's existing SVG artwork."""
from __future__ import annotations
import re
from pathlib import Path
from urllib.parse import urlsplit
import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://vayuyaan13.github.io/vayuyaan/"
OUT = ROOT / "assets" / "social"
OUT.mkdir(parents=True, exist_ok=True)

def get_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

def page_files():
    import xml.etree.ElementTree as ET
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    paths = []
    for node in root.iter():
        if not node.tag.endswith("loc") or not node.text:
            continue
        url = node.text.strip()
        if not url.startswith(SITE):
            continue
        rel = urlsplit(url).path[len(urlsplit(SITE).path):]
        page = ROOT / rel / "index.html" if rel and not rel.endswith(".html") else ROOT / (rel or "index.html")
        if page.is_file():
            paths.append(page)
    return sorted(set(paths))

def main():
    count = 0
    for page in page_files():
        html = page.read_text(encoding="utf-8")
        title_match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else "Vayuyaan Electronics Guides"
        og = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)', html, re.I)
        if not og:
            raise RuntimeError(f"Missing og:image in {page}")
        source_url = og.group(1)
        source_rel = urlsplit(source_url).path.split("/vayuyaan/", 1)[-1]
        source_path = ROOT / source_rel
        if page.parts[-2] == "what-is-esp32":
            source_path = ROOT / "assets" / "what-is-esp32.svg"
        if not source_path.is_file():
            raise RuntimeError(f"Missing source artwork: {source_path}")
        if source_path.suffix.lower() == ".svg":
            svg_data = source_path.read_bytes()
            # A few legacy SVG labels contain bare ampersands; escape them before XML parsing.
            svg_data = re.sub(rb"&(?!#\\d+;|#x[0-9A-Fa-f]+;|amp;|lt;|gt;|quot;|apos;)", b"&amp;", svg_data)
            try:
                png_bytes = cairosvg.svg2png(bytestring=svg_data, output_width=1200, output_height=630)
            except Exception as exc:
                raise RuntimeError(f"Could not rasterize {source_path}: {exc}") from exc
            import io
            image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
        else:
            image = Image.open(source_path).convert("RGB")
        image = ImageOps.fit(image, (1200, 630), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        # Add a restrained, page-specific title band while retaining the original artwork.
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rectangle((0, 535, 1200, 630), fill=(12, 20, 28, 225))
        font = get_font(30 if len(title) < 54 else 25, True)
        text = title
        while draw.textbbox((0, 0), text, font=font)[2] > 1080 and len(text) > 20:
            text = text[:-4].rstrip() + "…"
        draw.text((60, 565), text, font=font, fill=(255, 255, 255, 255))
        draw.text((60, 608), "VAYUYAAN  |  ELECTRONICS • ARDUINO • ROBOTICS", font=get_font(15, True), fill=(255, 215, 0, 255))
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        slug = "home" if page.name == "index.html" and page.parent == ROOT else page.parent.name
        target = OUT / f"{slug}.jpg"
        image.save(target, "JPEG", quality=88, optimize=True, progressive=True)
        public_url = SITE + "assets/social/" + target.name
        replacement = f'<meta property="og:image" content="{public_url}">'
        html, n = re.subn(r'<meta\s+property=["\']og:image["\']\s+content=["\'][^"\']+["\']\s*/?>', replacement, html, count=1, flags=re.I)
        if n != 1:
            raise RuntimeError(f"Could not update OG image in {page}")
        html, n = re.subn(r'<meta\s+name=["\']twitter:image["\']\s+content=["\'][^"\']+["\']\s*/?>', f'<meta name="twitter:image" content="{public_url}">', html, count=1, flags=re.I)
        if n != 1:
            raise RuntimeError(f"Could not update Twitter image in {page}")
        html = re.sub(r'<meta\\s+property=["\\']og:image:alt["\\'][^>]*>', "", html, flags=re.I)
        metadata = (
            f'\n<meta property="og:image:type" content="image/jpeg">'
            f'\n<meta property="og:image:width" content="1200">'
            f'\n<meta property="og:image:height" content="630">'
            f'\n<meta property="og:image:alt" content="{title.replace(chr(34), "&quot;")}">'
        )
        html = re.sub(r'(<meta\s+property=["\']og:image["\']\s+content=["\'][^"\']+["\']\s*/?>)', r'\1' + metadata, html, count=1, flags=re.I)
        page.write_text(html, encoding="utf-8")
        count += 1
    print(f"Generated {count} unique 1200x630 JPEG social cards.")

if __name__ == "__main__":
    main()
