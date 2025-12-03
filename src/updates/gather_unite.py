from datetime import datetime as dt, timedelta as td
from queue import Empty
import time
from func_timeout import exceptions
from copy import deepcopy as copy

# local imports (Placeholder for your specific imports)
# You would need to ensure these imports are available in the environment
from src.scrapers import (
    scrape_recvehic,
    scrape_sunarp,
    scrape_sutran,
    scrape_soat,
    scrape_satmul,
    scrape_satimp,
    scrape_revtec,
    scrape_brevete,
)
from src.utils.webdriver import ChromeUtils
from src.utils.constants import HEADLESS, ASEGURADORAS, NETWORK_PATH
from src.utils.utils import date_to_db_format
from PIL import Image, ImageDraw, ImageFont
import os
import io
import base64


def generic_gather(
    dash,
    queue_update_data,
    local_response,
    total_original,
    lock,
    card,
    subthread,
    config,
):
    """
    Centralized function to gather data for various scraping services.

    Args:
        dash: Dashboard object for logging updates.
        queue_update_data: Shared Queue for records to process.
        local_response: List to accumulate scraped results.
        total_original: Total number of records initially.
        lock: Threading Lock for shared resource access.
        card: Dashboard card ID.
        subthread: Subthread index.
        config: Dictionary containing service-specific configuration.
    """

    # Configuration extraction
    service_name = config["service_name"]
    driver_config = config["driver_config"]
    scraper_func = config["scraper_func"]
    get_queue_item = config["get_queue_item"]
    prepare_scraper_args = config["prepare_scraper_args"]
    process_response = config["process_response"]

    # 1. Build WebDriver
    chromedriver = ChromeUtils(**driver_config)
    webdriver = chromedriver.direct_driver()
    same_ip_scrapes = 0  # Only used/managed for SOAT, but harmless for others

    # 2. Initialize ETA variables
    tiempo_inicio = time.perf_counter()
    procesados = 0
    eta = 0

    while True:
        record_item = None
        try:
            # 3. Get next record from queue
            record_item = queue_update_data.get_nowait()
            display_info, scraper_id_args = get_queue_item(record_item)

        except Empty:
            # Log exit and break loop
            dash.log(
                card=card,
                title=f"{service_name}-{subthread}",
                status=3,
                text="Inactivo",
                lastUpdate=f"Fin: {dt.strftime(dt.now(),'%H:%M:%S')}",
            )
            break

        # 4. Main processing loop (with error handling)
        try:
            # Log start of processing
            dash.log(
                card=card,
                title=f"{service_name}-{subthread} [Pendientes: {total_original - procesados}]",
                status=1,
                text=f"Procesando: {display_info}",
                lastUpdate=f"ETA: {eta}",
            )

            # (SOAT specific: IP restart logic)
            if service_name == "SOATS" and same_ip_scrapes > 10:
                webdriver.quit()
                webdriver = chromedriver.proxy_driver()
                same_ip_scrapes = 0

            # Prepare arguments and call scraper
            scraper_args = prepare_scraper_args(scraper_id_args, webdriver, lock)
            scraper_response = scraper_func(**scraper_args)

            same_ip_scrapes += 1
            procesados += 1

            # 5. Handle Scraper Response (Error/Retry)
            if isinstance(scraper_response, str) and len(scraper_response) < 100:
                dash.log(card=card, status=2, lastUpdate=f"ERROR: {scraper_response}")

                # Return record to queue
                if record_item is not None:
                    queue_update_data.put(record_item)

                # Retry logic
                if "@" in scraper_response:
                    dash.log(card=card, text="Reinicio en 10 segundos", status=1)
                    time.sleep(10)
                    continue

                # Fatal error, break thread
                break

            # 6. Handle Empty Response
            if not scraper_response:
                empty_data = {"Empty": True, **scraper_id_args}
                # SUNARP, SUTRAN, SATMUL, SOAT, REVTEC use PlacaValidate.
                # RECVEHIC and BREVETES use IdMember_FK.
                # Add service-specific empty response handling if needed,
                # but generic dict merging is often enough.
                with lock:
                    local_response.append(empty_data)
                dash.log(action=f"[ {service_name} ] {display_info}")
                continue

            # 7. Process Successful Response
            with lock:
                process_response(scraper_response, scraper_id_args, local_response)

            # 8. Calculate ETA
            duracion_promedio = (time.perf_counter() - tiempo_inicio) / procesados
            eta = dt.strftime(
                dt.now()
                + td(seconds=duracion_promedio * (total_original - procesados)),
                "%H:%M:%S",
            )

            dash.log(action=f"[ {service_name} ] {display_info}")

        except exceptions.FunctionTimedOut:
            if record_item is not None:
                queue_update_data.put(record_item)
            dash.log(card=card, status=2, lastUpdate="ERROR: Timeout")
            # Continue or break depending on service policy for timeouts
            if service_name == "BREVETES" or service_name == "SATMULS":
                break  # Original files break on timeout
            continue

        except KeyboardInterrupt:
            quit()

        except Exception as e:
            # Handle general crash
            if record_item is not None:
                queue_update_data.put(record_item)
            dash.log(
                card=card,
                text=f"Crash (Gather): {str(e)[:55]}",
                status=2,
            )
            break

    # 9. Close WebDriver
    webdriver.quit()


