import os
import json
import re
import base64
import urllib.request
from pathlib import Path
from config.settings import settings
from .asset_processor import process_apparel_graphic

class ImageGenerationEngine:
    """
    Interfaces with OpenRouter API (GPT-5.4-image-2, Flux, etc.) to generate
    raw print assets and automatically process them into 5000x5000 300 DPI transparent PNGs.
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.DEFAULT_MODEL

    def generate_and_process(
        self,
        prompt: str,
        title: str,
        code: str,
        tone: str = "light",
        output_dir: str = None
    ) -> str:
        """
        Generates raw image via OpenRouter, saves raw artifact,
        and processes into final [Title] - [Code] - [Tone].png print asset.
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment or settings.")

        target_dir = Path(output_dir) if output_dir else settings.EXPORTS_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        raw_dir = target_dir / "RAW"
        raw_dir.mkdir(parents=True, exist_ok=True)

        filename_base = f"{title} - {code} - {tone}"
        raw_path = raw_dir / f"{filename_base}_Raw.png"
        final_5000_path = target_dir / f"{filename_base}.png"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/JawadStudioVision/UniversalApparelDesignEngine",
            "X-Title": "Universal Apparel Design Engine"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": f"Generate the following apparel design artwork as an image:\n\n{prompt}"
                }
            ]
        }

        print(f"[OpenRouter] Generating asset with model: {self.model}...")
        print(f"[OpenRouter] Title='{title}' | Code='{code}' | Tone='{tone}'")

        req = urllib.request.Request(
            settings.OPENROUTER_BASE_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Save debug JSON in system data directory, not designs folder
        with open(settings.DATA_DIR / "last_api_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"No choices returned from OpenRouter: {data}")

        msg = choices[0].get("message", {})
        content = msg.get("content", "")
        saved_raw = False

        # 1. Parse message.images
        images = msg.get("images", [])
        if images:
            img_obj = images[0]
            img_data = None
            if isinstance(img_obj, str):
                img_data = img_obj
            elif isinstance(img_obj, dict):
                img_data = (
                    img_obj.get("url") or 
                    (img_obj.get("image_url", {}).get("url") if isinstance(img_obj.get("image_url"), dict) else img_obj.get("image_url")) or 
                    img_obj.get("b64_json") or 
                    img_obj.get("image") or
                    img_obj.get("data")
                )

            if img_data:
                if str(img_data).startswith("http"):
                    urllib.request.urlretrieve(img_data, raw_path)
                    saved_raw = True
                elif "base64," in str(img_data) or len(str(img_data)) > 200:
                    raw_b64 = str(img_data).split("base64,")[-1]
                    with open(raw_path, "wb") as f:
                        f.write(base64.b64decode(raw_b64))
                    saved_raw = True

        # 2. Parse Markdown URL
        if not saved_raw:
            url_match = re.search(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)
            if url_match:
                urllib.request.urlretrieve(url_match.group(1), raw_path)
                saved_raw = True

        # 3. Parse Markdown base64
        if not saved_raw:
            b64_match = re.search(r'!\[.*?\]\(data:image/[a-zA-Z]+;base64,([A-Za-z0-9+/=]+)\)', content)
            if b64_match:
                with open(raw_path, "wb") as f:
                    f.write(base64.b64decode(b64_match.group(1)))
                saved_raw = True

        if not saved_raw:
            raise RuntimeError(f"Could not extract image from model response: {content[:300]}")

        print(f"[Generator] Raw artwork saved to: {raw_path.name}")

        # Process transparency & upscale with Pre-Flight QA Gate
        final_asset = process_apparel_graphic(
            input_path=str(raw_path),
            output_path=str(final_5000_path),
            target_width=settings.TARGET_CANVAS_WIDTH,
            target_height=settings.TARGET_CANVAS_HEIGHT,
            dpi=settings.TARGET_DPI
        )

        return final_asset
