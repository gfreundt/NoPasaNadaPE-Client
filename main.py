import sys
from src.monitor import monitor
from src.utils import maintenance
import time


def main():
    while True:
        try:

            # ejecutar mantenimiento previo al inicio
            maintenance.pre()

            # elegir ambiente TEST (local D:), DEV (cloud dev.) o PRODUCITON
            if "TEST" in "".join(sys.argv).upper():
                param = "TEST"
            elif "DEV" in "".join(sys.argv).upper():
                param = "DEV"
            else:
                param = "PROD"

            # crear objecto de dashboard y ejecutar servidor de Flask
            dash = monitor.Dashboard(param)
            dash.runx()

            # en el caso que el servidor de Flask termine naturalmente (Ctrl+C o SIGINT)
            break

        except Exception as e:  # <--- Start of except block
            print(
                f"------------- ERROR FATAL de MAIN: {e}. Reiniciando todo en 30 segundos..."
            )
            print("-" * 60)
            time.sleep(30)


if __name__ == "__main__":
    # sitecustomize.py active in .venv
    main()
    print("------------ FIN CRTL+C de MAIN ----------")
