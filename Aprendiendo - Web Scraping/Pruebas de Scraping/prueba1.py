
#   Importamos las librerias "requests" y "BeautifulSoup"
import requests
from bs4 import BeautifulSoup

#   h = nombre del user-agent -------  url = url de la pagina a analizar
h = {"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"}
url = "https://www.mercadolibre.com.ar/giorgio-armani-emporio-armani-stronger-with-you-intensely-pour-homme-edp-100ml-para-hombre/p/MLA19312692#polycard_client=search-nordic&wid=MLA1146354756&sid=search&searchVariation=MLA19312692&position=4&search_layout=grid&type=product&tracking_id=236ba1ad-68ba-4635-b6d6-a36870b5bb81"

res = requests.get(url, headers= h)

#   BeautifulSoup('html de la pagina', "html.parser")
soup = BeautifulSoup(res.text, "html.parser")

#   Utilizamos .text para que solo nos muestre el string del html
print(soup.title.text)
print('\n')
#   Utilizamos .strip() para limpiar saltos de linea al final y al principio del string del html
print(soup.find("h1", class_ = "ui-pdp-title").text.strip())


#print(soup.find("span", class_ = "andes-money-amount__currency-symbol").text)
#print(soup.find("span", class_ = "andes-money-amount__fraction").text)
precio = int(soup.find("div", class_ = "ui-pdp-price__second-line").find("span", class_ = "andes-money-amount__fraction").text.replace(".", ""))
print('\n')
print("PRECIO:")
print(soup.find("div", class_ = "ui-pdp-price__second-line").text)
print(precio)

#print('\n')
#masVendido = soup.find("a", class_ = "ui-pdp-promotions-pill-label__target").text
#print("NIVEL DE VENTAS:")
#print(masVendido)

print('\n')
estrellas = soup.find("span", "ui-pdp-review__rating").text
print("ESTRELLAS:")
print(estrellas)

print('\n')
textos = []
elementos = soup.find("div", class_ = "ui-pdp-header__title-container").find_all("a")
for i in elementos:
    textos.append(i.text)

print("NIVEL DE VENTAS: ")
print(textos[0])
print(textos[1])

print('\n')
print("LINK IMAGEN:")
imagen = soup.find("figure", class_= "ui-pdp-gallery__figure").find("img").attrs.get("src")
print(imagen)