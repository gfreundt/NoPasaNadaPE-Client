from src.utils.constants import AUTOSCRAPER_REPETICIONES
from src.utils.utils import send_pushbullet, check_vpn_online
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
            break
        else:
            self.actualizar()
            repetir += 1
            # excede cantidad de repeticiones, al menos un scraper no esta actualizando bien
            if repetir > AUTOSCRAPER_REPETICIONES:
                return (
                    f"{tipo_mensaje.upper()}: No se llego a 0 pendientes luego de {AUTOSCRAPER_REPETICIONES} intentos.",
                    False,
                )

            # reintentar scraping
            time.sleep(3)

    # crear correos de alertas/boletines
    if tipo_mensaje == "alertas":
        self.generar_alertas()

    elif tipo_mensaje == "boletines":
        self.generar_boletines()

    # enviar mensajes pendiente
    self.enviar_mensajes()

    return (
        f"{tipo_mensaje.upper()}: Se han enviado {len(self.created_messages)} mensajes.",
        True,
    )


def enviar_notificacion(mensaje):

    title = f"NoPasaNada AUTOSCRAPER - {dt.now()}"
    mensaje = "\n".join([i for i in mensaje])
    send_pushbullet(title=title, message=mensaje)


def iniciar_corrida(self):
    self.auto_scraper_corriendo = True
    mensaje = [f"Inicio Autoscraper: {dt.now()}"]

    # si VPN no esta en linea, no iniciar
    if not check_vpn_online():
        self.log(action="[ AUTOSCRAPER ] Proceso Abortado. No hay VPN en linea.")
        mensaje.append("Proceso ABORTADO. No hay VPN en linea.")
        exito1, exito2 = False

    else:
        self.log(action="[ AUTOSCRAPER ] Inicio")

        # procesar alertas
        respuesta, exito1 = flujo(self, tipo_mensaje="alertas")
        mensaje.append(respuesta)
        self.log(action="[ AUTOSCRAPER ] Fin Alertas")

        # procesar boletines
        respuesta, exito2 = flujo(self, tipo_mensaje="boletines")
        mensaje.append(respuesta)
        self.log(action="[ AUTOSCRAPER ] Fin Boletines")

    # enviar resumen de actividad, definir nueva hora de correr y retornar si pudo avanzar o no
    enviar_notificacion(mensaje=mensaje)
    self.siguiente_cron = dt.now() + td(minutes=5)
    self.auto_scraper_corriendo = False
    return exito1 and exito2


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
