import os
import io
import base64

# import pyautogui
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from src.utils.utils import use_truecaptcha
from src.utils.constants import NETWORK_PATH


def browser(doc_num, webdriver):

    # get paths to Downloads folder and destination folder
    target_folder = Path(os.path.join(NETWORK_PATH, "static"))

    for file_path in target_folder.glob("RECORD*.pdf"):
        file_path.unlink()

    # start browser, navigate to url
    url = "https://recordconductor.mtc.gob.pe/"

    webdriver.get(url)
    time.sleep(2)

    # outer loop: in case captcha is not accepted by webpage, try with a new one
    while True:
        try:
            # extraer texto de captcha
            _captcha_file_like = io.BytesIO(
                webdriver.find_element(By.ID, "idxcaptcha").screenshot_as_png
            )
            captcha_txt = use_truecaptcha(_captcha_file_like)["result"]

            # ingresar en formulario y apretar buscar
            webdriver.find_element(By.ID, "txtNroDocumento").send_keys(doc_num)
            webdriver.find_element(By.ID, "idCaptcha").send_keys(captcha_txt)
            time.sleep(1)
            webdriver.find_element(By.ID, "BtnBuscar").click()
            time.sleep(3)

            # mensaje de limite de consultas - dormir

            # obtener mensaje de alerta (si hay)
            _alerta = webdriver.find_elements(
                By.XPATH, "/html/body/div[5]/div/div/div[1]/label"
            )

            # mensaje de alerta: captcha equivocado
            if _alerta and "ingresado" in _alerta[0].text:
                webdriver.refresh()
                time.sleep(3)
                continue

            # mensaje de alerta: no hay informacion de la persona
            elif _alerta and "PERSONA" in _alerta[0].text:
                webdriver.quit()
                return -1

            # no hay alerta - proceder
            break

        except ValueError:
            # no cargo imagen de captcha, refrescar y volver a intentar
            webdriver.refresh()
            time.sleep(3)

    # click on download button
    webdriver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": os.path.join(NETWORK_PATH, "static"),
        },
    )
    b = webdriver.find_elements(By.ID, "btnprint")
    try:
        webdriver.execute_script("arguments[0].click();", b[0])
        time.sleep(2)

    except Exception:
        webdriver.quit()
        return "No Hay Boton Download"

    if os.path.isfile(
        os.path.join(NETWORK_PATH, "static", "RECORD DE CONDUCTOR (2).pdf")
    ):
        return "Multiples archivos de PDF."

    # esperar un maximo de 12 segundos hasta que baje el archivo y retornar imagen
    start_time = time.time()
    _file = os.path.join(NETWORK_PATH, "static", "RECORD DE CONDUCTOR.pdf")
    while time.time() - start_time < 12:
        if os.path.isfile(_file):
            with open(_file, "rb") as f:
                webdriver.quit()
                return base64.b64encode(f.read()).decode("utf-8")
        time.sleep(0.5)

    # si no se encontro imagen, retornar error
    webdriver.quit()
    return "No Se Puedo Bajar Archivo"


# def click_save_button_if_present(MAX_WAIT_TIME=5):

#     IMAGE_PATH = os.path.join(NETWORK_PATH, "static", "save_button.png")
#     start_time = time.time()

#     while time.time() - start_time < MAX_WAIT_TIME:
#         try:
#             button_location = pyautogui.locateCenterOnScreen(
#                 IMAGE_PATH, confidence=0.85
#             )
#             pyautogui.click(button_location)

#             # boton encontrado
#             return True

#         except pyautogui.ImageNotFoundException:
#             time.sleep(0.5)

#     # nunca encontro el boton
#     return False
