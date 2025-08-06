from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent
ua = UserAgent()
import asyncio
from playwright.async_api import Page


def scroll_by_pixels(page, pixels, delay=0.5):
    """
    Realiza scroll vertical bajando una cantidad específica de píxeles.

    :param page: Página de Playwright.
    :param pixels: Número de píxeles a desplazar verticalmente.
    :param delay: Tiempo de espera en segundos tras el scroll (opcional).
    """
    page.evaluate(f"window.scrollBy(0, {pixels});")
    time.sleep(delay)

def scroll_gradualmente_hasta_pixels(page, target_pixels, step=500, delay=0.5, max_intentos=50):
    """
    Realiza scroll gradual bajando de a 'step' pixeles hasta que se alcance o supere target_pixels.
    
    :param page: Objeto de la página de Playwright.
    :param target_pixels: Cantidad de pixeles hasta la cual se desea hacer scroll.
    :param step: Cantidad de pixeles que se desplaza en cada iteración.
    :param delay: Tiempo de espera entre iteraciones.
    :param max_intentos: Número máximo de intentos en caso de que el scroll no avance.
    """
    intentos = 0

    while intentos < max_intentos:
        current_scroll = page.evaluate("() => window.pageYOffset")
        print(f"Posición actual: {current_scroll} pixeles")

        # Si ya alcanzamos el objetivo, salimos
        if current_scroll >= target_pixels:
            print(f"✅ Se alcanzó el objetivo de {target_pixels} pixeles.")
            return

        # Realiza el scroll
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        new_scroll = page.evaluate("() => window.pageYOffset")
        # Si no hubo cambio en la posición, incrementamos intentos
        if new_scroll == current_scroll:
            intentos += 1
            print(f"Sin cambio en el scroll. Intento {intentos}/{max_intentos}.")
        else:
            intentos = 0  # Reiniciamos si hubo avance

    print(f"⚠️ Se agotaron los intentos sin alcanzar {target_pixels} pixeles.")

def scroll_hasta_elemento(page, selector_objetivo, step=500, delay=0.5, max_intentos=50):
    intentos = 0
    while intentos < max_intentos:
        try:
            # Verificar si el elemento ya está en viewport
            visible = page.evaluate(f"""
                () => {{
                    const el = document.querySelector("{selector_objetivo}");
                    if (!el) return false;
                    const rect = el.getBoundingClientRect();
                    return rect.top >= 0 && rect.bottom <= window.innerHeight;
                }}
            """)
            if visible:
                print(f"🎯 Elemento '{selector_objetivo}' ya está visible.")
                return
        except Exception as e:
            # Puede fallar si el elemento aún no existe
            pass

        # Scroll hacia abajo
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)
        intentos += 1

    print(f"⚠️ Se alcanzó el máximo de intentos. El elemento '{selector_objetivo}' no apareció.")

def scroll_gradualmente_hasta_el_final(page, step=500, delay=0.5, max_intentos=10):
    intentos = 0
    last_scroll_height = 0

    while intentos < max_intentos:
        # Baja un poco
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        # Esperar un poquito a que cargue
        current_scroll_height = page.evaluate("document.body.scrollHeight")

        if current_scroll_height == last_scroll_height:
            intentos += 1  # no creció, vamos contando intentos vacíos
        else:
            intentos = 0  # se cargó algo nuevo, reiniciamos el contador

        last_scroll_height = current_scroll_height

    print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")


# async def click_load_more_tuples_button(page: Page, wait_time: float = 2.0) -> bool:
#     """
#     Busca y hace clic en el botón 'Load More Tuples' si está presente.

#     Args:
#         page (Page): Instancia de Playwright Page.
#         wait_time (float): Tiempo de espera luego del clic (en segundos).

#     Returns:
#         bool: True si hizo clic, False si no encontró el botón.
#     """
#     try:
#         button = await page.query_selector('#lazy_load_next_btn_4')
#         if button:
#             await button.click()
#             await asyncio.sleep(wait_time)
#             return True
#         else:
#             print("Botón no encontrado.")
#     except Exception as e:
#         print(f"No se pudo hacer clic en el botón: {e}")
#     return False


