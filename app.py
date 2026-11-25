
from flask import Flask

from config import Config
from extensions import db, login_manager, csrf


def create_app():

    app = Flask(__name__)

    # Configuración
    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "Debes configurar la variable SECRET_KEY."
        )

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configuración de sesiones
    login_manager.login_view = "autenticacion.login"
    login_manager.session_protection = "strong"

    # Modelo de usuario
    from models.usuario import Usuario

    @login_manager.user_loader
    def cargar_usuario(user_id):
        return db.session.get(Usuario, int(user_id))

    # Importar Blueprints
    from routes import (
        autenticacion_bp,
        dashboard_bp,
        empleados_bp
    )

    # Importar módulos que contienen las rutas
    from routes import autenticacion
    from routes import dashboard
    from routes import empleados

    # Registrar Blueprints
    app.register_blueprint(autenticacion_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(empleados_bp)

    # Crear tablas
    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
