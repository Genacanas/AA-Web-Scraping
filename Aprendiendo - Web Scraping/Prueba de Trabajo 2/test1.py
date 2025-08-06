import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import os
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# =============================
# 0️⃣  Función para append al Excel
# =============================
def append_to_excel(path, df_batch):
    try:
        wb = load_workbook(path)
        ws = wb.active
        for r in dataframe_to_rows(df_batch, index=False, header=False):
            ws.append(r)
    except FileNotFoundError:
        df_batch.to_excel(path, index=False)
    else:
        wb.save(path)

# =============================
# 1️⃣  Leer Excel de direcciones
# =============================
def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df['property address'].tolist()

# =============================
# 2️⃣  Llamada principal a la API (manejo de status manual)
# =============================
def scrape_api_data(address):
    formatted = address.replace(" ", "%20").lower()
    url = (
        "https://www.bcpao.us/api/v1/search?"
        f"address={formatted}&activeonly=true"
        "&sortcolumn=siteaddress&sortorder=asc&size=10&page=1"
    )
    headers = {
        'User-Agent': 'TU_USER_AGENT',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bcpao.us/',
        'Origin': 'https://www.bcpao.us'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"  ❌ Conexión fallida (principal): {e}")
        return None

    if resp.status_code != 200:
        print(f"  ❌ Principal: status={resp.status_code}")
        return None

    data = resp.json()
    if not data:
        print(f"  ⚠️ Principal: sin resultados para '{address}'")
        return None

    d = data[0]
    return {
        "Account":        d.get("account"),
        "Owners":         d.get("owners"),
        "Mail Address":   d.get("mailAddress"),
        "Site Address":   d.get("siteAddress"),
        "Parcel ID":      d.get("parcelID"),
        "Property Use":   d.get("landUseCode"),
        "Market Value":   d.get("marketValue"),
        "Year Built":     d.get("yearBuilt"),
        "Last Sale Date": d.get("saleDate"),
        "Last Sale Price":d.get("salePrice"),
    }

# =============================
# 2.5️⃣  Fallback (size=1)
# =============================
def scrape_api_data_error(address):
    formatted = address.replace(" ", "%20").lower()
    url = (
        "https://www.bcpao.us/api/v1/search?"
        f"address={formatted}&activeonly=true"
        "&sortcolumn=siteaddress&sortorder=asc&page=1&size=1"
    )
    headers = {
        'User-Agent': 'TU_USER_AGENT',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bcpao.us/',
        'Origin': 'https://www.bcpao.us'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"  ❌ Conexión fallida (fallback): {e}")
        return None

    if resp.status_code != 200:
        print(f"  ❌ Fallback: status={resp.status_code}")
        return None

    data = resp.json()
    if not data:
        print(f"  ⚠️ Fallback: sin resultados para '{address}'")
        return None

    d = data[0]
    return {
        "Account":        d.get("account"),
        "Owners":         d.get("owners"),
        "Mail Address":   d.get("mailAddress"),
        "Site Address":   d.get("siteAddress"),
        "Parcel ID":      d.get("parcelID"),
        "Property Use":   d.get("landUseCode"),
        "Market Value":   d.get("marketValue"),
        "Year Built":     d.get("yearBuilt"),
        "Last Sale Date": d.get("saleDate"),
        "Last Sale Price":d.get("salePrice"),
    }

# =============================
# 3️⃣  Scrape de detalles con Playwright
# =============================
def scrape_property_details(account):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)
        page.goto(f"https://www.bcpao.us/PropertySearch/#/account/{account}")
        try:
            page.wait_for_selector("table#tSalesTransfers", timeout=10000, state="attached")
        except:
            pass
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    detalles = soup.select("div.cssDetails_Top_Cell_Data")
    site_code = detalles[8].get_text(strip=True) if len(detalles) > 8 else None
    land_desc = detalles[11].get_text(strip=True) if len(detalles) > 11 else None

    sales = []
    tbl = soup.select_one("table#tSalesTransfers")
    if tbl:
        for row in tbl.select("tbody tr"):
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 2:
                sales.append({"Date": cols[0], "Price": cols[1]})

    return {
        "Site Code":        site_code,
        "Land Description": land_desc,
        # convertimos a string JSON para Excel
        "Sales":            json.dumps(sales, ensure_ascii=False)
    }

# =============================
# 4️⃣  Función principal
# =============================
def main(file_path):
    print("Directorio:", os.getcwd())
    addresses = read_excel(file_path)
    batch = []
    out_path = "resultados_scraping.xlsx"

    for address in addresses:
        print(f"Procesando: {address}")
        api_data = scrape_api_data(address) or scrape_api_data_error(address)
        if not api_data or "Account" not in api_data:
            print("  ❌ Sin datos tras ambos intentos, salto.")
            continue

        details = scrape_property_details(api_data["Account"])
        combined = {**api_data, **details}
        batch.append(combined)

        if len(batch) >= 5:
            df_batch = pd.DataFrame(batch)
            append_to_excel(out_path, df_batch)
            print(f"  ✅ Se guardaron 5 registros en '{out_path}'")
            batch.clear()

    if batch:
        df_batch = pd.DataFrame(batch)
        append_to_excel(out_path, df_batch)
        print(f"  ✅ Se guardaron los {len(batch)} registros finales en '{out_path}'")

    print("✅ Proceso completo.")

# =============================
# 5️⃣  Ejecutar
# =============================
if __name__ == "__main__":
    main(r"Trabajo2\excel_property_address.xlsx")
