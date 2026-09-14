import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
NICHES_DIR = CONFIG_DIR / "niches"
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = PROJECT_ROOT / "exports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables (.env in project root or parent)
load_dotenv(PROJECT_ROOT / ".env")
if not os.environ.get("OPENROUTER_API_KEY"):
    load_dotenv(PROJECT_ROOT.parent.parent / ".env")
if not os.environ.get("OPENROUTER_API_KEY"):
    load_dotenv(PROJECT_ROOT.parent.parent / "YearningClubAutomationTShirt" / ".env")

class Settings:
    # API Configurations
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_IMAGE_MODEL", "openai/gpt-5.4-image-2")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1/chat/completions"

    # Apparel Resolution & DPI Standards
    TARGET_CANVAS_WIDTH: int = 5000
    TARGET_CANVAS_HEIGHT: int = 5000
    TARGET_DPI: int = 300
    CHEST_COVERAGE_MIN: float = 0.80
    CHEST_COVERAGE_MAX: float = 0.95

    # Printify & Shopify Integration
    SHOPIFY_STORE_DOMAIN: str = os.getenv("SHOPIFY_STORE_DOMAIN", "")
    SHOPIFY_ADMIN_ACCESS_TOKEN: str = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN", "")
    PRINTIFY_API_TOKEN: str = os.getenv("PRINTIFY_API_TOKEN", "")
    PRINTIFY_SHOP_ID: str = os.getenv("PRINTIFY_SHOP_ID", "")

settings = Settings()