import asyncio
# def scroll_y_click_load_more(page, step=1500, delay=0.5, max_intentos=50):
#     """
#     Scrollea gradualmente hasta el final de la página y clickea el botón
#     'Load More Tuples' cada vez que aparece.

#     Args:
#         page: instancia de Playwright Page.
#         step: pixeles que baja por scroll.
#         delay: segundos de espera entre scrolls.
#         max_intentos: cantidad de intentos sin cambios antes de detener.
#     """
#     intentos = 0
#     last_scroll_height = page.evaluate("document.body.scrollHeight")

#     while intentos < max_intentos:
#         # Scroll hacia abajo
#         page.evaluate(f"window.scrollBy(0, {step});")
#         time.sleep(delay)

#         # Clickea si encuentra el botón
#         try:
#             button = page.query_selector('#lazy_load_next_btn_4')
#             if button:
#                 button.click()
#                 time.sleep(delay)
#                 print("🟢 Botón clickeado.")
#         except Exception as e:
#             print(f"⚠️  Error al intentar clickear el botón: {e}")

#         # Verifica si el scroll creció
#         current_scroll_height = page.evaluate("document.body.scrollHeight")
#         if current_scroll_height == last_scroll_height:
#             intentos += 1
#         else:
#             intentos = 0
#         last_scroll_height = current_scroll_height

#     print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

def scroll_y_click_load_more(page, step=1500, delay=0.5, max_intentos=50):
    """
    Scrollea gradualmente hasta el final de la página y clickea el botón
    'Load More Tuples' cada vez que aparece.

    Args:
        page: instancia de Playwright Page.
        step: pixeles que baja por scroll.
        delay: segundos de espera entre scrolls.
        max_intentos: cantidad de intentos sin cambios antes de detener.
    """
    intentos = 0

    while intentos < max_intentos:
        # Scroll hacia abajo
        scroll_gradualmente_hasta_el_final(page, 1200, delay= 0.5, max_intentos=20)


        # Clickea si encuentra el botón
        try:
            button = page.query_selector("button.inf-pgntn.button.button--secondary.arrow")
            if button:
                button.click()
                time.sleep(delay)
                print("🟢 Botón clickeado.")
        except Exception as e:
            print(f"⚠️  Error al intentar clickear el botón: {e}")

        page.wait_for_timeout(1000)
        intentos += 1

    print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

# async def scroll_y_click_load_more(page, step=1500, delay=0.5, max_intentos=20):
#     """
#     Scrollea gradualmente hasta el final de la página y clickea el botón
#     'Load More Tuples' cada vez que aparece.
    
#     Args:
#         page: instancia de Playwright Page.
#         step: pixeles que baja por scroll.
#         delay: segundos de espera entre scrolls.
#         max_intentos: cantidad de intentos sin cambios antes de detener.
#     """
#     intentos = 0
#     last_scroll_height = await page.evaluate("document.body.scrollHeight")

#     while intentos < max_intentos:
#         # Scroll hacia abajo
#         await page.evaluate(f"window.scrollBy(0, {step});")
#         await asyncio.sleep(delay)

#         # Clickea si encuentra el botón
#         try:
#             button = await page.query_selector('#lazy_load_next_btn_4')
#             if button:
#                 await button.click()
#                 await asyncio.sleep(delay)
#                 print("🟢 Botón clickeado.")
#         except Exception as e:
#             print(f"⚠️  Error al intentar clickear el botón: {e}")

#         # Verifica si el scroll creció
#         current_scroll_height = await page.evaluate("document.body.scrollHeight")
#         if current_scroll_height == last_scroll_height:
#             intentos += 1
#         else:
#             intentos = 0
#         last_scroll_height = current_scroll_height

