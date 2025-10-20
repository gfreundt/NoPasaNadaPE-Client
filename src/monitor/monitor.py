from flask import Flask, render_template, jsonify, redirect
import threading
import logging
from copy import deepcopy as copy
import os
from datetime import datetime as dt
import requests
import subprocess
import json
from collections import deque
import time
from pprint import pprint
from src.utils.utils import get_local_ip
from src.utils.constants import NETWORK_PATH, UPDATER_TOKEN, SERVER_IP, SERVER_IP_TEST
from src.updates import gather_all
from src.test import tests


logging.getLogger("werkzeug").disabled = True


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

        # Define routes
        self.app.add_url_rule("/", endpoint="/", view_func=self.dashboard)
        self.app.add_url_rule("/data", "get_data", self.get_data)
        self.app.add_url_rule("/log/get", "log_get", self.log_get)

        self.app.add_url_rule(
            "/registros_pendientes",
            endpoint="registros_pendientes",
            view_func=self.registros_pendientes,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/actualizar",
            endpoint="actualizar",
            view_func=self.actualizar,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/crear_mensajes",
            endpoint="crear_mensajes",
            view_func=self.crear_mensajes,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/rp_act_cm",
            endpoint="rp_act_cm",
            view_func=self.rp_act_cm,
            methods=["POST"],
        )

        self.app.add_url_rule(
            "/enviar_mensajes",
            endpoint="enviar_mensajes",
            view_func=self.enviar_mensajes,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/test",
            endpoint="test",
            view_func=self.hacer_tests,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/logs",
            endpoint="logs",
            view_func=self.actualizar_logs,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/db_info",
            endpoint="db_info",
            view_func=self.db_info,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/db_backup",
            endpoint="db_backup",
            view_func=self.db_backup,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/actualizar_de_json",
            endpoint="actualizar_de_json",
            view_func=self.actualizar_de_json,
            methods=["POST"],
        )

        self.set_initial_data()
        self.update_kpis()

    def dashboard(self):
        return render_template("dashboard.html")

    def log(self, **kwargs):
        if "general_status" in kwargs:
            self.data["top_right"]["content"] = kwargs["general_status"][0]
            self.data["top_right"]["status"] = kwargs["general_status"][1]
            # write to permanent log in database
        if "action" in kwargs:
            _ft = f"{dt.now():%Y-%m-%d %H:%M:%S} > {kwargs["action"]}"
            self.log_entries.append(_ft)
        if "card" in kwargs:
            for field in kwargs:
                if field == "card":
                    continue
                self.data["cards"][kwargs["card"]][field] = kwargs[field]
        if "usuario" in kwargs:
            _ft = f"<b>{dt.now():%Y-%m-%d %H:%M:%S} ></b>{kwargs["usuario"]}"
            self.data["bottom_left"].append(_ft)
            if len(self.data["bottom_left"]) > 30:
                self.data["bottom_left"].pop(0)
            # write to permanent log in database

        # any time there is an action, update kpis
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
            "cards": [copy(empty_card) for _ in range(12)],
            "bottom_left": [],
            "bottom_right": [],
        }

    def update_kpis(self):
        # get number of users
        # self.db.cursor.execute("SELECT COUNT( ) FROM members")
        # self.data.update({"kpi_members": self.db.cursor.fetchone()[0]})

        # # get number of placas
        # self.db.cursor.execute("SELECT COUNT( ) FROM placas")
        # self.data.update({"kpi_placas": self.db.cursor.fetchone()[0]})

        # get balance left in truecaptcha
        try:
            url = r"https://api.apiTruecaptcha.org/one/hello?method=get_all_user_data&userid=gabfre%40gmail.com&apikey=UEJgzM79VWFZh6MpOJgh"
            r = requests.get(url)
            self.data.update(
                {
                    "kpi_truecaptcha_balance": r.json()["data"]["get_user_info"][4][
                        "value"
                    ]
                }
            )
        except ConnectionError:
            self.data.update({"truecaptcha_balance": "N/A"})

    def get_data(self):
        with self.data_lock:
            return jsonify(self.data)

    def registros_pendientes(self):
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "get_records_to_update",
        }
        self.records_to_update = requests.post(url=self.url, json=_json)
        _msg = "REGISTROS PENDIENTES: " + "  ".join(
            [f"{i} = {len(j)}" for i, j in self.records_to_update.json().items()]
        )
        self.log(action=_msg)

        return redirect("/")

    def actualizar(self):
        if not hasattr(self, "records_to_update"):
            self.log(action="ACTUALIZAR: ERROR - Correr Registros Pendientes Antes")
        else:
            self.log(action="ACTUALIZAR: En proceso")

            scraper_responses = gather_all.gather_threads(
                dash=self, all_updates=self.records_to_update.json()
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

        return redirect("/")

    def crear_mensajes(self):
        # Borrar todos los mensajes antiguos
        for i in os.listdir(os.path.join(NETWORK_PATH, "outbound")):
            os.remove(os.path.join(NETWORK_PATH, "outbound", i))

        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "create_messages",
        }
        created_messages = requests.post(url=self.url, json=_json).json()
        for i in created_messages:
            with open(
                os.path.join(NETWORK_PATH, "outbound", i), "w", encoding="utf-8"
            ) as outfile:
                outfile.write(created_messages[i])
        print(f"*** Mensajes Creados: {len(created_messages)}")

        return redirect("/")

    def rp_act_cm(self):
        self.registros_pendientes()
        time.sleep(3)
        self.actualizar()
        time.sleep(3)
        self.crear_mensajes()
        return redirect("/")

    def enviar_mensajes(self):
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "send_messages",
        }
        sent_messages = requests.post(url=self.url, json=_json)
        print(f"*** Mensajes enviados: {sent_messages.content}")

        return redirect("/")

    def hacer_tests(self):
        try:
            tests.main()
        except KeyboardInterrupt:
            print("*** Cannot execute test (server offline?)")
        return redirect("/")

    def db_info(self):
        _json = {"token": UPDATER_TOKEN, "instruction": "get_info_data"}
        response = requests.post(url=self.url, json=_json).json()
        response.update({"Timestamp": str(dt.now())})
        with open(
            os.path.join(NETWORK_PATH, "security", "latest_info.json"), mode="w"
        ) as outfile:
            json.dump(response, outfile)
        print("*** DB Info Actualizada")
        return redirect("/")

    def actualizar_logs(self):
        _json = {"token": UPDATER_TOKEN, "instruction": "get_logs", "max": 100}
        response = requests.post(url=self.url, json=_json)
        with open(
            os.path.join(NETWORK_PATH, "security", "latest_logs.json"), mode="w"
        ) as outfile:
            outfile.write(response.text)
            print("*** Logs Actualizados")
        return redirect("/")

    def db_backup(self):
        print("Iniciando DB Backup Local...")
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
            "nopasanadape@34.59.226.241:/home/nopasanadape/NoPasaNadaPE/server/data/members.db",
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
            print("*** DB Backup Local Correcto")
        else:
            print("Error de Backup:", result.stderr)

        return redirect("/")

    def actualizar_de_json(self):
        with open(
            os.path.join(NETWORK_PATH, "security", "last_update.json"), "r"
        ) as file:
            scraper_responses = json.load(file)
        print(
            "Payload Size: ",
            len(json.dumps(scraper_responses).encode("utf-8")) / 1024 / 1024,
            "MB",
        )
        _json = {
            "token": UPDATER_TOKEN,
            "instruction": "do_updates",
            "data": scraper_responses,
        }
        server_response = requests.post(url=self.url, json=_json)
        if server_response.status_code == 200:
            print("Actualizacion Completa")
        else:
            print(f"Error Enviando Actualizacion: {server_response.status_code}")
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


if __name__ == "__main__":
    app_instance = Dashboard(db=None)
    app_instance.run()
