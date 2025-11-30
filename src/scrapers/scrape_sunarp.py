from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import io

from func_timeout import func_set_timeout, exceptions
from src.utils.utils import use_truecaptcha
from src.utils.constants import SCRAPER_TIMEOUT


@func_set_timeout(SCRAPER_TIMEOUT["sunarps"])
def browser_wrapper(placa, webdriver):
    try:
        return browser(placa, webdriver)
    except exceptions.FunctionTimedOut:
        return "Timeout"


def browser(placa, webdriver):

    url_inicio = "https://www.gob.pe/sunarp"
    url_final = "https://www2.sunarp.gob.pe/consulta-vehicular/inicio"

    if webdriver.current_url != url_final:
        # abrir este url primero para evitar limite de consultas
        webdriver.get(url_inicio)
        time.sleep(2)

        # abrir url definitivo
        webdriver.get(url_final)
        time.sleep(4)

    # ingresar datos de placa
    webdriver.find_element(By.ID, "nroPlaca").send_keys(placa)
    time.sleep(0.5)

    intentos_captcha = 0
    while intentos_captcha < 5:

        # capture captcha image from webpage and save
        _captcha_file_like = io.BytesIO(
            webdriver.find_element(By.ID, "image").screenshot_as_png
        )
        captcha_txt = use_truecaptcha(_captcha_file_like)["result"]
        if not captcha_txt:
            return "Servicio Captcha Offline."

        # clear captcha field and enter captcha text
        webdriver.find_element(By.ID, "codigoCaptcha").send_keys(
            Keys.BACKSPACE * 6 + captcha_txt
        )
        time.sleep(0.5)

        # click on "Realizar Busqueda"
        btn = webdriver.find_element(
            By.XPATH,
            "/html/body/app-root/nz-content/div/app-inicio/app-vehicular/nz-layout/nz-content/div/nz-card/div/app-form-datos-consulta/div/form/fieldset/nz-form-item[3]/nz-form-control/div/div/div/button",
        )
        webdriver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

        # if captcha is not correct, refresh captcha and try again
        _alerta = webdriver.find_elements(By.ID, "swal2-html-container")
        if _alerta and "correctamente" in _alerta[0].text:
            # click salir de la alerta
            webdriver.find_element(
                By.XPATH, "/html/body/div/div/div[6]/button[1]"
            ).click()
            time.sleep(2)
            intentos_captcha += 1
            continue

        # captcha correcto, no hay imagen
        elif _alerta and "error" in _alerta[0].text:
            btn = webdriver.find_element(
                By.XPATH, "/html/body/div/div/div[6]/button[1]"
            )

            webdriver.execute_script("arguments[0].click();", btn)
            return "@Error de pagina."

        # esperar hasta 10 segundos a que termine de cargar la imagen
        time_start = time.perf_counter()
        _card_image = None
        while not _card_image and time.perf_counter() - time_start < 10:
            _card_image = webdriver.find_elements(
                By.XPATH,
                "/html/body/app-root/nz-content/div/app-inicio/app-vehicular/nz-layout/nz-content/div/nz-card/div/app-form-datos-consulta/div/img",
            )
            time.sleep(0.5)

        # error que luego de 10 segundos no cargo imagen
        if not _card_image:
            return "@No Carga Imagen."

        # solicitud correcta, no hay datos
        e = webdriver.find_elements(By.ID, "swal2-html-container")
        if e and "nuevamente" in e[0].text:
            webdriver.refresh()
            return []

        # solicitud correcta, si hay datos, regresar imagen como bytes
        image_bytes = _card_image[0].screenshot_as_base64

        # presionar "volver" para siguiente iteracion (temporalmente refrescar pagina)
        time.sleep(1)
        webdriver.refresh()
        # b = webdriver.find_element(
        #     By.CSS_SELECTOR, "ant-btn btn-sunarp-green ant-btn-primary ant-btn-lg"
        # )
        # webdriver.execute_script("arguments[0].click();", b)
        return image_bytes

    # demasiados intentos de captcha errados consecutivos
    return "Excede Intentos de Captcha"
