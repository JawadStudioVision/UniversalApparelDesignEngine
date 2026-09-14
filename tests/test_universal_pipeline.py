import os
import sys
import unittest
from pathlib import Path
from PIL import Image
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.spis_engine import SelfPromptImprovementEngine
from engine.qa_gatekeeper import validate_print_asset
from engine.asset_processor import extract_transparent_background

class TestUniversalPipeline(unittest.TestCase):

    def setUp(self):
        self.spis = SelfPromptImprovementEngine(niche_id="romance")

    def test_spis_evaluation_passes_10_10_prompt(self):
        prompt = (
            "A definitive 10/10 masterwork vintage woodcut engraving t-shirt graphic centered on a solid pure white background (#FFFFFF). "
            "Subject: Two delicate swallows perched intimately close on a bare winter branch with clean negative space. "
            "Typography: In bold vintage editorial serif with solid crisp letter fills: 'ALMOST IS' is arched above, and "
            "'MY FAVORITE PART' is anchored below with clean horizontal baseline. "
            "Style: 19th-century storybook woodcut engraving with razor-sharp vector cross-hatching for commercial DTG apparel printing. "
            "No soft digital airbrush gradients, no background clutter. "
            "Palette: Deep charcoal black with antique dark forest green accents on solid pure white background (#FFFFFF). "
            "Rule of One, isolated graphic artwork only, no t-shirt mockup, no human model."
        )
        res = self.spis.evaluate_prompt(prompt)
        self.assertTrue(res["passed"], f"Expected score >= 9.8, got {res['score']}")
        self.assertGreaterEqual(res["score"], 9.8)

    def test_qa_gatekeeper_rejects_tiny_unscaled_artwork(self):
        # Create 5000x5000 canvas with only a tiny 500x500 box in center (10% coverage)
        canvas = Image.new("RGBA", (5000, 5000), (0, 0, 0, 0))
        tiny_box = Image.new("RGBA", (500, 500), (0, 0, 0, 255))
        canvas.paste(tiny_box, (2250, 2250))

        report = validate_print_asset(canvas)
        self.assertFalse(report["passed"], "QA Gatekeeper must reject artwork with < 80% coverage!")
        self.assertFalse(report["checks"]["content_coverage"]["passed"])

    def test_qa_gatekeeper_approves_full_print_asset(self):
        # Create 5000x5000 canvas with 4500x4400 box (90% coverage) and clean perimeter
        canvas = Image.new("RGBA", (5000, 5000), (0, 0, 0, 0))
        proper_box = Image.new("RGBA", (4500, 4400), (0, 0, 0, 255))
        canvas.paste(proper_box, (250, 300))

        report = validate_print_asset(canvas)
        self.assertTrue(report["passed"], f"QA Gatekeeper failed: {report}")
        self.assertTrue(report["checks"]["content_coverage"]["passed"])
        self.assertTrue(report["checks"]["perimeter_transparency"]["passed"])

    def test_color_to_alpha_clears_white_background(self):
        # Create sample image with white background and dark center square
        raw = Image.new("RGB", (200, 200), (255, 255, 255))
        for x in range(50, 150):
            for y in range(50, 150):
                raw.putpixel((x, y), (20, 20, 20))

        trans = extract_transparent_background(raw, bg_color="white")
        # Corner must be 100% transparent
        self.assertEqual(trans.getpixel((0, 0))[3], 0)
        # Center must be opaque
        self.assertGreater(trans.getpixel((100, 100))[3], 240)

if __name__ == "__main__":
    unittest.main()
