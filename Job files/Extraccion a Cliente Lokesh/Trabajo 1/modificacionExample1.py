from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

data = []

# Nombre del archivo de salida
fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"parche_2.xlsx"

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0")
        page = context.new_page()
        url = "https://www.shiksha.com/medicine-health-sciences/ranking/top-medical-colleges-in-india/100-2-0-0-0"
        page.goto(url)
        page.wait_for_timeout(3000)

        items = page.locator("a.rank_clg.ripple.dark")
        
        for i in range(2, items.count()):
            page.wait_for_selector("a.rank_clg.ripple.dark")
            page.wait_for_timeout(500)
            university_name = page.locator("a.rank_clg.ripple.dark").nth(i).inner_text()
            items.nth(i).click()

            page.wait_for_selector("span.d9de._9c85")
            page.locator("span.d9de._9c85").first.click()
            page.wait_for_selector("h3.f7cc")
            try:
                text = page.locator("div._793c").first.inner_text()
                number = int(''.join(filter(str.isdigit, text)))
            except:
                number = 0

            allCourses = page.locator("div.c8ff")

            for j in range(0, number):
                a = 0
                b = 3
                page.wait_for_timeout(500)
                page.wait_for_selector("div.c8ff")
                page.wait_for_timeout(500)
                allCourses.nth(j).click()
                page.wait_for_timeout(3000)
                allSpecific = page.locator("div.c8ff")
                page.wait_for_timeout(500)
                for k in range(allSpecific.count()):
                    try:
                        try:
                            text = page.locator("div.dcfd.undefined").nth(a).inner_text()
                            seat_breakup = int(text)
                        except (IndexError, ValueError, TimeoutError):
                            seat_breakup = "No seats available"
                        a = a+4
                        try:
                            total_tuition_fee = page.locator("div.dcfd.undefined").nth(b).inner_text()
                        except:
                            total_tuition_fee = "Total tuition fee not found"
                        b = b+4
                        page.wait_for_selector("div.c8ff")
                        allSpecific.nth(k).click()
                        try:
                            page.wait_for_selector("div._11113e", timeout=5000)
                            page.wait_for_timeout(500)
                            course_name = page.locator("div._11113e").first.inner_text()
                        except:
                            course_name = "Course name not found"

                        try:
                            duration = page.locator("span._22a5 ").first.inner_text()
                        except:
                            duration = "Duration not found"

                        try:
                            page.locator("a.listItem.ripple.dark").nth(5).click()
                            page.wait_for_selector("ul.c2fa")
                            page.wait_for_timeout(2000)
                            elegibility_criteria = page.locator("ul.c2fa").first.inner_text()
                        except:
                            elegibility_criteria = "Eligibility criteria not found"

                        # Guardar la fila
                        new_row = {
                            "University Name": university_name,
                            "Course Name": course_name,
                            "Duration": duration,
                            "Seat breakup": seat_breakup,
                            "Total Tuition Fee": total_tuition_fee,
                            "Eligibility Criteria": elegibility_criteria
                        }
                        data.append(new_row)

                        # Escribir en el Excel en tiempo real cada 5 iteraciones
                        if len(data) % 5 == 0:
                            df = pd.DataFrame(data)
                            df.to_excel(filename, index=False)
                            print("----PACK DE 5 GUARDADO---")
                        print(f"✅ Guardado: {course_name} de {university_name}")

                        page.go_back()
                        page.go_back()
                        page.go_back()
                        page.wait_for_timeout(1000)

                    except Exception as e:
                        print(f"⚠️ Error en curso específico: {e}")
                        continue
                    
                page.go_back()

            page.go_back()
            page.go_back()
        # Guardar lo que haya quedado pendiente
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

        browser.close()    


    print(f"📁 Finalizado. Archivo guardado: {filename}")

scrape()
