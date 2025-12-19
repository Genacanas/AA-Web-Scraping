from bs4 import BeautifulSoup
import json
import re
import requests
import sys  # Used here to set console encoding on Windows

sys.stdout.reconfigure(encoding="utf-8")

# URL de la página a analizar
url_princ = "https://bucco.com.ar"  # Reemplazá con la URL real

# Obtener HTML desde la URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
}
response = requests.get(url_princ, headers=headers)
print(response.status_code)
#print(response.text) 

html = response.text
soup = BeautifulSoup(html, "html.parser")

print(soup.select("li.footer-menu-item")[-2])