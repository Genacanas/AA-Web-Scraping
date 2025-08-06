
#   Cap 25, Web Scraping 04
#           ----SCRAPING CON SELENIUM PERO SIN BEAUTIFULSOUP----

from webdriver_manager.chrome import ChromeDriverManager
from seleniumbase import Driver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys

#   CREO UNA FUNCION PARA INICIAR CHROME CON PARAMETROS ESPECIFICOS Y DEVUELVE EL DRIVER
def inicarChrome():
    options = Options()
    user_agent= "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-web.security") #Deshabilita la politica del origen
    options.add_argument("--disable-extensions") #Para que no cargue las extensiones de Chorme
    #options.add_argument("--disable-notifications") #Deshabilita las noti de Chorme
    options.add_argument("--ignore-certificate-errors") #Ignora el aviso "Su conexion no es privada"
    options.add_argument("--no-sandbox") #Deshabilita el moso SandBox
    options.add_argument("--log-level=3") #Para que chormedirver no muestre nada en la terminal
    options.add_argument("--allow-running-insecure-content") #Desactiva el aviso de "Contenido no seguro"
    #options.add_argument("--no-default-browser-check") #Deshabilitqa el aviso de "Chrome no es el navegador por defecto"
    options.add_argument("--no-first-run") #Evita la ejecucion de tareas que se realizan la primera vez que abrimos Chrome
    options.add_argument("--no-proxy-server") #Para no usar proxy, sino conexiones directas

    #options.add_argument("--disable-blink-features=AutomationControlled") #EVITA QUE SELENIUM SEA DETECTADO, osea que no se nos detecte como bots al entrar a una pagina
    #PARAMETROS A OMITIR EN EL INICIO DE CHROMEDRIVER
    exp_opt = [
        'enable-automation', #Para que no muestre la noti "Un software automatizado de pruebas esta controlando Chrome"
        'ignore-certificate-errors', #Para ignorar errores de certificacion de la pagina
        'enable-logging' #Para no mostrar un mesaje en la terminal
        ]
    options.add_experimental_option("excludeSwitches", exp_opt)

    driver = Driver(uc=True)
    return driver

#-----------------------MAIN-----------------------
if __name__ == '__main__':
    driver = inicarChrome()
    input("Pulsa ENTER para salir")
    driver.quit()