from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USER = ''
PASSWORD = ''
URL = "https://mobilityado.awsapps.com/start/#/?tab=accounts";
ELEMENTS = {'ELEMENT0':{'ELEMENT':'//strong[contains(.,"AWS_ACCOUNT")]','SELECTOR':'XPATH','ACCTION':1}, 'ELEMENT1':{'ELEMENT':'//a[contains(.,"Access keys")]','SELECTOR':'XPATH','ACCTION':1}, 'ELEMENT2':{'ELEMENT':'//div[4]/div/div[2]/div/div[2]/div/div[2]/div/div/input','SELECTOR':'XPATH','ACCTION':3,'VALUE':'ACCESS_KEY_ID'},'ELEMENT3':{'ELEMENT':'//div[4]/div/div[2]/div/div[3]/div/div[2]/div/div/input','SELECTOR':'XPATH','ACCTION':3,'VALUE':'SECRET_ACCESS_KEY'},'ELEMENT4':{'ELEMENT':'//div[4]/div/div[2]/div/div[4]/div/div[2]/div/div/input','SELECTOR':'XPATH','ACCTION':3,'VALUE':'SESSION_TOCKEN'},'ELEMENT5':{'ELEMENT':'awsui_dismiss-control_1d2i7_1mjvw_381','SELECTOR':'CLASS','ACCTION':1},'ELEMENT6':{'ELEMENT':'//strong[contains(.,"AWS_ACCOUNT")]','SELECTOR':'XPATH','ACCTION':1}}
ACCOUNTS = [ {'ACCOUNT':'AWS-Servicios-Test','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Data-Dev','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Data-Prod','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Data-Test','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'fgs-dev','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'fgs-Prod','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'fgs-test','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Mone-Dev','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Mone-Prod','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Mone-test','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'MoneRepo-Dev','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'MoneRepo-Prod','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'MoneRepo-Test','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Servicios-Dev','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False}, {'ACCOUNT':'Servicios-Prod','ACCESS_KEY_ID':'','SECRET_ACCESS_KEY':'','SESSION_TOCKEN':'','GET':False} ]
IS_PRINT = False
sandbox_enabled = False

def print_task(msg):
    if IS_PRINT:
        print(msg)
        
def findElement(driver, element, selector):
    if selector == 'ID':
        print_task(f'BUSCANDO POR ID {element}')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, element)))
        print_task('ENCONTRADO POR ID')
        return driver.find_element(By.ID, element)
    elif selector == 'CLASS':
        print_task(f'BUSCANDO POR CLASS {element}')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, element)))
        print_task('ENCONTRADO POR CLASS')
        return driver.find_element(By.CLASS_NAME, element)
    elif selector == 'XPATH':
        print_task(f'BUSCANDO POR XPATH {element}')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, element)))
        print_task('ENCONTRADO POR XPATH')
        return driver.find_element(By.XPATH, element)
    return None

def getCredencialesAWS(user_input,pass_input,url_imput):
    options = Options()
    if sandbox_enabled:
        print('Sandbox habilitado')
    else:
        print('Sandbox deshabilitado')
        options.add_argument('--no-sandbox')
        #options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless') 
    options.add_argument('incognito')
    options.add_argument('--start-maximized')  
    driver = webdriver.Chrome(options=options)
    try:
       driver.get(url_imput)
       elemento = findElement(driver, 'awsui-input-0', 'ID')
       elemento.send_keys(user_input)
       elemento = findElement(driver, '//awsui-button[@id="username-submit-button"]/button', 'XPATH')
       elemento.click()
       elemento = findElement(driver, 'awsui-input-1', 'ID')
       elemento.send_keys(pass_input)
       elemento = findElement(driver, '//awsui-button[@id="password-submit-button"]/button/span', 'XPATH')
       elemento.click()
       for account in ACCOUNTS:
           for key, value in ELEMENTS.items():
               element_rp = value['ELEMENT'].replace("AWS_ACCOUNT",account['ACCOUNT'])
               elemento = findElement(driver,element_rp,value['SELECTOR'])
               if value['ACCTION'] == 1:
                   #driver.execute_script("arguments[0].scrollIntoView(true);", elemento)   
                   #elemento.click()
                   driver.execute_script("arguments[0].click();", elemento)
               elif value['ACCTION'] == 2:
                   elemento.send_keys(value['VALUE'])
               elif value['ACCTION'] == 3:
                   texto_elemento = elemento.get_attribute("value")
                   account[value['VALUE']] = texto_elemento
           account['GET'] = True         
       elemento = findElement(driver, '//div[3]/span/a[contains(.,"Sign out")]', 'XPATH')
       elemento.click()
    except Exception as e:
         print(f"Erorr en getCredencialesAWS: {e}") 
    finally:
        driver.quit()
    return ACCOUNTS

def recorreArray():
    for account in ACCOUNTS:
        print('----------------------------------------------------------')
        print("Nombre de la cuenta:", account['ACCOUNT'])
        for key, value in ELEMENTS.items():
            print("XPath:", value['ELEMENT'].replace("AWS_ACCOUNT",account['ACCOUNT']))

if __name__ == "__main__":
    #recorreArray()
    array_accouts=getCredencialesAWS(USER,PASSWORD,URL)
    for account in array_accouts:
        print('----------------------------------------------------------')
        print("Obtenido:", account['GET'])
    