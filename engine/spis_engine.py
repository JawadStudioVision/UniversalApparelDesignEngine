import json
import re
from pathlib import Path
from config.settings import NICHES_DIR

class SelfPromptImprovementEngine:
    """
    Evaluates draft apparel graphic prompts against commercial DTG/screen-print standards
    and niche-specific design rules. Automatically refines prompts until they achieve >= 9.8/10.
    """

    CRITERIA_WEIGHTS = {
        "rule_of_one": 1.5,
        "solid_background": 1.5,
        "arched_typography": 1.5,
        "solid_letter_fills": 1.0,
        "high_contrast_linework": 1.0,
        "vector_woodcut_style": 1.0,
        "zero_digital_gradients": 1.0,
        "clean_negative_space": 0.5,
        "no_mockups_or_models": 1.0
    }

    def __init__(self, niche_id="romance"):
        self.niche_id = niche_id
        self.niche_config = self._load_niche_config(niche_id)

    def _load_niche_config(self, niche_id):
        niche_file = NICHES_DIR / f"{niche_id}.json"
        if niche_file.exists():
            with open(niche_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def evaluate_prompt(self, prompt: str) -> dict:
        """Scores a prompt out of 10 and returns diagnostic feedback."""
        prompt_lower = prompt.lower()
        score = 0.0
        max_possible = sum(self.CRITERIA_WEIGHTS.values())
        feedback = []

        # 0. Strict Non-Violence & No Weapons Policy
        forbidden = self.niche_config.get("forbidden_themes", ["violence", "burn", "burning", "dagger", "sword", "weapon", "blood", "kill", "destroy"])
        found_forbidden = [w for w in forbidden if w in prompt_lower]
        if found_forbidden:
            feedback.append(f"VIOLATION: Prompt contains forbidden violent/weapon words: {found_forbidden}. Only peaceful, tender, slow-burn romantic phrases permitted.")
            return {"score": 0.0, "passed": False, "feedback": feedback}

        # 1. Rule of One
        if any(w in prompt_lower for w in ["single", "centered", "one", "delicate", "isolated"]):
            score += self.CRITERIA_WEIGHTS["rule_of_one"]
        else:
            feedback.append("Missing explicit single-subject focal anchor (Rule of One).")

        # 2. Solid Background
        if "solid pure white background" in prompt_lower or "solid pure black background" in prompt_lower:
            score += self.CRITERIA_WEIGHTS["solid_background"]
        else:
            feedback.append("Must specify 'solid pure white background (#FFFFFF)' or 'solid pure black background (#000000)'.")

        # 3. Arched & Anchored Typography
        if "arched" in prompt_lower and ("anchored" in prompt_lower or "baseline" in prompt_lower):
            score += self.CRITERIA_WEIGHTS["arched_typography"]
        else:
            feedback.append("Typography should specify arched header and horizontal baseline footer.")

        # 4. Solid Letter Fills
        if "solid" in prompt_lower and ("fill" in prompt_lower or "letter" in prompt_lower):
            score += self.CRITERIA_WEIGHTS["solid_letter_fills"]
        else:
            feedback.append("Specify solid crisp letter fills (no hatched or degraded fonts).")

        # 5. Woodcut / Etching Style
        if any(w in prompt_lower for w in ["woodcut", "etching", "engraving", "cross-hatching"]):
            score += self.CRITERIA_WEIGHTS["vector_woodcut_style"]
        else:
            feedback.append("Style should specify 19th-century woodcut engraving or storybook etching.")

        # 6. Zero Gradients
        if "no soft digital airbrush" in prompt_lower or "no gradient" in prompt_lower or "vector" in prompt_lower:
            score += self.CRITERIA_WEIGHTS["zero_digital_gradients"]
        else:
            feedback.append("Explicitly prohibit soft digital airbrush gradients.")

        # 7. No Mockups or Models
        if "no t-shirt mockup" in prompt_lower and "no human model" in prompt_lower:
            score += self.CRITERIA_WEIGHTS["no_mockups_or_models"]
        else:
            feedback.append("Must explicitly include 'no t-shirt mockup, no human model'.")

        # 8. Contrast
        if "high contrast" in prompt_lower or "luminous" in prompt_lower or "deep charcoal" in prompt_lower:
            score += self.CRITERIA_WEIGHTS["high_contrast_linework"]

        # 9. Clean negative space
        if "clean negative space" in prompt_lower or "isolated" in prompt_lower:
            score += self.CRITERIA_WEIGHTS["clean_negative_space"]

        final_score = round((score / max_possible) * 10.0, 1)
        return {
            "score": final_score,
            "passed": final_score >= 9.8,
            "feedback": feedback
        }

    def elevate_prompt(self, subject: str, header_text: str, footer_text: str, tone: str = "light") -> str:
        """Constructs an immediate 10/10 masterwork prompt based on niche rules."""
        style = self.niche_config.get("visual_style", "19th-century storybook woodcut engraving with razor-sharp vector cross-hatching")
        colorway = self.niche_config.get("colorways", {}).get(tone, {})
        ink = colorway.get("ink_palette", "Deep charcoal black with dark forest green accents")
        bg = colorway.get("background", "Solid pure white background (#FFFFFF)")

        prompt = (
            f"A definitive 10/10 masterwork vintage woodcut engraving t-shirt graphic centered on a {bg}. "
            f"Subject: {subject} "
            f"The composition is horizontally balanced with clean negative space and zero background clutter. "
            f"Typography: In perfectly unified, bold vintage editorial book serif typography with solid crisp letter fills (no hatched lettering): "
            f"\"{header_text}\" is gracefully arched above with delicate filigree ornament rules, and \"{footer_text}\" is boldly anchored below in an aligned horizontal baseline with bookend rules. "
            f"Style: {style} for premium commercial apparel printing. No soft digital airbrush gradients. "
            f"Palette: {ink} on {bg}. "
            f"Rule of One, isolated graphic artwork only, no t-shirt mockup, no human model."
        )
        return prompt
