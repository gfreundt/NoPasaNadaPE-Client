import sys
from src.monitor import monitor
from src.utils import maintenance


def main():

    # sitecustomize.py active in .venv

    # ejecutar mantenimiento previo al inicio
    maintenance.pre()

    if "TEST" in "".join(sys.argv).upper():
        param = "TEST"
    elif "DEV" in "".join(sys.argv).upper():
        param = "DEV"
    else:
        param = "PROD"

    dash = monitor.Dashboard(param)
    dash.runx()


if __name__ == "__main__":
    main()
