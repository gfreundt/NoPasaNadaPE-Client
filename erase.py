import requests

url = "http://172.20.165.114:5000/alta"


token = "6f1a9d4b27c3e8a0f5b19c2d43e7a8d1"
usuario = "castrol"
correo = "test@test.com"


f = requests.post(
    url=url, params={"token": token, "usuario": usuario, "correo": correo}
)

print(f.status_code)
print(f.content)
