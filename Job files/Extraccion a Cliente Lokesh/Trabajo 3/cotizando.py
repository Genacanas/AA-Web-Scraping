import requests
from bs4 import BeautifulSoup

cookies = {
    'ASP.NET_SessionId': 'moqjodkfl4fmqaxm3w2iwojh',
    'GlobalOpportunities': 'admin_userid=195&counsellor_id=shiksha&access=Agent Incoming&email=shiksha@global-opportunities.net',
    'GlobalOppurtunitiesABO': 'ABO_admin_userid=195&ABO_counsellor_id=shiksha&ABO_access=Agent Incoming&ABO_email=shiksha@global-opportunities.net&ABO_user_type=ABO'
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
}

url = "https://gopagent.global-opportunities.co.in/Registration_details.aspx?id=2755885"


#response = requests.get(url, headers= headers, cookies= cookies)
session = requests.Session()

# Paso 1: Obtener tokens necesarios (como __VIEWSTATE, etc.)
login_page = session.get("https://gopagent.global-opportunities.co.in/Default.aspx")
soup = BeautifulSoup(login_page.text, 'html.parser')
viewstate = soup.select_one("#__VIEWSTATE")["value"]
event_validation = soup.select_one("#__EVENTVALIDATION")["value"]

# Paso 2: Simular login
payload = {
    "__VIEWSTATE": viewstate,
    "__EVENTVALIDATION": event_validation,
    "__VIEWSTATEGENERATOR": soup.select_one("#__VIEWSTATEGENERATOR")["value"],
    "txt_username": "shiksha",
    "txt_password": "shiksha123",
    "ImageButton1.x": "0",  # Necesario para emular clic en botón imagen
    "ImageButton1.y": "0",
}

login_headers = {
    "User-Agent": headers["User-Agent"],
    "Content-Type": "application/x-www-form-urlencoded"
}

response = session.post("https://gopagent.global-opportunities.co.in/Default.aspx", data=payload, headers=login_headers)

# Paso 3: Ir a la URL protegida
protected = session.get("https://gopagent.global-opportunities.co.in/Registration_details.aspx?id=2755885")

print("Status code:", protected.status_code)
print(protected.text)


ids = [2755885, 2755884, 2755883]  # los IDs que quieras
for id_ in ids:
    url = f"https://gopagent.global-opportunities.co.in/Registration_details.aspx?id={id_}"
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    nombre = soup.select_one('#lbl_FirstName')
    email = soup.select_one('#lbl_email')
    
    print(f"ID: {id_}")
    print("Nombre:", nombre.text.strip() if nombre else "No encontrado")
    print("Email:", email.text.strip() if email else "No encontrado")
    print("-" * 40)

# print("Status code: ", response.status_code)
# print("Contenido: ")
# print(response.text)

