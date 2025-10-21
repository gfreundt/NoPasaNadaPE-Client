from datetime import datetime as dt

# local imports
from src.utils.utils import date_to_db_format
from src.scrapers import scrape_brevete


def gather(dash, update_data, full_response):

    # add table to accumulation variable
    full_response.update({"DataMtcBrevetes": []})

    CARD = 0

    # log first action
    dash.log(
        card=CARD,
        title=f"Brevete [{len(update_data)}]",
        status=1,
        progress=100,
        text="Inicializando",
        lastUpdate="Actualizado:",
    )

    # iterate on all records that require updating and get scraper results
    for counter, (id_member, doc_tipo, doc_num) in enumerate(update_data):

        # skip member if doc tipo is not DNI (CE mostly) - should have been filtered, double check
        if doc_tipo != "DNI":
            continue

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {doc_tipo} {doc_num}")

                # send request to scraper
                brevete_response = scrape_brevete.browser(doc_num=doc_num)

                # update memberLastUpdate table with last update information
                _now = dt.now().strftime("%Y-%m-%d")

                # next record if blank response from scraper
                if not brevete_response:
                    full_response["DataMtcBrevetes"].append(
                        {"Empty": True, "IdMember_FK": id_member}
                    )
                    break

                # go to next record if no brevete info
                if brevete_response == -1:
                    continue

                # adjust date to match db format (YYYY-MM-DD)
                _n = date_to_db_format(data=brevete_response)

                # add foreign key and current date to scraper response
                full_response["DataMtcBrevetes"].append(
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
                        "LastUpdate": _now,
                    }
                )

                dash.log(
                    action=f'[ BREVETES ] {"|".join([str(i) for i in full_response["DataMtcBrevetes"][-1]])}'
                )

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((counter / len(update_data)) * 100),
                    lastUpdate=dt.now(),
                )

                # no errors - next member and resent consecutive exceptions counter
                consecutive_exceptions = 0
                break

            except KeyboardInterrupt:
                quit()

            except Exception:

                # control general browser/webpage errors to stop scraping completely
                consecutive_exceptions += 1
                if consecutive_exceptions > 5:
                    dash.log(
                        card=CARD,
                        msg=f"|ADVERTENCIA| Error {doc_tipo}-{doc_num}.",
                        status=2,
                        lastUpdate=dt.now(),
                    )

                # control individual record to skip it
                retry_attempts += 1
                dash.log(
                    card=CARD, msg=f"|ADVERTENCIA| Reintentando {doc_tipo}-{doc_num}."
                )

    # log last action
    dash.log(
        card=CARD,
        title="Brevetes",
        progress=0,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
