

from flask import (
    render_template,
    abort,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from extensions import db
from models.usuario import Usuario
from routes import dashboard_bp


def requiere_admin():
    if not current_user.es_administrador():
        abort(403)


@dashboard_bp.route("/")
@login_required
def index():

    requiere_admin()

    return render_template("dashboard/index.html")


@dashboard_bp.route("/empleados")
@login_required
def listar_empleados():

    requiere_admin()

    empleados = (
        Usuario.query
        .filter(
            Usuario.rol.in_(["OPERADOR", "JEFE_EMBARQUE"])
        )
        .order_by(Usuario.nombre.asc())
        .all()
    )

    return render_template(
        "dashboard/empleados.html",
        empleados=empleados
    )


@dashboard_bp.route("/empleados/nuevo", methods=["GET", "POST"])
@login_required
def crear_empleado():

    requiere_admin()

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        rol = request.form.get("rol", "OPERADOR").strip()

        if not nombre or not usuario or not password:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("dashboard.crear_empleado"))

        if len(nombre) > 100 or len(usuario) > 40:
            flash("El nombre o usuario excede la longitud permitida.", "error")
            return redirect(url_for("dashboard.crear_empleado"))

        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
            return redirect(url_for("dashboard.crear_empleado"))

        if rol not in ("OPERADOR", "JEFE_EMBARQUE"):
            flash("El rol seleccionado no es válido.", "error")
            return redirect(url_for("dashboard.crear_empleado"))

        existente = Usuario.query.filter_by(
            usuario=usuario
        ).first()

        if existente:
            flash("Ese nombre de usuario ya está registrado.", "error")
            return redirect(url_for("dashboard.crear_empleado"))

        empleado = Usuario(
            nombre=nombre,
            usuario=usuario,
            rol=rol,
            id_proveedor=None,
            id_sucursal=None
        )

        empleado.establecer_password(password)

        db.session.add(empleado)
        db.session.commit()

        flash("Empleado registrado correctamente.", "success")

        return redirect(url_for("dashboard.listar_empleados"))

    return render_template("dashboard/nuevo_empleado.html")

