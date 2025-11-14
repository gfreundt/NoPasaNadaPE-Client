import os
import io
import base64
import time
from datetime import datetime as dt
from copy import deepcopy as copy
from queue import Empty
from PIL import Image, ImageDraw, ImageFont

# local imports
from src.utils.utils import date_to_db_format, use_truecaptcha, change_vpn_manually
from src.scrapers import scrape_soat
from src.utils.constants import ASEGURADORAS, NETWORK_PATH


def gather(dash, queue_update_data, local_response, total_original, lock):

    CARD = 5

    # log first action
    dash.log(
        card=CARD,
        title=f"Certificados Soat [{total_original}]",
        status=1,
        progress=100,
        text="Inicializando",
        lastUpdate="Actualizado:",
    )

    # iterate on every placa and write to database
    while not queue_update_data.empty():

        # grab next record from update queue unless empty
        try:
            placa = queue_update_data.get_nowait()
            print("placa", placa)
        except Empty:
            break

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            scraper = scrape_soat.Soat()
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {placa}")

                # grab captcha image from website and solve and send to scraper
                captcha_file_like = scraper.get_captcha()
                captcha = use_truecaptcha(captcha_file_like)["result"]
                response_soat = scraper.browser(placa=placa, captcha_txt=captcha)

                # wrong captcha / no data - try three times if not skip record
                if response_soat == -1 and retry_attempts < 2:
                    retry_attempts += 1
                    continue
                elif response_soat == -1:
                    break

                # superado el limite de consultas
                if response_soat == -2:
                    print("*********** LIMITE CONSULTAS SOAT ************")
                    dash.log(card=CARD, text="Cambiando VPN", status=1)

                    # avisa a usuario para cambiar de VPN
                    time.sleep(1)
                    attempt = change_vpn_manually()
                    if not attempt:
                        dash.log(card=CARD, text="Error Cambiando VPN", status=1)
                        return
                    else:
                        break

                # fatal webdriver error, restart attempt
                if response_soat == -3:
                    retry_attempts += 1
                    continue

                # data correcta, proceder
                _n = date_to_db_format(data=response_soat)
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

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((queue_update_data.qsize() / total_original) * 100),
                    lastUpdate=dt.now(),
                )
                dash.log(
                    action=f'[ SOATS ] {"|".join([str(i) for i in local_response[-1].values()])}'
                )

                # no errors - next member, reset limite counter
                break

            except KeyboardInterrupt:
                quit()

            # except Exception:
            #     retry_attempts += 1
            #     dash.log(
            #         card=CARD,
            #         text=f"|ADVERTENCIA| Reintentando [{retry_attempts}/3]: {placa}",
            #     )

        # if code gets here, means scraping has encountred three consecutive errors, skip record
        dash.log(card=CARD, msg=f"|ERROR| No se pudo procesar {placa}.")

    # log last action and close webdriver
    dash.log(
        card=CARD,
        title="Certificados Soat",
        progress=0,
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
