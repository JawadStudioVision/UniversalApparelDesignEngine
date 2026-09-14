import os
import shutil
import sys
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from engine.asset_processor import process_apparel_graphic

SOURCE_DIR = Path(r'C:\Users\AI Factorz\Documents\TheYearningClub\DesignedImages\New Designs 2')
DEST_DIR = Path(r'C:\Users\AI Factorz\Documents\TheYearningClub\DesignedImages\New Designs\NewDesignsPhase2\AutomatThroughAPIKey')
RAW_DIR = DEST_DIR / "RAW"

CATALOG_MAPPING = [
    # TG03: Getting Invested
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_18_57 AM.png",
        "title": "Getting Invested",
        "code": "TG03",
        "tone": "light"
    },
    # IG04 & TG05: All This Tension
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_19_15 AM (1).png",
        "title": "All This Tension",
        "code": "TG04",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_19_16 AM (2).png",
        "title": "All This Tension",
        "code": "TG05",
        "tone": "dark"
    },
    # TG06 & TG07: Strategic Jealousy
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_21_56 AM (1).png",
        "title": "Strategic Jealousy",
        "code": "TG06",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_21_56 AM (2).png",
        "title": "Strategic Jealousy",
        "code": "TG07",
        "tone": "dark"
    },
    # TG08 & IG09: Too Late Pretend
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_26_03 AM (1).png",
        "title": "Too Late Pretend",
        "code": "TG08",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_26_04 AM (2).png",
        "title": "Too Late Pretend",
        "code": "TG09",
        "tone": "dark"
    },
    # IG10 & TG11: Chapter Twelve
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_29_22 AM (1).png",
        "title": "Chapter Twelve",
        "code": "TG10",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_29_23 AM (2).png",
        "title": "Chapter Twelve",
        "code": "TG11",
        "tone": "dark"
    },
    # TG12 to TG17: Cute Animals (Pink Poster Series)
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 05_41_19 AM.png",
        "title": "Financially Irresponsible",
        "code": "TG12",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 06_02_41 AM (1).png",
        "title": "Mixed Signals",
        "code": "TG13",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 06_02_42 AM (2).png",
        "title": "Three Books Kiss",
        "code": "TG14",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 06_02_43 AM (3).png",
        "title": "Need Tension",
        "code": "TG15",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 06_02_44 AM (4).png",
        "title": "Forty Percent",
        "code": "TG16",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 06_02_45 AM (5).png",
        "title": "Romantically Unconfirmed",
        "code": "TG17",
        "tone": "light"
    },
    # TG18 to TG22: Vintage Linocut Series (Textured Cream)
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 10_02_08 AM (1).png",
        "title": "Mixed Signals Vintage",
        "code": "TG18",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 10_02_09 AM (2).png",
        "title": "Three Books Vintage",
        "code": "TG19",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 10_02_09 AM (3).png",
        "title": "Need Tension Vintage",
        "code": "TG20",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 10_02_09 AM (4).png",
        "title": "Forty Percent Vintage",
        "code": "TG21",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 10_02_10 AM (5).png",
        "title": "Romantically Unconfirmed Vintage",
        "code": "TG22",
        "tone": "light"
    },
    # TG23 & TG24: Yearing Club Peeking Bunny
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 11_42_45 PM.png",
        "title": "Zero Composure Bunny",
        "code": "TG23",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 11_43_38 PM.png",
        "title": "Zero Composure Bunny",
        "code": "TG24",
        "tone": "dark"
    },
    # TG25, TG26 & TG27: Cheeky Bunny
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 11_51_26 PM.png",
        "title": "Cheeky Bunny Reading",
        "code": "TG25",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 11_56_13 PM.png",
        "title": "One Glance Bunny",
        "code": "TG26",
        "tone": "light"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 11_57_52 PM.png",
        "title": "One Glance Bunny",
        "code": "TG27",
        "tone": "dark"
    },
    # TG28 & TG29: Patriotic Love Series
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 03_54_49 AM (1).png",
        "title": "Patriotic Pinup Love",
        "code": "TG28",
        "tone": "Darli"
    },
    {
        "src_file": "ChatGPT Image Sep 13, 2026, 03_54_50 AM (2).png",
        "title": "American Pinup Love",
        "code": "TG29",
        "tone": "Darli"
    },
    # TG01 Raw Verification (Already finalized)
    {
        "src_file": "ChatGPT Image Sep 14, 2026, 12_02_10 AM.png",
        "title": "Almost Favorite Part",
        "code": "TG01",
        "tone": "light",
        "skip_final": True
    }
]

def run_batch():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    print("========================================================")
    print(f"BATCH INGESTION & PROCESSING: {len(CATALOG_MAPPING)} ASSETS")
    print(f"Destination: {DEST_DIR}")
    print(f"Raw Archive: {RAW_DIR}")
    print("========================================================\n")

    results = []

    for idx, item in enumerate(CATALOG_MAPPING, start=1):
        src_path = SOURCE_DIR / item["src_file"]
        title = item["title"]
        code = item["code"]
        tone = item["tone"]

        base_name = f"{title} - {code} - {tone}"
        raw_dest_path = RAW_DIR / f"{base_name}_Raw.png"
        final_dest_path = DEST_DIR / f"{base_name}.png"

        print(f"[{idx:02d}/{len(CATALOG_MAPPING):02d}] Processing: {base_name}")

        if not src_path.exists():
            print(f"  [ERROR] Source file missing: {src_path.name}")
            results.append({"code": code, "name": base_name, "status": "SRC_MISSING"})
            continue

        if not raw_dest_path.exists():
            shutil.copy2(src_path, raw_dest_path)
            print(f"  [Archived Raw] -> RAW/{raw_dest_path.name}")
        else:
            print(f"  [Archived Raw] Exists -> RAW/{raw_dest_path.name}")

        if item.get("skip_final"):
            print(f"  [Skipped Final] Already finalized: {final_dest_path.name}")
            results.append({"code": code, "name": base_name, "status": "ALREADY_FINALIZED"})
            continue

        try:
            process_apparel_graphic(
                input_path=str(raw_dest_path),
                output_path=str(final_dest_path),
                target_width=5000,
                target_height=5000,
                dpi=300,
                method="auto"
            )
            print(f"  [SUCCESS] Master Asset Created -> {final_dest_path.name}\n")
            results.append({"code": code, "name": base_name, "status": "SUCCESS"})
        except Exception as e:
            print(f"  [FAILED] Error processing {base_name}: {e}\n")
            results.append({"code": code, "name": base_name, "status": f"FAILED: {e}"})

    print("\n========================================================")
    print("BATCH SUMMARY:")
    for res in results:
        print(f"  - [{res['status']}] {res['code']}: {res['name']}")
    print("========================================================")

if __name__ == '__main__':
    run_batch()
