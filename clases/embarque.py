import sys
from datetime import datetime
from pathlib import Path

RAIZ_PROYECTO = str(Path(__file__).resolve().parent.parent)
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

from clases.tarima import Tarima


class Embarque:
    ANDENES_EMBARQUE_MAX = 3
    MAX_TARIMAS_TORTON = 12
    MAX_PESO_KG_TORTON = 12000.0
    ESTADOS_VALIDOS = {"abierto", "listo_para_salida", "despachado"}

    def __init__(
        self,
        folio_embarque: str,
        sucursal_destino: int,
        anden_embarque: int,
        tipo_unidad: str = "Torton",
    ):
        if not folio_embarque or not folio_embarque.strip():
            raise ValueError("El folio_embarque no puede estar vacio.")
        if not 1 <= sucursal_destino <= 32:
            raise ValueError("La sucursal_destino debe estar entre 1 y 32.")
        if not 1 <= anden_embarque <= self.ANDENES_EMBARQUE_MAX:
            raise ValueError(
                f"El anden_embarque debe estar entre 1 y {self.ANDENES_EMBARQUE_MAX}."
            )
        if not tipo_unidad or not tipo_unidad.strip():
            raise ValueError("El tipo_unidad no puede estar vacio.")

        self._folio_embarque = folio_embarque.strip()
        self._sucursal_destino = int(sucursal_destino)
        self._anden_embarque = int(anden_embarque)
        self._tipo_unidad = tipo_unidad.strip()
        self._peso_actual_kg = 0.0
        self._tarimas: list[Tarima] = []
        self._estado = "abierto"
        self._fecha_salida: str | None = None

    # --- Propiedades publicas de consulta --- #
    @property
    def folio_embarque(self) -> str:
        return self._folio_embarque

    @property
    def sucursal_destino(self) -> int:
        return self._sucursal_destino

    @property
    def anden_embarque(self) -> int:
        return self._anden_embarque

    @property
    def tipo_unidad(self) -> str:
        return self._tipo_unidad

    @property
    def peso_actual_kg(self) -> float:
        return self._peso_actual_kg

    @property
    def cantidad_tarimas(self) -> int:
        return len(self._tarimas)

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def fecha_salida(self) -> str | None:
        return self._fecha_salida

    # --- Metodos publicos con reglas del CEDI --- #
    def puede_cargar_tarima(self, tarima: Tarima) -> dict:
        """Valida sucursal, incidencia activa, limite de 12 tarimas y 12,000 kg."""
        if self._estado != "abierto":
            return {
                "qr": tarima.codigo_qr,
                "puede_cargar": False,
                "motivo": f"El embarque esta en estado '{self._estado}' y no acepta carga.",
            }
        if tarima.sucursal_destino != self._sucursal_destino:
            return {
                "qr": tarima.codigo_qr,
                "puede_cargar": False,
                "motivo": (
                    f"Tarima de sucursal {tarima.sucursal_destino} no coincide "
                    f"con embarque de sucursal {self._sucursal_destino}."
                ),
            }
        if tarima.incidencia != "ninguna":
            return {
                "qr": tarima.codigo_qr,
                "puede_cargar": False,
                "motivo": f"Tarima con incidencia activa '{tarima.incidencia}'.",
            }
        if self.cantidad_tarimas + 1 > self.MAX_TARIMAS_TORTON:
            return {
                "qr": tarima.codigo_qr,
                "puede_cargar": False,
                "motivo": f"Excede limite de {self.MAX_TARIMAS_TORTON} tarimas del {self._tipo_unidad}.",
            }

        peso_proyectado = self._peso_actual_kg + tarima.peso_kg
        if peso_proyectado > self.MAX_PESO_KG_TORTON:
            return {
                "qr": tarima.codigo_qr,
                "puede_cargar": False,
                "motivo": (
                    f"Excede peso maximo del {self._tipo_unidad} "
                    f"({peso_proyectado} kg > {self.MAX_PESO_KG_TORTON} kg)."
                ),
            }

        return {
            "qr": tarima.codigo_qr,
            "puede_cargar": True,
            "peso_proyectado_kg": peso_proyectado,
            "tarimas_proyectadas": self.cantidad_tarimas + 1,
            "motivo": "OK",
        }

    def cargar_tarima(self, tarima: Tarima) -> dict:
        """Agrega la tarima al embarque y actualiza su estado a 'embarcada'."""
        evaluacion = self.puede_cargar_tarima(tarima)
        if not evaluacion["puede_cargar"]:
            raise ValueError(f"No se puede cargar tarima: {evaluacion['motivo']}")

        tarima.cambiar_estado("embarcada")
        self._tarimas.append(tarima)
        self._peso_actual_kg += tarima.peso_kg

        return {
            "folio_embarque": self._folio_embarque,
            "anden_embarque": self._anden_embarque,
            "qr": tarima.codigo_qr,
            "tarimas_cargadas": self.cantidad_tarimas,
            "max_tarimas": self.MAX_TARIMAS_TORTON,
            "peso_total_kg": self._peso_actual_kg,
            "max_peso_kg": self.MAX_PESO_KG_TORTON,
        }

    def despachar(self) -> dict:
        """Cierra el embarque, registra fecha/hora de salida y devuelve la relacion."""
        if not self._tarimas:
            raise ValueError("No se puede despachar un embarque sin tarimas.")
        self._estado = "despachado"
        self._fecha_salida = datetime.now().isoformat(timespec="seconds")
        return self.generar_relacion_embarque()

    def generar_relacion_embarque(self) -> dict:
        """Genera el documento/resumen de relacion de embarque para la sucursal."""
        return {
            "folio_embarque": self._folio_embarque,
            "estado": self._estado,
            "fecha_salida": self._fecha_salida,
            "tipo_unidad": self._tipo_unidad,
            "anden_embarque": self._anden_embarque,
            "sucursal_destino": self._sucursal_destino,
            "total_tarimas": self.cantidad_tarimas,
            "limite_tarimas": self.MAX_TARIMAS_TORTON,
            "peso_total_kg": self._peso_actual_kg,
            "limite_peso_kg": self.MAX_PESO_KG_TORTON,
            "detalle_tarimas": [
                {
                    "qr": t.codigo_qr,
                    "folio_factura": t.folio_factura,
                    "peso_kg": t.peso_kg,
                    "alto_m": t.alto_m,
                }
                for t in self._tarimas
            ],
        }


if __name__ == "__main__":
    emb1 = Embarque(
        folio_embarque="EMB-2026-001",
        sucursal_destino=12,
        anden_embarque=2,
        tipo_unidad="Torton",
    )
    t_ok = Tarima(
        codigo_qr="QR-CEDI-010",
        folio_factura="FAC-9900",
        sucursal_destino=12,
        peso_kg=950.0,
        alto_m=1.60,
        estado="acomodada",
    )
    print("Carga:", emb1.cargar_tarima(t_ok))
    print("Relacion de embarque:", emb1.despachar())