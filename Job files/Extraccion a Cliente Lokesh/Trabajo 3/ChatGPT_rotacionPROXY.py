import requests
from bs4 import BeautifulSoup
import time

# Datos del proxy de DataImpulse (puede variar)
PROXY_HOST = "proxy.dataimpulse.com"
PROXY_PORT = "8000"
PROXY_USER = "your_username"
PROXY_PASS = "your_password"

def get_proxy():
    return {
        "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
        "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    }

# Número de requests antes de cambiar de proxy (recomendado: cada 50-100 requests)
ROTATE_EVERY = 100

def start_scraper(ids):
    session = requests.Session()
    session.proxies.update(get_proxy())  # primer proxy

    # Obtener tokens de login
    login_page = session.get("https://gopagent.global-opportunities.co.in/Default.aspx")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    viewstate = soup.select_one("#__VIEWSTATE")["value"]
    event_validation = soup.select_one("#__EVENTVALIDATION")["value"]
    viewstate_generator = soup.select_one("#__VIEWSTATEGENERATOR")["value"]

    payload = {
        "__VIEWSTATE": viewstate,
        "__EVENTVALIDATION": event_validation,
        "__VIEWSTATEGENERATOR": viewstate_generator,
        "txt_username": "shiksha",
        "txt_password": "shiksha123",
        "ImageButton1.x": "0",
        "ImageButton1.y": "0",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Login
    response = session.post("https://gopagent.global-opportunities.co.in/Default.aspx", data=payload, headers=headers)
    print("Login:", response.status_code)

    for i, id_ in enumerate(ids):
        if i > 0 and i % ROTATE_EVERY == 0:
            # Rotamos el proxy
            print(f"Rotando proxy después de {i} requests...")
            session.proxies.update(get_proxy())
            time.sleep(3)  # Opcional: espera pequeña tras rotar

        url = f"https://gopagent.global-opportunities.co.in/Registration_details.aspx?id={id_}"
        try:
            r = session.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')

            nombre = soup.select_one('#lbl_FirstName')
            email = soup.select_one('#lbl_email')

            print(f"ID: {id_}")
            print("Nombre:", nombre.text.strip() if nombre else "No encontrado")
            print("Email:", email.text.strip() if email else "No encontrado")
            print("-" * 40)
        except requests.exceptions.RequestException as e:
            print(f"Error con ID {id_}: {e}")
            continue

# Lista simulada de IDs
ids = list(range(2755885, 2755885 - 60000, -1))
start_scraper(ids)
