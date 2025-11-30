from random import randrange as rr
from pprint import pprint


def main():

    dic = {}

    for b in (
        "brevete",
        "revtec",
        "recvehic",
        "soat",
        "satmul",
        "satimp",
        "sunarp",
        "sutran",
    ):
        dic2 = {}
        for a in ("status", "pendientes", "ETA", "ultimaactividad"):
            dic2.update({a: str(rr(99))})
        dic.update({b: dic2})

    return {"scrape_kpis": dic}
