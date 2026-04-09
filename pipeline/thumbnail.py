"""Step 5: 썸네일 생성 — 텍스트 오버레이 이미지"""

from pathlib import Path


def generate_thumbnail(
    script_data: dict, config: dict, output_dir: str, dry_run: bool = False
) -> dict:
    """쇼츠 썸네일 이미지를 생성한다."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    thumb_path = out / "thumbnail.png"

    title = script_data.get("title", "사물쇼츠")
    hook = script_data["sections"][0]["text"] if script_data.get("sections") else title

    if dry_run:
        thumb_path.write_text(f"[DRY-RUN] Thumbnail for: {title}")
        return {"thumbnail_path": str(thumb_path), "status": "dry-run"}

    from PIL import Image, ImageDraw, ImageFont

    thumb_config = config.get("thumbnail", {})
    w = thumb_config.get("width", 1280)
    h = thumb_config.get("height", 720)

    img = Image.new("RGB", (w, h), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Use default font (cross-platform safe)
    try:
        font_large = ImageFont.truetype("arial.ttf", 64)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = font_large

    # Title centered
    bbox = draw.textbbox((0, 0), title, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, h // 3), title, fill=(255, 255, 255), font=font_large)

    # Hook text below
    bbox2 = draw.textbbox((0, 0), hook, font=font_small)
    hw = bbox2[2] - bbox2[0]
    draw.text(
        ((w - hw) // 2, h // 2 + 30), hook, fill=(200, 200, 200), font=font_small
    )

    img.save(str(thumb_path))
    return {"thumbnail_path": str(thumb_path), "status": "complete"}
