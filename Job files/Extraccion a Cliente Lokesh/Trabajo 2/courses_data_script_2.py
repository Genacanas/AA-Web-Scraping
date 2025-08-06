from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent
ua = UserAgent()
import os

filename = f"array_data.xlsx"
filename2 = f"data_buffer.xlsx"
data = []

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


def scroll_gradualmente_hasta_el_final(page, step=500, delay=0.5, max_intentos=15):
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


def scrape():
    with sync_playwright() as p:

        data_buffer = 0

        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
        page = context.new_page()
        url = "https://www.shiksha.com/mba/ranking/top-mba-colleges-in-india/2-2-0-0-0"
        page.goto(url)
        scroll_gradualmente_hasta_el_final(page, step=1100, delay=0.5)
        page.wait_for_selector("h4.f14_bold.link")
        html = page.content()

        soup = BeautifulSoup(html, "html.parser")
        name_universities = soup.select("h4.f14_bold.link")
        name_U = []
        for name_university in name_universities:
            name_U.append(name_university.text)
        #name_U = name_U[25:]#------------------------------------------------------
        print(f"Nombres extraidos {name_U}")
        titles = soup.select("a.rank_clg.ripple.dark")
        print(f"Url extraida {titles}")
        universities = []

        for title in titles:
            universities.append(title.attrs.get("href"))
        
        #universities = universities[25:]#---------------------------------------------
        print(f"Universidades extraidas {universities}")
        k = 0
        #ENTRY IN EACH UNIVERSITY
        for university in universities:
            url_university = f'https://www.shiksha.com{university}'
            print(f"Entro a la universidad https://www.shiksha.com{university}")
            page.close()
            context.close()
            context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
            page = context.new_page()
            page.goto(url_university)
            #scroll_gradualmente_hasta_pixels(page, 3000, step=1500, delay=0.075)
            page.wait_for_selector("a._59a5._5a11.ripple.dark")
            html_university = page.content()
            soup_u = BeautifulSoup(html_university, "html.parser")

            menu_items1 = soup_u.select("ul.cd4637.navbarSlider a.listItem.ripple.dark")
            view_allFaculty = None
            for item1 in menu_items1:
                if "Courses" in item1.text:
                    view_allFaculty = item1.get("href")
                    break
            #view_allFaculty = soup_u.select_one("a._59a5._5a11.ripple.dark").attrs.get("href")
            #ENTRY TO VIEW ALL FACULTY
            url_viewallFaculty = f'https://www.shiksha.com{view_allFaculty}'
            print(f"View all faculties extraido {url_viewallFaculty}")
            page.close()
            context.close()
            context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
            page = context.new_page()
            print(f"Entro a ver todas las facultades https://www.shiksha.com{view_allFaculty}")
            page.goto(url_viewallFaculty)
            scroll_gradualmente_hasta_el_final(page, step=1500, delay=0.35)
            print("Entrada exitosa")
            
            #CLICK BUTTON TO SEE ALL COURSES
            try:
                page.locator("div._3102").click()
                print("✅Boton de ver todos los cursos clickeado con exito")
                time.sleep(1)
            except:
                print("❌No se encontro el boton para ver todos los cursos")
            
            html_VAfaculty = page.content()
            soup_VAf = BeautifulSoup(html_VAfaculty, "html.parser")
            #EXTRACT NUMBER OF PROGRAMS
            text_numberFaculties = soup_VAf.find("div", class_="_793c").find("strong").text
            print(f"Text number of faculties extraido {text_numberFaculties}")
            numberFaculties = int(''.join(filter(str.isdigit, text_numberFaculties)))
            print(f"Number of faculties extraido {numberFaculties}")

            box_faculties = soup_VAf.find_all("div", class_="_8165")
            box_faculties = box_faculties[:numberFaculties]

            print(f"Box faculty {box_faculties}")
            for box_faculty in box_faculties:
                #ENTRY IN EACH FACULTY
                url_faculty = box_faculty.select_one("a.ripple.dark").attrs.get("href")
                print(f"Url faculty {url_faculty}")
                url_faculty = f'https://www.shiksha.com{url_faculty}'
                print(f"Entro a la faculty {url_faculty}")
                page.close()
                context.close()
                context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                page = context.new_page()
                page.goto(url_faculty)
                print("Entrada exitosa")
                scroll_gradualmente_hasta_pixels(page,6000, step=1500, delay=0.3)
                html_faculty = page.content()
                soup_c = BeautifulSoup(html_faculty, "html.parser")

                box_course = soup_c.find_all("div", class_="_8165")
                #box_course = box_course[:numberCourses]
                print(f"Box course {box_course}")
                
                for box in box_course:
                    #ENTRY IN EACH COURSE
                    try:
                        course = box.find("div", class_="c8ff").find("a").attrs.get("href")
                        print(f"Url course {course}")
                        url_course = f'https://www.shiksha.com{course}'
                        print(f"Entro a la course https://www.shiksha.com{course}")
                        page.close()
                        context.close()
                        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                        page = context.new_page()
                        page.goto(url_course)
                        print("Entrada exitosa")
                        html_course = page.content()
                        soup_c = BeautifulSoup(html_course, "html.parser")
                        course_name = soup_c.find("div", class_= "_11113e").text
                        print(f"Name course extraido {course_name}")
                        try:
                            overview = soup_c.select_one("div.faq__according-wrapper").get_text(strip=True)
                        except Exception as e:
                            print(f"No se encontro el Overview del curso: {e}")
                            overview = "Course Overview not found"

                        # Selección de la tabla
                        try: 
                            tabla = soup_c.select_one("table.table._3367.d00e.d8b0.b3f1")

                            # Contar el número de filas <tr>
                            filas = tabla.select("tr")
                            print(f"Cantidad de filas encontradas: {len(filas)}")
                            print(tabla)
                            # Diccionario para almacenar los datos
                            
                            duration = "Duration not found"
                            fees = "No fees available"
                            mode_course = "Mode of course not found"
                            course_level = "Course level not found"
                            type_university ="Type of university not found"

                            # Iterar sobre cada fila
                            for fila in filas:
                                columnas = fila.find_all("td")
                                if len(columnas) == 2:  # Nos aseguramos de que existan dos columnas (nombre y valor)
                                    nombre = columnas[0].get_text(strip=True)
                                    valor = columnas[1].get_text(strip=True)

                                    # Comprobamos y asignamos según el nombre encontrado
                                    match nombre:
                                        case "Duration":
                                            duration = valor
                                        case "Total fee" | "Total Tuition Fees":
                                            fees = valor
                                        case "Mode of Course":
                                            mode_course = valor
                                        case "Course Level":
                                            course_level = valor
                                        case "Type of University":
                                            type_university = valor
                        except Exception as e:
                            print(f"No se encontro la Tabla: {e}")

                        menu_items = soup_c.select("ul.cd4637.navbarSlider a.listItem.ripple.dark")
                        admissions = None

                        for item in menu_items:
                            if "Admissions" in item.text:
                                admissions = item.get("href")
                                break

                        if admissions:
                            try:
                                print("✅ Admissions href encontrado:", admissions)
                                url_admissions = f'https://www.shiksha.com{admissions}'
                                print(f"Entro a addmisions {url_admissions}")
                                page.close()
                                context.close()
                                context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                                page = context.new_page()
                                page.goto(url_admissions)
                                print("Entrada exitosa")
                                scroll_gradualmente_hasta_pixels(page, 2000, step=1000, delay=0.075)
                                html_addmisions = page.content()
                                soup_a = BeautifulSoup(html_addmisions, "html.parser")
                                try:
                                    elegibility_criteria = soup_a.find("ul", class_="c2fa").text
                                except:
                                    elegibility_criteria = "No eligibility criteria available"
                                print(f"Elegibility criteria extraido {elegibility_criteria}")
                            except Exception as e:
                                print(f"❌ Error accediendo a admissions: {e}")
                                elegibility_criteria = "No eligibility criteria available"
                        else:
                            print("❌ No se encontró el enlace de Admissions.")
                            elegibility_criteria = "No eligibility criteria available"

                        placements = None
                        for item in menu_items:
                            if "Placements" in item.text:
                                placements = item.get("href")
                                break
                        
                        if placements:
                            try:
                                print("✅ Placements href encontrado:", placements)
                                url_placements = f'https://www.shiksha.com{placements}'
                                print(f"Entro a addmisions {url_placements}")
                                page.close()
                                context.close()
                                context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                                page = context.new_page()
                                page.goto(url_placements)
                                html_placements = page.content()
                                soup_p = BeautifulSoup(html_placements, "html.parser")
                                try:
                                    placement_overview = soup_p.select_one("div.faq__according-wrapper").text
                                except:
                                    placement_overview = "No Placement overview available"
                                print(f"Placement overview extraido {placement_overview}")
                            except Exception as e:
                                print(f"❌ Error accediendo a Placements: {e}")
                                placement_overview = "No Placement overview available"
                        else:
                            print("❌ No se encontró el enlace de Placements.")
                            placement_overview = "No Placement overview available"

                        new_row = {
                            "University Name": name_U[k],
                            "Course Name": course_name,
                            "Duration": duration,
                            "Total Tuition Fee": fees,
                            "Eligibility Criteria": elegibility_criteria,
                            "Mode of Course": mode_course,
                            "Type of University": type_university,
                            "Course Level": course_level,
                            "Placement Overview": placement_overview,
                            "Overview": overview
                        }
                        print(f"New row {new_row}")
                        data.append(new_row)
                        data_buffer = data_buffer + 1
                        if data_buffer >= 10:
                            # Guardar todo el progreso actual en el archivo de respaldo
                            pd.DataFrame(data).to_excel(filename2, index=False)

                            # Limpiar el buffer para los próximos 10
                            data_buffer = 0

                    except Exception as e:
                        print(f"❌ Error procesando box_course: {e}")
                        print("Probablemente no existe la url")
                        continue

            k = k+1

        if data_buffer:
            pd.DataFrame(data).to_excel(filename2, index=False)
            print("✅ Datos restantes en buffer guardados exitosamente.")
            

scrape()

df = pd.DataFrame(data)
df.to_excel(filename, index=False)