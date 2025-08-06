import json
import requests
from bs4 import BeautifulSoup
import re



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

# URL de la página a analizar
url_princ = "https://filter-v9.globo.io/api/apiFilter?callback=jQuery371043414669521343896_1747917080279&filter_id=3955&shop=goecm.myshopify.com&collection=201902555285&sort_by=title-ascending&country=AR&limit=250&event=init&cid=13127598-9091-46ca-9aa3-070e58201133&did=16ede793-851c-4a90-a28a-7d89c87a4e7b&page_type=collection&ncp=1183"  # Reemplazá con la URL real

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
        #title = product.get("title")
        handle = product["handle"]
        finish_url.append(handle)
        #title = product["title"]
        #tags = product.get("tags")
        #price = product["variants"][0].get("price")
        #image = product.get("image", {}).get("src")

        #print(f"Producto: {title}")
        #print(finish_url)
        #print(f"Handle: {handle}")
        #print(f"Tags: {tags}")
        #print(f"Precio: {price}")
        #print(f"Imagen: {image}")
        #print("-" * 30)
else:
    print(f"Error: {response.status_code}")

urls = []

for finish in finish_url:
    urls.append(f"https://goecm.com/products/{finish}")

# for url in urls:
#     print(url)


for url in urls:
    response1 = requests.get(url, headers=headers)
    soup = BeautifulSoup(response1.text, "html.parser")
    # if response1.status_code == 200:
    #     data_product = "{" + response1.text.split("bcpo_product={")[1].split("};")[0] + "}"#.replace("};","}")
    #     #TURN DATA_PRODUCT TO JSON
    #     data_product = json.loads(data_product)
    description = soup.select_one("h1.h2.product-single__title").text.strip()
    sku = get_sku_from_last_word(description)
    print(description)
    print(sku)
    starting_year = get_years_from_first_word(description)[0]
    ending_year = get_years_from_first_word(description)[1]
    print(starting_year)
    print(ending_year)
    try:
        price = soup.select_one("span.product__price").text.strip()
    except:
        price = ""
    print(price)
    try:
        stock = soup.select_one("ul.sales-points").text
        stock = ' '.join(stock.split()).strip()
    except:
        stock = "No stock information available"
    print(stock)

    
