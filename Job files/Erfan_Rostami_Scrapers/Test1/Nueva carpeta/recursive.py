#!/usr/bin/env python3
"""
Vishay Recursive Scraper
------------------------
- Recursively extracts categories, sub-categories, and product links from the mobile menu on https://www.vishay.com
- Outputs a JSON tree with nodes: name, url, sub_topics, breadcrumbs
- Handles multiple levels via recursive descent on nested accordion blocks

Usage:
    python get_structure.py --out output/topic_structure_recursive.json
"""

import sys
import json
import argparse
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

# Ensure Windows terminals print Unicode correctly
sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://www.vishay.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
    )
}


def fetch_soup(url: str) -> BeautifulSoup:
    """HTTP GET + parse to BeautifulSoup with basic robustness."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def normalize_url(href: str, base: str = BASE_URL) -> str:
    """Build absolute URL from relative/absolute href; return empty string if invalid."""
    if not href:
        return ""
    return urljoin(base, href.strip())


def make_node(name: str, url: str, breadcrumbs: list) -> dict:
    """Create a standard node for the JSON tree."""
    return {
        "name": (name or "").strip(),
        "url": url or "",
        "sub_topics": [],
        "breadcrumbs": breadcrumbs[:],
    }


def extract_title_and_link(container: Tag) -> tuple[str, str]:
    """
    Try several selectors to get a human-friendly title and a representative link
    from a category/subcategory container.
    """
    title_el = (
        container.select_one(".vsh-mobile-menu-heading")
        or container.select_one(".vsh-mobile-menu-subheading")
        or container.select_one(".vsh-accordion-btn")
        or container.select_one("h1, h2, h3, h4")
        or container.select_one("a")
    )
    name = title_el.get_text(strip=True) if title_el else "Category"
    link_el = container.select_one("a[href]")
    url = normalize_url(link_el.get("href")) if link_el else ""
    return name, url


def collect_products(container: Tag, breadcrumbs: list) -> list[dict]:
    """
    Collect product-like anchors within the given container.
    This is heuristic: we take anchors in 'div.vsh-home-content' if present,
    otherwise anchors in the container.
    """
    box = container.select_one("div.vsh-home-content") or container
    anchors = box.select("a[href]")

    seen = set()
    nodes = []
    for a in anchors:
        name = a.get_text(strip=True)
        href = normalize_url(a.get("href"))
        if not name or not href:
            continue
        key = (name, href)
        if key in seen:
            continue
        seen.add(key)
        node = make_node(name, href, breadcrumbs + [name])
        nodes.append(node)
    return nodes


def parse_accordion(
    section: Tag, breadcrumbs: list, max_depth: int, depth: int = 0
) -> dict:
    """
    Recursively parse a 'vsh-accordion' section:
    - Create a node for the subcategory
    - Add product leaves (anchors found under the section)
    - Recurse into any *direct child* accordions
    """
    name, url = extract_title_and_link(section)
    node = make_node(name, url, breadcrumbs + [name])

    # Add product leaves under this section
    node["sub_topics"].extend(collect_products(section, node["breadcrumbs"]))

    # Recurse into direct child accordions if depth allows
    if depth < max_depth:
        # Only direct children to avoid re-processing the same section
        children = section.find_all("div", class_="vsh-accordion", recursive=False)
        for child in children:
            child_node = parse_accordion(
                child, node["breadcrumbs"], max_depth, depth + 1
            )
            node["sub_topics"].append(child_node)

    return node


def parse_menu_panel(menu: Tag, max_depth: int) -> dict:
    """
    Parse a top-level menu panel (e.g., Passive Components / Semiconductors):
    - Builds a top-level category node
    - Iterates its top-level accordions (subcategories)
    """
    cat_name, cat_url = extract_title_and_link(menu)
    cat_node = make_node(cat_name, cat_url, [cat_name])

    # Top-level accordions within this menu panel
    subcats = menu.find_all("div", class_="vsh-accordion", recursive=False)
    for acc in subcats:
        sub_node = parse_accordion(acc, cat_node["breadcrumbs"], max_depth, depth=0)
        cat_node["sub_topics"].append(sub_node)

    return cat_node


def scrape_vishay(max_depth: int = 5) -> list[dict]:
    """Main entry: scrape homepage, find mobile menu, parse both product panels recursively."""
    soup = fetch_soup(BASE_URL)

    overlay = soup.select_one("div.vsh-mobile-menu-overlay")
    if not overlay:
        # Fallback: if overlay is not present (JS-driven), return empty result gracefully
        return []

    menus = []
    m1 = overlay.select_one("#ulMobileProdMenu1")
    m2 = overlay.select_one("#ulMobileProdMenu2")
    if m1:
        menus.append(m1)
    if m2:
        menus.append(m2)

    results = []
    for menu in menus:
        try:
            results.append(parse_menu_panel(menu, max_depth=max_depth))
        except Exception as e:
            # Graceful degradation: log and continue with other panels
            print(f"[warn] Failed to parse a menu panel: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Recursively scrape Vishay product structure into JSON."
    )
    parser.add_argument(
        "--out", default="topic_structure_recursive.json", help="Output JSON file path"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum recursion depth for nested accordions",
    )
    args = parser.parse_args()

    data = scrape_vishay(max_depth=args.max_depth)

    # Save JSON
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(data)} top-level categories to {args.out}")


if __name__ == "__main__":
    main()
