from selenium.webdriver.common.by import By
import time
import io
from src.utils.webdriver import ChromeUtils
from src.utils.constants import HEADLESS


class Soat:

    def __init__(self):
        self.webdriver = ChromeUtils().init_driver(
            headless=HEADLESS["soat"], maximized=True, verbose=False, incognito=True
        )

    def get_captcha(self):
        self.webdriver.get("https://www.soat.com.pe/servicios-soat/")
        time.sleep(3)
        self.webdriver.switch_to.frame(0)  # Switches to the first frame
        time.sleep(3)
        _img = self.webdriver.find_element(By.CLASS_NAME, "captcha-img")

        return io.BytesIO(_img.screenshot_as_png)

    def browser(self, placa, captcha_txt):

        # self.webdriver.get("https://webapp.apeseg.org.pe/consulta-soat/?source=soat")

        # existing_windows = set(self.webdriver.window_handles)

        # llenar campo de placa
        # self.webdriver.find_element(
        #     By.XPATH,
        #     "/html/body/div/main/article/div/section[1]/div/div/div[1]/div/div[1]/div/div[1]/div/div[2]/form/div[1]/input",
        # ).send_keys(placa)

        self.webdriver.find_element(By.ID, "placa").send_keys(placa)

        # llenar campo de captcha
        # self.webdriver.find_element(
        #     By.XPATH,
        #     "/html/body/div/main/article/div/section[1]/div/div/div[1]/div/div[1]/div/div[1]/div/div[2]/form/div[2]/input",
        # ).send_keys(captcha_txt)

        self.webdriver.find_element(By.ID, "captcha").send_keys(captcha_txt)

        # apretar "Consultar"
        # self.webdriver.find_element(
        #     By.ID,
        #     "SOATForm",
        # ).click()

        self.webdriver.find_element(
            By.XPATH, "/html/body/div/div/main/div/form/button"
        ).click()

        # esperar que nueva ventana se abra y cambiar a esa
        # time.sleep(2)
        # for _ in range(10):
        #     new_windows = set(self.webdriver.window_handles) - existing_windows
        #     if new_windows:
        #         self.webdriver.switch_to.window(new_windows.pop())
        #         break
        #     time.sleep(1)
        # else:
        #     self.webdriver.quit()
        #     return -3

        time.sleep(3)

        # revisar si se excedio el numero de intentos
        if "superado" in self.webdriver.page_source:
            self.webdriver.quit()
            return -2

        # check for three possible outputs: no table, table with one record, table with multiple records
        # table_one = self.webdriver.find_elements(
        #     By.XPATH,
        #     "/html/body/form/center/table/tbody/tr/td/div/table/tbody/tr/td[1]",
        # )
        # table_multiple = self.webdriver.find_elements(
        #     By.XPATH,
        #     "/html/body/form/center/table/tbody/tr/td/div/table/tbody/tr[1]/td[1]",
        # )

        # no records (wrong captcha or no SOAT info)
        msg = self.webdriver.find_elements(
            By.XPATH, "/html/body/div/div/main/div/div/h2"
        )
        if msg and "la placa solicitada" in msg[0].text:
            self.webdriver.quit()
            return -1

        # table with 2+ records
        # if table_multiple:
        #     _tr = "[1]"

        # table with only one record
        # else:
        #     _tr = ""

        # extract top record of table
        # response = [
        #     self.webdriver.find_element(
        #         By.XPATH,
        #         f"/html/body/form/center/table/tbody/tr/td/div/table/tbody/tr{_tr}/td[{i}]",
        #     ).text.strip()
        #     for i in range(2, 12)
        # ]

        response = [
            self.webdriver.find_element(
                By.XPATH,
                f"/html/body/div/div/main/div/div/table/tbody/tr[{i}]/td",
            ).text.strip()
            for i in range(1, 13)
        ]

        # close driver, return record
        self.webdriver.quit()
        return response
