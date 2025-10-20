import os
import io
import base64
from selenium.webdriver.common.by import By
import time
from src.utils.chromedriver import ChromeUtils
from src.utils.utils import use_truecaptcha
from src.utils.constants import HEADLESS


def browser(doc_num):

    # get paths to Downloads folder and destination folder
    from_path = os.path.join(
        os.path.expanduser("~/Downloads"), "RECORD DE CONDUCTOR.pdf"
    )

    # erase file from Downloads folder before downloading new one
    if os.path.exists(from_path):
        os.remove(from_path)

    # start browser, navigate to url
    webdriver = ChromeUtils().init_driver(
        headless=HEADLESS["recvehic"], verbose=False, maximized=True
    )
    webdriver.get("https://recordconductor.mtc.gob.pe/")

    # outer loop: in case captcha is not accepted by webpage, try with a new one
    retry_captcha = False
    while True:
        # inner loop: in case OCR cannot figure out captcha, retry new captcha
        captcha_txt = ""
        while not captcha_txt:
            if retry_captcha:
                webdriver.refresh()
                time.sleep(2)
            # capture captcha image from webpage and store in variable
            try:

                # convert image to text using OCR
                _captcha_file_like = io.BytesIO(
                    webdriver.find_element(By.ID, "idxcaptcha").screenshot_as_png
                )
                captcha_txt = use_truecaptcha(_captcha_file_like)["result"]
                retry_captcha = True

            except ValueError:
                # captcha image did not load, reset webpage
                webdriver.refresh()
                time.sleep(1.5)

        # enter data into fields and run
        webdriver.find_element(By.ID, "txtNroDocumento").send_keys(doc_num)
        webdriver.find_element(By.ID, "idCaptcha").send_keys(captcha_txt)
        time.sleep(3)
        webdriver.find_element(By.ID, "BtnBuscar").click()
        time.sleep(1)

        # if captcha is not correct, refresh and restart cycle, if no data found, return blank
        _alerta = webdriver.find_elements(By.ID, "idxAlertmensaje")
        if _alerta and "ingresado" in _alerta[0].text:
            # click on "Cerrar" to close pop-up
            webdriver.find_element(
                By.XPATH, "/html/body/div[5]/div/div/div[2]/button"
            ).click()
            # clear webpage for next iteration and small wait
            time.sleep(1)
            webdriver.refresh()
            continue
        elif _alerta and "PERSONA" in _alerta[0].text:
            webdriver.quit()
            return -1
        else:
            break

    # click on download button
    b = webdriver.find_elements(By.ID, "btnprint")
    try:
        b[0].click()
    except Exception:
        webdriver.quit()
        return -1

    # wait max 10 sec while file is downloaded
    count = 0
    while not os.path.isfile(os.path.join(from_path)) and count < 10:
        time.sleep(1)
        count += 1

    webdriver.quit()

    # if file was downloaded successfully, decode PDF into bytes --> string
    if count < 10:
        with open(from_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
