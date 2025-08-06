from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd


filename = f"universities.xlsx"
data = []

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0")
        page = context.new_page()
        url = "https://www.shiksha.com/medicine-health-sciences/ranking/top-medical-colleges-in-india/100-2-0-0-0"
        page.goto(url)
        page.wait_for_selector("h4.f14_bold.link")
        html = page.content()

        soup = BeautifulSoup(html, "html.parser")
        name_universities = soup.find_all("h4", class_="f14_bold link")
        name_U = []
        for name_university in name_universities:
            name_U.append(name_university.text)
        print(f"Nombres extraidos {name_U}")
        titles = soup.find_all("a", class_="rank_clg ripple dark",limit=1)
        print(f"Url extraida {titles}")
        universities = []

        for title in titles:
            universities.append(title.attrs.get("href"))
        print(f"Universidades extraidas {universities}")
        k = 0
        #ENTRY IN EACH UNIVERSITY
        for university in universities:
            url_university = f'https://www.shiksha.com{university}'
            page.goto(url_university)
            print(f"Entro a la universidad https://www.shiksha.com{university}")
            page.wait_for_selector("a._59a5._5a11.ripple.dark")
            html_university = page.content()
            soup_u = BeautifulSoup(html_university, "html.parser")
            view_allFaculty = soup_u.find("a", class_="_59a5 _5a11 ripple dark").attrs.get("href")
            print(f"View all faculties extraido {view_allFaculty}")
            #ENTRY TO VIEW ALL FACULTY
            url_viewallFaculty = f'https://www.shiksha.com{view_allFaculty}'
            page.goto(url_viewallFaculty)
            print(f"Entro a la facultad https://www.shiksha.com{view_allFaculty}")
            page.wait_for_selector("div._793c")
            html_VAfaculty = page.content()
            soup_VAf = BeautifulSoup(html_VAfaculty, "html.parser")
            #EXTRACT NUMBER OF PROGRAMS
            text_numberFaculties = soup_VAf.find("div", class_="_793c").find("strong").text
            print(f"Text number of faculties extraido {text_numberFaculties}")
            numberFaculties = int(''.join(filter(str.isdigit, text_numberFaculties)))
            print(f"Number of faculties extraido {numberFaculties}")
            page.wait_for_selector("div.c8ff")
            faculties_links = soup_VAf.find_all("div", class_="c8ff", limit=numberFaculties)#.find("a").attrs.get("href")
            allFaculties = []
            for faculty_link in faculties_links:
                allFaculties.append(faculty_link.find("a").attrs.get("href"))
            print(f"Faculties extraidas {allFaculties}")
            for faculty in allFaculties:
                #ENTRY IN EACH FACULTY
                print(f"Entro a la facultad https://www.shiksha.com{faculty}")
                url_faculty = f'https://www.shiksha.com{faculty}'
                page.goto(url_faculty)
                page.wait_for_selector("div.c8ff")
                html_faculty = page.content()
                soup_f = BeautifulSoup(html_faculty, "html.parser")
                courses_links = soup_f.find_all("div", class_="c8ff")
                allCourses = []
                for course_link in courses_links:
                    allCourses.append(course_link.find("a").attrs.get("href"))
                print(f"Courses extraidos {allCourses}")

                page.wait_for_selector("div.dcfd.undefined")
                all_seats = soup_f.find_all("div", class_= "dcfd undefined")
                all_fees = soup_f.select("div.dcfd.f860")
                fees = []
                seats = []
                for one_seat in all_seats:
                    seats.append(one_seat.text)
                print(f"Seats and fees extraidos {seats}")
                for one_fee in all_fees:
                    fees.append(one_fee.text)
                print(f"Fees extraidos {fees}")
                i = 0
                j = 0
                for course in allCourses:

                    try:
                        seat_offered_text = seats[i]
                        seat_offered = int(seat_offered_text)
                        print(f"Seats offered {seat_offered}")
                    except(IndexError, ValueError):
                        seat_offered = "No seats available"

                    try:
                        total_tuition_fees = fees[j]
                        print(f"Total tuition fees {total_tuition_fees}")
                    except:
                        total_tuition_fees = "No tuition fees available"
                    #ENTRY IN EACH COURSE
                    print(f"Entro a la course https://www.shiksha.com{course}")
                    url_course = f'https://www.shiksha.com{course}'
                    page.goto(url_course)
                    page.wait_for_selector("div._11113e")
                    html_course = page.content()
                    soup_c = BeautifulSoup(html_course, "html.parser")
                    name_course = soup_c.find("div", class_= "_11113e").text
                    print(f"Name course extraido {name_course}")
                    page.wait_for_selector("span._22a5")
                    duration = soup_c.find("span", class_="_22a5").text
                    print(f"Duration extraido {duration}")
                    page.wait_for_selector("a.listItem.ripple.dark")
                    addmisions = soup_c.find_all("a", class_= " listItem ripple dark")[0].attrs.get("href")
                    print(f"Addmisions extraido {addmisions}")
                    #ENTRY TO ADDMISIONS
                    url_addmisions = f'https://www.shiksha.com{addmisions}'
                    
                    page.goto(url_addmisions)
                    print(f"Entro a addmisions https://www.shiksha.com{addmisions}")
                    page.wait_for_selector("ul.c2fa")
                    html_addmisions = page.content()
                    soup_a = BeautifulSoup(html_addmisions, "html.parser")
                    elegibility_criteria = soup_a.find("ul", class_="c2fa").text
                    print(f"Elegibility criteria extraido {elegibility_criteria}")
                    new_row = {
                        "University Name": name_U[k],
                        "Course Name": name_course,
                        "Duration": duration,
                        "Seat breakup": seat_offered,
                        "Total Tuition Fee": total_tuition_fees,
                        "Eligibility Criteria": elegibility_criteria
                    }
                    print(f"New row {new_row}")
                    data.append(new_row)
                    i = i+3
                    j = j+1

        k = k+1
                    # page.goto(faculty)
                    # html_faculty = page.content()
                    # soup_f = BeautifulSoup(html_faculty, "html.parser")

scrape()

df = pd.DataFrame(data)
df.to_excel(filename, index=False)
