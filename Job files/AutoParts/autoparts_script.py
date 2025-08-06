from bs4 import BeautifulSoup
import json
import re
import requests
import pandas as pd


def extract_hardware_numbers_from_description(description):
    """
    Extrae códigos de tipo 'ABC-123' o 'ABC-123A' desde la descripción del producto.

    Args:
        description (str): Texto plano de la descripción.

    Returns:
        str: Lista de códigos separados por comas, sin duplicados.
    """
    if not description:
        return ""

    # Patrón: 3 letras, guion, 3 dígitos, opcionalmente una letra (como A, B, etc.)
    pattern = r'\b[A-Z]{3}-\d{3}[A-Z]?\b'
    matches = re.findall(pattern, description.upper())

    # Eliminar duplicados y ordenar
    unique_matches = sorted(set(matches))
    return ", ".join(unique_matches)


def extract_part_type_from_title(title):
    """
    Extrae un 'Part Type' conocido desde el título del producto, si no se encuentra en la tabla.
    
    Args:
        title (str): Título del producto.
    
    Returns:
        str: Part Type encontrado o cadena vacía si no hay coincidencia.
    """
    part_types = [
        "ACM", "ECM", "Electronic Control Module (ECM)",
        "Engine Control Module (ECM)", "FICM",
        "Fuse Box", "Fuse Box Module",
        "Fuse Box Module [Central Junction]", "Fuse Box Module [Power Distribution Box]",
        "GPCM", "IDM", "Injector", "IPM", "MCM",
        "Motor Control Module [MCM2.1]", "Motor Control Module [MCM2]",
        "PCM", "TCM", "TIPM"
    ]
    
    title_upper = title.upper()

    for part in part_types:
        # Convertimos el part type a mayúsculas y lo buscamos como palabra entera
        pattern = r'\b' + re.escape(part.upper()) + r'\b'
        if re.search(pattern, title_upper):
            return part

    return ""


def get_sku_from_last_word(title):
    last_word = title.strip().split()[-1].upper()  # Última palabra en mayúsculas
    pattern = r'^(?=.*\d)[A-Z0-9-]{5,}$'  # Al menos 5 caracteres, letras/números/guión, y contiene un número
    if re.match(pattern, last_word):
        return last_word
    else:
        last_word = ""
        return last_word

def get_years_from_first_word(title):
    first_word = title.strip().split()[0].upper()  # Primera palabra en mayúsculas
    pattern = r'^\d{4}(-\d{2,4})?$'
    if re.match(pattern, first_word):
        try:
            divition = first_word.split("-")
            if(len(divition) == 2):
                starting_year = divition[0]
                ending_year = int(divition[1])
                if 00 <= ending_year <= 25:
                    ending_year = ending_year + 2000
                else:
                    ending_year = ending_year + 1900
                #ending_year = divition[1]
            else:
                starting_year = first_word
                ending_year = ""
        except:
            starting_year = first_word
            ending_year = ""

        return starting_year, ending_year
    else:
        starting_year = ""
        ending_year = ""
        return starting_year, ending_year

    
def extract_part_numbers(description_html):
    """
    Busca la tabla de 'Interchangeable Part Numbers' dentro del HTML de descripción
    y devuelve una lista de todos los valores encontrados en las celdas.

    Args:
        description_html (str): HTML de la descripción extraído desde bcpo_product["description"]

    Returns:
        list: Lista de part numbers como strings
    """
    soup = BeautifulSoup(description_html, "html.parser")
    part_numbers = []

    # Buscar texto que indique la sección de part numbers
    referencia = soup.find(string=re.compile(r'interchangeable.*part number', re.IGNORECASE))
    if referencia:
        tabla = referencia.find_next("table")
        if tabla:
            for row in tabla.find_all("tr"):
                for td in row.find_all("td"):
                    value = td.get_text(strip=True)
                    if value:
                        part_numbers.append(value)
        else:
            print("❌ Tabla no encontrada después del texto.")
    else:
        print("❌ Texto de referencia no encontrado.")

    return part_numbers

def extract_part_type(value):
    match = re.search(r"\[([A-Z]{2,6})\]", value)
    if match:
        return match.group(1).strip()  # Solo el texto entre corchetes
    else:
        return value.strip()  # Todo el texto si no hay corchetes

