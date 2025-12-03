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


SERVER_IP_TEST = "http://localhost:5000"
# SERVER_IP = "http://10.128.0.2:5000"
SERVER_IP = "https://www.nopasanadape.com"

INTERNAL_AUTH_TOKEN = "xsw5R0oHBUJWJhxUqTmHdGmuYhHUNVy62bdJMPtxFjXgjdpCg5K3NgIXQkqwxCujUQ5GtC7m8GWe8JawqlOEkYdmUQLcQTLy"
EXTERNAL_AUTH_TOKEN = "6f1a9d4b27c3e8a0f5b19c2d43e7a8d1"

# info email account
ZOHO_INFO_PASSWORD = "5QJWEKi0trAL"

# api email
ZOHO_MAIL_API_CLIENT_ID = "1000.400ELE5I2WU72H931RQI8HTIY2Y30E"
ZOHO_MAIL_API_CLIENT_SECRET = "fe41ea63cc1c667091b32b1068660cf0b44fffd823"
ZOHO_MAIL_API_REDIRECT_URL = "https://www.nopasanadape.com/redir"

# zeptomail
ZOHO_INFO_PASSWORD = "5QJWEKi0trAL"
ZEPTOMAIL_INFO_TOKEN = "Zoho-enczapikey wSsVR60lrkb4B/h8mmGtLutrmA5WDlzxQEwsiVGo7HKvSvrFosc/khXIBgGgT6UcGDFrQDMS9rIgyR4IgDAPjNotnAoGXiiF9mqRe1U4J3x17qnvhDzJXGxclROKKIwNwQRinmZkEs8m+g=="

# BrightData  proxy
PROXY_DC_USERNAME = (
    "brd-customer-hl_8874517e-zone-datacenter_proxy1:session_random=1"  # not used
)
PROXY_DC_USERNAME = "brd-customer-hl_8874517e-zone-datacenter_proxy1-session-"
PROXY_RES_USERNAME = (
    "brd-customer-hl_8874517e-zone-residential_proxy1-country-pe-session-"
)
PROXY_DC_PASSWORD = "8ydfm761xeeh"
PROXY_RES_PASSWORD = "u30iyjwv3gb3"
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = "33335"
BRIGHT_DATA_API_KEY = "41e410c7-1bc3-47de-8635-3b6401d378e6"

# truecaptcha
TRUECAPTCHA_API_KEY = "UEJgzM79VWFZh6MpOJgh"

# 2captcha recaptcha solver
TWOCAPTCHA_API_KEY = "852d1d8f6c105fbc6b5d86abed7a2370"

# google cloud
GC_BILLING_ACCOUNT_ID = "012345-67890A-BCDEF0"  # FAKE!
GC_BUDGET_ID = "projects/123456789012/budgets/MyMonthlyBudget"  # FAKE!

# pushbullet
PUSHBULLET_API_TOKEN = "o.BMp5HNWSPNMS8Gbqsufntv94feuklPMg"

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
    "brevetes": True,
    "satimp": True,
    "soat": True,
    "jneafil": True,
    "jnemulta": True,
    "osiptel": True,
    "satmul": True,
    "recvehic": True,
    "revtec": True,
    "sunarp": True,
    "sunat": True,
    "sutran": True,
}

# nombre de tablas
TABLAS_BD = {
    "DataMtcRecordsConductores",
    "DataMtcBrevetes",
    "DataSatMultas",
    "DataSatImpuestos",
    "DataMtcRevisionesTecnicas",
    "DataSutranMultas",
    "DataSunarpFichas",
    "DataApesegSoats",
}


SCRAPER_TIMEOUT = {
    "brevetes": 60,
    "satimps": 60,
    "soat": 60,
    "jneafil": True,
    "jnemulta": True,
    "osiptel": True,
    "satmuls": 240,
    "recvehic": 60,
    "revtec": 60,
    "sunarps": 60,
    "sunat": True,
    "sutrans": 60,
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
    "desarmador": 10,
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

GATHER_ITERATIONS = 3
AUTOSCRAPER_REPETICIONES = 3
