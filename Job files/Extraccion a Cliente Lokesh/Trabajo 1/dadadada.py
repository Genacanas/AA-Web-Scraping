
#--Script modificado por chatGPT (guardar datos en excel de forma distinta)---

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent
ua = UserAgent()
#--------------AGREGADOS------------------
import os
from openpyxl import load_workbook
#--------------------------------------

filename = f"universities.xlsx"
#data = []

#---------------AGREGADOS------------------
def flush_data(data_buffer, filename, header_written):
    df = pd.DataFrame(data_buffer)
    
    if (not os.path.exists(filename)) or (not header_written):
        df.to_excel(filename, index=False)
        header_written = True
        print(f"Se creó el archivo {filename} con {len(data_buffer)} registros.")
    else:
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            # Se asignan las hojas disponibles usando el workbook que ya carga el writer
            writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
            startrow = writer.book.active.max_row
            df.to_excel(writer, index=False, header=False, startrow=startrow)
        print(f"Se añadieron {len(data_buffer)} registros al archivo {filename}.")
    
    data_buffer.clear()
    return header_written
#--------------------------------------

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


def scroll_gradualmente_hasta_el_final(page, step=500, delay=0.5, max_intentos=50):
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
        #-----------AGREGADOS------------------
        data_buffer = []          # Buffer para acumular new_row
        header_written = False    # Indica si ya se escribió el header en el Excel
        #--------------------------------------

        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
        page = context.new_page()
        url = "https://www.shiksha.com/medicine-health-sciences/ranking/top-medical-colleges-in-india/100-2-0-0-0"
        page.goto(url)
        scroll_gradualmente_hasta_pixels(page, 3000, step=1500, delay=0.075)
        page.wait_for_selector("h4.f14_bold.link")
        html = page.content()

        soup = BeautifulSoup(html, "html.parser")
        name_universities = soup.find_all("h4", class_="f14_bold link")
        name_U = []
        for name_university in name_universities:
            name_U.append(name_university.text)
        print(f"Nombres extraidos {name_U}")
        titles = soup.find_all("a", class_="rank_clg ripple dark",limit=10)
        print(f"Url extraida {titles}")
        universities = []

        for title in titles:
            universities.append(title.attrs.get("href"))
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
            scroll_gradualmente_hasta_pixels(page, 3000, step=1500, delay=0.075)
            page.wait_for_selector("a._59a5._5a11.ripple.dark")
            html_university = page.content()
            soup_u = BeautifulSoup(html_university, "html.parser")
            view_allFaculty = soup_u.select_one("a._59a5._5a11.ripple.dark").attrs.get("href")
            #ENTRY TO VIEW ALL FACULTY
            url_viewallFaculty = f'https://www.shiksha.com{view_allFaculty}'
            print(f"View all faculties extraido {url_viewallFaculty}")
            page.close()
            context.close()
            context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
            page = context.new_page()
            print(f"Entro a ver todas las facultades https://www.shiksha.com{view_allFaculty}")
            page.goto(url_viewallFaculty)
            scroll_gradualmente_hasta_pixels(page, 5000, step=1500, delay=0.075)
            print("Entrada exitosa")
            html_VAfaculty = page.content()
            soup_VAf = BeautifulSoup(html_VAfaculty, "html.parser")
            #EXTRACT NUMBER OF PROGRAMS
            text_numberFaculties = soup_VAf.find("div", class_="_793c").find("strong").text
            print(f"Text number of faculties extraido {text_numberFaculties}")
            numberFaculties = int(''.join(filter(str.isdigit, text_numberFaculties)))
            print(f"Number of faculties extraido {numberFaculties}")

            box_faculties = soup_VAf.find_all("div", class_="_8165")
            box_faculties = box_faculties[:numberFaculties]
            print(f"Box course {box_faculties}")
            for box_faculty in box_faculties:
                #ENTRY IN EACH FACULTY
                url_faculty = box_faculty.select_one("a.ripple.dark").attrs.get("href")
                print(f"Url course {url_faculty}")
                url_faculty = f'https://www.shiksha.com{url_faculty}'
                print(f"Entro a la course {url_faculty}")
                page.close()
                context.close()
                context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
                page = context.new_page()
                page.goto(url_faculty)
                print("Entrada exitosa")
                scroll_gradualmente_hasta_pixels(page, 7000, step=1500, delay=0.075)
                html_faculty = page.content()
                soup_c = BeautifulSoup(html_faculty, "html.parser")
                box_course = soup_c.find_all("div", class_="_8165")
                print(f"Box course {box_faculties}")
                for box in box_course:
                    seats = box.find("div", class_="dcfd undefined").text
                    try:
                        seats_offered = int(''.join(filter(str.isdigit, seats)))
                    except(IndexError, ValueError):
                        seats_offered = "No seats available"
                    print(f"Seats {seats_offered}")
                    try:
                        fees = box.find("div", class_="dcfd f860").text
                    except:
                        fees = "No fees available"
                    print(f"Fees {fees}")

                    #ENTRY IN EACH COURSE
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
                    duration = soup_c.find("span", class_="_22a5").text
                    print(f"Duration extraido {duration}")
                    print(soup_c.select_one("ul.cd4637.navbarSlider").select("a.listItem.ripple.dark"))
                    #addmisions = soup_c.select_one("ul.cd4637.navbarSlider").select("a.listItem.ripple.dark")[5].attrs.get("href")
                    menu_items = soup_c.select("ul.cd4637.navbarSlider a.listItem.ripple.dark")
                    admissions = None

                    for item in menu_items:
                        if "Admissions" in item.text:
                            admissions = item.get("href")
                            break

                    if admissions:
                        print("✅ Admissions href encontrado:", admissions)
                    else:
                        print("❌ No se encontró el enlace de Admissions.")

                    #ENTRY TO ADDMISIONS
                    url_admissions = f'https://www.shiksha.com{admissions}'
                    print(f"Entro a addmisions https://www.shiksha.com{admissions}")
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
                        elegibility_criteria = "No elegibility criteria available"
                    print(f"Elegibility criteria extraido {elegibility_criteria}")
                    new_row = {
                        "University Name": name_U[k],
                        "Course Name": course_name,
                        "Duration": duration,
                        "Seat breakup": seats_offered,
                        "Total Tuition Fee": fees,
                        "Eligibility Criteria": elegibility_criteria
                    }
                    print(f"New row {new_row}")
                    
                    #----------------AGREGADOS------------------
                    data_buffer.append(new_row)
                    if len(data_buffer) >= 10:
                        header_written = flush_data(data_buffer, filename, header_written)
                    #--------------------------------------
                    #data.append(new_row)
            k = k + 1
        #----------------AGREGADOS------------------    
        if data_buffer:
            header_written = flush_data(data_buffer, filename, header_written)
          
        # Finalizamos cerrando la página y el navegador
        page.close()
        context.close()
        browser.close()
        #--------------------------------------

        
        #     print(f"Number of faculties extraido {numberFaculties}")
        #     page.wait_for_selector("div.c8ff")
        #     faculties_links = soup_VAf.find_all("div", class_="c8ff")#.find("a").attrs.get("href")
        #     faculties_links = faculties_links[numberFaculties:]
        #     allFaculties = []
        #     for faculty_link in faculties_links:
        #         allFaculties.append(faculty_link.find("a").attrs.get("href"))
        #     print(f"Faculties extraidas {allFaculties}")
            
        #     for faculty in allFaculties:
        #         #ENTRY IN EACH FACULTY
        #         print(f"Entro a la facultad https://www.shiksha.com{faculty}")
        #         url_faculty = f'https://www.shiksha.com{faculty}'
        #         page.goto(url_faculty)
        #         page.wait_for_selector("div.c8ff")
        #         html_faculty = page.content()
        #         soup_f = BeautifulSoup(html_faculty, "html.parser")
        #         courses_links = soup_f.find_all("div", class_="c8ff")
        #         allCourses = []
        #         for course_link in courses_links:
        #             allCourses.append(course_link.find("a").attrs.get("href"))
        #         print(f"Courses extraidos {allCourses}")

        #         for course in allCourses:

        #             try:
        #                 seat_offered_text = seats[i]
        #                 seat_offered = int(seat_offered_text)
        #                 print(f"Seats offered {seat_offered}")
        #             except(IndexError, ValueError):
        #                 seat_offered = "No seats available"

        #             try:
        #                 total_tuition_fees = fees[j]
        #                 print(f"Total tuition fees {total_tuition_fees}")
        #             except:

        #             #ENTRY IN EACH COURSE
        #             print(f"Entro a la course https://www.shiksha.com{course}")
        #             url_course = f'https://www.shiksha.com{course}'
        #             page.goto(url_course)
        #             page.wait_for_selector("div._11113e")
        #             html_course = page.content()
        #             soup_c = BeautifulSoup(html_course, "html.parser")
        #             name_course = soup_c.find("div", class_= "_11113e").text
        #             print(f"Name course extraido {name_course}")
        #             page.wait_for_selector("span._22a5")
        #             duration = soup_c.find("span", class_="_22a5").text
        #             print(f"Duration extraido {duration}")
        #             page.wait_for_selector("a.listItem.ripple.dark")
        #             addmisions = soup_c.find_all("a", class_= " listItem ripple dark")[0].attrs.get("href")
        #             print(f"Addmisions extraido {addmisions}")
        #             #ENTRY TO ADDMISIONS
        #             url_addmisions = f'https://www.shiksha.com{addmisions}'
        #             page.goto(url_addmisions)
        #             print(f"Entro a addmisions https://www.shiksha.com{addmisions}")
        #             page.wait_for_selector("ul.c2fa")
        #             html_addmisions = page.content()
        #             soup_a = BeautifulSoup(html_addmisions, "html.parser")
        #             elegibility_criteria = soup_a.find("ul", class_="c2fa").text
        #             print(f"Elegibility criteria extraido {elegibility_criteria}")
        #             new_row = {
        #                 "University Name": name_U[k],
        #                 "Course Name": name_course,
        #                 "Duration": duration,
        #                 "Seat breakup": seat_offered,
        #                 "Total Tuition Fee": total_tuition_fees,
        #                 "Eligibility Criteria": elegibility_criteria
        #             }
        #             print(f"New row {new_row}")
        #             data.append(new_row)
        #             i = i+3
        #             j = j+1

        # k = k+1
                    # page.goto(faculty)
                    # html_faculty = page.content()
                    # soup_f = BeautifulSoup(html_faculty, "html.parser")

scrape()

#df = pd.DataFrame(data)
#df.to_excel(filename, index=False)
