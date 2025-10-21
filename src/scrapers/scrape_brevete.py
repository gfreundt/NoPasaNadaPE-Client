import os
import time
import pyautogui
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from src.utils.webdriver import ChromeUtils
from src.utils.constants import HEADLESS, NETWORK_PATH, MTC_CAPTCHAS


def browser(doc_num):

    webdriver = ChromeUtils().init_driver(
        headless=HEADLESS["brevete"], verbose=False, maximized=False
    )
    url = "https://licencias.mtc.gob.pe/#/index"

    # load webpage
    webdriver.set_page_load_timeout(10)
    try:
        webdriver.get(url)
    except TimeoutException:
        webdriver.quit()
        return {}, []

    # wait for pop-up button to activate (max 10 sec), then click
    popup_btn, k = [], 0
    while not popup_btn and k < 20:
        popup_btn = webdriver.find_elements(
            By.XPATH,
            "/html/body/div/div[2]/div/mat-dialog-container/app-popupanuncio/div/mat-dialog-actions/button",
        )
        time.sleep(0.5)
        k += 1
    popup_btn[0].click()

    # ingresar documento
    webdriver.find_element(By.ID, "mat-input-0").send_keys(doc_num)
    time.sleep(1)

    # click on "Si, acepto"
    checkbox = webdriver.find_element(By.ID, "mat-checkbox-2-input")
    webdriver.execute_script("arguments[0].click();", checkbox)
    time.sleep(1)

    # evade captcha ("No Soy Un Robot")
    evade_captcha(webdriver)

    # click on Buscar
    webdriver.find_element(
        By.XPATH,
        "/html/body/app-root/div[2]/app-home/div/mat-card[1]/form/div[5]/div[1]/button",
    ).click()
    time.sleep(3)

    # si no hay informacion de usuario
    _test = webdriver.find_elements(By.ID, "swal2-html-container")
    if _test and "No se" in _test[0].text:
        webdriver.quit()
        return []

    # scrape data
    _id_tipo = 11 if webdriver.find_elements(By.ID, "mat-input-11") else 17
    response = []
    for pos in (5, 6, _id_tipo, 7, 8, 9, 10):
        response.append(
            webdriver.find_element(
                By.ID,
                f"mat-input-{pos}",
            ).get_attribute("value")
        )

    # check if no licencia registrada, respond with empty for each field
    _nr = webdriver.find_elements(By.CLASS_NAME, "div_non_data")
    if _nr:
        webdriver.quit()
        return -1

    # next tab (Puntos) - make sure all is populated before tabbing along (with timeout) and wait a little
    timeout = 0
    while not webdriver.find_elements(By.ID, "mat-tab-label-0-0"):
        time.sleep(1)
        timeout += 1
        if timeout > 10:
            webdriver.quit()
            return []
    time.sleep(1.5)

    action = ActionChains(webdriver)
    # enter key combination to open tabs
    for key in (Keys.TAB * 5, Keys.RIGHT, Keys.ENTER):
        action.send_keys(key)
        action.perform()
        time.sleep(0.5)

    # extract data
    _puntos = webdriver.find_element(
        By.XPATH,
        "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[2]/div/div/mat-card/mat-card-content/div/app-visor-sclp/mat-card/mat-card-content/div/div[2]/label",
    )

    _puntos = int(_puntos.text.split(" ")[0]) if " " in _puntos.text else 0
    response.append(_puntos)

    # next tab (Record)
    time.sleep(0.8)
    action.send_keys(Keys.RIGHT)
    action.perform()
    time.sleep(0.7)
    action.send_keys(Keys.ENTER)
    action.perform()
    time.sleep(0.5)

    _recordnum = webdriver.find_element(
        By.XPATH,
        "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[3]/div/div/mat-card/mat-card-content/div/app-visor-record/div[1]/div/mat-card-title",
    ).text
    response.append(_recordnum[9:] if _recordnum else None)

    # process completed succesfully
    webdriver.quit()
    return response


def evade_captcha(webdriver):

    # click on "No Soy un Robot" checkbox
    x, y = pyautogui.locateCenterOnScreen(
        os.path.join(NETWORK_PATH, "static", "mtc_no_soy_un_robot_checkbox.png"),
        confidence=0.8,
    )
    pyautogui.click((x - 15, y))
    time.sleep(2)

    # identify which image captcha is looking for
    captcha_img_description = webdriver.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/mat-dialog-container/app-captcha-imagenes-popup/div/mat-dialog-content/app-captcha-imagenes/div[1]/p",
    ).text.split()[-1]

    if MTC_CAPTCHAS.get(captcha_img_description):
        for i in range(1, 9):
            _img_filename = f"https://licencias.mtc.gob.pe/assets/captcha/{MTC_CAPTCHAS[captcha_img_description]}.png"
            _element_xpath = f"/html/body/div/div[2]/div/mat-dialog-container/app-captcha-imagenes-popup/div/mat-dialog-content/app-captcha-imagenes/div[2]/div[{i}]/img"
            element = webdriver.find_element(By.XPATH, _element_xpath)
            if element.get_attribute("src") == _img_filename:
                element.click()
                time.sleep(1)
                return
    else:
        print("****** MANUAL CAPTCHA NEEDED")
        time.sleep(10)