#     print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
        page = context.new_page()
        url = "https://www.shiksha.com/engineering/ranking/top-engineering-colleges-in-india/44-2-0-0-0?pageNo=6"
        page.goto(url)
        page.wait_for_timeout(1000)
        #scroll_gradualmente_hasta_pixels(page, 2500, step=1500, delay=0.4)
        scroll_gradualmente_hasta_el_final(page, step=1100, delay=0.34)
        #scroll_gradualmente_hasta_pixels(page,6000, step=1500, delay=0.3)
        #page.wait_for_timeout(60000)
        #page.wait_for_timeout(10000)
        

        # try:
        #     page.locator("#viewMoreCTA").click()
        #     print("✅Boton de ver todos los cursos clickeado con exito")
        #     time.sleep(1)
        # except:
        #     print("❌No se encontro el boton para ver todos los cursos")
            
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        # text_numberFaculties = soup.find("div", class_="_793c").find("strong").text
        # print(f"Text number of faculties extraido {text_numberFaculties}")
        # numberFaculties = int(''.join(filter(str.isdigit, text_numberFaculties)))
        # print(f"Number of faculties extraido {numberFaculties}")
        # box_faculties = soup.find_all("div", class_="_8165")
        # print(len(box_faculties))
        # box_faculties = box_faculties[:numberFaculties]
        # print(len(box_faculties))
        # nombres = []
        # for box in box_faculties:
        #     nombre = box.select_one("div.c8ff").text
        #     nombres.append(nombre) 

        #print(f"Box faculty {box_faculties}")
        #print(f"Nombre de las facultades: {nombres}")


        name_universities = soup.select("h4.f14_bold.link")
        name_U = []
        for name_university in name_universities:
           name_U.append(name_university.text)
        name_U = name_U[25:]#------------------------------------------------------
        print(f"Nombres extraidos {name_U}")
        print(len(name_U))
        # titles = soup.select("a.rank_clg.ripple.dark")
        # print(f"Url extraida {titles}")
        # universities = []

        # for title in titles:
        #    universities.append(title.attrs.get("href"))     
        # print(f"Universidades extraidas {universities}")
        # print(len(name_U))
        # print(len(universities))

        #page.wait_for_timeout(1000)
                # Selección de la tabla
        #tabla = soup.select_one("table.table._3367.d00e.d8b0.b3f1")

        # Contar el número de filas <tr>
        #filas = tabla.select("tr")
        #print(f"Cantidad de filas encontradas: {len(filas)}")
        #print(tabla)
        #overview = soup.select_one("div.faq__according-wrapper").select_one("p").text
        #placements = soup.select_one("div.faq__according-wrapper").select_one("p").text
        #print(overview)
        #print(placements)
        # Extraer el nombre de las universidades
        #####name_universities = soup.find_all("h4", class_="f14_bold link")
        #####name_U = []
        #####for name_university in name_universities:
            #####name_U.append(name_university.text)
            #if "Sri Venkateswara College of Engineering and Technology, Chittoor" in name_university:
            #   break
            
        #####print(f"Nombres extraidos {name_U}")
        #####titles = soup.find_all("a", class_="rank_clg ripple dark")
        #####print(f"Url extraida {titles}")
        #####universities = []

        #####for title in titles:
        #####    universities.append(title.attrs.get("href"))
        #####print(f"Universidades extraidas {universities}")
        #####universities = universities[77:]
        #####name_U = name_U[77:]
        #####numeroNombres = len(name_U)
        #####print(f"Name U {name_U}")
        #####print(f"Numero de universidades extraidas {numeroNombres}")
        # menu_items = soup.select("ul.cd4637.navbarSlider a.listItem.ripple.dark")
        # admissions_href = None

        # for item in menu_items:
        #     if "Admissions" in item.text:
        #         admissions_href = item.get("href")
        #         break

        # if admissions_href:
        #     print("✅ Admissions href encontrado:", admissions_href)
        # else:
        #     print("❌ No se encontró el enlace de Admissions.")


        # a = soup.find_all("div", class_="_8165")[9].find("a", class_="ripple dark").text
        # print(a)
    
scrape()