from flask import Flask, render_template, jsonify, redirect
import threading
import inspect
import logging
from copy import deepcopy as copy
import os
from datetime import datetime as dt
import requests
import subprocess
import json
from collections import deque
import time
from src.monitor import settings, auto_scraper
from src.utils import maintenance
from src.utils.utils import get_local_ip, check_vpn_online
from src.utils.constants import (
    NETWORK_PATH,
    UPDATER_TOKEN,
    SERVER_IP,
    SERVER_IP_TEST,
)
from src.updates import gather_all
from src.test import tests
from src.monitor import update_kpis, update_scraper_status

from pprint import pprint


logging.getLogger("werkzeug").disabled = True


class ThreadMonitor:
    def __init__(self, include_prefixes=None, include_files=None, interval=1):

        self.include_prefixes = include_prefixes or []
        self.include_files = include_files or []
        self.interval = interval

    def is_user_thread(self, thread):
        return True
        """Return True only if the thread matches your filters."""

        # 1. Filter by thread name prefix (recommended)
        if self.include_prefixes:
            if any(thread.name.startswith(p) for p in self.include_prefixes):
                return True

        # 2. Filter by file where the thread target function lives
        if self.include_files:
            target = getattr(thread, "_target", None)
            if target:
                try:
                    file = inspect.getsourcefile(target) or ""
                except Exception:
                    file = ""
                if any(x in file for x in self.include_files):
                    return True

        return False

    def start(self):
        def run():
            while True:
                self.user_threads = [
                    t for t in threading.enumerate() if self.is_user_thread(t)
                ]
                time.sleep(self.interval)

        monitor_thread = threading.Thread(
            target=run, name="ThreadMonitorDaemon", daemon=True
        )
        monitor_thread.start()


