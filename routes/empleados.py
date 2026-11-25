
from flask import Blueprint, request, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from functools import wraps

from extensions import db, csrf
from models.usuario import Usuario
from routes import empleados_bp


def crear_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="logistica-empleados-api"
    )


def requiere_empleado(f):
    @wraps(f)
    def decorada(*args, **kwargs):

        autorizacion = request.headers.get("Authorization", "")

        if not autorizacion.startswith("Bearer "):
            return jsonify({
                "error": "Token de acceso requerido."
            }), 401

        token = autorizacion.split(" ", 1)[1]

        try:
            datos = crear_serializer().loads(
                token,
                max_age=43200
            )
        except SignatureExpired:
            return jsonify({
                "error": "El token ha expirado."
            }), 401
        except BadSignature:
            return jsonify({
                "error": "Token inválido."
            }), 401

        usuario = db.session.get(Usuario, datos.get("usuario_id"))

        if (
            not usuario
            or not usuario.activo
            or usuario.rol != "EMPLEADO"
        ):
            return jsonify({
                "error": "Acceso no autorizado."
            }), 403

        return f(usuario, *args, **kwargs)

    return decorada


@empleados_bp.route("/login", methods=["POST"])
@csrf.exempt
def login_api():

    datos = request.get_json(silent=True) or {}

    usuario = datos.get("usuario", "").strip()
    password = datos.get("password", "")

    if not usuario or not password:
        return jsonify({
            "error": "Debes proporcionar usuario y contraseña."
        }), 400

    usuario_db = Usuario.query.filter_by(
        usuario=usuario
    ).first()

    if not usuario_db or not usuario_db.verificar_password(password):
        return jsonify({
            "error": "Usuario o contraseña incorrectos."
        }), 401

    if not usuario_db.activo:
        return jsonify({
            "error": "La cuenta está desactivada."
        }), 403

    if usuario_db.rol != "EMPLEADO":
        return jsonify({
            "error": "Esta aplicación es exclusiva para empleados."
        }), 403

    token = crear_serializer().dumps({
        "usuario_id": usuario_db.id
    })

    return jsonify({
        "mensaje": "Inicio de sesión correcto.",
        "token": token,
        "usuario": {
            "id": usuario_db.id,
            "nombre": usuario_db.nombre,
            "usuario": usuario_db.usuario,
            "rol": usuario_db.rol
        }
    }), 200


@empleados_bp.route("/me", methods=["GET"])
@requiere_empleado
def perfil_empleado(usuario):

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "usuario": usuario.usuario,
        "rol": usuario.rol
    }), 200
