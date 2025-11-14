from src.utils.webdriver import ChromeUtils
from src.test.temp_email import TempEmail
from src.utils.constants import API_TOKEN_MAQUINARIAS
from selenium.webdriver.common.by import By
import time
import random
import string
import requests


class Test:

    def __init__(self, log):

        self.log = log

        self.crea_correo_temporal()
        self.password_descartable = "Test21"

        # abrir pagina de pruebas
        self.webdriver = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True, incognito=True
        )
        self.webdriver.get("https://www.nopasanadape.com")
        self.webdriver.set_window_size(1920, 1080)
        time.sleep(3)

    def crea_correo_temporal(self):
        self.email = TempEmail(self.log)
        correo_perfil = self.email.get_temp_email()

        self.correo_descartable = correo_perfil["email_address"]
        self.account_id = correo_perfil["account_id"]
        self.password = correo_perfil["password"]
        self.token = correo_perfil["token"]

        self.log(action=f"✅ Correo temporal: {self.correo_descartable}")

    def check_for_test_marker(self, text):
        return (
            self.webdriver.find_element(By.ID, "test-marker").get_attribute(
                "tracking-id"
            )
            == text
        )

    def crear_cuenta(self):

        # logout
        self.webdriver.find_element(By.XPATH, "/html/body/nav/div/div/div/a[4]").click()
        time.sleep(2)

        # presionar crear cuenta
        self.webdriver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[2]/a"
        ).click()

        # ingresar datos fijos basura con correo descartable del inicio
        self.webdriver.find_element(By.ID, "nombre").send_keys("PruebaPRUEBAPrueba")
        self.webdriver.find_element(By.ID, "dni").send_keys("98653299")
        self.webdriver.find_element(By.ID, "correo").send_keys(self.correo_descartable)
        self.webdriver.find_element(By.ID, "celular").send_keys("990990990")
        self.webdriver.find_element(By.ID, "acepta_terminos").click()
        self.webdriver.find_element(By.ID, "acepta_privacidad").click()
        self.webdriver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div/form/button"
        ).click()

        # esperar codigo temporal llegado a correo descartable e ingresar en consola
        body = self.email.wait_for_new_email(
            jwt_token=self.token,
            timeout=120,  # Wait for 2 minutes
            interval=5,  # Check every 5 seconds
        )
        code = body.split(":")[1][1:5]

        # ingresar codigo y elegit password
        self.webdriver.find_element(By.ID, "codigo").send_keys(code)
        self.webdriver.find_element(By.ID, "password1").send_keys(
            self.password_descartable
        )
        self.webdriver.find_element(By.ID, "password2").send_keys(
            self.password_descartable
        )
        self.webdriver.find_element(By.ID, "btn-registro-crear-cuenta").click()
        time.sleep(2)

        # exito = en la pagina de mis datos
        return self.check_for_test_marker("cuenta-mis-datos")

    def login(self):

        # logout
        self.webdriver.find_element(By.XPATH, "/html/body/nav/div/div/div/a[4]").click()
        time.sleep(2)

        # ingresar a la cuenta de forma regular
        self.webdriver.find_element(By.ID, "correo").send_keys(self.correo_descartable)
        self.webdriver.find_element(By.ID, "password").send_keys(
            self.password_descartable
        )
        self.webdriver.find_element(By.ID, "btn-login-empezar").click()
        time.sleep(2)

        # exito = en la pagina de mis datos
        return self.check_for_test_marker("cuenta-mis-datos")

    def cambiar_datos_nombre(self):

        # dentro de datos, cambiar nombre por algo random
        field = self.webdriver.find_element(By.ID, "nombre")
        field.clear()
        field.send_keys("".join(random.choices(string.ascii_uppercase, k=8)))
        self.webdriver.find_element(By.ID, "btn-mis-datos-actualizar").click()
        time.sleep(2)

        # exito = mensaje de cambiado con exito
        if self.webdriver.find_elements(By.XPATH, "/html/body/div[1]/div"):
            return True

        return False

    def cambiar_datos_celular(self):

        # dentro de datos, cambiar celular por random
        field = self.webdriver.find_element(By.ID, "celular")
        field.clear()
        field.send_keys("".join(random.choices(string.digits, k=9)))
        self.webdriver.find_element(By.ID, "btn-mis-datos-actualizar").click()
        time.sleep(2)

        # exito = mensaje de cambiado con exito
        if self.webdriver.find_elements(By.XPATH, "/html/body/div[1]/div"):
            return True

        return False

    def cambiar_datos_placas(self):

        # dentro de datos, cambiar las tres placas por random
        field1 = self.webdriver.find_element(By.ID, "placa1")
        field1.clear()
        field1.send_keys(
            "".join(random.choices(string.ascii_uppercase, k=3))
            + "".join(random.choices(string.digits, k=3))
        )

        field2 = self.webdriver.find_element(By.ID, "placa2")
        field2.clear()
        field2.send_keys(
            "".join(random.choices(string.ascii_uppercase, k=3))
            + "".join(random.choices(string.digits, k=3))
        )

        field3 = self.webdriver.find_element(By.ID, "placa3")
        field3.clear()
        field3.send_keys(
            "".join(random.choices(string.ascii_uppercase, k=3))
            + "".join(random.choices(string.digits, k=3))
        )

        self.webdriver.find_element(By.ID, "btn-mis-datos-actualizar").click()
        time.sleep(2)

        # exito = mensaje de cambiado con exito
        if self.webdriver.find_elements(By.XPATH, "/html/body/div[1]/div"):
            return True

        return False

    def cambiar_datos_contrasena(self):

        # dentro de datos, "cambiar" la contraseña pero dejarla igual
        field1 = self.webdriver.find_element(By.ID, "contra1")
        field1.send_keys(self.password_descartable)
        field2 = self.webdriver.find_element(By.ID, "contra2")
        field2.send_keys(self.password_descartable)
        field3 = self.webdriver.find_element(By.ID, "contra3")
        field3.send_keys(self.password_descartable + "!")

        self.webdriver.find_element(By.ID, "btn-mis-datos-actualizar").click()
        time.sleep(2)

        # exito = mensaje de cambiado con exito
        if self.webdriver.find_elements(By.XPATH, "/html/body/div[1]/div"):
            return True

        return False

    def mis_vencimientos(self):

        # dentro de datos, cambiar en navbar a Mis Vencimientos
        self.webdriver.find_element(By.XPATH, "/html/body/nav/div/div/div/a[2]").click()
        time.sleep(2)

        # exito = en la pagina de mis vencimientos
        return self.check_for_test_marker("cuenta-mis-vencimientos")

    def logout(self):

        self.webdriver.find_element(By.XPATH, "/html/body/nav/div/div/div/a[4]").click()
        time.sleep(2)

        # exito = de regreso a la pagina principal
        return self.check_for_test_marker("ui-login")

    def recuperar_contrasena(self):

        # presionar recuperar contraseña
        self.webdriver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div/a"
        ).click()
        time.sleep(2)

        # solicitar codigo
        self.webdriver.find_element(By.ID, "correo").send_keys(self.correo_descartable)
        self.webdriver.find_element(By.ID, "btn-recuperar-siguiente").click()
        time.sleep(2)

        # ingresar codigo y cambiar contraseña
        code = input(
            f"********** Ingrese Codigo Temporal ({self.correo_descartable}): "
        ).upper()
        self.webdriver.find_element(By.ID, "codigo").send_keys(code)
        self.webdriver.find_element(By.ID, "password1").send_keys(
            self.password_descartable
        )
        self.webdriver.find_element(By.ID, "password2").send_keys(
            self.password_descartable
        )
        self.webdriver.find_element(By.ID, "btn-recuperar-siguiente").click()
        time.sleep(2)

        # exito = de regreso a la pagina principal
        return self.check_for_test_marker("ui-login")

    def eliminar_cuenta(self):

        # logout
        self.webdriver.find_element(By.XPATH, "/html/body/nav/div/div/div/a[4]").click()
        time.sleep(2)

        # login
        self.webdriver.find_element(By.ID, "correo").send_keys(self.correo_descartable)
        self.webdriver.find_element(By.ID, "password").send_keys(
            self.password_descartable
        )
        self.webdriver.find_element(By.ID, "btn-login-empezar").click()
        time.sleep(2)

        # presionar Eliminar Cuenta
        self.webdriver.find_element(By.ID, "btn-mis-datos-eliminar-cuenta").click()
        time.sleep(2)

        # persionar Confirmar
        self.webdriver.find_element(By.ID, "btn-mis-datos-eliminar-confirmar").click()
        time.sleep(2)

        # exito = de regreso a la pagina principal
        return self.check_for_test_marker("ui-login")

    def datos_estaticos(self):

        # logout
        self.webdriver.find_element(By.XPATH, "/html/body/nav/div/div/div/a[3]").click()
        time.sleep(2)

        # exito = de regreso a la pagina principal
        t1 = self.check_for_test_marker("ui-acerca")

        # presionar Terminos y Condiciones
        link = self.webdriver.find_element(
            By.XPATH, "/html/body/div[1]/div[3]/div/p/a[1]"
        )
        self.webdriver.execute_script("arguments[0].click();", link)
        time.sleep(2)

        t2 = True  # TODO: cambiar de tab y revisar tag, falta incluir tag en html

        # presionar Politicas de Privacidad
        link = self.webdriver.find_element(
            By.XPATH, "/html/body/div[1]/div[3]/div/p/a[2]"
        )
        self.webdriver.execute_script("arguments[0].click();", link)
        time.sleep(2)

        t3 = True  # TODO: cambiar de tab y revisar tag, falta incluir tag en html

        return t1 and t2 and t3

    def api_alta(self):

        url = "https://nopasanadape.com/api/v1"
        token = API_TOKEN_MAQUINARIAS
        usuario = "TST-000"
        correo = "prueba@prueba.com"

        f = requests.post(
            url=url,
            params={
                "token": token,
                "solicitud": "alta",
                "usuario": usuario,
                "correo": correo,
            },
        )
        return int(f.status_code) == 200

    def api_baja(self):

        url = "https://nopasanadape.com/api/v1"
        token = API_TOKEN_MAQUINARIAS
        usuario = "TST-000"
        correo = "prueba@prueba.com"

        f = requests.post(
            url=url,
            params={
                "token": token,
                "solicitud": "baja",
                "usuario": usuario,
                "correo": correo,
            },
        )
        return int(f.status_code) == 200

    def api_info(self):

        url = "https://nopasanadape.com/api/v1"
        token = API_TOKEN_MAQUINARIAS
        usuario = "TST-000"

        f = requests.post(
            url=url,
            params={
                "token": token,
                "solicitud": "info",
                "usuario": usuario,
                "correo": [],
            },
        )
        return int(f.status_code) == 200

    def get_dom(self):
        return self.webdriver.execute_script(
            "return document.documentElement.outerHTML;"
        )


