import datetime

import sys
from pathlib import Path

RAIZ_REPO = str(Path(__file__).resolve().parent.parent)
if RAIZ_REPO not in sys.path:
    sys.path.insert(0, RAIZ_REPO)


class Agendamiento:
    ANDENES_RECIBO_MAX = 4
    HORA_APERTURA = datetime.time(8, 0)
    HORA_CIERRE = datetime.time(18, 0)
    ESTADOS_VALIDOS = {
        "programada",
        "en_anden",
        "completada",
        "retrasada",
        "cancelada",
    }

    def __init__(
        self,
        codigo_cita: str,
        proveedor: str,
        folio_orden: str,
        folio_factura: str,
        fecha_hora_inicio: datetime.datetime,
        fecha_hora_fin: datetime.datetime,
        anden_recibo: int,
        origen_correo: str = "",
        estado: str = "programada",
    ):
        if not codigo_cita or not codigo_cita.strip():
            raise ValueError("El codigo_cita no puede estar vacio.")
        if not proveedor or not proveedor.strip():
            raise ValueError("El proveedor no puede estar vacio.")
        if not folio_orden or not folio_orden.strip():
            raise ValueError("El folio_orden no puede estar vacio.")
        if not 1 <= anden_recibo <= self.ANDENES_RECIBO_MAX:
            raise ValueError(
                f"El anden_recibo debe estar entre 1 y {self.ANDENES_RECIBO_MAX}."
            )
        if fecha_hora_fin <= fecha_hora_inicio:
            raise ValueError(
                "La fecha_hora_fin debe ser posterior a fecha_hora_inicio."
            )

        self._codigo_cita = codigo_cita.strip()
        self._proveedor = proveedor.strip()
        self._folio_orden = folio_orden.strip()
        self._folio_factura = folio_factura.strip()
        self._fecha_hora_inicio = fecha_hora_inicio
        self._fecha_hora_fin = fecha_hora_fin
        self._anden_recibo = int(anden_recibo)
        self._origen_correo = origen_correo.strip()
        self._estado = (
            estado.strip().lower()
            if estado.strip().lower() in self.ESTADOS_VALIDOS
            else "programada"
        )
        self._tarimas_qr: list[str] = []

    # --- Propiedades publicas de consulta ---
    @property
    def codigo_cita(self) -> str:
        return self._codigo_cita

    @property
    def proveedor(self) -> str:
        return self._proveedor

    @property
    def folio_orden(self) -> str:
        return self._folio_orden

    @property
    def folio_factura(self) -> str:
        return self._folio_factura

    @property
    def fecha_hora_inicio(self) -> datetime.datetime:
        return self._fecha_hora_inicio

    @property
    def fecha_hora_fin(self) -> datetime.datetime:
        return self._fecha_hora_fin

    @property
    def anden_recibo(self) -> int:
        return self._anden_recibo

    @property
    def origen_correo(self) -> str:
        return self._origen_correo

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def tarimas_qr(self) -> list[str]:
        return list(self._tarimas_qr)

    # --- Metodos publicos con reglas del CEDI ---
    def validar_ventana_operativa(self) -> dict:
        """Verifica lunes a sabado y ventana de 08:00 a 18:00."""
        mismo_dia = self._fecha_hora_inicio.date() == self._fecha_hora_fin.date()
        dia_semana = self._fecha_hora_inicio.weekday()  # 0=Lun .. 5=Sab, 6=Dom
        es_dia_laboral = mismo_dia and (0 <= dia_semana <= 5)

        inicio_t = self._fecha_hora_inicio.time()
        fin_t = self._fecha_hora_fin.time()
        dentro_horario = (inicio_t >= self.HORA_APERTURA) and (
            fin_t <= self.HORA_CIERRE
        )

        valida = es_dia_laboral and dentro_horario
        motivo = "OK"
        if not mismo_dia:
            motivo = "La cita debe iniciar y terminar el mismo dia."
        elif dia_semana == 6:
            motivo = "El CEDI no opera citas los domingos (lunes a sabado)."
        elif not dentro_horario:
            motivo = "Fuera del horario de operacion (08:00 a 18:00)."

        return {
            "codigo_cita": self._codigo_cita,
            "anden_recibo": self._anden_recibo,
            "valida": valida,
            "motivo": motivo,
        }

    def asignar_anden(self, nuevo_anden: int) -> None:
        if not 1 <= nuevo_anden <= self.ANDENES_RECIBO_MAX:
            raise ValueError(
                f"El anden debe estar entre 1 y {self.ANDENES_RECIBO_MAX}."
            )
        self._anden_recibo = int(nuevo_anden)

    def agregar_qr_esperado(self, codigo_qr: str) -> None:
        qr_limpio = codigo_qr.strip()
        if not qr_limpio:
            raise ValueError("El codigo_qr no puede estar vacio.")
        if qr_limpio not in self._tarimas_qr:
            self._tarimas_qr.append(qr_limpio)

    def cambiar_estado(self, nuevo_estado: str) -> None:
        estado_limpio = nuevo_estado.strip().lower()
        if estado_limpio not in self.ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado no valido '{nuevo_estado}'. Usa: {', '.join(sorted(self.ESTADOS_VALIDOS))}."
            )
        self._estado = estado_limpio

    def to_dict(self) -> dict:
        return {
            "codigo_cita": self._codigo_cita,
            "proveedor": self._proveedor,
            "folio_orden": self._folio_orden,
            "folio_factura": self._folio_factura,
            "fecha_hora_inicio": self._fecha_hora_inicio.isoformat(),
            "fecha_hora_fin": self._fecha_hora_fin.isoformat(),
            "anden_recibo": self._anden_recibo,
            "origen_correo": self._origen_correo,
            "estado": self._estado,
            "tarimas_qr": list(self._tarimas_qr),
        }


if __name__ == "__main__":
    cita1 = Agendamiento(
        codigo_cita="CITA-2026-001",
        proveedor="Distribuidora Golfo",
        folio_orden="OC-4501",
        folio_factura="FAC-9841",
        fecha_hora_inicio=datetime.datetime(2026, 11, 25, 9, 0),
        fecha_hora_fin=datetime.datetime(2026, 11, 25, 10, 30),
        anden_recibo=2,
        origen_correo="compras@BIC.com", 
    )
    cita1.agregar_qr_esperado("QR-CEDI-001")
    print("Ventana operativa:", cita1.validar_ventana_operativa())
    cita1.cambiar_estado("en_anden")
    print("Cita actual:", cita1.to_dict())