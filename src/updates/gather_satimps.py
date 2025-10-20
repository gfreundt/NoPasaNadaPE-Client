from datetime import datetime as dt
import threading
import queue

# local imports
from src.scrapers import scrape_satimp
from src.utils.constants import GATHER_ITERATIONS


def manage_sub_threads(dash, update_data, full_response):

    # create variable that accumulates all sub-thread responses
    local_response_codigos, local_response_deudas = [], []

    # load queue with data that needs to be updated
    queue_update_data = queue.Queue()
    for item in update_data:
        queue_update_data.put(item)

    # launch and join N sub-threads for the main thread
    lock = threading.Lock()
    threads = []
    for _ in range(GATHER_ITERATIONS):
        t = threading.Thread(
            target=gather,
            args=(
                dash,
                queue_update_data,
                local_response_codigos,
                local_response_deudas,
                len(update_data),
                lock,
            ),
        )
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    # put all respones into global collector variables
    full_response.update({"DataSatImpuestosCodigos": local_response_codigos})
    full_response.update({"DataSatImpuestosDeudas": local_response_deudas})


def gather(
    dash,
    queue_update_data,
    local_response_codigos,
    local_response_deudas,
    total_original,
    lock,
):

    CARD = 3

    # log first action
    dash.log(
        card=CARD,
        title=f"Impuestos SAT [{total_original}]",
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
        except queue.Empty:
            break

        retry_attempts = 0

        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                dash.log(card=CARD, text=f"Procesando: {doc_tipo} {doc_num}")

                # send request to scraper
                new_records = scrape_satimp.browser(doc_tipo=doc_tipo, doc_num=doc_num)

                if not new_records:
                    with lock:
                        local_response_codigos.append(
                            {
                                "Empty": True,
                                "IdMember_FK": id_member,
                            }
                        )
                    break

                _now = dt.now().strftime("%Y-%m-%d")

                for _n in new_records:
                    with lock:
                        local_response_codigos.append(
                            {
                                "IdMember_FK": id_member,
                                "Codigo": _n["codigo"],
                                "LastUpdate": _now,
                            }
                        )
                    if _n["deudas"]:
                        for deuda in _n["deudas"]:
                            local_response_deudas.append(
                                {
                                    "Codigo": _n["codigo"],
                                    "Ano": deuda[0],
                                    "Periodo": deuda[1],
                                    "DocNum": deuda[2],
                                    "TotalAPagar": deuda[3],
                                    "FechaHasta": deuda[4],
                                    "LastUpdate": _now,
                                }
                            )
                    else:
                        local_response_deudas.append(
                            {
                                "Empty": True,
                                "Codigo": _n["codigo"],
                            }
                        )

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((queue_update_data.qsize() / total_original) * 100),
                    lastUpdate=dt.now(),
                )

                # next record
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

        # if code gets here, means scraping has encountred three consecutive errors, skip record
        dash.log(card=CARD, msg=f"|ERROR| No se pudo procesar {doc_tipo} {doc_num}.")

    # log last action
    dash.log(
        card=CARD,
        title="Impuestos SAT",
        progress=0,
        status=3,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
