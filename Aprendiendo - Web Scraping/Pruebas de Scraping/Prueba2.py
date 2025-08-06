#   IMPORTAMOS WEBDRIVER
from webdriver_manager.chrome import ChromeDriverManager
from seleniumbase import Driver
from bs4 import BeautifulSoup
driver = Driver(browser="chrome")
url = "https://www.venex.com.ar/notebooks/notebook-lenovo-ideapad-slim-3-15amn8-ryzen-5-7520u-8gb-ssd-512gb-15-6-free-arctic-grey.html"
driver.get(url)
driver.page_source
soup = BeautifulSoup(driver.page_source, "html.parser")

print('\n')
print("PRODUCTO:", soup.find("h1", class_="tituloProducto visible-xs").text.strip(), sep=" ")
print("PRECIO:", soup.find("div", class_="textPrecio text-green").text.strip(), sep=" ")
print("CUAOTAS:", soup.find("div", class_ = "form-control ui-autocomplete-input").text, sep=" ")
print("IMAGEN:", soup.find("div", class_="owl-item active").find("img").attrs.get("src"), sep=" ")