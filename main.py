import argparse
import sys
from pathlib import Path
from engine.spis_engine import SelfPromptImprovementEngine
from engine.image_generator import ImageGenerationEngine
from engine.asset_processor import process_apparel_graphic
from engine.qa_gatekeeper import validate_print_asset
from engine.lifecycle_miner import CommercialLifecycleMiner
from config.settings import settings

def main():
    parser = argparse.ArgumentParser(
        description="Universal Apparel Design Engine — Commercial POD Generation, Background Extraction & QA Gatekeeper"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Generate and process a master apparel design")
    gen_parser.add_argument("--niche", default="romance", help="Niche ID (e.g. romance, fitness, coffee)")
    gen_parser.add_argument("--subject", required=True, help="Central subject description")
    gen_parser.add_argument("--header", required=True, help="Arched top typography text")
    gen_parser.add_argument("--footer", required=True, help="Anchored bottom typography text")
    gen_parser.add_argument("--title", required=True, help="2-3 word product title for mobile")
    gen_parser.add_argument("--code", required=True, help="Sequential product code (e.g. TG01)")
    gen_parser.add_argument("--tone", choices=["light", "dark", "darli"], default="light", help="Garment tone")
    gen_parser.add_argument("--output-dir", default=None, help="Directory to save final asset")

    # Command: process
    proc_parser = subparsers.add_parser("process", help="Process existing raw image into 5000x5000 transparent PNG")
    proc_parser.add_argument("--input", required=True, help="Path to raw image")
    proc_parser.add_argument("--output", required=True, help="Path for final transparent PNG")

    # Command: qa
    qa_parser = subparsers.add_parser("qa", help="Run automated Pre-Flight QA Gatekeeper on an asset")
    qa_parser.add_argument("--file", required=True, help="Path to transparent PNG to validate")
    qa_parser.add_argument("--raw", default=None, help="Path to raw counterpart image (optional)")

    # Command: sales-audit
    subparsers.add_parser("sales-audit", help="Mine Printify/Shopify sales data and update lifecycle tiers")

    args = parser.parse_args()

    if args.command == "generate":
        print(f"=== Universal Apparel Design Engine: Generating Asset [{args.code}] ===")
        spis = SelfPromptImprovementEngine(niche_id=args.niche)
        prompt = spis.elevate_prompt(
            subject=args.subject,
            header_text=args.header,
            footer_text=args.footer,
            tone=args.tone
        )
        eval_res = spis.evaluate_prompt(prompt)
        print(f"[SPIS] Prompt Quality Score: {eval_res['score']}/10 (Passed: {eval_res['passed']})")

        engine = ImageGenerationEngine()
        out_file = engine.generate_and_process(
            prompt=prompt,
            title=args.title,
            code=args.code,
            tone=args.tone,
            output_dir=args.output_dir
        )
        print(f"\n>>> Asset Generation Complete: {out_file}")

    elif args.command == "process":
        print(f"=== Processing Apparel Graphic: {args.input} ===")
        out = process_apparel_graphic(input_path=args.input, output_path=args.output)
        print(f">>> Processed and QA Approved: {out}")

    elif args.command == "qa":
        from PIL import Image
        print(f"=== Running Pre-Flight QA Gate on: {args.file} ===")
        trans_img = Image.open(args.file)
        raw_img = Image.open(args.raw) if args.raw else None
        res = validate_print_asset(trans_img, raw_img=raw_img)
        print(f"Overall Result: {'PASS' if res['passed'] else 'FAIL'}")
        for check, data in res["checks"].items():
            print(f"  - [{('PASS' if data['passed'] else 'FAIL')}] {check}: {data['details']}")
        sys.exit(0 if res["passed"] else 1)

    elif args.command == "sales-audit":
        print("=== Mining Sales Performance & Lifecycle Feedback ===")
        miner = CommercialLifecycleMiner()
        res = miner.audit_catalog()
        print("Done.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
