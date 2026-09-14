"""
Universal Apparel Design Engine
Commercial-grade, niche-agnostic apparel design generation, background extraction, and quality assurance system.
"""
from .spis_engine import SelfPromptImprovementEngine
from .asset_processor import process_apparel_graphic, extract_transparent_background
from .qa_gatekeeper import validate_print_asset
from .image_generator import ImageGenerationEngine
from .lifecycle_miner import CommercialLifecycleMiner

__all__ = [
    "SelfPromptImprovementEngine",
    "process_apparel_graphic",
    "extract_transparent_background",
    "validate_print_asset",
    "ImageGenerationEngine",
    "CommercialLifecycleMiner"
]
