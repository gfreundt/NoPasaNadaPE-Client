from datetime import datetime as dt
import os
import re
import time
import requests
import base64
import socket
import random
import pyautogui
from pyautogui import ImageNotFoundException
from src.utils.constants import MONTHS_3_LETTERS, NETWORK_PATH


def date_to_db_format(data):
    """Takes dd.mm.yyyy date formats with different separators and returns yyyy-mm-dd."""

    # define valid patterns, everything else is returned as is
    pattern1 = r"^(0[1-9]|[12][0-9]|3[01])[/-](0[1-9]|1[012])[/-]\d{4}$"
    pattern2 = r"^\d{2}-[a-zA-Z]{3}-\d{4}$"

    new_record_dates_fixed = []

    for data_item in data:

        # test to determine if format is date we can change to db format
        try:
            if re.fullmatch(pattern1, data_item):
                # if record has date structure, alter it, everything else throws exception and no changes made
                sep = "/" if "/" in data_item else "-" if "-" in data_item else None
                new_record_dates_fixed.append(
                    dt.strftime(dt.strptime(data_item, f"%d{sep}%m{sep}%Y"), "%Y-%m-%d")
                )
            elif re.fullmatch(pattern2, data_item):
                # month in 3 letters to number
                _m = MONTHS_3_LETTERS.index(data_item[3:6]) + 1
                # if record has date structure, alter it, everything else throws exception and no changes made
                new_record_dates_fixed.append(
                    f"{data_item[7:]}-{_m:02}-{data_item[:2]}"
                )

            else:
                new_record_dates_fixed.append(data_item)

        except Exception:
            new_record_dates_fixed.append(data_item)

    return new_record_dates_fixed


def date_to_mail_format(fecha, delta=False):
    _day = fecha[8:]
    _month = MONTHS_3_LETTERS[int(fecha[5:7]) - 1]
    _year = fecha[:4]
    _deltatxt = ""
    if delta:
        _delta = int((dt.strptime(fecha, "%Y-%m-%d") - dt.now()).days)
        _deltatxt = f"[ {_delta:,} días ]" if _delta > 0 else "[ VENCIDO ]"
    return f"{_day}-{_month}-{_year} {_deltatxt}"


def date_to_user_format(fecha):
    # change date format to a more legible one
    _months = (
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    )
    _day = fecha[8:]
    _month = _months[int(fecha[5:7]) - 1]
    _year = fecha[:4]

    return f"{_day}-{_month}-{_year}"


def use_truecaptcha(image):

    # legacy: transform received path to object
    if type(image) is str:
        image = open(image, "rb")

    _url = "https://api.apitruecaptcha.org/one/gettext"
    _data = {
        "userid": "gabfre@gmail.com",
        "apikey": "UEJgzM79VWFZh6MpOJgh",
        "data": base64.b64encode(image.read()).decode("ascii"),
    }
    response = requests.post(url=_url, json=_data)
    return response.json()


def base64_to_image(base64_string, output_path):
    try:
        image_data = base64.b64decode(base64_string)
        with open(output_path, "wb") as file:
            file.write(image_data)
    except Exception as e:
        print(f"An error occurred (base64_to_image): {e}")


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))  # connect() for UDP doesn't send packets
    return s.getsockname()[0]


def change_vpn_manually():
    COUNTRIES = [
        "Alemania",
        "Argentina",
        "Argelia",
        "Brasil",
        "Ecuador",
        "Espa",
        "Egipto",
        "Atlanta",
        "Miami",
        "Phoenix",
        "Letonia",
        "Venezuela",
        "Uruguay",
        "Nueva Ze",
    ]

    new_vpn = random.choice(COUNTRIES)

    while True:
        try:
            x = pyautogui.locateCenterOnScreen(
                os.path.join(NETWORK_PATH, "static", "arrowVPN.png"),
                region=(2500, 1200, 4000, 1800),
                confidence=0.7,
            )
            pyautogui.click(x)
            time.sleep(1)
            for i in new_vpn:
                pyautogui.press(i)
                time.sleep(0.2)
            pyautogui.moveRel((-380, -390))
            pyautogui.click()
            time.sleep(3)
            return True

        except (ValueError, ImageNotFoundException):
            try:
                x = pyautogui.locateCenterOnScreen(
                    os.path.join(NETWORK_PATH, "static", "iconVPN.png"),
                    region=(2000, 2050, 2800, 2180),
                    confidence=0.9,
                )
                time.sleep(1)
                pyautogui.click(x)
            except (ValueError, ImageNotFoundException):
                return False
