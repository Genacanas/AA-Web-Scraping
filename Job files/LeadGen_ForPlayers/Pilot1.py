import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

url = "https://www.rugbyalberta.com/findaclub/"


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://www.rugbyalberta.com/clubprofile/61601/",
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
    "_ga": "GA1.1.1477819657.1756237778",
    "_ga_6XTX5S9WVJ": "GS2.1.s1756254317$o2$g1$t1756254317$j60$l0$h0",
    "_ga_0YZGFT6BCZ": "GS2.1.s1756254317$o2$g1$t1756254317$j60$l0$h0",
}

response = requests.get(url, headers=headers, cookies=cookies)

# response.text.split("= [{")[1].split(", searchClub);")[0]
dataJson = json.loads("[{" + response.text.split("= [{")[1].split("}];")[0] + "}]")
# data = "[{" + response.text.split("= [{")[1].split("}];")[0] + "}]"#.replace("}];", "}]")
# html = data
# soup = BeautifulSoup(html, "html.parser")
# print(soup)

final_data = []

for item in dataJson:
    final_data.append(
        {
            "ClubName": item["clubName"],
            "Phone": item["mobile"],
            "Email": item["email"],
            "Website": item["webAddress"],
            "instagram": item["instagram_url"],
            "facebook": item["facebook_url"],
            "twitter": item["twitter_url"]
        }
    )


df = pd.DataFrame(final_data)
df.to_excel("RugbyClubs.xlsx", index=False)
