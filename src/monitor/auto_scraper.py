from src.utils.constants import AUTOSCRAPER_REPETICIONES
import time


def enviar_correo_resumen(mensaje):
    print("******************", mensaje, "*******************")


def workflow_alertas(self):

    # intentar una cantidad de veces actualizar el 100% de pendientes
    repetir = 0
    while True:

        # solicitar alertas pendientes para enviar a actualizar
        self.datos_alerta()

        # si ya no hay actualizaciones pendientes, siguiente paso
        pendientes = self.actualizar_datos.json()

        # revisar si actualizar detuvo el proceso de autoscraper
        if not self.auto_scraper_continue_flag:
            self.log(action="[ AUTOSCRAPER ] Abortado.")
            return

        # si no quedan registros por actualizar, continuar
        if all([len(j) == 0 for j in pendientes.values()]):
            break
        else:
            self.actualizar()
            repetir += 1

        # excede cantidad de repeticiones, al menos un scraper no esta actualizando bien
        if repetir > AUTOSCRAPER_REPETICIONES:
            enviar_correo_resumen("ALERTAS: No se puedo completar scraping.")
            return "error scrapers"

        time.sleep(1)

    # crear correos de alertas
    self.generar_alertas()
    enviar_correo_resumen(f"Mensajes creados: {len(self.created_messages)}")


def workflow_boletines(self):

    # intentar una cantidad de veces actualizar el 100% de pendientes
    repetir = 0
    while True:

        # solicitar alertas pendientes para enviar a actualizar
        self.datos_boletin()
        pendientes = self.actualizar_datos.json()

        # si ya no hay actualizaciones pendientes, siguiente paso
        if all([len(j) == 0 for j in pendientes.values()]):
            break
        else:
            self.actualizar()
            repetir += 1

            # revisar si actualizar detuvo el proceso de autoscraper
            if not self.auto_scraper_continue_flag:
                self.log(action="[ AUTOSCRAPER ] Abortado.")
                return

            # excede cantidad de repeticiones, al menos un scraper no esta actualizando bien
            elif repetir > AUTOSCRAPER_REPETICIONES:
                enviar_correo_resumen("BOLETNES: No se puedo completar scraping.")
                return "error scrapers"

            time.sleep(1)

    # crear correos de alertas
    self.generar_boletines()
    enviar_correo_resumen(f"Mensajes creados: {len(self.created_messages)}")


def flujo(self, tipo_mensaje):

    # intentar una cantidad de veces actualizar el 100% de pendientes
    repetir = 0
    while True:

        # solicitar alertas/boletines pendientes para enviar a actualizar
        if tipo_mensaje == "alertas":
            self.datos_alerta()
        elif tipo_mensaje == "boletines":
            self.datos_boletin()

        # tomar datos pendientes de ser actualizados del atributo
        pendientes = self.actualizar_datos.json()

        # si ya no hay actualizaciones pendientes, siguiente paso
        if all([len(j) == 0 for j in pendientes.values()]):
            break
        else:
            self.actualizar()
            repetir += 1

            # revisar si actualizar detuvo el proceso de autoscraper
            if not self.auto_scraper_continue_flag:
                self.log(action="[ AUTOSCRAPER ] Abortado.")
                return

            # excede cantidad de repeticiones, al menos un scraper no esta actualizando bien
            elif repetir > AUTOSCRAPER_REPETICIONES:
                enviar_correo_resumen("BOLETNES: No se puedo completar scraping.")
                return "error scrapers"

            time.sleep(1)

    # crear correos de alertas/boletines
    if tipo_mensaje == "alertas":
        self.generar_alertas()
    elif tipo_mensaje == "boletines":
        self.generar_boletines()

    enviar_correo_resumen(f"Mensajes creados: {len(self.created_messages)}")


def main(self):

    self.log(action="[ AUTOSCRAPER ] Inicio")

    # ----- ALERTAS -----
    flujo(self, tipo_mensaje="alertas")
    self.log(action="[ AUTOSCRAPER ] Fin Alertas")

    # ----- BOLETINES -----
    flujo(self, tipo_mensaje="boletines")
    self.log(action="[ AUTOSCRAPER ] Fin Boletines")

    self.log(action="[ AUTOSCRAPER ] Fin")
