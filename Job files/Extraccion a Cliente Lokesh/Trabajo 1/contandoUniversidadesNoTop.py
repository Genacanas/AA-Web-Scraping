from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import pandas as pd
import os

ua = UserAgent()
filename = "array_data.xlsx"
filename2 = "data_buffer.xlsx"
data = []
data_buffer = []

def scroll_gradualmente_hasta_pixels(page, target_pixels, step=500, delay=0.5, max_intentos=50):
    intentos = 0
    while intentos < max_intentos:
        current_scroll = page.evaluate("() => window.pageYOffset")
        print(f"Posición actual: {current_scroll} pixeles")

        if current_scroll >= target_pixels:
            print(f"✅ Se alcanzó el objetivo de {target_pixels} pixeles.")
            return

        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        new_scroll = page.evaluate("() => window.pageYOffset")
        if new_scroll == current_scroll:
            intentos += 1
            print(f"Sin cambio en el scroll. Intento {intentos}/{max_intentos}.")
        else:
            intentos = 0

    print(f"⚠️ Se agotaron los intentos sin alcanzar {target_pixels} pixeles.")

def scroll_gradualmente_hasta_el_final(page, step=500, delay=0.5, max_intentos=50):
    intentos = 0
    last_scroll_height = 0

    while intentos < max_intentos:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        current_scroll_height = page.evaluate("document.body.scrollHeight")

        if current_scroll_height == last_scroll_height:
            intentos += 1
        else:
            intentos = 0

        last_scroll_height = current_scroll_height

    print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

