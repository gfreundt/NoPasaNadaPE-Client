from src.utils.constants import NETWORK_PATH, UPDATER_TOKEN, SERVER_IP, SERVER_IP_TEST
from src.updates import gather_all
import requests
from flask import jsonify, redirect
import time, json, os


def actualizar_alerta(self):
    _json = {
        "token": UPDATER_TOKEN,
        "instruction": "actualizar_alerta",
    }
    actualizar_alerta = requests.post(url=self.url, json=_json)

    return actualizar_alerta.json()


def actualizar(self, actualizar_alerta):
    scraper_responses = gather_all.gather_threads(
        dash=self, all_updates=actualizar_alerta
    )
    with open("latest_update.json", "w") as outfile:
        outfile.write(json.dumps(scraper_responses))

    _json = {
        "token": UPDATER_TOKEN,
        "instruction": "do_updates",
        "data": scraper_responses,
    }
    server_response = requests.post(url=self.url, json=_json)
    if server_response.status_code == 200:
        self.log(
            action=f"ACTUALIZAR: Completo - Envio: {len(json.dumps(scraper_responses).encode("utf-8")) / 1024 / 1024:.2f} MB",
        )
    else:
        self.log(action=f"[ERROR] Actualizacion: {server_response.status_code}")


def crear_mensajes(self):
    # borrar todos los mensajes antiguos
    _json = {
        "token": UPDATER_TOKEN,
        "instruction": "create_messages",
    }
    created_messages = requests.post(url=self.url, json=_json).json()
    return created_messages


def enviar_correo_resumen(self, mensaje):
    print(mensaje)


def enviar_alertas(self):
    _json = {
        "token": UPDATER_TOKEN,
        "instruction": "send_messages",
    }
    sent_messages = requests.post(url=self.url, json=_json)
    self.log(action=f"*** Mensajes enviados: {sent_messages.content}")

    return redirect("/")


def main(self):

    # 1. solicitar alertas que requieren actualizacion, actualizar y grabar
    repetir = 0
    while True:

        # solicitar alertas pendientes para enviar a actualizar
        alertas = actualizar_alerta(self)

        # si ya no hay actualizaciones pendientes, siguiente paso
        if all([len(j) == 0 for j in alertas.values()]):
            break
        else:
            actualizar(self, alertas)
            repetir += 1
            if repetir > 3:
                enviar_correo_resumen(self, "Error")
                return "error scrapers"
            time.sleep(1)

    # 2. crear correos de alertas
    f = crear_mensajes(self)
    enviar_correo_resumen(self, f"Mensajes creados: {len(f)}")
    return f"Mensajes creados: {len(f)}"

    # 3. enviar correos de alertas
    # enviar_alertas(self)
