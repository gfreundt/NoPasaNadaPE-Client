from datetime import datetime as dt
from queue import Empty

# local imports
from src.scrapers import scrape_sunarp


def gather(dash, queue_update_data, local_response, total_original, lock):

    CARD = 6

    # log first action
    dash.log(
        card=CARD,
        title=f"Fichas Sunarp [{total_original}]",
        status=1,
        progress=100,
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

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {placa}")

                # send request to scraper
                image_bytes = scrape_sunarp.browser(placa=placa)

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((queue_update_data.qsize() / total_original) * 100),
                    lastUpdate=dt.now(),
                )

                # correct captcha, no image for placa - next placa
                if not image_bytes:
                    break

                _now = dt.now().strftime("%Y-%m-%d")

                # add foreign key and current date to response
                with lock:
                    local_response.append(
                        {
                            "IdPlaca_FK": 999,
                            "PlacaValidate": placa,
                            "Serie": "",
                            "VIN": "",
                            "Motor": "",
                            "Color": "",
                            "Marca": "",
                            "Modelo": "",
                            "Ano": "",
                            "PlacaVigente": "",
                            "PlacaAnterior": "",
                            "Estado": "",
                            "Anotaciones": "",
                            "Sede": "",
                            "Propietarios": "",
                            "ImageBytes": image_bytes,
                            "LastUpdate": _now,
                        }
                    )

                # skip to next record
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
        title="Fichas Sunarp",
        status=3,
        progress=0,
        text="Inactivo",
        lastUpdate=dt.now(),
    )


# TODO: move to post-processing
def extract_data_from_image(img_filename):
    return [""] * 13