def scroll_y_click_load_more(page, step=500, delay=1, max_intentos=50):
    intentos = 0
    last_scroll_height = page.evaluate("document.body.scrollHeight")

    while intentos < max_intentos:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        try:
            button = page.query_selector("div.load-more-container")
            if button:
                button.click()
                time.sleep(delay)
                print("🟢 Botón clickeado.")
        except Exception as e:
            print(f"⚠️  Error al intentar clickear el botón: {e}")

        current_scroll_height = page.evaluate("document.body.scrollHeight")
        if current_scroll_height == last_scroll_height:
            intentos += 1
        else:
            intentos = 0
        last_scroll_height = current_scroll_height

    print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
        page = context.new_page()

        page.goto("https://www.shiksha.com/engineering/ranking/top-engineering-colleges-in-india/44-2-0-0-0")
        page.wait_for_timeout(1000)

        scroll_y_click_load_more(page)

        page.wait_for_timeout(3000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        name_universities = soup.find_all("h4", class_="f14_bold link")
        name_U = [name.text for name in name_universities]

        print(f"Nombres extraidos {name_U}")

        titles = soup.find_all("a", class_="rank_clg ripple dark")
        universities = [title.attrs.get("href") for title in titles]
        print(f"Universidades extraidas {universities}")

        name_U = name_U[95:]  # si querés omitir los primeros
        universities = universities[95:]

        for k, university in enumerate(universities):
            url_university = f'https://www.shiksha.com{university}'
            print(f"Entro a la universidad {url_university}")
            context.close()
            context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
            page = context.new_page()
            page.goto(url_university)
            scroll_gradualmente_hasta_pixels(page, 3000, step=1500, delay=0.075)
            page.wait_for_selector("a._59a5._5a11.ripple.dark")
            html_university = page.content()
            soup_u = BeautifulSoup(html_university, "html.parser")
            view_allFaculty = soup_u.select_one("a._59a5._5a11.ripple.dark").attrs.get("href")
            url_viewallFaculty = f'https://www.shiksha.com{view_allFaculty}'

            print(f"Entro a ver todas las facultades {url_viewallFaculty}")
            context.close()
            context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
            page = context.new_page()
            page.goto(url_viewallFaculty)
            scroll_gradualmente_hasta_el_final(page, step=1500, delay=0.075)
            html_VAfaculty = page.content()
            soup_VAf = BeautifulSoup(html_VAfaculty, "html.parser")

            text_numberFaculties = soup_VAf.find("div", class_="_793c").find("strong").text
            numberFaculties = int(''.join(filter(str.isdigit, text_numberFaculties)))
            box_faculties = soup_VAf.find_all("div", class_="_8165")[:numberFaculties]

            for box_faculty in box_faculties:
                url_faculty = box_faculty.select_one("a.ripple.dark").attrs.get("href")
                url_faculty = f'https://www.shiksha.com{url_faculty}'
                print(f"Entro a la faculty {url_faculty}")
                context.close()
                context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                page = context.new_page()
                page.goto(url_faculty)
                scroll_gradualmente_hasta_el_final(page, step=1500, delay=0.075)
                html_faculty = page.content()
                soup_c = BeautifulSoup(html_faculty, "html.parser")

                box_course = soup_c.find_all("div", class_="_8165")

                for box in box_course:
                    try:
                        seats_text = box.select_one("label.abce").text
                        fee_text = box.select_one("div._77ff label.abce").text
                        seats = box.find("div", class_="dcfd undefined").text
                    except:
                        continue

                    seats_offered = int(''.join(filter(str.isdigit, seats))) if "Seats Offered" in seats_text else "No seats available"

                    try:
                        fees = box.select_one("div.dcfd.undefined").text
                    except:
                        fees = "No fees available"

                    try:
                        course = box.find("div", class_="c8ff").find("a").attrs.get("href")
                    except:
                        continue

                    url_course = f'https://www.shiksha.com{course}'
                    print(f"Entro a la course {url_course}")
                    context.close()
                    context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                    page = context.new_page()
                    page.goto(url_course)
                    html_course = page.content()
                    soup_c = BeautifulSoup(html_course, "html.parser")

                    course_name = soup_c.find("div", class_="_11113e").text
                    try:
                        duration = soup_c.find("span", class_="_22a5").text
                    except:
                        duration = "Duration not found"

                    menu_items = soup_c.select("ul.cd4637.navbarSlider a.listItem.ripple.dark")
                    admissions = None
                    for item in menu_items:
                        if "Admissions" in item.text:
                            admissions = item.get("href")
                            break

                    if admissions:
                        try:
                            url_admissions = f'https://www.shiksha.com{admissions}'
                            print(f"Entro a admissions {url_admissions}")
                            context.close()
                            context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                            page = context.new_page()
                            page.goto(url_admissions)
                            scroll_gradualmente_hasta_pixels(page, 2000, step=1000, delay=0.075)
                            html_adm = page.content()
                            soup_a = BeautifulSoup(html_adm, "html.parser")
                            elegibility_criteria = soup_a.find("ul", class_="c2fa").text
                        except:
                            elegibility_criteria = "No eligibility criteria available"
                    else:
                        elegibility_criteria = "No eligibility criteria available"

                    new_row = {
                        "University Name": name_U[k],
                        "Course Name": course_name,
                        "Duration": duration,
                        "Seat breakup": seats_offered,
                        "Total Tuition Fee": fees,
                        "Eligibility Criteria": elegibility_criteria
                    }
                    print(f"New row {new_row}")
                    data.append(new_row)
                    data_buffer.append(new_row)

                    if len(data_buffer) >= 10:
                        new_df = pd.DataFrame(data_buffer)
                        if os.path.exists(filename2):
                            existing_df = pd.read_excel(filename2)
                            final_df = pd.concat([existing_df, new_df], ignore_index=True)
                        else:
                            final_df = new_df
                        final_df.to_excel(filename2, index=False)
                        data_buffer = []

        if data_buffer:
            new_df = pd.DataFrame(data_buffer)
            if os.path.exists(filename2):
                existing_df = pd.read_excel(filename2)
                final_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                final_df = new_df
            final_df.to_excel(filename2, index=False)
            print("✅ Datos restantes en buffer guardados exitosamente.")

# Ejecutar
scrape()
