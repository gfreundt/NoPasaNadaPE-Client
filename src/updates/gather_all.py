import time
import os
import json
import atexit
import queue
from threading import Thread, Lock
from src.utils.constants import NETWORK_PATH, GATHER_ITERATIONS

# local imports
from src.updates import (
    gather_brevetes,
    gather_revtecs,
    gather_sutrans,
    gather_satimps,
    gather_recvehic,
    gather_sunarps,
    gather_satmuls,
    gather_sunats,
    gather_osipteles,
    gather_jnemultas,
    gather_jneafils,
    gather_soats,
)

# TODO: find a jnemultas with actual multas


def gather_threads(dash, all_updates):

    # log change of dashboard status
    dash.log(general_status=("Activo", 1))

    all_threads = []
    full_response = {}
    atexit.register(update_local_gather_file, full_response)

    # records vehiculares
    if all_updates.get("recvehic"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["recvehic"],
                    full_response,
                    gather_recvehic,
                    "DataMtcRecordsConductores",
                    1,
                ),
            )
        )

    # brevetes
    if all_updates.get("brevetes"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["brevetes"],
                    full_response,
                    gather_brevetes,
                    "DataMtcBrevetes",
                ),
            )
        )

    # multas sat
    if all_updates.get("satmuls"):
        all_threads.append(
            Thread(
                target=gather_satmuls.gather,
                args=(dash, all_updates["satmuls"], full_response),
            )
        )

    # revisiones tecnicas
    if all_updates.get("revtecs"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["revtecs"],
                    full_response,
                    gather_revtecs,
                    "DataMtcRevisionesTecnicas",
                ),
            )
        )

    # multas sutran
    if all_updates.get("sutrans"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["sutrans"],
                    full_response,
                    gather_sutrans,
                    "DataSutranMultas",
                ),
            )
        )

    # impuestos sat
    if all_updates.get("satimps"):
        all_threads.append(
            Thread(
                target=gather_satimps.manage_sub_threads,
                args=(dash, all_updates["satimps"], full_response),
            )
        )

    # sunat
    if all_updates.get("sunats"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["sunats"],
                    full_response,
                    gather_sunats,
                    "DataSunatRucs",
                ),
            )
        )

    # lineas osiptel
    if all_updates.get("osipteles"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["osipteles"],
                    full_response,
                    gather_osipteles,
                    "DataOsiptelLineas",
                ),
            )
        )

    # multas jne
    if all_updates.get("jnemultas"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["jnemultas"],
                    full_response,
                    gather_jnemultas,
                    "DataJneMultas",
                ),
            )
        )

    # afiliaciones jne
    if all_updates.get("jneafils"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["jneafils"],
                    full_response,
                    gather_jneafils,
                    "DataJneAfiliaciones",
                ),
            )
        )

    # fichas sunarp
    if all_updates.get("sunarps"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["sunarps"],
                    full_response,
                    gather_sunarps,
                    "DataSunarpFichas",
                ),
            )
        )

    # soat
    if all_updates.get("soats"):
        all_threads.append(
            Thread(
                target=manage_sub_threads,
                args=(
                    dash,
                    all_updates["soats"],
                    full_response,
                    gather_soats,
                    "DataApesegSoats",
                ),
            )
        )

    # start all threads with a time gap to avoid webdriver conflict
    for thread in all_threads:
        thread.start()
        time.sleep(1.5)

    # grabar cada 90 segundos lo que este en memoria de respuestas por si hay un error critico
    # y mas adelante poder actualizar manualmente la respuesta parcial
    start_time = time.perf_counter()
    while any(t.is_alive() for t in all_threads):
        time.sleep(10)
        if time.perf_counter() - start_time > 90:
            update_local_gather_file(full_response)
            start_time = time.perf_counter()

    # final log update
    dash.log(general_status=("Esperando", 2))

    # update local changes file and return all update data as a dictionary
    update_local_gather_file(full_response)
    return full_response


def manage_sub_threads(
    dash, update_data, full_response, target_func, update_key, iterations=None
):

    # create variable that accumulates all sub-thread responses
    local_response = []
    full_response[update_key] = local_response

    # load queue with data that needs to be updated
    queue_update_data = queue.Queue()
    for item in update_data:
        queue_update_data.put(item)

    # launch and join N sub-threads for the main thread
    lock = Lock()
    threads = []
    for i in range(iterations or GATHER_ITERATIONS):
        card = max(dash.assigned_cards) + 1 if dash.assigned_cards else 0
        dash.assigned_cards.append(card)
        t = Thread(
            target=target_func.gather,
            args=(
                dash,
                queue_update_data,
                local_response,
                len(update_data),
                lock,
                card,
                i,
            ),
            name=f"{target_func}-{i}",
        )
        t.start()
        threads.append(t)

    # wait for all active threads to finish
    start_time = time.perf_counter()
    while any([i.is_alive() for i in threads]):
        time.sleep(5)

        # update local gather file every 90 sec in case of fatal error get partial data
        if time.perf_counter() - start_time > 90:
            start_time = time.perf_counter()
            with lock:
                update_local_gather_file(full_response)

    # put all respones into global collector variable
    full_response.update({update_key: local_response})


def update_local_gather_file(full_response):
    update_files = [
        int(i[-10:-5])
        for i in os.listdir(os.path.join(NETWORK_PATH, "security"))
        if "update_" in i
    ]
    next_secuential = max(update_files) + 1
    with open(
        os.path.join(NETWORK_PATH, "security", f"update_{next_secuential:05d}.json"),
        mode="w",
    ) as outfile:
        outfile.write(json.dumps(full_response))
