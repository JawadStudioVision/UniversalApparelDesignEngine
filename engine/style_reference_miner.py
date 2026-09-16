import os
from pathlib import Path
from typing import Dict, List, Any

class StyleReferenceMiner:
    """
    Analyzes and extracts visual style DNA, composition archetypes,
    and typographic hierarchy from user-provided design reference directories.
    Synthesizes external inspiration with niche research parameters.
    """

    DEFAULT_REFERENCE_DIR = Path(r"C:\Users\AI Factorz\Documents\Printify Popup Store\Christmas\Designs\raw_backup")

    STYLE_ARCHETYPES = {
        "botanical_wreath_enclosure": {
            "name": "Circular Botanical Wreath / Arch Badge Enclosure",
            "inspiration_sources": ["christmas_mug_warm_wishes.jpg", "Designer.png", "christmas_tshirt_stay_festive.jpg"],
            "romance_adaptation": (
                "Self-contained circular or arched botanical badge enclosure. "
                "Delicate climbing wild roses, ivy vines, and starlight embers framing a central focal emblem. "
                "Creates a cohesive, premium DTG print footprint with no awkward empty corners."
            ),
            "prompt_keywords": [
                "circular botanical wreath badge frame",
                "arched floral vignette enclosure",
                "delicate climbing wild roses and ivy border",
                "perfectly self-contained emblem layout"
            ]
        },
        "multi_tier_typographic_lockup": {
            "name": "Multi-Tier Dual-Font Typography Lockup with Ornamental Bookends",
            "inspiration_sources": ["Designer.png", "01_festive_overtime.png", "Screenshot 2026-09-16 015244.png"],
            "romance_adaptation": (
                "High-contrast typographic hierarchy: Vintage bold editorial serif header arched overhead, "
                "paired with fluid cursive script or solid Roman slab anchor, "
                "flanked by ornamental bookend dashes, floral sprigs, or star divider bars (e.g. '— WORD —')."
            ),
            "prompt_keywords": [
                "bold vintage serif arched header",
                "fluid romantic script central accent",
                "clean horizontal baseline anchor",
                "ornamental bookend dashes and floral sprig dividers"
            ]
        },
        "luminous_ethereal_filament": {
            "name": "Luminous Filament Linework & Celestial Starlight Ribbon (Dark Edition Focus)",
            "inspiration_sources": ["ChatGPT Image Sep 16, 2026, 04_55_31 AM (1).png (Swans)", "04_23_27 AM (1).png (Turntable Star Ribbon)"],
            "romance_adaptation": (
                "Ethereal, glowing fine-line vector art on pure pitch black (#000000). "
                "Subjects like twin swans forming a delicate heart silhouette under a radiant North Star, "
                "or a glowing ribbon of starlight tracing between lovers hands or rising from open book pages. "
                "Rendered in luminous ivory cream (#FDFBF7) and starlight gold linework."
            ),
            "prompt_keywords": [
                "ethereal luminous filament vector linework",
                "radiant North Star celestial accent",
                "flowing ribbon of golden starlight dust",
                "high-contrast ivory and gold lines on pitch black"
            ]
        },
        "cozy_storybook_warmth": {
            "name": "Tactile Storybook Crosshatching & Domestic Cozy Romance",
            "inspiration_sources": ["04_light_came_near.png", "ChatGPT Image Sep 16, 2026, 05_01_25 AM (5).png", "03_58_52 AM (1).png"],
            "romance_adaptation": (
                "Storybook ink hatching and warm tactile textures. "
                "Antique porcelain teacups with heart silhouettes rising in warm steam, "
                "open hardcovers with gold star bookmarks, pressed botanical carnations, and vintage brass lanterns."
            ),
            "prompt_keywords": [
                "storybook crosshatched ink etching",
                "cozy domestic romance vignette",
                "steaming vintage ceramic mug with subtle heart steam",
                "pressed botanical flora and warm ambient glow"
            ]
        }
    }

    def __init__(self, reference_dir: Path = None):
        self.reference_dir = Path(reference_dir) if reference_dir else self.DEFAULT_REFERENCE_DIR

    def scan_reference_assets(self) -> Dict[str, Any]:
        if not self.reference_dir.exists():
            return {"exists": False, "count": 0, "recent_files": []}
        files = sorted(
            [f for f in self.reference_dir.iterdir() if f.is_file() and f.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        return {
            "exists": True,
            "directory": str(self.reference_dir),
            "count": len(files),
            "recent_files": [f.name for f in files[:10]]
        }

    def get_synthesized_style_prompt(self, archetype_key: str, tone: str = "light") -> str:
        archetype = self.STYLE_ARCHETYPES.get(archetype_key, self.STYLE_ARCHETYPES["botanical_wreath_enclosure"])
        keywords = ", ".join(archetype["prompt_keywords"])
        if tone.lower() == "dark":
            tone_directives = (
                "Solid pure pitch-black background (#000000). "
                "Luminous ivory cream (#FDFBF7) and muted warm gold linework with crisp white highlights. "
                "Zero dark perimeter glow, zero drop shadows."
            )
        else:
            tone_directives = (
                "Solid pure white background (#FFFFFF). "
                "Deep rich espresso brown, midnight navy, or dark forest green linework with crisp solid fills. "
                "Zero off-white background tint, zero digital drop shadows."
            )
        return f"{keywords}. {tone_directives}"

style_miner = StyleReferenceMiner()
