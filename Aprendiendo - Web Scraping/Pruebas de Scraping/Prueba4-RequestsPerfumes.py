import requests
from bs4 import BeautifulSoup 
import pandas as pd

h = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"}
url = "https://listado.mercadolibre.com.ar/stronger-with-you#D[A:stronger%20with%20you,L:undefined]"

res1 = requests.get(url, headers=h)
soup1 = BeautifulSoup(res1.text, "html.parser")

#print(soup.find("h2", class_="poly-box poly-component__title").find("a").attrs.get("href"))

endpoints = soup1.find_all("h2", class_="poly-box poly-component__title")

endpoint = []
for i in endpoints:
    endpoint.append(i.find("a").attrs.get("href"))

#for j in endpoint:
    #print(j)
#print(endpoints[1].find("a").attrs.get("href"))
#print(endpoints)
datos =[]
res = []

for enlace in endpoint:
    res = requests.get(enlace, headers=h)
    soup = BeautifulSoup(res.text, "html.parser")
    imagen = soup.find("figure", class_="ui-pdp-gallery__figure").find("img").attrs.get("src")
    precio = soup.find("span", class_="andes-money-amount__fraction").text
    datos.append({"Precio": precio, "Imagen": imagen})

df = pd.DataFrame(datos)
df.to_csv("Perfumes.csv", index=False)
df.to_excel("Perfumes.xlsx", index=False, engine='openpyxl')