from src.utils.constants import AUTOSCRAPER_REPETICIONES
from src.utils.utils import send_pushbullet, check_vpn_online, start_vpn, stop_vpn
import time
from datetime import datetime as dt, timedelta as td


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
            return True
        else:
            self.actualizar()

            # cambiar de pais en VPN
            stop_vpn()
            self.log(action="[ VPN OFF ]")

            if self.vpn_location == "PE":
                self.vpn_location = "AR"
            else:
                self.vpn_location = "PE"

            start_vpn(self.vpn_location)
            self.log(action=f"[ VPN PRENDIDA ({self.vpn_location})]")

            # aumentar contador de repeticiones, si excede limite parar
            repetir += 1
            if repetir > AUTOSCRAPER_REPETICIONES:
                return False

            # reintentar scraping
            time.sleep(3)


def enviar_notificacion(mensaje):

    title = f"NoPasaNada AUTOSCRAPER - {dt.now()}"
    mensaje = "\n".join([i for i in mensaje])
    send_pushbullet(title=title, message=mensaje)


def iniciar_corrida(self):

    self.auto_scraper_corriendo = True
    self.log(action="[ AUTOSCRAPER ] Inicio")
    # prender VPN
    start_vpn(self.vpn_location)
    self.log(action=f"[ VPN PRENDIDA ({self.vpn_location})]")

    # si VPN no esta en linea, no iniciar
    if not check_vpn_online():
        self.log(action="[ AUTOSCRAPER ] Proceso Abortado. No hay VPN en linea.")
        exito1 = exito2 = False

    else:

        # procesar alertas
        exito1 = flujo(self, tipo_mensaje="alertas")
        self.log(action="[ AUTOSCRAPER ] Fin Alertas")

        # procesar boletines
        exito2 = flujo(self, tipo_mensaje="boletines")
        self.log(action="[ AUTOSCRAPER ] Fin Boletines")

    # apagar VPN
    stop_vpn()
    self.log(action="[ VPN OFF ]")

    # enviar resumen de actividad
    enviar_notificacion(mensaje="Mensajes enviados")

    # definir nueva hora de correr
    self.siguiente_cron = dt.now() + td(minutes=5)
    self.auto_scraper_corriendo = False

    if exito1 and exito2:
        # generar y enviar mensajes
        self.generar_alertas()
        self.generar_boletines()
        self.enviar_mensajes()
        # retornar proceso completo
        return True
    # retornar proceso no puedo terminar
    return False


def main(self):

    self.auto_scraper_corriendo = False

    while True:
        print(
            f"Autoscraper check: {str(dt.now())[:20]} - Siguiente: {str(self.siguiente_cron)[:20]} - Corriendo: {self.auto_scraper_corriendo}"
        )
        if dt.now() > self.siguiente_cron and not self.auto_scraper_corriendo:
            exito = iniciar_corrida(self)
            self.log(
                action=f"[ SERVICIO ] CRON: Autoscraper {"SIN PROBLEMAS" if exito else "NO TERMINO"}. Siguiente: {str(self.siguiente_cron)[:20]}"
            )
        time.sleep(30)
