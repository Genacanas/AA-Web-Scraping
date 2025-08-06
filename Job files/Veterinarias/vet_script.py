import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# URL de la página a analizar
url_princ = "https://redveterinaria.com.ar/wp-admin/admin-ajax.php"  # Reemplazá con la URL real

# Obtener HTML desde la URL
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
# }
headers = {
    "accept": "*/*",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://redveterinaria.com.ar",
    "referer": "https://redveterinaria.com.ar/en/cordoba/?utm_source=chatgpt.com",
    "sec-ch-ua": '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
    "x-requested-with": "XMLHttpRequest"
}
cookies = {
    "cmplz_banner-status": "dismissed"
}
datos = []
for i in range(1,15):
    data = f"0=1&1=1&2=1&title=&post_type=gd_place&category=4&related_to=&tags=&post_author=&category_title=&sort_by=az&title_tag=h2&list_order=&post_limit=30&post_ids=&layout=3&listing_width=&add_location_filter=1&character_count=20&show_featured_only=0&show_special_only=0&with_pics_only=0&with_videos_only=0&show_favorites_only=0&favorites_by_user=&use_viewing_post_type=0&use_viewing_term=0&hide_if_empty=0&view_all_link=0&with_pagination=1&top_pagination=0&bottom_pagination=1&pagination_info=&template_type=&tmpl_page=&tmpl_part=&skin_id=&skin_column_gap=&skin_row_gap=&column_gap=&row_gap=&card_border=&card_shadow=&bg=&mt=&mb=3&mr=&ml=&pt=&pb=&pr=&pl=&border=&rounded=&rounded_size=&shadow=&with_carousel=&with_controls=&with_indicators=&slide_interval=5&slide_ride=&center_slide=&widget_title_tag=&widget_title_size_class=&widget_title_align_class=&widget_title_color_class=&widget_title_border_class=&widget_title_border_color_class=&widget_title_mt_class=&widget_title_mr_class=&widget_title_mb_class=&widget_title_ml_class=&widget_title_pt_class=&widget_title_pr_class=&widget_title_pb_class=&widget_title_pl_class=&nearby_gps=0&indicators_mb=&css_class=loop_principal&is_open=&country=&region=&city=&neighbourhood=&posts_per_page=30&is_geodir_loop=1&gd_location=1&order_by=az&distance_to_post=0&pageno={i}&is_gd_author=0&excerpt_length=20&tax_query[0][taxonomy]=gd_placecategory&tax_query[0][field]=id&tax_query[0][terms][]=4&count_only=0&set_query_vars[pagename]=en&set_query_vars[region]=cordoba&set_query_vars[gd_is_geodir_page]=true&set_query_vars[tax_query][0][taxonomy]=gd_placecategory&set_query_vars[tax_query][0][field]=id&set_query_vars[tax_query][0][terms][]=4&action=geodir_widget_listings&security=0b7577c882"

    response = requests.post(url_princ, headers=headers, cookies=cookies, data=data)
    print(response.status_code)
    print(f"hecha la response {i}")
    html = response.json()["data"]["content"]
    soup = BeautifulSoup(html, "html.parser")
    
    boxes = soup.select("div.card-body.p-2.pe-2.ps-2")

    for box in boxes:
        nombre = box.select_one("div.geodir-post-title.bsui.sdel-3decc927").text
        print(nombre)
        direccion = box.select_one("div.direccion").text
        print(direccion)
        telefono = box.select_one("div.phone_info").text
        print(telefono)
        datos.append({
            "nombre": nombre,
            "direccion": direccion,
            "telefono": telefono
        })
        print(datos)

filename = "tel_vet.xlsx"
df = pd.DataFrame(datos)
df.to_excel(filename, index=False)