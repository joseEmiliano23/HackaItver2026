from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class Usuario(UserMixin, db.Model):

    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)

    usuario = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    rol = db.Column(
        db.String(15),
        nullable=False
    )

    id_proveedor = db.Column(
    db.Integer,
    nullable=True
    )

    id_sucursal = db.Column(
           db.Integer,
            nullable=True
    )
    __table_args__ = (
        db.CheckConstraint(
            "rol IN ('PROVEEDOR', 'OPERADOR', "
            "'JEFE_EMBARQUE', 'SUCURSAL', 'GERENCIA')",
            name="usuario_rol_check"
        ),
    )

    # Flask-Login necesita una propiedad llamada id
    def get_id(self):
        return str(self.id_usuario)

    def establecer_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def es_administrador(self):
        return self.rol == "GERENCIA"

    def es_empleado(self):
        return self.rol in ("OPERADOR", "JEFE_EMBARQUE")

    def __repr__(self):
        return f"<Usuario {self.usuario}>"