# --- Service-Specific Configuration Dictionaries ---


## 1. MTC Records Vehiculares (RecVehic)
def recvehic_get_queue_item(record_item):
    id_member, doc_tipo, doc_num = record_item
    display_info = f"{doc_tipo} {doc_num}"
    scraper_id_args = {
        "IdMember_FK": id_member,
        "doc_tipo": doc_tipo,
        "doc_num": doc_num,
    }
    return display_info, scraper_id_args


def recvehic_prepare_scraper_args(scraper_id_args, webdriver, lock):
    return {"doc_num": scraper_id_args["doc_num"], "webdriver": webdriver, "lock": lock}


def recvehic_process_response(scraper_response, scraper_id_args, local_response):
    local_response.append(
        {
            "IdMember_FK": scraper_id_args["IdMember_FK"],
            "ImageBytes": scraper_response,
            "LastUpdate": dt.now().strftime("%Y-%m-%d"),
        }
    )


RECVEHIC_CONFIG = {
    "service_name": "Record Vehicular",
    "driver_config": {"headless": HEADLESS["revtec"]},
    "scraper_func": scrape_recvehic.browser_wrapper,
    "get_queue_item": recvehic_get_queue_item,
    "prepare_scraper_args": recvehic_prepare_scraper_args,
    "process_response": recvehic_process_response,
}


## 2. SUNARPS (Fichas Sunarp)
def sunarp_get_queue_item(record_item):
    placa = record_item
    display_info = placa
    scraper_id_args = {"PlacaValidate": placa}
    return display_info, scraper_id_args


def sunarp_prepare_scraper_args(scraper_id_args, webdriver, lock):
    # lock is not used by sunarp scraper but we pass it for consistency
    return {"placa": scraper_id_args["PlacaValidate"], "webdriver": webdriver}


def sunarp_process_response(scraper_response, scraper_id_args, local_response):
    _now = dt.now().strftime("%Y-%m-%d")
    local_response.append(
        {
            "IdPlaca_FK": 999,
            "PlacaValidate": scraper_id_args["PlacaValidate"],
            # ... other fields from scraper_response ...
            "ImageBytes": scraper_response,  # Assuming scraper_response is the image bytes
            "LastUpdate": _now,
        }
    )


SUNARPS_CONFIG = {
    "service_name": "SUNARPS",
    "driver_config": {
        "headless": HEADLESS["sunarp"],
        "incognito": True,
        "window_size": (1920, 1080),
    },
    "scraper_func": scrape_sunarp.browser_wrapper,
    "get_queue_item": sunarp_get_queue_item,
    "prepare_scraper_args": sunarp_prepare_scraper_args,
    "process_response": sunarp_process_response,
}


## 3. SUTRAN (Multas Sutran)
def sutran_get_queue_item(record_item):
    placa = record_item
    display_info = placa
    scraper_id_args = {"PlacaValidate": placa}
    return display_info, scraper_id_args


def sutran_prepare_scraper_args(scraper_id_args, webdriver, lock):
    return {"placa": scraper_id_args["PlacaValidate"], "webdriver": webdriver}


def sutran_process_response(scraper_response, scraper_id_args, local_response):
    # scraper_response is a list of multas
    for resp in scraper_response:
        _n = date_to_db_format(data=resp)
        local_response.append(
            {
                "PlacaValidate": scraper_id_args["PlacaValidate"],
                "Documento": _n[0],
                "Tipo": _n[1],
                "FechaDoc": _n[2],
                "CodigoInfrac": _n[3],
                "Clasificacion": _n[4],
                "LastUpdate": dt.now().strftime("%Y-%m-%d"),
            }
        )


