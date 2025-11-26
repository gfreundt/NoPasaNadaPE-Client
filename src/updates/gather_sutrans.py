from datetime import datetime as dt
from queue import Empty

# local imports
from src.utils.utils import date_to_db_format
from src.scrapers import scrape_sutran


def gather(dash, queue_update_data, local_response, total_original, lock):

    CARD = 7

    # log first action
    dash.log(
        card=CARD,
        title=f"Sutran [{total_original}]",
        status=1,
        progress=0,
        text="Inicializando",
        lastUpdate="Actualizado:",
    )

    # iterate on all records that require updating and get scraper results
    while not queue_update_data.empty():

        # grab next record from update queue unless empty
        try:
            placa = queue_update_data.get_nowait()
        except Empty:
            break

        # loop to catch scraper errors and retry limited times
        try:
            # log action
            dash.log(card=CARD, text=f"Procesando: {placa}")

            # send request to scraper
            sutran_response = scrape_sutran.browser(placa=placa)

            _now = dt.now().strftime("%Y-%m-%d")

            # update dashboard with progress and last update timestamp
            dash.log(
                card=CARD,
                progress=int(
                    ((total_original - queue_update_data.qsize()) / total_original)
                    * 100
                ),
                lastUpdate=dt.now(),
            )

            # if response is blank, skip to next placa
            if not sutran_response:
                with lock:
                    local_response.append({"Empty": True, "PlacaValidate": placa})
                break

            # iterate on all multas
            for resp in sutran_response:
                _n = date_to_db_format(data=resp)
                with lock:
                    local_response.append(
                        {
                            "PlacaValidate": placa,
                            "Documento": _n[0],
                            "Tipo": _n[1],
                            "FechaDoc": _n[2],
                            "CodigoInfrac": _n[3],
                            "Clasificacion": _n[4],
                            "LastUpdate": _now,
                        }
                    )

                # insert gathered record of member
                dash.log(
                    action=f"[ SUTRANS ] {"|".join([str(i) for i in local_response[-1]])}"
                )

        except KeyboardInterrupt:
            quit()

        except Exception:
            dash.log(
                card=CARD,
                text="|ERROR| Proceso Incompleto",
            )
            return

    # log last action
    dash.log(
        card=CARD,
        title="Sutran",
        progress=100,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
