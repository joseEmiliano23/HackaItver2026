
from flask import Blueprint

autenticacion_bp = Blueprint(
    "autenticacion",
    __name__,
    url_prefix="/auth"
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/admin"
)

empleados_bp = Blueprint(
    "empleados",
    __name__,
    url_prefix="/api/empleados"
)
