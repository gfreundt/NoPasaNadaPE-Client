def set_routes(self):

    # -------- URL DE INGRESO --------
    self.app.add_url_rule(
        "/",
        endpoint="/",
        view_func=self.dashboard,
    )

    # -------- APIS --------

    # empieza el autoscraper
    self.app.add_url_rule(
        "/auto_scraper",
        endpoint="auto_scraper",
        view_func=self.auto_scraper,
        methods=["POST"],
    )

    # endpoint usado por JavaScript para actualizar datos (AJAX)
    self.app.add_url_rule(
        "/data",
        "get_data",
        self.get_data,
    )

    # ?
    # self.app.add_url_rule(
    #     "/log/get",
    #     "log_get",
    #     self.log_get,
    # )

    # -------- BOTONES --------
    self.app.add_url_rule(
        "/datos_alertas",
        endpoint="datos_alerta",
        view_func=self.datos_alerta,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/datos_boletines",
        endpoint="datos_boletin",
        view_func=self.datos_boletin,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/actualizar",
        endpoint="actualizar",
        view_func=self.actualizar,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/generar_alertas",
        endpoint="generar_alertas",
        view_func=self.generar_alertas,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/enviar_mensajes",
        endpoint="enviar_mensajes",
        view_func=self.enviar_mensajes,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/generar_boletines",
        endpoint="generar_boletines",
        view_func=self.generar_boletines,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/test",
        endpoint="test",
        view_func=self.hacer_tests,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/logs",
        endpoint="logs",
        view_func=self.actualizar_logs,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/db_info",
        endpoint="db_info",
        view_func=self.db_info,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/db_backup",
        endpoint="db_backup",
        view_func=self.db_completa,
        methods=["POST"],
    )
    self.app.add_url_rule(
        "/actualizar_de_json",
        endpoint="actualizar_de_json",
        view_func=self.actualizar_de_json,
        methods=["POST"],
    )
