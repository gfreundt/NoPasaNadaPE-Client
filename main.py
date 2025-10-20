import sys
from src.monitor import monitor


def main():
    dash = monitor.Dashboard(test="TEST" in "".join(sys.argv).upper())
    dash.runx()


if __name__ == "__main__":
    main()
