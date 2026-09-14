import numpy as np
from PIL import Image
from typing import Dict, Any, Optional

def validate_print_asset(
    transparent_img: Image.Image,
    raw_img: Optional[Image.Image] = None,
    target_width: int = 5000,
    target_height: int = 5000,
    min_coverage: float = 0.75,
    max_coverage: float = 0.95
) -> Dict[str, Any]:
    """
    Automated Pre-Flight Gatekeeper:
    Enforces that every apparel graphic complies with commercial POD specifications:
    1. Exact 5000x5000 RGBA format
    2. Artwork occupies 80-95% chest coverage (rejects tiny unscaled images)
    3. 100% clean perimeter transparency (no edge background bleed)
    4. Typography and composition preservation (verifies top and bottom text were not stripped)
    """
    report = {"passed": True, "checks": {}}

    # 1. Dimensions & Mode
    dim_ok = bool((transparent_img.size == (target_width, target_height)) and (transparent_img.mode == "RGBA"))
    report["checks"]["dimensions_and_mode"] = {
        "passed": dim_ok,
        "details": f"{transparent_img.size}, {transparent_img.mode}"
    }
    if not dim_ok:
        report["passed"] = False

    # 2. Content Bounding Box & Scale Coverage
    bbox = transparent_img.getbbox()
    if not bbox:
        report["checks"]["content_coverage"] = {"passed": False, "details": "Empty canvas (all transparent)"}
        report["passed"] = False
        return report

    content_w = bbox[2] - bbox[0]
    content_h = bbox[3] - bbox[1]
    max_dim = max(content_w, content_h)
    coverage_ratio = max_dim / max(target_width, target_height)

    coverage_ok = bool(min_coverage <= coverage_ratio <= max_coverage)
    report["checks"]["content_coverage"] = {
        "passed": coverage_ok,
        "details": f"Artwork: {content_w}x{content_h} ({coverage_ratio*100:.1f}% coverage, target: {min_coverage*100:.0f}-{max_coverage*100:.0f}%)"
    }
    if not coverage_ok:
        report["passed"] = False

    # 3. Perimeter Transparency (No Edge Bleed)
    arr = np.array(transparent_img)
    alpha = arr[:, :, 3]
    perimeter_alpha = np.concatenate([
        alpha[0:15, :].ravel(),
        alpha[-15:, :].ravel(),
        alpha[:, 0:15].ravel(),
        alpha[:, -15:].ravel()
    ])
    max_perimeter_alpha = int(np.max(perimeter_alpha))
    perimeter_ok = bool(max_perimeter_alpha == 0)
    report["checks"]["perimeter_transparency"] = {
        "passed": perimeter_ok,
        "details": f"Max perimeter alpha: {max_perimeter_alpha} (expected: 0)"
    }
    if not perimeter_ok:
        report["passed"] = False

    # 4. Content Preservation vs Raw Image
    if raw_img is not None:
        raw_rgb = np.array(raw_img.convert("RGB"), dtype=float)
        bg_corners = np.vstack([raw_rgb[0:10, :].reshape(-1, 3), raw_rgb[-10:, :].reshape(-1, 3)])
        bg_color = np.median(bg_corners, axis=0)
        raw_dist = np.sqrt(np.sum((raw_rgb - bg_color)**2, axis=2))
        raw_mask = raw_dist > 25.0

        y_indices, x_indices = np.where(raw_mask)
        if len(y_indices) > 0:
            raw_top_span = float(np.min(y_indices) / raw_img.height)
            raw_bottom_span = float(np.max(y_indices) / raw_img.height)

            trans_y_indices, trans_x_indices = np.where(alpha > 20)
            trans_top_span = float(np.min(trans_y_indices) / target_height)
            trans_bottom_span = float(np.max(trans_y_indices) / target_height)

            top_preserved = bool((trans_top_span <= 0.15) if (raw_top_span <= 0.15) else True)
            bottom_preserved = bool((trans_bottom_span >= 0.85) if (raw_bottom_span >= 0.85) else True)
            preservation_ok = bool(top_preserved and bottom_preserved)
            report["checks"]["typography_preservation"] = {
                "passed": preservation_ok,
                "details": f"Raw span [{raw_top_span:.2f}, {raw_bottom_span:.2f}] -> Final span [{trans_top_span:.2f}, {trans_bottom_span:.2f}]"
            }
            if not preservation_ok:
                report["passed"] = False

    return report
