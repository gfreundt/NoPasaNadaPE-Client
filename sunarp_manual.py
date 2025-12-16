from datetime import datetime as dt, timedelta as td
import os
import json

# local imports
from src.scrapers import scrape_sunarp_manual
from src.utils.webdriver import ChromeUtils
from src.utils.utils import NETWORK_PATH


def gather(data):

    response = []

    # construir webdriver con parametros especificos
    chromedriver = ChromeUtils(
        headless=False,
        incognito=True,
        window_size=(1920, 1080),
    )
    # webdriver = chromedriver.proxy_driver()
    webdriver = chromedriver.direct_driver()

    # iniciar variables para calculo de ETA
    for placa in data:

        # send request to scraper
        scraper_response = scrape_sunarp_manual.browser(
            placa=placa, webdriver=webdriver
        )

        # si respuesta es texto, hubo un error -- regresar
        if isinstance(scraper_response, str) and len(scraper_response) < 100:
            print(f"Error con {placa}")
            break

        # respuesta es en blanco
        if not scraper_response:
            response.append(
                {
                    "Empty": True,
                    "PlacaValidate": placa,
                }
            )
            continue

        _now = dt.now().strftime("%Y-%m-%d")

        # add foreign key and current date to response
        response.append(
            {
                "IdPlaca_FK": 999,
                "PlacaValidate": placa,
                "Serie": "",
                "VIN": "",
                "Motor": "",
                "Color": "",
                "Marca": "",
                "Modelo": "",
                "Ano": "",
                "PlacaVigente": "",
                "PlacaAnterior": "",
                "Estado": "",
                "Anotaciones": "",
                "Sede": "",
                "Propietarios": "",
                "ImageBytes": scraper_response,
                "LastUpdate": _now,
            }
        )

        with open(
            os.path.join(NETWORK_PATH, "security", "update_manual_sunarp.json"),
            mode="a",
        ) as outfile:
            outfile.write(json.dumps(response))

    webdriver.quit()


data = ["CRN441"]  # , 'CBW476', 'CJA223']
gather(data)
