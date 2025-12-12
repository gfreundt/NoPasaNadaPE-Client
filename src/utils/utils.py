from datetime import datetime as dt
import os
import re
import time
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException
import base64
import socket
import json
import subprocess


# import pyautogui
# from pyautogui import ImageNotFoundException
from selenium.webdriver.common.by import By
from src.utils.constants import (
    MONTHS_3_LETTERS,
    TWOCAPTCHA_API_KEY,
    PUSHBULLET_API_TOKEN,
    NETWORK_PATH,
    OVPN_CONFIG,
)


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


def use_truecaptcha(image, retries=3):
    """
    Recibe imagen y la envia al servicio externo de deteccion TRUECAPTCHA
    para transformarlo en texto

    :param image: Objeto en Bytes
    :param retries: Cuantas veces volver a intentar si el servicio esta offline

    Correcto: retorna diccionario, con el texto en llave "result"
    Error: retorna False
    """

    # legacy: transform received path to object
    if type(image) is str:
        image = open(image, "rb")

    retry_attempts = 0
    _url = "https://api.apitruecaptcha.org/one/gettext"
    _data = {
        "userid": "gabfre@gmail.com",
        "apikey": "UEJgzM79VWFZh6MpOJgh",
        "data": base64.b64encode(image.read()).decode("ascii"),
    }
    while True:
        try:
            response = requests.post(url=_url, json=_data)
            return response.json()
        except ConnectionError:
            retry_attempts += 1
            if retry_attempts <= retries:
                time.sleep(10)
                continue
            return False


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
    try:
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

    except Exception:
        return False


def base64_to_image(base64_string, output_path):
    try:
        image_data = base64.b64decode(base64_string)
        with open(output_path, "wb") as file:
            file.write(image_data)
    except Exception as e:
        print(f"An error occurred (base64_to_image): {e}")


def send_pushbullet(title, message=""):

    # do not accept blank title
    if not title:
        return False

    API_URL = "https://api.pushbullet.com/v2/pushes"
    payload = {"type": "note", "title": title, "body": message}

    try:
        response = requests.post(
            API_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            auth=(PUSHBULLET_API_TOKEN, ""),
        )

        if response.status_code == 200:
            return True
        else:
            return False

    except (Timeout, ConnectionError, RequestException):
        return False


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))  # connect() for UDP doesn't send packets
    return s.getsockname()[0]


def get_public_ip():
    """Fetches the current public IP address."""
    try:
        # Use a reliable IP check service (e.g., ipify.org)
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["ip"]
    except requests.RequestException as e:
        print(f"Error fetching IP: {e}")
        return None


def check_vpn_online():
    """
    Revisa si el VPN esta en linea.
    Si el Network Prefix del IP es diferente a del ISP, retorna True
    """
    current_ip = get_public_ip()
    if current_ip and current_ip[:3] != "190":
        return True


def start_vpn(location_code):
    """
    Triggers the pre-configured, elevated task in the Windows Task Scheduler.
    """
    task_name = OVPN_CONFIG[location_code]["task_name"]
    command = ["schtasks", "/run", "/tn", task_name]

    try:
        # Use subprocess.run() for this short, blocking command
        subprocess.run(
            command,
            check=True,  # Raise an exception if the command fails
            capture_output=True,
            text=True,
        )
        time.sleep(10)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def stop_vpn():
    """
    Checks defined ports, identifies the active VPN, and shuts it down.
    """
    task_name = r"\GFT\Kill openvpn.exe"
    command = ["schtasks", "/run", "/tn", task_name]

    try:
        # Use subprocess.run() for this short, blocking command
        subprocess.run(
            command,
            check=True,  # Raise an exception if the command fails
            capture_output=True,
            text=True,
        )
        time.sleep(10)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
