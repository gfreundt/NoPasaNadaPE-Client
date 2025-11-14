import os
import platform


# paths
if platform.system() == "Linux":
    NETWORK_PATH = os.path.join("/root/pythonCode/nopasanada")
elif platform.system() == "Windows":
    NETWORK_PATH = os.path.join("d:", r"\pythonCode", "NoPasaNadaPE-Client")

DB_NETWORK_PATH = os.path.join(NETWORK_PATH, "data", "members.db")
DB_LOCAL_PATH = os.path.join("data", "members.db")


# security tokens
UPDATER_TOKEN = """b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABDJEpEA9Y
VHHd4hXY8dD5yhAAAAGAAAAAEAAAEXAAAAB3NzaC1yc2EAAAADAQABAAABAQDlg8ho2tsN
CucL7iimU7P57OMdXsVPGnf8KdEHeX7r+1+V1KSSFPRFOPlBixsxNurtUKG7jNpvn/MqRJ
"""
API_TOKEN_MAQUINARIAS = "6f1a9d4b27c3e8a0f5b19c2d43e7a8d1"


SERVER_IP_TEST = "http://172.20.165.114:5000"
# SERVER_IP = "http://10.128.0.2:5000"
SERVER_IP = "https://www.nopasanadape.com"

INTERNAL_AUTH_TOKEN = "xsw5R0oHBUJWJhxUqTmHdGmuYhHUNVy62bdJMPtxFjXgjdpCg5K3NgIXQkqwxCujUQ5GtC7m8GWe8JawqlOEkYdmUQLcQTLy"

# info email account
ZOHO_INFO_PASSWORD = "5QJWEKi0trAL"

# api email
ZOHO_MAIL_API_CLIENT_ID = "1000.400ELE5I2WU72H931RQI8HTIY2Y30E"
ZOHO_MAIL_API_CLIENT_SECRET = "fe41ea63cc1c667091b32b1068660cf0b44fffd823"
ZOHO_MAIL_API_REDIRECT_URL = "https://www.nopasanadape.com/redir"

# 3-letter months
MONTHS_3_LETTERS = (
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
)

# scrapers headless (debugging)
HEADLESS = {
    "brevete": False,
    "satimp": True,
    "soat": True,
    "jneafil": True,
    "jnemulta": True,
    "osiptel": True,
    "satmul": False,
    "recvehic": True,
    "revtec": True,
    "sunarp": True,
    "sunat": True,
    "sutran": True,
}

DASHBOARD_URL = "wvpeagu2d27l6v7b"

# aseguradora info
ASEGURADORAS = {
    "Interseguro": "(01) 500 - 0000",
    "Rimac Seguros": "(01) 615 - 1515",
    "Pacifico Seguros": "(01) 415 - 1515",
    "La Positiva": "(01)  211 - 0211",
    "Mapfre Perú": "(01)  213 - 3333",
    "Protecta": "(01) 391 - 3000",
    "Vivir Seguros": "(01) 604 - 2000",
}

MTC_CAPTCHAS = {
    "anillo": 1,
    "arbol": 2,
    "carro": 3,
    "avion": 4,
    "bicicleta": 5,
    "billetera": 6,
    "botella": 7,
    "camion": 8,
    "cinturon": 9,
    "destornillador": 10,
    "edificio": 11,
    "gafas": 12,
    "gato": 13,
    "laptop": 14,
    "linterna": 15,
    "llaves": 16,
    "manzana": 17,
    "media": 18,
    "mesa": 19,
    "mochila": 20,
    "perro": 21,
    "pez": 22,
    "pinia": 23,
    "platano": 24,
    "puerta": 25,
    "reloj": 26,
    "patineta": 27,
    "silla": 28,
    "tasa": 29,
    "tienda": 30,
    "timon": 31,
    "zapato": 32,
}

GATHER_ITERATIONS = 4
