from src.utils.constants import AUTOSCRAPER_REPETICIONES
from src.utils.utils import send_pushbullet, check_vpn_online
import time
from datetime import datetime as dt


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
                return f"{tipo_mensaje.upper()}: No se llego a 0 pendientes luego de {AUTOSCRAPER_REPETICIONES} intentos."

            # reintentar scraping
            time.sleep(3)

    # crear correos de alertas/boletines
    if tipo_mensaje == "alertas":
        self.generar_alertas()
    elif tipo_mensaje == "boletines":
        self.generar_boletines()

    return f"{tipo_mensaje.upper()}: Scrapers completos. Se han generado {len(self.created_messages)} mensajes."


def enviar_notificacion(mensaje):

    title = f"NoPasaNada AUTOSCRAPER - {dt.now()}"
    mensaje = "\n".join([i for i in mensaje])
    send_pushbullet(title=title, message=mensaje)


def main(self):

    mensaje = [f"Inicio Autoscraper: {dt.now()}"]

    # si VPN no esta en linea, no iniciar
    if not check_vpn_online():
        self.log(action="[ AUTOSCRAPER ] Proceso Abortado. No hay VPN en linea.")
        mensaje.append("Proceso ABORTADO. No hay VPN en linea.")

    else:
        self.log(action="[ AUTOSCRAPER ] Inicio")

        # procesar alertas
        respuesta = flujo(self, tipo_mensaje="alertas")
        mensaje.append(respuesta)
        self.log(action="[ AUTOSCRAPER ] Fin Alertas")

        # procesar boletines
        respuesta = flujo(self, tipo_mensaje="boletines")
        mensaje.append(respuesta)
        self.log(action="[ AUTOSCRAPER ] Fin Boletines")

        # cerrar proceso
        self.log(action="[ AUTOSCRAPER ] Fin")

    # enviar resumen de actividad
    enviar_notificacion(mensaje=mensaje)
