import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import random

driver = uc.Chrome()

url = ("https://www.booking.com/searchresults.html"
       "?ss=San+Carlos%2C+Sonora%2C+Mexico"
       "&checkin=2026-09-15"
       "&checkout=2026-09-22"
       "&group_adults=2"
       "&no_rooms=1")

driver.get(url)
time.sleep(8)

# Cada click en "Cargar más resultados" agrega ~25 tarjetas más.
# Con 4-5 clicks deberías llegar a 100-125 alojamientos, suficiente
# para filtrar hasta tus ~80.
MAX_CLICKS = 5

for i in range(MAX_CLICKS):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4))  # variar tiempos, no ser tan predecible

    try:
        boton = driver.find_element(
            By.XPATH,
            "//button[contains(., 'Cargar') or contains(., 'Load more') or contains(., 'more results')]"
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
        time.sleep(1)
        boton.click()
        print(f"Click {i+1}/{MAX_CLICKS} en 'cargar más' - ok")
        time.sleep(random.uniform(3, 5))
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"No se encontró/pudo hacer click en el botón (intento {i+1}): {type(e).__name__}")
        break

with open("resultado_selenium.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("Título:", driver.title)
print("Caracteres:", len(driver.page_source))

driver.quit()