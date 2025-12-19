# --- Web Scraper (Vishay) ---
# Purpose: collect product categories, subcategories, and product links from vishay.com
# Output: a JSON file (topic_structure.json) with nodes: name, url, sub_topics, breadcrumbs
# Note: this version traverses the mobile menu DOM; recursion and deeper levels can be added later.

import requests  # HTTP client to fetch pages
from bs4 import BeautifulSoup  # HTML parser / DOM navigation
import sys  # Used here to set console encoding on Windows
import json  # Serialize Python objects to JSON
import argparse
import os

sys.stdout.reconfigure(
    encoding="utf-8"
)  # Ensure Unicode prints correctly on Windows terminals

final_data = []  # Accumulator for the final tree structure to be saved as JSON
url_princ = (
    "https://www.vishay.com"  # Base URL (also used to build absolute links later)
)

headers = {
    # Spoof a common desktop browser to reduce the chance of being blocked by basic server checks
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
}

response = requests.get(url_princ, headers=headers)  # Fetch the homepage HTML

print("Status Code:", response.status_code)  # Quick sanity check of the HTTP response
html = response.text  # Raw HTML content as text (decoded by requests)
soup = BeautifulSoup(html, "html.parser")  # Parse HTML into a navigable BeautifulSoup object

products = soup.select_one(
    "div.vsh-mobile-menu-overlay"
)  # Container for the mobile product menu
menus = []  # Will hold the two top-level product panels
prodMenu1 = products.select_one("div#ulMobileProdMenu1")  # First product menu panel
prodMenu2 = products.select_one("div#ulMobileProdMenu2")  # Second product menu panel
menus.append(prodMenu1)  # Add panel 1 (may be None if markup changes)
menus.append(prodMenu2)  # Add panel 2 (may be None if markup changes)


for menu in menus:  # Iterate over both panels
    category = menu.select_one(
        "div.vsh-mobile-menu-heading"
    ).text.strip()  # Category title (e.g., "Passive Components")
    final_data.append(  # Add a top-level category node to the result tree
        {
            "name": category,
            "url": "",  # URL left blank here; can be populated if available
            "sub_topics": [],  # Children (subcategories or products)
            "breadcrumbs": [category],  # Root-level breadcrumb
        }
    )
    try:
        sub_category = menu.select(
            "div.vsh-accordion"
        )  # Each accordion block corresponds to a subcategory
        amount_sub = len(sub_category)  # Number of subcategories found in this panel
    except Exception as e:
        print(
            f"Error processing menu {menu}: {e}"
        )  # Basic error logging if the expected structure is missing

    while amount_sub > 0:  # Walk subcategories in reverse order using a counter
        sub_category_text = (sub_category[amount_sub - 1].select_one("span").text.strip())  # Subcategory display text

        final_data[-1]["sub_topics"].append(  # Append the subcategory node under the current category
            {
                "name": sub_category_text,
                "url": "",  # URL left blank; can be set if a link exists
                "sub_topics": [],  # Will hold product nodes for this subcategory
                "breadcrumbs": [category, sub_category_text],
            }
        )

        products_box = sub_category[amount_sub - 1].select_one("div.vsh-home-content")  # Container with product links (if present)

        names = products_box.select("a")  # All anchors considered as product names
        links = products_box.select("a")  # Same anchors used to read hrefs (paired below)

        for name, link in zip(names, links):  # Pair each anchor's text with its href
            name = name.text.strip()  # Product display name
            new_link = ("https://www.vishay.com" + link.get("href").strip())  # Build absolute URL from relative href
            new_prod = {  # Product node with empty sub_topics (leaf)
                "name": name,
                "url": new_link,
                "sub_topics": [],
                "breadcrumbs": [category, sub_category_text, name],
            }
            final_data[-1]["sub_topics"][-1]["sub_topics"].append(new_prod)  # Append product under the latest subcategory
        amount_sub -= 1  # Move to the previous subcategory in this panel


print(final_data)

# CLI: --out path/to/file.json  (default: topic_structure.json)
parser = argparse.ArgumentParser(description="Dump scraped structure to JSON.")
parser.add_argument(
    "--out", default="topic_structure.json", help="Output JSON file path"
)
args = parser.parse_args()

# Create parent folder if needed (e.g., 'output/')
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

# Save JSON to the path provided via --out
with open(args.out, "w", encoding="utf-8") as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)
