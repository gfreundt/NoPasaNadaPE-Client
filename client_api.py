import requests
from pprint import pprint
from src.utils.constants import EXTERNAL_AUTH_TOKEN, INTERNAL_AUTH_TOKEN
import json
import sys
import random


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


def sunarp_manual(url):

    return requests.post(
        url=url + "/admin",
        params={
            "token": INTERNAL_AUTH_TOKEN,
            "solicitud": "sunarp_manual",
        },
    )


def alta_prueba(url, correo):

    clientes = [
        {
            "celular": "",
            "codigo_externo": f"MAQ-{str(random.randrange(9999))}",
            "correo": correo,
            "nombre": "Es una prueba",
            "numero_documento": "",
            "tipo_documento": "",
        },
    ]

    return requests.post(
        url=url + "/api/v1",
        headers=HEADER,
        json={
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
        headers=HEADER,
        json={
            "usuario": "SEX-000",
            "solicitud": "baja",
            "clientes": clientes,
        },
    )


def mensajes_enviados_prueba(url):

    return requests.post(
        url=url + "/api/v1",
        headers=HEADER,
        json={
            "usuario": "SEX-000",
            "solicitud": "mensajes_enviados",
            "fecha_desde": "2025-12-01",
        },
    )


def clientes_autorizados(url):

    return requests.post(
        url=url + "/api/v1",
        headers=HEADER,
        json={
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


url = "https://dev.nopasanadape.com"  # DEV
# url = "http://localhost:5000"  # TEST
args = sys.argv

if len(args) < 2:
    print("Incompleto")
    quit()

HEADER = {
    "Authorization": "Bearer " + EXTERNAL_AUTH_TOKEN,
    "Content-Type": "application/json",
}

if args[1] == "ALTA":
    f = alta_prueba(url, args[2])
    pprint(json.loads(f.content.decode()))

if args[1] == "KILL":
    f = kill_prueba(url, args[2])
    pprint(json.loads(f.content.decode()))

if args[1] == "MSG":
    f = mensajes_enviados_prueba(url)
    pprint(json.loads(f.content.decode()))

if args[1] == "BAJA":
    f = baja_prueba(url, args[2])
    pprint(json.loads(f.content.decode()))

if args[1] == "CLI":
    f = clientes_autorizados(url)
    pprint(json.loads(f.content.decode()))

if args[1] == "SUNARP":
    f = sunarp_manual(url)
    pprint(json.loads(f.content.decode()))
