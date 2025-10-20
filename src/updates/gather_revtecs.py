from datetime import datetime as dt
from queue import Empty

# local imports
from src.utils.utils import date_to_db_format
from src.scrapers import scrape_revtec


def gather(dash, queue_update_data, local_response, total_original, lock):

    CARD = 2

    # log first action
    dash.log(
        card=CARD,
        title=f"Revisión Técnica [{total_original}]",
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
        except Empty:
            break

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {placa}")

                # send request to scraper
                revtec_response = scrape_revtec.browser(placa=placa)

                # webpage is down: stop gathering and show error in dashboard
                if revtec_response == 404:
                    dash.log(
                        card=CARD,
                        status=2,
                        text="MTC offline",
                        lastUpdate=dt.now(),
                    )
                    return

                # update placas table with last update information
                _now = dt.now().strftime("%Y-%m-%d")

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((queue_update_data.qsize() / total_original) * 100),
                    lastUpdate=dt.now(),
                )

                # empty response if blank response from scraper
                if not revtec_response:
                    with lock:
                        local_response.append(
                            {
                                "Empty": True,
                                "PlacaValidate": placa,
                            }
                        )
                    break

                # adjust date to match db format (YYYY-MM-DD)
                _n = date_to_db_format(data=revtec_response)
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
                            "LastUpdate": _now,
                        }
                    )

                dash.log(
                    action=f"[ REVTECS ] {'|'.join([str(i) for i in local_response[-1]])}"
                )

                # skip to next record
                break

            except KeyboardInterrupt:
                quit()

            except Exception:
                retry_attempts += 1
                dash.log(
                    card=CARD,
                    text=f"|ADVERTENCIA| Reintentando [{retry_attempts}/3]: {placa}",
                )

    # log last action
    dash.log(
        card=CARD,
        title="Revisión Técnica",
        progress=0,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
