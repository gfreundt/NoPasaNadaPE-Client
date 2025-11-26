import os
from src.utils.constants import NETWORK_PATH


def pre():

    security_folder = os.path.join(NETWORK_PATH, "security")
    update_files = [i for i in os.listdir(security_folder) if "update_" in i]

    # borrar todos los backups de updates excepto los ultimos 15
    for file in update_files[:-15]:
        os.remove(os.path.join(NETWORK_PATH, "security", file))
