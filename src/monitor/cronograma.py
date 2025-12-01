import time
import schedule


def main(self):

    # autoscraper
    hora_inicio = "09:41"
    schedule.every().day.at(hora_inicio).do(self.auto_scraper)
    self.log(action=f"[ SERVICIO ] CRON: Autoscraper diario a las {hora_inicio}.")

    # lanzar proceso
    while True:
        schedule.run_pending()
        time.sleep(60)
