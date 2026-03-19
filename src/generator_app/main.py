from generator_app.app.bootstrap import bootstrap_application


def main() -> int:
    app, window = bootstrap_application()
    window.show()
    return app.exec()
