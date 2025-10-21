import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import requests
from io import BytesIO
from PIL import Image
from src.utils.webdriver import ChromeUtils
from src.utils.constants import HEADLESS


def browser(placa):

    TIMEOUT = 90  # seconds

    webdriver = ChromeUtils().init_driver(
        headless=HEADLESS["satmul"], verbose=False, maximized=True, incognito=False
    )

    webdriver.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")

    time.sleep(0.5)
    _target = (
        "https://www.sat.gob.pe/VirtualSAT/modulos/papeletas.aspx?tri=T&mysession="
        + webdriver.current_url.split("=")[-1]
    )
    webdriver.get(_target)
    time.sleep(0.5)

    # select alternative option from dropdown to reset it
    drop = Select(webdriver.find_element(By.ID, "tipoBusquedaPapeletas"))
    drop.select_by_value("busqLicencia")
    time.sleep(0.5)

    # select Busqueda por Documento from dropdown
    drop.select_by_value("busqPlaca")
    time.sleep(0.5)

    # enter placa
    c = webdriver.find_element(By.ID, "ctl00_cplPrincipal_txtPlaca")
    c.send_keys(placa)

    # wait until clicking on Buscar does not produce error (means "I'm not a robot passed")
    # or return with timeout
    timeout_start = time.time()
    while webdriver.find_elements(By.ID, "ctl00_cplPrincipal_txtPlaca"):
        if time.time() - timeout_start > TIMEOUT:
            webdriver.quit()
            return -1
        time.sleep(0.5)
        e = webdriver.find_elements(By.ID, "ctl00_cplPrincipal_CaptchaContinue")
        if e:
            try:
                e[0].click()
            except Exception:
                pass

    time.sleep(2)
    v = webdriver.find_elements(By.ID, "ctl00_cplPrincipal_lblMensajeVacio")

    # blank response if no papeletas found
    if v and "No se encontraron" in v[0].text:
        webdriver.find_element(By.ID, "menuOption10").click()
        webdriver.quit()
        return []

    # if papeletas found, go through all and return list of papeletas
    n = 2
    responses = []
    xpath = lambda row, col: webdriver.find_elements(
        By.XPATH,
        f"/html/body/form/div[3]/section/div/div/div[2]/div[8]/div/div/div[1]/div/div/table/tbody/tr[{row}]/td[{col}]",
    )

    while xpath(n, 1):

        resp = [xpath(n, k + 2)[0].text for k in range(14) if k != 10]

        # process images

        ids = (
            "ctl00_cplPrincipal_grdEstadoCuenta_ctl02_lnkImagen",
            "ctl00_cplPrincipal_grdEstadoCuenta_ctl02_lnkDocumento",
        )

        urls = []
        for id in ids:
            w = webdriver.find_elements(By.ID, id)
            urls.append(w[0].get_attribute("href")) if w else ""

        ids = ("imgPapel", "imgPapeleta")
        for id, url in zip(ids, urls):
            # check if image found, add bytes or None to list
            if url:
                webdriver.get(url)
                time.sleep(3)
                img = webdriver.find_elements(By.ID, id)
                if img:
                    img_url = img[0].get_attribute("src")
                    response = requests.get(img_url, stream=True)
                    resp.append(base64.b64encode(response.content).decode("utf-8"))
                else:
                    resp.append("")
            else:
                resp.append("")

        responses.append(resp)
        n += 1

    webdriver.quit()
    return responses
