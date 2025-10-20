from datetime import datetime as dt
from queue import Empty

# local imports
from src.scrapers import scrape_jneafil


def gather(dash, queue_update_data, local_response, total_original, lock):

    CARD = 9

    # log first action
    dash.log(
        card=CARD,
        title=f"JNE Afiliacion [{total_original}]",
        status=1,
        progress=100,
        text="Inicializando",
        lastUpdate="Actualizado:",
    )

    # iterate on every placa and write to database
    while not queue_update_data.empty():

        # grab next record from update queue unless empty
        try:
            id_member, doc_tipo, doc_num = queue_update_data.get_nowait()
        except Empty:
            break

        retry_attempts = 0
        while retry_attempts < 3:
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {doc_num}")

                # send request to scraper
                jne_response = scrape_jneafil.browser(doc_num)

                # update memberLastUpdate table with last update information
                _now = dt.now().strftime("%Y-%m-%d")

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((queue_update_data.qsize() / total_original) * 100),
                    lastUpdate=dt.now(),
                )

                # add foreign key, True/False flag and current date to scraper response
                with lock:
                    local_response.append(
                        {
                            "IdMember_FK": id_member,
                            "Afiliacion": bool(jne_response),
                            "ImageBytes": jne_response,
                            "LastUpdate": _now,
                        }
                    )

                dash.log(
                    action=f"[ JNE AFILIACIONES ] {'|'.join([str(i) for i in local_response[-1]])}"
                )

                # next record
                break

            except KeyboardInterrupt:
                quit()

            except Exception:
                retry_attempts += 1
                dash.log(
                    card=CARD,
                    text=f"|ADVERTENCIA| Reintentando [{retry_attempts}/3]: {doc_num}",
                )

    # log last action
    dash.log(
        card=CARD,
        title="JNE Afiliacion",
        progress=0,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
