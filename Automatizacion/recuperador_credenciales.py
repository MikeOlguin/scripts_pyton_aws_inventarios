from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ruta completa al ejecutable de ChromeDriver
ruta_chromedriver = r'C:\usr\bin\109.0.5414\chromedriver.exe'

# Configuración del navegador
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = ruta_chromedriver  # Ruta al ejecutable de Chrome

# Añade la ruta de ChromeDriver al path de ChromeOptions
chrome_options.add_argument(f"webdriver.chrome.driver={ruta_chromedriver}")

# Inicia el navegador con las opciones configuradas
driver = webdriver.Chrome(options=chrome_options)

# Acceder a la página
driver.get("https://mobilityado.awsapps.com/start/#/")
# Encontrar el campo de usuario y escribir el nombre de usuario
username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "awsui-input-0")))
username_input.send_keys("jmolguinh@mobilityado.com")

# Hacer clic en el botón "Next"
next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username-submit-button")))
next_button.click()

# Encontrar el campo de contraseña y escribir la contraseña
password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "awsui-input-1")))
password_input.send_keys("Spidermike1990*")

# Hacer clic en el botón "Sign In"
sign_in_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password-submit-button")))
sign_in_button.click()

# Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
driver.implicitly_wait(10)

# Extraer el primer título de la página después de iniciar sesión
pagina_despues_de_login_titulo = driver.title
print("Título de la página después de iniciar sesión:", pagina_despues_de_login_titulo)

driver.quit()
