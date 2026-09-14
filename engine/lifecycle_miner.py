import os
import json
import re
import datetime
import requests
from pathlib import Path
from config.settings import settings, DATA_DIR

class CommercialLifecycleMiner:
    """
    Connects to Printify and Shopify APIs to mine order history,
    scores designs based on sales velocity, generates winner expansion briefs (2-3 month mark),
    and blacklists/deprecates failed designs (1-year zero-sale mark).
    """

    def __init__(self):
        self.shopify_domain = settings.SHOPIFY_STORE_DOMAIN
        self.shopify_token = settings.SHOPIFY_ADMIN_ACCESS_TOKEN
        self.printify_token = settings.PRINTIFY_API_TOKEN
        self.printify_shop_id = settings.PRINTIFY_SHOP_ID

        self.shopify_headers = {
            "X-Shopify-Access-Token": self.shopify_token,
            "Content-Type": "application/json"
        }
        self.printify_headers = {
            "Authorization": f"Bearer {self.printify_token}",
            "Content-Type": "application/json"
        }

        self.performance_file = DATA_DIR / "design_sales_performance.json"
        self.winner_briefs_file = DATA_DIR / "winner_expansion_briefs.json"
        self.blacklist_file = DATA_DIR / "deprecated_designs_blacklist.json"

    def fetch_printify_orders(self):
        """Fetches all orders from Printify API."""
        if not self.printify_token or not self.printify_shop_id:
            print("[Notice] Printify credentials not set; skipping Printify orders.")
            return []

        orders = []
        page = 1
        while True:
            url = f"https://api.printify.com/v1/shops/{self.printify_shop_id}/orders.json?page={page}&limit=50"
            res = requests.get(url, headers=self.printify_headers, timeout=20)
            if res.status_code != 200:
                break
            data = res.json()
            items = data.get("data", [])
            if not items:
                break
            orders.extend(items)
            if page >= data.get("last_page", 1):
                break
            page += 1
        return orders

    def audit_catalog(self):
        """Runs the complete lifecycle audit and updates winner/blacklist registries."""
        print("[Lifecycle Miner] Auditing sales performance...")
        orders = self.fetch_printify_orders()
        sales_by_code = {}

        for order in orders:
            for item in order.get("line_items", []):
                meta = item.get("metadata", {})
                title = meta.get("title", "")
                qty = item.get("quantity", 1)
                price = float(meta.get("price", 2999)) / 100.0

                code_match = re.search(r'\b([A-Z]{1,2}\d{2,3})\b', title)
                if code_match:
                    code = code_match.group(1)
                    if code not in sales_by_code:
                        sales_by_code[code] = {"units": 0, "revenue": 0.0, "title": title}
                    sales_by_code[code]["units"] += qty
                    sales_by_code[code]["revenue"] += price * qty

        with open(self.performance_file, "w", encoding="utf-8") as f:
            json.dump(sales_by_code, f, indent=2)

        print(f"[Lifecycle Miner] Successfully audited {len(sales_by_code)} active earning SKUs.")
        return sales_by_code