def parse_spec_table(description_html):
    new_row = {
    "Make": "",
    "Model": "",
    "Part Number[s]": "",
    "Part Type": "",
    "Engine Size": "",
    "Condition": "",
    "Replacement Number": "",
    "Hardware Number[s]": ""
    }
    soup = BeautifulSoup(description_html, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        return new_row

    specs_table = tables[0]  # Primera tabla (la de especificaciones)


    for row in specs_table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(separator=", ", strip=True)

            match key:
                case "Make":
                    new_row["Make"] = value
                case "Model":
                    if len(value.split()) == 1:
                        new_row["Model"] = value.replace("/", ", ")
                    else:
                        new_row["Model"] = value
                case "Part Number[s]":
                    new_row["Part Number[s]"] = value
                case "Part Type":
                    new_row["Part Type"] = extract_part_type(value)
                case "Engine Size":
                    new_row["Engine Size"] = value
                case "Condition":
                    new_row["Condition"] = value
                case "Replacement Number":
                    new_row["Replacement Number"] = value
                case "Hardware Number[s]":
                    new_row["Hardware Number[s]"] = value.replace("/", ", ")

    return new_row


final_data = []

# URL de la página a analizar
url_princ = "https://filter-v9.globo.io/api/apiFilter?callback=jQuery371012842513601251926_1748282504342&filter_id=3955&shop=goecm.myshopify.com&collection=201902555285&sort_by=title-ascending&country=AR&limit=250&page=5&event=init&cid=13127598-9091-46ca-9aa3-070e58201133&did=16ede793-851c-4a90-a28a-7d89c87a4e7b&page_type=collection&ncp=1185"  # Reemplazá con la URL real

# Obtener HTML desde la URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
}

response = requests.get(url_princ, headers=headers)

finish_url =[]

if response.status_code == 200:
    data = "{" + response.text.split("({")[-1].replace(");","")
    data = json.loads(data)
    for product in data["products"]:
        handle = product["handle"]
        finish_url.append(handle)
else:
    print(f"Error: {response.status_code}")

urls = []

for finish in finish_url:
    urls.append(f"https://goecm.com/products/{finish}")

# for url in urls:
#     print(url)

for url in urls:
    response1 = requests.get(url, headers=headers)
    html = response1.text
    soup = BeautifulSoup(html, "html.parser")
    # if response1.status_code == 200:
    #     data_product = "{" + response1.text.split("bcpo_product={")[1].split("};")[0] + "}"#.replace("};","}")
    #     #TURN DATA_PRODUCT TO JSON
    #     data_product = json.loads(data_product)
    description = soup.select_one("h1.h2.product-single__title").text.strip()
    sku = get_sku_from_last_word(description)
    #print(description)
    #print(sku)
    starting_year = get_years_from_first_word(description)[0]
    ending_year = get_years_from_first_word(description)[1]
    #print(starting_year)
    #print(ending_year)
    try:
        price = soup.select_one("span.product__price").text.strip()
    except:
        price = ""
    #print(price)
    try:
        stock = soup.select_one("ul.sales-points").text
        stock = ' '.join(stock.split()).strip()
    except:
        stock = "No stock information available"
    #print(stock)

    # url = "https://goecm.com/products/dodge-ram-pickup-5-9l-ecm-56027300"

    # 1. Extraer contenido crudo de `bcpo_product`
    data_product = "{" + html.split("bcpo_product={")[1].split("};")[0] + "}"
    data_product = json.loads(data_product)
    description_html = data_product["description"]

    # 2. Extraer la primera tabla (especificaciones)
    new_row  = parse_spec_table(description_html)
    if new_row["Part Type"] == "":
        try:
            new_row["Part Type"] = extract_part_type_from_title(description)
        except:
            print("No se encontro el Part Type en la Descripcion")
    if new_row["Hardware Number[s]"] == "":
        try:
            new_row["Hardware Number[s]"] = extract_hardware_numbers_from_description(description)
        except:
            print("No se encontro el Hardware Number[s] en la Descripcion")
    # 3. Extraer la segunda tabla (part numbers)
    part_numbers = extract_part_numbers(description_html)

    # Combinar todos los datos en un solo diccionario
    new_row.update({
        "Heading SKU": sku,
        "Starting Year": starting_year,
        "Ending Year": ending_year,
        "Price": price,
        "Stock": stock,
        "Description": description,
        "Interchangable Part Numbers": ", ".join(part_numbers)
    })

    final_data.append(new_row)

    # 4. Mostrar resultados    
    print("\n🧾 Fila completa:")
    for k, v in new_row.items():
        print(f"{k}: {v}")

filename = f"auto_parts_modif.xlsx"
column_order = [
    "Heading SKU", "Part Number[s]", "Hardware Number[s]",
    "Starting Year", "Ending Year", "Make", "Model",
    "Price", "Stock", "Part Type", "Engine Size",
    "Condition", "Replacement Number", "Description",
    "Interchangable Part Numbers"
]   
df = pd.DataFrame(final_data)[column_order]
df.to_excel(filename, index=False)
        # print("📋 Especificaciones:")
        # #print(new_row)
        # for k, v in new_row.items():
        #     print(f"  {k}: {v}")
        # print("\n🔧 Part Numbers:")
        # print(", ".join(part_numbers))
