from src.utils.webdriver import ChromeUtils
from selenium.webdriver.common.by import By
import time
import random
import string
import sys


class Test:

    def __init__(self):
        self.webdriver = ChromeUtils().init_driver(
            headless=False, verbose=False, maximized=True, incognito=True
        )
        # self.webdriver.get("https://www.nopasanadape.com")
        self.webdriver.get("http://172.20.165.114:5000/")
        self.webdriver.set_window_size(1920, 1080)
        time.sleep(3)
        self.correo_descartable = (
            "wolabo1346@mardiek.com" if len(sys.argv) < 2 else sys.argv[1]
        )
        self.password_descartable = "Test21"

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
        self.webdriver.find_element(By.ID, "nombre").send_keys("Descartado")
        self.webdriver.find_element(By.ID, "dni").send_keys("98653299")
        self.webdriver.find_element(By.ID, "correo").send_keys(self.correo_descartable)
        self.webdriver.find_element(By.ID, "celular").send_keys("990990990")
        self.webdriver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div/form/button"
        ).click()

        # esperar codigo temporal llegado a correo descartable e ingresar en consola
        code = input(
            f"********** Ingrese Codigo Temporal ({self.correo_descartable}): "
        ).upper()

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

    def get_dom(self):
        return self.webdriver.execute_script(
            "return document.documentElement.outerHTML;"
        )


def main():

    test = Test()

    print(f"Crear Cuenta y Salir: {test.crear_cuenta()}")
    print(f"Login: {test.login()}")
    print(f"Cambiar Nombre: {test.cambiar_datos_nombre()}")
    print(f"Cambiar Celular: {test.cambiar_datos_celular()}")
    print(f"Cambiar Placas: {test.cambiar_datos_placas()}")
    print(f"Cambiar Contraseña: {test.cambiar_datos_contrasena()}")
    print(f"Tab Vencimientos: {test.mis_vencimientos()}")
    print(f"Logout: {test.logout()}")
    print(f"Recuperar Contraseña: {test.recuperar_contrasena()}")
    print(f"Eliminar Cuenta: {test.eliminar_cuenta()}")


if __name__ == "__main__":
    main()
