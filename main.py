import sys
from src.monitor import monitor
from src.utils import maintenance


def main():

    # sitecustomize.py active in .venv

    # ejecutar mantenimiento previo al inicio
    maintenance.pre()

    dash = monitor.Dashboard(test="TEST" in "".join(sys.argv).upper())
    dash.runx()


if __name__ == "__main__":
    main()