def main(self):

    self.log(action="[INICIANDO PRUEBA DE SERVIDOR]")

    test = Test(self.log)

    self.log(action=f"Crear Cuenta y Salir: {test.crear_cuenta()}")
    self.log(action=f"Login: {test.login()}")
    self.log(action=f"Cambiar Nombre: {test.cambiar_datos_nombre()}")
    self.log(action=f"Cambiar Celular: {test.cambiar_datos_celular()}")
    self.log(action=f"Cambiar Placas: {test.cambiar_datos_placas()}")
    self.log(action=f"Cambiar Contraseña: {test.cambiar_datos_contrasena()}")
    self.log(action=f"Tab Vencimientos: {test.mis_vencimientos()}")
    self.log(action=f"Logout: {test.logout()}")
    # self.log(action=f"Recuperar Contraseña: {test.recuperar_contrasena()}")
    self.log(action=f"Eliminar Cuenta: {test.eliminar_cuenta()}")
    self.log(action=f"Informacion Estatica: {test.datos_estaticos()}")
    self.log(action=f"API - Alta: {test.api_alta()}")
    self.log(action=f"API - Baja: {test.api_baja()}")
    self.log(action=f"API - Info: {test.api_info()}")

    self.log(action="[FIN PRUEBA DE SERVIDOR]")
