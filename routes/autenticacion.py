
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models.usuario import Usuario
from routes import autenticacion_bp


@autenticacion_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        if current_user.rol == "ADMIN":
            return redirect(url_for("dashboard.index"))

        return redirect("/api/empleados/")

    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        usuario_db = Usuario.query.filter_by(
            usuario=usuario
        ).first()

        if not usuario_db or not usuario_db.verificar_password(password):
            flash("Usuario o contraseña incorrectos.", "error")
            return redirect(url_for("autenticacion.login"))

        if not usuario_db.activo:
            flash("Tu cuenta está desactivada.", "error")
            return redirect(url_for("autenticacion.login"))

        login_user(usuario_db)

        if usuario_db.rol == "ADMIN":
            return redirect(url_for("dashboard.index"))

        return redirect("/api/empleados/")

    return render_template("autenticacion/login.html")


@autenticacion_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("Sesión cerrada correctamente.", "success")

    return redirect(url_for("autenticacion.login"))
