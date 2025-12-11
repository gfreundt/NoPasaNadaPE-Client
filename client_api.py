import requests
from pprint import pprint
from src.utils.constants import EXTERNAL_AUTH_TOKEN, INTERNAL_AUTH_TOKEN
import json


"""Simulacion de API de Maquinarias"""


def nuevo_pwd(url, correo):

    return requests.post(
        url=url + "/admin",
        params={
            "token": INTERNAL_AUTH_TOKEN,
            "solicitud": "nuevo_password",
            "correo": correo,
        },
    )


def alta_prueba(url, correo):

    clientes = [
        {
            "celular": "",
            "codigo_externo": "MAQ-007",
            "correo": correo,
            "nombre": "Luis La Torre",
            "numero_documento": "",
            "tipo_documento": "",
        },
    ]

    return requests.post(
        url=url + "/api/v1",
        json={
            "token": EXTERNAL_AUTH_TOKEN,
            "usuario": "USU-007",
            "solicitud": "alta",
            "clientes": clientes,
        },
    )


def baja_prueba(url, correo):

    clientes = [
        {
            "correo": correo,
        },
    ]

    return requests.post(
        url=url + "/api/v1",
        json={
            "token": EXTERNAL_AUTH_TOKEN,
            "usuario": "SEX-000",
            "solicitud": "baja",
            "clientes": clientes,
        },
    )


def mensajes_enviados_prueba(url):

    return requests.post(
        url=url + "/api/v1",
        json={
            "token": EXTERNAL_AUTH_TOKEN,
            "usuario": "SEX-000",
            "solicitud": "mensajes_enviados",
            "fecha_desde": "2025-12-01",
        },
    )


def clientes_autorizados(url):

    return requests.post(
        url=url + "/api/v1",
        json={
            "token": EXTERNAL_AUTH_TOKEN,
            "usuario": "SEX-000",
            "solicitud": "clientes_autorizados",
        },
    )


def kill_prueba(url, correo):

    return requests.post(
        url=url + "/admin",
        params={
            "token": INTERNAL_AUTH_TOKEN,
            "solicitud": "kill",
            "correo": correo,
        },
    )


correo = "lucholtc@gmail.com"
# url = "https://nopasanadape.com"  # PROD
# url = "http://localhost:5000"  # TEST
url = "https://dev.nopasanadape.com"  # DEV


# f = mensajes_enviados_prueba(url)
# f = nuevo_pwd(url,correo)
# f = kill_prueba(url, correo)
f = alta_prueba(url, correo)
# f = baja_prueba(url,correo)

pprint(f.status_code)
x = json.loads(f.content.decode())
pprint(x)
