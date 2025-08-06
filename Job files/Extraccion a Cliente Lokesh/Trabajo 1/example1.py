from playwright.sync_api import sync_playwright
import pandas as pd

data = []
def scrape():
    #INICIAR PLAYWRIGHT
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) #CAMBIAR A TRUE SI NO QUEREMOS VER EL NAVEGADOR
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0")
        page = context.new_page()
        #ABRE LA PAG WEB
        url = "https://www.shiksha.com/medicine-health-sciences/ranking/top-medical-colleges-in-india/100-2-0-0-0"
        page.goto(url)

        page.wait_for_timeout(3000)

        items = page.locator("a.rank_clg.ripple.dark")
        university = []
  
        for i in range(items.count()):
            #UNIVERSITY NAME SCRAPPED
            page.wait_for_selector("h4.f14_bold.link")
            page.wait_for_timeout(1000)
            university_name = page.query_selector_all("h4.f14_bold.link")[0].inner_text()
            #CLICK UNIVERSITY
            items.nth(i).click()
            #VIEW ALL COURSES
            page.wait_for_selector("span.d9de._9c85")
            page.wait_for_timeout(1000)
            page.locator("span.d9de._9c85").first.click()
            page.wait_for_selector("h3.f7cc")
            text = page.locator("div._793c").first.inner_text()
            number = int(''.join(filter(str.isdigit, text)))
            allCourses = page.locator("h3.f7cc")
            for j in range(0, number -1):
                
                page.wait_for_timeout(1000)

                #CLICK COURSE
                allCourses.nth(j).click()
                allSpecific = page.locator("h3.f7cc")
                page.wait_for_timeout(1000)
                
                for k in range(allSpecific.count()):
                    page.wait_for_selector("h3.f7cc")
                    page.wait_for_timeout(1000)

                    #CLICK SPECIFIC COURSE
                    allSpecific.nth(k).click()
                    page.wait_for_selector("div._11113e")
                    page.wait_for_timeout(1000)
                    try:
                       course_name = page.locator("div._11113e").first.inner_text()
                    except:
                        course_name = "Course name not found"

                    try:
                        duration = page.locator("span._22a5 ").first.inner_text()
                    except:
                        duration = "Duration not found"

                    try:
                        seat_breakup = page.query_selector_all("div._75f3")[1].inner_text()
                    except:
                        seat_breakup = "Seat breakup not found"

                    try:
                        total_tuition_fee = page.locator("span._69e0 ").first.inner_text()
                    except:
                        total_tuition_fee = "Total tuition fee not found"

                    try:
                        page.query_selector_all("a.listItem.ripple.dark")[5].click()
                        page.wait_for_selector("ul.c2fa")
                        page.wait_for_timeout(1000)
                        elegibility_criteria = page.locator("ul.c2fa").first.inner_text()
                    except:
                        elegibility_criteria = "Eligibility criteria not found"

                    #I STORE THE DATA IN AN ARRAY
                    university.append({
                        "University Name": university_name,
                        "Course Name": course_name, 
                        "Duration": duration, 
                        "Seat breakup": seat_breakup, 
                        "Total Tuition Fee": total_tuition_fee, 
                        "Elegibility Criteria": elegibility_criteria
                        })
                    data.append(university)
                    df = pd.DataFrame(data)
                    df.to_csv("universities_data.csv", index=False)
                    #RETURN TO THE PREVIOUS PAGE
                    page.go_back()
                    page.go_back()
                    page.go_back()
                    page.wait_for_timeout(8000)
                page.go_back()

#        page.locator("h1.tituloProducto.hidden-xs ").inner_text()
#        page.locator("h1.tituloProducto.hidden-xs ").inner_text()
 #       page.locator("h1.tituloProducto.hidden-xs ").inner_text()



scrape()