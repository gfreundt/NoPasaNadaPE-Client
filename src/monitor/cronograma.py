import time
from datetime import datetime as dt, timedelta as td


def main(self):

    # autoscraper
    hora_inicio = "09:41"
    schedule.every().day.at(hora_inicio).do(self.auto_scraper)
    self.log(action=f"[ SERVICIO ] CRON: Autoscraper diario a las {hora_inicio}.")

    # lanzar proceso
    while True:
        if dt.now() > self.siguiente_cron:
            self.auto_scraper()
        time.sleep(60)
