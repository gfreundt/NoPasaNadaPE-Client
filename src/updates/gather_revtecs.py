from datetime import datetime as dt, timedelta as td
import time
from queue import Empty

# local imports
from src.utils.utils import date_to_db_format
from src.scrapers import scrape_revtec
from src.utils.webdriver import ChromeUtils
from src.utils.constants import HEADLESS, GATHER_ITERATIONS


def gather(
    dash, queue_update_data, local_response, total_original, lock, card, subthread
):

    # construir webdriver con parametros especificos
    chromedriver = ChromeUtils(headless=HEADLESS["revtec"])
    webdriver = chromedriver.direct_driver()

    # registrar inicio en dashboard
    dash.log(
        card=card,
        title=f"Revisión Técnica ({subthread}) [Pendientes: {total_original}]",
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
            placa = queue_update_data.get_nowait()
        except Empty:
            # log de salida del scraper
            dash.log(
                card=card,
                title=f"Revisión Técnica ({subthread})",
                status=3,
                text="Inactivo",
                lastUpdate=f"Fin: {dt.now()}",
            )
            break

        # se tiene un registro, intentar extraer la informacion
        try:
            dash.log(card=card, text=f"Procesando: {placa}")

            # enviar registro a scraper
            revtec_response = scrape_revtec.browser_wrapper(
                placa=placa, webdriver=webdriver
            )

            # si respuesta es texto, hubo un error -- regresar
            if isinstance(revtec_response, str):
                dash.log(
                    card=card,
                    status=2,
                    lastUpdate=f"ERROR: {revtec_response}",
                )
                break

            # respuesta es en blanco
            if not revtec_response:
                with lock:
                    local_response.append(
                        {
                            "Empty": True,
                            "PlacaValidate": placa,
                        }
                    )
                continue

            # ajustar formato de fechas al de la base de datos (YYYY-MM-DD)
            _n = date_to_db_format(data=revtec_response)

            # agregar registo a acumulador de respuestas (compartido con otros scrapers)
            with lock:
                local_response.append(
                    {
                        "IdPlaca_FK": 999,
                        "Certificadora": _n[0],
                        "PlacaValidate": _n[2],
                        "Certificado": _n[3],
                        "FechaDesde": _n[4],
                        "FechaHasta": _n[5],
                        "Resultado": _n[6],
                        "Vigencia": _n[7],
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
                title=f"Revisión Técnica ({subthread}) [Pendientes: {queue_update_data.qsize()//GATHER_ITERATIONS}]",
                lastUpdate=f"ETA: {str(eta).split('.')[0]}",
            )
            dash.log(action=f"[ REVTECS ] {_n[2]}")

        except KeyboardInterrupt:
            quit()

        except Exception as e:
            dash.log(card=card, text=f"|REVTEC| Crash (Gather): {e}", status=2)
            return

    # cerrar el driver antes de volver
    webdriver.quit()