SUTRANS_CONFIG = {
    "service_name": "Sutran",
    "driver_config": {"headless": HEADLESS["revtec"]},  # Uses revtec HEADLESS config
    "scraper_func": scrape_sutran.browser_wrapper,
    "get_queue_item": sutran_get_queue_item,
    "prepare_scraper_args": sutran_prepare_scraper_args,
    "process_response": sutran_process_response,
}


## 4. SOATS (Apeseg Soats)
def soat_get_queue_item(record_item):
    placa = record_item
    display_info = placa
    scraper_id_args = {"PlacaValidate": placa}
    return display_info, scraper_id_args


def soat_prepare_scraper_args(scraper_id_args, webdriver, lock):
    return {"placa": scraper_id_args["PlacaValidate"], "webdriver": webdriver}


def soat_process_response(scraper_response, scraper_id_args, local_response):
    _n = date_to_db_format(data=scraper_response)
    local_response.append(
        {
            "IdPlaca_FK": 999,
            "Aseguradora": _n[0],
            "FechaInicio": _n[2],
            "FechaHasta": _n[3],
            "PlacaValidate": _n[4],
            # ... other fields ...
            "ImageBytes": create_certificate(data=copy(_n)),
            "LastUpdate": dt.now().strftime("%Y-%m-%d"),
        }
    )


SOATS_CONFIG = {
    "service_name": "SOATS",
    "driver_config": {
        "headless": HEADLESS["soat"],
        "incognito": True,
        "window_size": (1920, 1080),
    },
    "scraper_func": scrape_soat.browser_wrapper,
    "get_queue_item": soat_get_queue_item,
    "prepare_scraper_args": soat_prepare_scraper_args,
    "process_response": soat_process_response,
}


## 5. SAT Multas (SatMuls)
def satmul_get_queue_item(record_item):
    placa = record_item
    display_info = placa
    scraper_id_args = {"PlacaValidate": placa}
    return display_info, scraper_id_args


def satmul_prepare_scraper_args(scraper_id_args, webdriver, lock):
    return {"placa": scraper_id_args["PlacaValidate"], "webdriver": webdriver}


def satmul_process_response(scraper_response, scraper_id_args, local_response):
    # scraper_response is a list of multas
    for resp in scraper_response:
        _n = date_to_db_format(data=resp)
        local_response.append(
            {
                "IdPlaca_FK": 999,
                "PlacaValidate": _n[0],
                "Reglamento": _n[1],
                # ... other fields ...
                "ImageBytes2": _n[14] if len(_n) > 14 else "",
                "LastUpdate": dt.now().strftime("%Y-%m-%d"),
            }
        )


SATMULS_CONFIG = {
    "service_name": "Multas SAT",
    "driver_config": {
        "headless": HEADLESS["satmul"],
        "incognito": True,
        "window_size": (1920, 1080),
    },
    "scraper_func": scrape_satmul.browser_wrapper,
    "get_queue_item": satmul_get_queue_item,
    "prepare_scraper_args": satmul_prepare_scraper_args,
    "process_response": satmul_process_response,
}


## 6. SAT Impuestos (SatImps)
# Note: SAT Impuestos is complex as it returns two lists (codigos and deudas)
# It requires a custom `manage_sub_threads` logic (as seen in gather_satimps.py)
# so full centralization into a single `gather` function is not ideal without
# a major refactor of `manage_sub_threads` in `gather_all.py`.
# For the purpose of *centralizing* the `gather` logic, we will define its
# config but acknowledge the need for a separate manager function.


def satimp_get_queue_item(record_item):
    id_member, doc_tipo, doc_num = record_item
    display_info = f"{doc_tipo} {doc_num}"
    scraper_id_args = {
        "IdMember_FK": id_member,
        "doc_tipo": doc_tipo,
        "doc_num": doc_num,
    }
    return display_info, scraper_id_args


def satimp_prepare_scraper_args(scraper_id_args, webdriver, lock):
    return {
        "doc_tipo": scraper_id_args["doc_tipo"],
        "doc_num": scraper_id_args["doc_num"],
        "webdriver": webdriver,
    }


