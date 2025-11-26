import base64
import time
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from src.utils.webdriver import ChromeUtils
from src.utils.constants import HEADLESS, TWOCAPTCHA_API_KEY


def solve_recaptcha(webdriver, page_url):
    """
    Extracts the sitekey, sends solve request to 2captcha,
    polls for result, and returns the token.
    """

    # Find recaptcha sitekey
    sitekey = webdriver.find_element(By.CSS_SELECTOR, ".g-recaptcha").get_attribute(
        "data-sitekey"
    )

    # Send solve request
    resp = requests.post(
        "http://2captcha.com/in.php",
        data={
            "key": TWOCAPTCHA_API_KEY,
            "method": "userrecaptcha",
            "googlekey": sitekey,
            "pageurl": page_url,
        },
    ).text

    if "OK|" not in resp:
        return False

    task_id = resp.split("|")[1]

    # Poll until solved
    token = None
    for _ in range(48):  # ~4 minutes max
        time.sleep(5)
        check = requests.get(
            "http://2captcha.com/res.php",
            params={"key": TWOCAPTCHA_API_KEY, "action": "get", "id": task_id},
        ).text

        if check == "CAPCHA_NOT_READY":
            continue

        if "OK|" in check:
            token = check.split("|")[1]
            break

        return False

    if not token:
        return False

    return token


def browser(placa):

    # construir webdriver con parametros especificos
    chromedriver = ChromeUtils(
        headless=HEADLESS["satmul"],
    )
    webdriver = chromedriver.direct_driver()

    # Load SAT portal
    webdriver.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")
    time.sleep(5)

    # Redirect to papeletas page
    sess = webdriver.current_url.split("=")[-1]
    target = f"https://www.sat.gob.pe/VirtualSAT/modulos/papeletas.aspx?tri=T&mysession={sess}"
    webdriver.get(target)
    time.sleep(1)

    # Reset dropdown
    drop = Select(webdriver.find_element(By.ID, "tipoBusquedaPapeletas"))
    drop.select_by_value("busqLicencia")
    time.sleep(0.5)
    drop.select_by_value("busqPlaca")

    # Enter placa
    campo = webdriver.find_element(By.ID, "ctl00_cplPrincipal_txtPlaca")
    campo.send_keys(placa)
    time.sleep(0.5)

    # ----------------------------------------------------
    # SOLVE CAPTCHA HERE
    # ----------------------------------------------------
    token = solve_recaptcha(webdriver, webdriver.current_url)
    if not token:
        return -1

    # Inject token into g-recaptcha-response
    webdriver.execute_script(
        """
        document.getElementById('g-recaptcha-response').style.display = 'block';
        document.getElementById('g-recaptcha-response').value = arguments[0];
        document.getElementById('g-recaptcha-response').dispatchEvent(new Event('input'));
        document.getElementById('g-recaptcha-response').dispatchEvent(new Event('change'));
    """,
        token,
    )

    time.sleep(1)

    # Click Buscar button (CaptchaContinue)
    try:
        webdriver.find_element(By.ID, "ctl00_cplPrincipal_CaptchaContinue").click()
    except Exception:
        pass

    # Wait for results to load
    time.sleep(3)

    # ----------------------------------------------------
    # PARSE RESULTS
    # ----------------------------------------------------
    empty_msg = webdriver.find_elements(By.ID, "ctl00_cplPrincipal_lblMensajeVacio")
    if empty_msg and "No se encontraron" in empty_msg[0].text:
        webdriver.find_element(By.ID, "menuOption10").click()
        webdriver.quit()
        return []

    # Papeletas found
    n = 2
    responses = []

    xpath = lambda row, col: webdriver.find_elements(
        By.XPATH,
        f"/html/body/form/div[3]/section/div/div/div[2]/div[8]/div/div/div[1]/div/div/table/tbody/tr[{row}]/td[{col}]",
    )

    while xpath(n, 1):

        # Extract fields (except col 12)
        resp = [xpath(n, k + 2)[0].text for k in range(14) if k != 10]

        # Extract image/document URLs
        ids = (
            "ctl00_cplPrincipal_grdEstadoCuenta_ctl02_lnkImagen",
            "ctl00_cplPrincipal_grdEstadoCuenta_ctl02_lnkDocumento",
        )

        urls = []
        for id in ids:
            w = webdriver.find_elements(By.ID, id)
            urls.append(w[0].get_attribute("href") if w else "")

        # Download images
        ids = ("imgPapel", "imgPapeleta")
        for id, url in zip(ids, urls):
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
