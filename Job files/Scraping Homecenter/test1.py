import requests
import json
import pandas as pd

url = "https://www.homecenter.com.co/homecenter-co/category/cat740127/cerraduras-inteligentes-y-digitales/"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8,fr;q=0.7",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
}

cookies = {
    "__CO_exp": "comCo-23",
    "experience": "CATALYST",
    "__cf_bm": "ji52NqP60uglcn_WdNi_cl8LbfdazzEOA.ZTIcsyca8-1757948547-1.0.1.1-QEHDtd2M0vY5UuMZn.O1saiYSevK7bcMaEcB.ajw3eHWnrPL7zOO5p9XoVOt.K4uyOMs4KEInV05F5cOirTnxq7UQEZpXU_EZ7g16Ax.wDw",
    "_cfuvid": "3ZL_Kw7B66h1ypYKEBYBxRQ9D1vcsSsCbk9ngALp6mM-1757948547337-0.0.1.1-604800000",
    # ⚠️ Aquí deberías seguir pegando el resto de cookies que están en tu curl
    # He dejado cortado para no sobrecargar el ejemplo, pero simplemente las pasas igual que en el curl
}

response = requests.get(url, headers=headers, cookies=cookies)

print(response.status_code)

data = response.text.split('"itemOffered":')[1].split("]")[0] + "\n]"
print(data)
data = json.loads(data)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

#Export to CSV
df = pd.json_normalize(data)
df.to_csv("data.csv", index=False)