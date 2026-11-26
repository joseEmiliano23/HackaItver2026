
from flask import render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from routes import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():

    # Solo los administradores pueden entrar
    if current_user.rol != "ADMIN":
        abort(403)

    return render_template("dashboard/index.html")
