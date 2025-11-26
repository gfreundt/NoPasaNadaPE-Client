from datetime import datetime as dt, timedelta as td
import time
from queue import Empty

# local imports
from src.utils.utils import date_to_db_format
from src.scrapers import scrape_brevete
from src.utils.webdriver import ChromeUtils
from src.utils.constants import HEADLESS, GATHER_ITERATIONS


def gather(
    dash, queue_update_data, local_response, total_original, lock, card, subthread
):

    # construir webdriver con parametros especificos
    chromedriver = ChromeUtils(headless=HEADLESS["brevetes"])
    webdriver = chromedriver.direct_driver()

    # registrar inicio en dashboard
    dash.log(
        card=card,
        title=f"Brevetes ({subthread}) [Pendientes: {total_original}]",
        status=1,
        lastUpdate="Calulando ETA...",
    )

    # iniciar variables para calculo de ETA
    tiempo_inicio = time.perf_counter()
    procesados = 0

    # iterar hasta vaciar la cola compartida con otras instancias del scraper
    while True:

        # intentar extraer siguiente registro de cola compartida
        try:
            id_member, doc_tipo, doc_num = queue_update_data.get_nowait()
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
            dash.log(card=card, text=f"Procesando: {doc_num}")

            # enviar registro a scraper
            brevete_response = scrape_brevete.browser_wrapper(
                doc_num=doc_num, webdriver=webdriver
            )

            # si respuesta es texto, hubo un error -- regresar
            if isinstance(brevete_response, str):
                dash.log(
                    card=card,
                    status=2,
                    lastUpdate=f"ERROR: {brevete_response}",
                )
                break

            # respuesta es en blanco
            if not brevete_response:
                with lock:
                    local_response.append(
                        {
                            "Empty": True,
                            "IdMember_FK": doc_num,
                        }
                    )
                continue

            # ajustar formato de fechas al de la base de datos (YYYY-MM-DD)
            _n = date_to_db_format(data=brevete_response)

            # agregar registo a acumulador de respuestas (compartido con otros scrapers)
            local_response.append(
                {
                    "IdMember_FK": id_member,
                    "Clase": _n[0],
                    "Numero": _n[1],
                    "Tipo": _n[2],
                    "FechaExp": _n[3],
                    "Restricciones": _n[4],
                    "FechaHasta": _n[5],
                    "Centro": _n[6],
                    "Puntos": _n[7],
                    "Record": _n[8],
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
                title=f"Brevetes ({subthread}) [Pendientes: {queue_update_data.qsize()//GATHER_ITERATIONS}]",
                lastUpdate=f"ETA: {str(eta).split('.')[0]}",
            )
            dash.log(action=f"[ BREVETES ] {_n[2]}")

        except KeyboardInterrupt:
            quit()

        except Exception as e:
            dash.log(card=card, text=f"|BREVETES| Crash (Gather): {e}", status=2)
            break

    # cerrar el driver antes de volver
    webdriver.quit()