def satimp_process_response(scraper_response, scraper_id_args, local_response):
    # This requires local_response to be a tuple/list of two lists (codigos, deudas),
    # which breaks the simple local_response list pattern.
    # We define a placeholder to show the required structure.
    local_response_codigos = local_response[
        0
    ]  # Assumes local_response is passed as a list of shared lists
    local_response_deudas = local_response[1]

    _now = dt.now().strftime("%Y-%m-%d")
    for _n in scraper_response:
        local_response_codigos.append(
            {
                "IdMember_FK": scraper_id_args["IdMember_FK"],
                "Codigo": _n["codigo"],
                "LastUpdate": _now,
            }
        )
        # ... logic for deudas ...


SATIMPS_CONFIG_PLACEHOLDER = {
    "service_name": "Impuestos SAT",
    "driver_config": {"headless": HEADLESS["revtec"]},
    "scraper_func": scrape_satimp.browser_wrapper,
    "get_queue_item": satimp_get_queue_item,
    "prepare_scraper_args": satimp_prepare_scraper_args,
    "process_response": satimp_process_response,  # Custom logic needed
}


## 7. Revisiones Técnicas (RevTecs)
def revtec_get_queue_item(record_item):
    placa = record_item
    display_info = placa
    scraper_id_args = {"PlacaValidate": placa}
    return display_info, scraper_id_args


def revtec_prepare_scraper_args(scraper_id_args, webdriver, lock):
    return {"placa": scraper_id_args["PlacaValidate"], "webdriver": webdriver}


def revtec_process_response(scraper_response, scraper_id_args, local_response):
    _n = date_to_db_format(data=scraper_response)
    local_response.append(
        {
            "IdPlaca_FK": 999,
            "Certificadora": _n[0],
            "PlacaValidate": _n[2],
            # ... other fields ...
            "LastUpdate": dt.now().strftime("%Y-%m-%d"),
        }
    )


REVTECS_CONFIG = {
    "service_name": "Revisión Técnica",
    "driver_config": {"headless": HEADLESS["revtec"]},
    "scraper_func": scrape_revtec.browser_wrapper,
    "get_queue_item": revtec_get_queue_item,
    "prepare_scraper_args": revtec_prepare_scraper_args,
    "process_response": revtec_process_response,
}


## 8. Brevetes (MTC Brevetes)
def brevete_get_queue_item(record_item):
    id_member, doc_tipo, doc_num = record_item
    display_info = f"{doc_tipo} {doc_num}"
    scraper_id_args = {
        "IdMember_FK": id_member,
        "doc_tipo": doc_tipo,
        "doc_num": doc_num,
    }
    return display_info, scraper_id_args


def brevete_prepare_scraper_args(scraper_id_args, webdriver, lock):
    return {"doc_num": scraper_id_args["doc_num"], "webdriver": webdriver}


def brevete_process_response(scraper_response, scraper_id_args, local_response):
    _n = date_to_db_format(data=scraper_response)
    local_response.append(
        {
            "IdMember_FK": scraper_id_args["IdMember_FK"],
            "Clase": _n[0],
            # ... other fields ...
            "LastUpdate": dt.now().strftime("%Y-%m-%d"),
        }
    )


BREVETES_CONFIG = {
    "service_name": "Brevetes",
    "driver_config": {"headless": HEADLESS["brevetes"]},
    "scraper_func": scrape_brevete.browser_wrapper,
    "get_queue_item": brevete_get_queue_item,
    "prepare_scraper_args": brevete_prepare_scraper_args,
    "process_response": brevete_process_response,
}

# --- Export Mapped Configurations ---
# This dictionary would be used by `gather_all.py` to map the service name
# to the correct configuration for calling `generic_gather`.
GATHER_CONFIGS = {
    "recvehic": RECVEHIC_CONFIG,
    "sunarps": SUNARPS_CONFIG,
    "sutrans": SUTRANS_CONFIG,
    "soats": SOATS_CONFIG,
    "satmuls": SATMULS_CONFIG,
    "revtecs": REVTECS_CONFIG,
    "brevetes": BREVETES_CONFIG,
    # satimps remains special and should use its own `manage_sub_threads`
    # which calls its own simplified `gather` or a specially configured `generic_gather`.
}


# To use this, you would refactor `gather_all.py`'s `manage_sub_threads` to call
# `generic_gather` with the appropriate configuration object.
def gather(*args, **kwargs):
    """Alias for the centralized function to maintain original signature style."""
    return generic_gather(*args, **kwargs)
