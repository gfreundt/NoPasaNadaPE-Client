from datetime import datetime as dt
from queue import Empty

# local imports
from src.scrapers import scrape_recvehic


def gather(dash, queue_update_data, local_response, total_original, lock):

    CARD = 1

    # log first action
    dash.log(
        card=CARD,
        title=f"Record Conductor [{total_original}]",
        status=1,
        progress=100,
        text="Inicializando",
        lastUpdate="Actualizado:",
    )

    # iterate on all records that require updating and get scraper results
    while not queue_update_data.empty():

        # grab next record from update queue unless empty
        try:
            id_member, doc_tipo, doc_num = queue_update_data.get_nowait()
        except Empty:
            break

        # records are only available for members with DNI
        if doc_tipo != "DNI":
            continue

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {doc_tipo} {doc_num}")

                # send request to scraper
                pdf_bytes = scrape_recvehic.browser(doc_num=doc_num)

                # update memberLastUpdate table with last update information
                _now = dt.now().strftime("%Y-%m-%d")

                # response from scraper is that there is no record
                if pdf_bytes == -1:
                    with lock:
                        local_response.append({"Empty": True, "IdMember_FK": id_member})
                    break

                # stop process if blank response from scraper
                if not pdf_bytes:
                    dash.log(
                        card=CARD,
                        status=2,
                        text="Scraper crash",
                        lastUpdate=dt.now(),
                    )
                    return

                # add response
                with lock:
                    local_response.append(
                        {
                            "IdMember_FK": id_member,
                            "ImageBytes": pdf_bytes,
                            "LastUpdate": _now,
                        }
                    )

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((queue_update_data.qsize() / total_original) * 100),
                    lastUpdate=dt.now(),
                )

                # no errors - next member
                break

            except KeyboardInterrupt:
                quit()

            except Exception:
                retry_attempts += 1
                dash.log(
                    card=CARD,
                    status=2,
                    text=f"|ADVERTENCIA| Reintentando [{retry_attempts}/3]: {doc_tipo} {doc_num}",
                )

    # log last action
    dash.log(
        card=CARD,
        title="Record del Conductor",
        progress=0,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
