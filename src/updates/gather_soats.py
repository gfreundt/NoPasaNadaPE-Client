import os
import io
import base64
from datetime import datetime as dt, timedelta as td
from copy import deepcopy as copy
from queue import Empty
from PIL import Image, ImageDraw, ImageFont
import time

# local imports
from src.utils.utils import date_to_db_format
from src.scrapers import scrape_soat as scraper
from src.utils.constants import ASEGURADORAS, NETWORK_PATH, HEADLESS, GATHER_ITERATIONS
from src.utils.webdriver import ChromeUtils


def gather(
    dash, queue_update_data, local_response, total_original, lock, card, subthread
):

    # construir webdriver con parametros especificos
    chromedriver = ChromeUtils(
        headless=HEADLESS["soat"],
        incognito=True,
        window_size=(1920, 1080),
    )
    webdriver = chromedriver.proxy_driver()
    same_ip_scrapes = 0

    # registrar inicio en dashboard
    dash.log(
        card=card,
        title=f"Soat ({subthread}) [Pendientes: {total_original}]",
        status=1,
        lastUpdate="Calculando ETA...",
    )

    # iniciar variables para calculo de ETA
    tiempo_inicio = time.perf_counter()
    procesados = 0

    # iterar hasta vaciar la cola compartida con otras instancias del scraper
    while True:

        # intentar extraer siguiente registro de cola compartida
        try:
            placa = queue_update_data.get_nowait()
        except Empty:
            # log de salida del scraper
            dash.log(
                card=card,
                status=3,
                text="Inactivo",
                lastUpdate=f"Fin: {dt.now()}",
            )
            break

        # se tiene un registro, intentar extraer la informacion
        try:
            dash.log(card=card, text=f"Procesando: {placa}")

            # si se esta llegando al limite con un mismo IP, reiniciar con IP nuevo
            if same_ip_scrapes > 10:
                webdriver.quit()
                webdriver = chromedriver.proxy_driver()

            # aumentar contador de usos del mismo IP y mandar a scraper
            same_ip_scrapes += 1
            soat_response = scraper.browser_wrapper(placa=placa, webdriver=webdriver)

            # si respuesta es texto, hubo un error -- regresar
            if isinstance(soat_response, str):
                dash.log(
                    card=card,
                    status=2,
                    lastUpdate=f"ERROR: {soat_response}",
                )
                break

            # placa no genera resultados
            if not soat_response:
                with lock:
                    local_response.append({"Empty": True, "PlacaValidate": placa})
                    break

            # placa si tiene resultados
            _n = date_to_db_format(data=soat_response)
            with lock:
                local_response.append(
                    {
                        "IdPlaca_FK": 999,
                        "Aseguradora": _n[0],
                        "FechaInicio": _n[2],
                        "FechaHasta": _n[3],
                        "PlacaValidate": _n[4],
                        "Certificado": _n[5],
                        "Uso": _n[6],
                        "Clase": _n[7],
                        "Vigencia": _n[1],
                        "Tipo": _n[8],
                        "FechaVenta": _n[9],
                        "ImageBytes": create_certificate(data=copy(_n)),
                        "LastUpdate": dt.now().strftime("%Y-%m-%d"),
                    }
                )

            # calcular ETA aproximado
            procesados += 1
            duracion_promedio = (time.perf_counter() - tiempo_inicio) / procesados
            eta = dt.now() + td(
                seconds=duracion_promedio
                * (queue_update_data.qsize() // GATHER_ITERATIONS)
            )

            # actualizar dashboard
            dash.log(
                card=card,
                title=f"Soat ({subthread}) [Pendientes: {queue_update_data.qsize()//GATHER_ITERATIONS}]",
                lastUpdate=f"ETA: {str(eta).split('.')[0]}",
            )
            dash.log(action=f"[ SOATS ] {_n[2]}")

        except KeyboardInterrupt:
            quit()

        except Exception as e:
            dash.log(card=card, text=f"Crash (Gather): {e}", status=2)

    # log last action and close webdriver
    dash.log(
        card=card,
        title="Certificados Soat",
        progress=100,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )


def create_certificate(data):

    # load fonts
    _resources = os.path.join(r"D:\pythonCode", "Resources", "Fonts")
    font_small = ImageFont.truetype(os.path.join(_resources, "seguisym.ttf"), 30)
    font_large = ImageFont.truetype(os.path.join(_resources, "seguisym.ttf"), 45)

    # get list of available company logos
    _templates_path = os.path.join(NETWORK_PATH, "static")
    cias = [i.split(".")[0] for i in os.listdir(_templates_path)]

    # open blank template image and prepare for edit
    base_img = Image.open(os.path.join(_templates_path, "SOAT_base.png"))
    editable_img = ImageDraw.Draw(base_img)

    # turn date into correct format for certificate
    # data[1] = dt.strftime(dt.strptime(data[1], "%Y-%m-%d"), "%d/%m/%Y")
    # data[2] = dt.strftime(dt.strptime(data[2], "%Y-%m-%d"), "%d/%m/%Y")

    # if logo in database add it to image, else add word
    if data[0] in cias:
        logo = Image.open(os.path.join(_templates_path, f"{data[0]}.png"))
        logo_width, logo_height = logo.size
        logo_pos = (10 + (340 - logo_width) // 2, 250 + (120 - logo_height) // 2)

        # add insurance company logo to image
        base_img.paste(logo, logo_pos)

        _phone = ASEGURADORAS.get(data[0])

        # add insurance company phone number to image
        editable_img.text(
            (400, 275), _phone if _phone else "", font=font_large, fill=(59, 22, 128)
        )
    else:
        editable_img.text(
            (40, 275), data[0].upper(), font=font_large, fill=(59, 22, 128)
        )

    # positions for each text in image
    coordinates = [
        (40, 516, 4),
        (40, 588, 1),
        (40, 665, 2),
        (337, 588, 1),
        (337, 665, 2),
        (40, 819, 3),
        (40, 897, 6),
        (40, 970, 5),
        (406, 971, 1),
    ]

    # loop through all positions and add them to image
    for a, b, c in coordinates:
        editable_img.text((a, b), data[c].upper(), font=font_small, fill=(59, 22, 128))

    # Save image to memory buffer
    buffer = io.BytesIO()
    base_img = base_img.convert("RGB")
    base_img.save(buffer, format="JPEG")
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")
