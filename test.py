from src.test.tests import Test


def main():

    test = Test()

    print(f"Crear Cuenta y Salir: {test.crear_cuenta()}")
    print(f"Login: {test.login()}")
    print(f"Cambiar Nombre: {test.cambiar_datos_nombre()}")
    print(f"Cambiar Celular: {test.cambiar_datos_celular()}")
    print(f"Cambiar Placas: {test.cambiar_datos_placas()}")
    print(f"Cambiar Contraseña: {test.cambiar_datos_contrasena()}")
    print(f"Tab Vencimientos: {test.mis_vencimientos()}")
    print(f"Logout: {test.logout()}")
    # print(f"Recuperar Contraseña: {test.recuperar_contrasena()}")
    print(f"Eliminar Cuenta: {test.eliminar_cuenta()}")
    print(f"Informacion Estatica: {test.datos_estaticos()}")
    print(f"API - Alta: {test.api_alta()}")
    print(f"API - Baja: {test.api_baja()}")
    print(f"API - Info: {test.api_info()}")


main()
