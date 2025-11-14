import requests
from pprint import pprint
from src.utils.constants import INTERNAL_AUTH_TOKEN

url = "https://nopasanadape.com/api/v1"
url = "http://172.20.165.114:5000/admin"

correo = "gfreundt@gmail.com"


f = requests.post(
    url=url,
    params={
        "token": INTERNAL_AUTH_TOKEN,
        "solicitud": "nuevo_password",
        "correo": correo,
    },
)

print(f.status_code)
print(f.content.decode())
