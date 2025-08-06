from bs4 import BeautifulSoup
import json
import pandas as pd
import requests
#   patmJWBOkywPqsKsx.6ae8dc7a7ea7ac085c231f2eb5b3d4b02d41c93db02fa4c446f49d3e3f09dc90

b = "https://valarie59522.softr.app/v1/datasource/airtable/cdc75747-e8b8-495f-96c5-27f009e90324/d5355337-db49-48bb-a886-4f5721dd38cd/e36fd3ce-da25-441d-84f0-b023973a5d87/2bff462b-d25b-4956-862c-46fe357bb701/data/"

# ---------- 1) Configuración fija ----------

h = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://valarie59522.softr.app",
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
    # Si tu cURL llevaba cookies que hagan falta:
    # "Cookie": "softr_jwt=...; softr_workspace=..."
}
p = {
    "options": {"cellFormat": "string", "timeZone": "UTC", "userLocale": "en-US"},
    "pageContext": None,
    "filterCriteria": {}
}

# https://valarie59522.softr.app/v1/datasource/airtable/cdc75747-e8b8-495f-96c5-27f009e90324/fe788800-6da8-4081-b534-a1d92972994c/84431ac5-c46d-41e5-910c-214a623c2ff2/08a48fe6-588a-40a4-857f-5aff8ae0f7c8/data/
#--- 1) URL --------------------------------------------------------------------
url = ("https://valarie59522.softr.app/v1/datasource/airtable/"
       "cdc75747-e8b8-495f-96c5-27f009e90324/"
       "fe788800-6da8-4081-b534-a1d92972994c/"
       "84431ac5-c46d-41e5-910c-214a623c2ff2/"
       "08a48fe6-588a-40a4-857f-5aff8ae0f7c8/data/")

#--- 2) Payload (igual al --data-raw) -----------------------------------------
payload = {
    "options":      {"cellFormat": "string", "timeZone": "UTC", "userLocale": "en-US"},
    "pageContext":  None,
    "filterCriteria": {},
    "pagingOption": {"offset": None, "count": 100},
    "sortingOption": {"sortingField": "H+T Sort", "sortType": "ASC"}
}

#--- 3) Encabezados mínimos que el backend realmente usa ----------------------
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://valarie59522.softr.app",
    "Referer": ("https://valarie59522.softr.app/embed/pages/"
                "fe788800-6da8-4081-b534-a1d92972994c/blocks/spkr-grid1"),
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"),
}

# --- 4) Petición ---------------------------------------------------------------


#print(json.dumps(data, indent=2, ensure_ascii=False))
#print(data["offset"])
fullData = []
while True:
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()        # lanza excepción si no es 2xx
    data = resp.json()             # dict / list con tu JSON
    for record in data["records"]:

        specific_url = b + record["id"]
        r = requests.post(specific_url, headers=h, json=p, timeout=30)
        #print(r.json())
        specific_data = r.json()
        #print(specific_data["records"][0]["fields"]["Pers LinkedIn"])
        try:
            linkedIn = specific_data["records"][0]["fields"]["Pers LinkedIn"]
        except:
            linkedIn = "No LinkedIn link available"
            
        title = record["fields"]["Role"]
        if title == "":
            title = "No Title available"

        new_data = {
        "id": record["id"],
        "Name": record["fields"]["Full Name"],
        "Title": title,
        "LinkedIn": linkedIn
        }
        print(new_data)
        fullData.append(new_data)
    
    if data["offset"] == None:
        print(data["offset"])
        break
    else:
        print(payload["pagingOption"]["offset"])
        payload["pagingOption"]["offset"] = data["offset"]
        print(payload["pagingOption"]["offset"])

#print(fullData)
filename = "speakers.xlsx"
df = pd.DataFrame(fullData)
df.to_excel(filename, index=False)







# # ---------- 2) Supongamos que ya tienes la lista de recordId -------------
# record_ids = ["reckAjLJfYacigZLE", "recxSm8FhNS0vUz15"]  # …añade los que obtuviste

# # ---------- 3) Bucle para pedir el detalle de cada persona ---------------
# details = {}

# for rec_id in record_ids:
#     urln = b + rec_id
#     r = requests.post(urln, headers=h, json=p, timeout=30)
#     r.raise_for_status()
#     details[rec_id] = r.json()          # guarda la respuesta completa

# # ---------- 4) Ahora `details` tiene los JSON de cada persona ------------
# print(json.dumps(details, indent=2, ensure_ascii=False))

