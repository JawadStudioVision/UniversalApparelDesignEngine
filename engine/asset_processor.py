import os
from pathlib import Path
from PIL import Image
import numpy as np
from .qa_gatekeeper import validate_print_asset

def extract_transparent_background(img: Image.Image, bg_color: str = "white", t_low: float = 8.0, t_high: 32.0 = 32.0) -> Image.Image:
    """
    High-precision mathematical Color-to-Alpha unmixing for apparel graphics.
    Eliminates solid backgrounds without destroying typography, filigree, or line art,
    and unmixes edge pixels to prevent white/black halo fringe on shirts.
    """
    img_rgb = img.convert("RGB")
    arr = np.array(img_rgb, dtype=float)

    # 1. Estimate background color from outer border samples
    border_pixels = np.vstack([
        arr[0:15, :].reshape(-1, 3),
        arr[-15:, :].reshape(-1, 3),
        arr[:, 0:15].reshape(-1, 3),
        arr[:, -15:].reshape(-1, 3)
    ])
    bg_est = np.median(border_pixels, axis=0)

    # 2. Compute Euclidean distance from background color
    dist = np.sqrt(np.sum((arr - bg_est)**2, axis=2))

    # 3. Calculate smooth anti-aliased alpha
    alpha = np.clip((dist - t_low) / (t_high - t_low), 0.0, 1.0)

    # 4. De-fringe / unmix RGB foreground from background
    alpha_expanded = alpha[:, :, np.newaxis]
    safe_alpha = np.maximum(alpha_expanded, 1e-4)
    fg_unmixed = (arr - (1.0 - alpha_expanded) * bg_est) / safe_alpha
    fg_clean = np.clip(fg_unmixed, 0.0, 255.0)

    # 5. Reassemble RGBA
    final_rgba = np.dstack([fg_clean, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(final_rgba, mode="RGBA")

def process_apparel_graphic(
    input_path: str,
    output_path: str,
    target_width: int = 5000,
    target_height: int = 5000,
    dpi: int = 300,
    bg_color: str = "auto",
    method: str = "auto"
) -> str:
    """
    Takes a raw generated graphic, extracts high-precision transparency,
    upscales typography and illustration to 5000x5000 at 300 DPI (occupying 90% printable chest area),
    and validates through the Pre-Flight QA Gatekeeper before saving.
    
    method: 'color_to_alpha', 'rembg', or 'auto' (selects color_to_alpha for solid white/black, rembg for textured/colored/checkerboard)
    """
    input_p = Path(input_path)
    output_p = Path(output_path)

    if not input_p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"[Processor] Opening raw image: {input_p.name}...")
    img = Image.open(input_p)

    # 1. Determine background and extraction method
    corners = [
        img.getpixel((0, 0)),
        img.getpixel((img.width - 1, 0)),
        img.getpixel((0, img.height - 1)),
        img.getpixel((img.width - 1, img.height - 1))
    ]
    avg_brightness = sum(sum(c[:3]) / 3 for c in corners) / 4
    if bg_color == "auto":
        bg_color = "white" if avg_brightness > 128 else "black"

    chosen_method = method
    if chosen_method == "auto":
        # Check corner pixel variance to identify textured/checkerboard vs pure solid
        corner_arr = np.array([c[:3] for c in corners], dtype=float)
        corner_std = np.mean(np.std(corner_arr, axis=0))
        # Solid white (>245) or solid black (<15) with low variance
        if corner_std < 10.0 and (avg_brightness > 245 or avg_brightness < 15):
            chosen_method = "color_to_alpha"
        else:
            chosen_method = "rembg"

    print(f"[Processor] Selected method: {chosen_method.upper()} (bg: {bg_color.upper()}, brightness: {avg_brightness:.1f})")

    # 2. Extract Transparency
    if chosen_method == "rembg":
        import rembg
        transparent_img = rembg.remove(img)
    else:
        transparent_img = extract_transparent_background(img, bg_color=bg_color)

    # 3. Auto-crop to content bounding box
    bbox = transparent_img.getbbox()
    if bbox:
        cropped = transparent_img.crop(bbox)
        print(f"[Processor] Content bounding box: {bbox} ({cropped.width}x{cropped.height} px)")
    else:
        cropped = transparent_img

    # 4. Upscale cleanly to printable chest area (90% target)
    printable_w = int(target_width * 0.90)
    printable_h = int(target_height * 0.90)

    scale = min(printable_w / cropped.width, printable_h / cropped.height)
    new_w = int(round(cropped.width * scale))
    new_h = int(round(cropped.height * scale))
    print(f"[Processor] Scaling artwork: {cropped.width}x{cropped.height} -> {new_w}x{new_h} (scale: {scale:.2f}x)...")

    scaled = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 5. Create final 5000x5000 canvas and center artwork
    final_canvas = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    offset_x = (target_width - new_w) // 2
    offset_y = (target_height - new_h) // 2
    final_canvas.paste(scaled, (offset_x, offset_y), scaled)

    # 6. Automated Pre-Flight Quality Assurance Gate
    qa_report = validate_print_asset(final_canvas, raw_img=img, target_width=target_width, target_height=target_height)
    if not qa_report["passed"]:
        print(f"[QA FAILED] Pre-flight inspection failed for: {output_p.name}")
        for check_name, check_data in qa_report["checks"].items():
            status = "PASS" if check_data["passed"] else "FAIL"
            print(f"  - [{status}] {check_name}: {check_data['details']}")
        raise RuntimeError(f"Pre-flight QA validation failed: {qa_report}")

    # 7. Save with 300 DPI metadata
    output_p.parent.mkdir(parents=True, exist_ok=True)
    final_canvas.save(output_p, "PNG", dpi=(dpi, dpi), optimize=True)
    print(f"[Processor Success] Master print asset generated & QA Approved: {output_p.name}")
    print(f"[Processor Specs] Resolution: {target_width}x{target_height} | DPI: {dpi} | Span: {new_w}x{new_h}")
    return str(output_p.resolve())
