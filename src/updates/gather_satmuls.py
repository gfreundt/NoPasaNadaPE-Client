from datetime import datetime as dt

# local imports
from src.utils.utils import date_to_db_format
from src.scrapers import scrape_satmul


def gather(dash, update_data, full_update):

    full_update.update({"DataSatMultas": []})

    CARD = 4

    # log first action
    dash.log(
        card=CARD,
        title=f"Multas SAT Lima [{len(update_data)}]",
        status=1,
        progress=0,
        text="Inicializando",
        lastUpdate="Actualizado:",
    )

    # iterate on every placa and write to database
    for counter, placa in enumerate(update_data, start=1):

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {placa}")

                # send request to scraper
                response_satmul = scrape_satmul.browser(placa=placa)

                # captcha timeout - manual user not there to enter captcha, skip process
                if response_satmul == -1:
                    # add the response captured so far
                    dash.log(
                        card=CARD,
                        title="Multas SAT Lima",
                        status=2,
                        text="Captcha Service Offline",
                        lastUpdate=dt.now(),
                    )
                    return True  # tells gather all that user has timed out

                # valid but blank response
                if not response_satmul:
                    full_update["DataSatMultas"].append(
                        {
                            "Empty": True,
                            "PlacaValidate": placa,
                        }
                    )

                # if there is data in response, enter into database, go to next placa
                else:
                    _now = dt.now().strftime("%Y-%m-%d")
                    for resp in response_satmul:

                        # adjust date to match db format (YYYY-MM-DD)
                        _n = date_to_db_format(data=resp)
                        full_update["DataSatMultas"].append(
                            {
                                "IdPlaca_FK": 999,
                                "PlacaValidate": _n[0],
                                "Reglamento": _n[1],
                                "Falta": _n[2],
                                "Documento": _n[3],
                                "FechaEmision": _n[4],
                                "Importe": _n[5],
                                "Gastos": _n[6],
                                "Descuento": _n[7],
                                "Deuda": _n[8],
                                "Estado": _n[9],
                                "Licencia": _n[10],
                                "DocTipoSatmul": _n[11],
                                "DocNumSatmul": _n[12],
                                "ImageBytes1": _n[13],
                                "ImageBytes2": _n[14] if len(_n) > 14 else "",
                                "LastUpdate": _now,
                            }
                        )

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((counter / len(update_data)) * 100),
                    lastUpdate=dt.now(),
                )

                # no errors - update database and next member
                break

            except KeyboardInterrupt:
                quit()

            # except Exception:
            #     retry_attempts += 1
            #     dash.log(
            #         card=CARD,
            #         text=f"|ADVERTENCIA| Reintentando [{retry_attempts}/3]: {placa}",
            #     )

        # if code gets here, means scraping has encountred three consecutive errors, skip record
        dash.log(card=CARD, msg=f"|ERROR| No se pudo procesar {placa}.")

    # log last action
    dash.log(
        card=CARD,
        title="Multas SAT Lima",
        progress=100,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