class Dashboard:
    def __init__(self, test):
        self.app = Flask(
            __name__,
            template_folder=os.path.join(NETWORK_PATH, "templates"),
            static_folder=os.path.join(NETWORK_PATH, "static"),
        )
        self.data_lock = threading.Lock()
        self.url = f"{SERVER_IP_TEST if test else SERVER_IP}/update"
        self.log_entries = deque(maxlen=55)
        self.data = {"activities": ""}
        self.thread_monitor = ThreadMonitor()
        self.thread_monitor.start()
        self.assigned_cards = []

        # definir rutas de flask
        settings.set_routes(self)

        self.set_initial_data()
        self.update_kpis()

    def set_initial_data(self):
        empty_card = {
            "title": "No Asignado",
            "progress": 0,
            "msg": [],
            "status": 0,
            "text": "Inactivo",
            "lastUpdate": "Pendiente",
        }
        self.data = {
            "top_left": "No Pasa Nada Dashboard",
            "top_right": {"content": "Inicializando...", "status": 0},
            "cards": [copy(empty_card) for _ in range(32)],
            "bottom_left": [],
            "bottom_right": [],
        }

    def log(self, **kwargs):
        if "general_status" in kwargs:
            self.data["top_right"]["content"] = kwargs["general_status"][0]
            self.data["top_right"]["status"] = kwargs["general_status"][1]
            # write to permanent log in database

        if "action" in kwargs:
            _ft = f"{dt.now():%Y-%m-%d %H:%M:%S} > {kwargs["action"]}"
            self.log_entries.append(_ft)
            self.data["bottom_left"].append(_ft[:140])

        if "card" in kwargs:
            for field in kwargs:
                if field == "card":
                    continue
                self.data["cards"][kwargs["card"]][field] = kwargs[field]

        if "usuario" in kwargs:
            _ft = f"<b>{dt.now():%Y-%m-%d %H:%M:%S} ></b>{kwargs["usuario"]}"
            self.data["bottom_left"].append(_ft[:140])
            if len(self.data["bottom_left"]) > 30:
                self.data["bottom_left"].pop(0)

        # any time there is an action, update kpis
        self.update_kpis()

    def update_kpis(self):
        """
        actualiza informacion de vigencia/saldo de servicios de terceros
        """
        kpis = update_kpis.main()
        self.data.update(kpis)
        # status = update_scraper_status.main(self.das)
        # self.data.update(status)

    # -------- ACCION DE URL DE INGRESO --------
    def dashboard(self):
        return render_template("dashboard.html")

    # ------- ACCIONES DE APIS (INTERNO) -------
    def auto_scraper(self):
        print(f"********* AUTOSCRAPER TRIGGERED {dt.now()}")
        self.auto_scraper_continue_flag = True
        auto_scraper.main(self)
        return redirect("/")

    def get_data(self):
        """
        endpoint for dashboard to update continually on dashboard information:
        sends back a dictionary (self.data)
        """
        with self.data_lock:
            return jsonify(self.data)

    # -------- ACCIONES DE BOTONES ----------
    def datos_alerta(self):
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "datos_alerta",
        }
        self.actualizar_datos = requests.post(url=self.url, json=_json)
        _msg = "[ DATOS ALERTA ] " + " ".join(
            [f"{i}: {len(j)}" for i, j in self.actualizar_datos.json().items()]
        )
        self.log(action=_msg)
        return redirect("/")

    def datos_boletin(self):
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "datos_boletin",
        }
        self.actualizar_datos = requests.post(url=self.url, json=_json)
        _msg = "[ DATOS BOLETIN ] " + " ".join(
            [f"{i[:4]}={len(j)}" for i, j in self.actualizar_datos.json().items()]
        )
        self.log(action=_msg)

        return redirect("/")

    def actualizar(self):

        # detener si VPN no esta en linea
        if not check_vpn_online():
            self.log(
                action="[ ACTUALIZACION ] ERROR - VPN no esta en linea.",
            )
            # cambiar flag para detener autoscraper si solicitud de actualizar vino de ahi
            self.auto_scraper_continue_flag = True

            return redirect("/")

        if not hasattr(self, "actualizar_datos"):
            self.log(
                action="[ ACTUALIZACION ] ERROR - Correr Registros Pendientes Antes"
            )
        else:
            self.log(action="[ ACTUALIZACION ] En proceso")

            scraper_responses = gather_all.gather_threads(
                dash=self, all_updates=self.actualizar_datos.json()
            )
            _json = {
                "token": UPDATER_TOKEN,
                "instruction": "do_updates",
                "data": scraper_responses,
            }
            server_response = requests.post(url=self.url, json=_json)
            if server_response.status_code == 200:
                self.log(
                    action=f"[ ACTUALIZACION ] Tamaño: {len(json.dumps(scraper_responses).encode("utf-8")) / 1024:.3f} kB",
                )
            else:
                self.log(action=f"[ERROR] Actualizacion: {server_response.status_code}")

            # borrar informacion de datos para actualizar, obliga a actualizarlos otra vez
            delattr(self, "actualizar_datos")

        return redirect("/")

    def generar_alertas(self):

        # borrar todos los mensajes antiguos
        maintenance.clear_outbound_folder(tipo="alertas")

        # dar comando al servidor
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "generar_alertas",
        }
        self.created_messages = requests.post(url=self.url, json=_json).json()

        # grabar copia local de los mensjes generados por el servidor
        for secuencial, texto in enumerate(self.created_messages, start=1):
            with open(
                os.path.join(NETWORK_PATH, "outbound", f"alerta-{secuencial:04d}.html"),
                "w",
                encoding="utf-8",
            ) as outfile:
                outfile.write(texto)
        self.log(
            action=f"[ CREAR MENSAJES ] Mensajes Creados: {len(self.created_messages)}"
        )

        # mantenerse en la misma pagina
        return redirect("/")

    def generar_boletines(self):

        # borrar todos los mensajes antiguos
        maintenance.clear_outbound_folder(tipo="boletines")

        # dar comando al servidor
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "generar_boletines",
        }
        self.created_messages = requests.post(url=self.url, json=_json).json()

        # grabar copia local de los mensjes generados por el servidor
        for secuencial, texto in enumerate(self.created_messages, start=1):
            with open(
                os.path.join(
                    NETWORK_PATH, "outbound", f"boletin-{secuencial:04d}.html"
                ),
                "w",
                encoding="utf-8",
            ) as outfile:
                outfile.write(texto)
        self.log(
            action=f"[ CREAR MENSAJES ] Mensajes Creados: {len(self.created_messages)}"
        )

        # mantenerse en la misma pagina
        return redirect("/")

    def enviar_mensajes(self):
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "send_messages",
        }
        sent_messages = requests.post(url=self.url, json=_json)
        self.log(action=f"*** Mensajes enviados: {sent_messages.content}")

        return redirect("/")

    def hacer_tests(self):
        try:
            tests.main(self)
        except KeyboardInterrupt:
            self.log(action="*** Cannot execute test (server offline?)")
        return redirect("/")

    def db_info(self):
        _json = {"token": UPDATER_TOKEN, "instruction": "get_info_data"}
        response = requests.post(url=self.url, json=_json).json()
        response.update({"Timestamp": str(dt.now())})
        with open(
            os.path.join(NETWORK_PATH, "security", "latest_info.json"), mode="w"
        ) as outfile:
            json.dump(response, outfile)
        self.log(action="DB Info Actualizada")
        return redirect("/")

    def actualizar_logs(self):
        _json = {"token": UPDATER_TOKEN, "instruction": "get_logs", "max": 100}
        response = requests.post(url=self.url, json=_json)
        with open(
            os.path.join(NETWORK_PATH, "security", "latest_logs.json"), mode="w"
        ) as outfile:
            outfile.write(response.text)
            self.log(action="Logs Actualizados")
        return redirect("/")

    def db_backup(self):
        cmd = [
            "scp",
            "-i",
            f"{NETWORK_PATH}/security/virtual_machine_access",
            "-o",
            "IdentitiesOnly=yes",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "StrictHostKeyChecking=no",
            "nopasanadape@35.208.218.61:/home/nopasanadape/NoPasaNadaPE-Server/data/members.db",
            f"{NETWORK_PATH}/security/",
        ]
        # copy file from remote server
        result = subprocess.run(cmd, capture_output=True, text=True)

        # rename file to append current timestamp
        _now = dt.now().strftime("%Y-%m-%d_%H.%M.%S")

        os.rename(
            os.path.join(NETWORK_PATH, "security", "members.db"),
            os.path.join(NETWORK_PATH, "security", f"members_backup_{_now}.db"),
        )

        if result.returncode == 0:
            self.log(action="*** DB Backup Local Correcto")
        else:
            self.log(action="Error de Backup:" + result.stderr)

        return redirect("/")

    def actualizar_de_json(self):
        with open(
            os.path.join(NETWORK_PATH, "security", "last_update.json"), "r"
        ) as file:
            scraper_responses = json.load(file)
        self.log(
            action="Payload Size: "
            + str(len(json.dumps(scraper_responses).encode("utf-8")) / 1024 / 1024)
            + " MB",
        )
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "do_updates",
            "data": scraper_responses,
        }
        server_response = requests.post(url=self.url, json=_json)
        if server_response.status_code == 200:
            self.log(action="*** Actualizacion Completa")
        else:
            self.log(
                action=f"Error Enviando Actualizacion: {server_response.status_code}"
            )
        return redirect("/")

    def log_get(self):
        return jsonify(log="\n".join(self.log_entries))

    def run_in_background(self):
        flask_thread = threading.Thread(target=self.run, daemon=True)
        flask_thread.start()
        return flask_thread

    def runx(self):
        print(f"MONITOR RUNNING ON: http://{get_local_ip()}:7400")
        self.app.run(debug=False, threaded=True, host="0.0.0.0", port=7400)
