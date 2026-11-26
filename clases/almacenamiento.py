import sys
from pathlib import Path

RAIZ_PROYECTO = str(Path(__file__).resolve().parent.parent)
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

from clases.tarima import Tarima

class Almacenamiento:
    ZONAS_VALIDAS = {"A", "B", "C"}
    CAPACIDAD_MAX_KG = 32000.0
    ALTURA_MAX_RACK_M = 6.0
    NIVELES = 4
    TARIMAS_POR_NIVEL = 8
    CAPACIDAD_MAX_TARIMAS = NIVELES * TARIMAS_POR_NIVEL  # 32 posiciones

    def __init__(
        self,
        rack_id: str,
        sucursal_id: int,
        zona: str,
        frecuencia_dias: int = 1,
        es_expansion: bool = False,
    ):
        zona_limpia = zona.strip().upper()
        if not rack_id or not rack_id.strip():
            raise ValueError("El rack_id no puede estar vacio.")
        if not 1 <= sucursal_id <= 32:
            raise ValueError("El sucursal_id debe estar entre 1 y 32.")
        if zona_limpia not in self.ZONAS_VALIDAS:
            raise ValueError("La zona debe ser 'A', 'B' o 'C'.")
        if frecuencia_dias < 1:
            raise ValueError("La frecuencia_dias debe ser de al menos 1 dia.")

        self._rack_id = rack_id.strip()
        self._sucursal_id = int(sucursal_id)
        self._zona = zona_limpia
        self._frecuencia_dias = int(frecuencia_dias)
        self._es_expansion = bool(es_expansion)
        self._peso_actual_kg = 0.0
        # Posiciones ocupadas: {(nivel, slot): codigo_qr}
        self._posiciones: dict[tuple[int, int], str] = {}

    # --- Propiedades publicas de consulta ---
    @property
    def rack_id(self) -> str:
        return self._rack_id

    @property
    def sucursal_id(self) -> int:
        return self._sucursal_id

    @property
    def zona(self) -> str:
        return self._zona

    @property
    def frecuencia_dias(self) -> int:
        return self._frecuencia_dias

    @property
    def es_expansion(self) -> bool:
        return self._es_expansion

    @property
    def peso_actual_kg(self) -> float:
        return self._peso_actual_kg

    @property
    def tarimas_ocupadas(self) -> int:
        return len(self._posiciones)

    # --- Metodos publicos con reglas del CEDI ---
    def buscar_posicion_libre(self) -> tuple[int, int] | None:
        """Devuelve la primera tupla (nivel, posicion) libre o None si esta lleno."""
        for nivel in range(1, self.NIVELES + 1):
            for posicion in range(1, self.TARIMAS_POR_NIVEL + 1):
                if (nivel, posicion) not in self._posiciones:
                    return (nivel, posicion)
        return None

    def puede_acomodar(self, tarima: Tarima) -> dict:
        """Valida peso total del rack (32,000 kg), altura de tarima y espacio libre."""
        altura_ok = not tarima.validar_altura()["excede_altura"] and (
            tarima.alto_m <= self.ALTURA_MAX_RACK_M
        )
        peso_resultante = self._peso_actual_kg + tarima.peso_kg
        peso_ok = peso_resultante <= self.CAPACIDAD_MAX_KG
        posicion_libre = self.buscar_posicion_libre()
        espacio_ok = posicion_libre is not None
        sin_incidencia = tarima.incidencia == "ninguna"

        motivo = "OK"
        if not sin_incidencia:
            motivo = f"Tarima con incidencia activa ({tarima.incidencia})."
        elif not altura_ok:
            motivo = f"Altura {tarima.alto_m} m excede limite permitido ({Tarima.ALTURA_MAX_M} m)."
        elif not peso_ok:
            motivo = (
                f"Excede capacidad del rack ({peso_resultante} kg > {self.CAPACIDAD_MAX_KG} kg)."
            )
        elif not espacio_ok:
            motivo = "Rack sin posiciones libres (32/32 ocupadas)."

        return {
            "rack_id": self._rack_id,
            "zona": self._zona,
            "qr": tarima.codigo_qr,
            "puede_acomodar": altura_ok and peso_ok and espacio_ok and sin_incidencia,
            "posicion_sugerida": posicion_libre,
            "peso_resultante_kg": peso_resultante,
            "motivo": motivo,
        }

    def acomodar_tarima(self, tarima: Tarima) -> dict:
        """Acomoda la tarima en la primera posicion libre si cumple todas las reglas."""
        evaluacion = self.puede_acomodar(tarima)
        if not evaluacion["puede_acomodar"]:
            raise ValueError(f"No se puede acomodar tarima: {evaluacion['motivo']}")

        nivel, posicion = evaluacion["posicion_sugerida"]
        self._posiciones[(nivel, posicion)] = tarima.codigo_qr
        self._peso_actual_kg += tarima.peso_kg
        tarima.cambiar_estado("acomodada")

        return {
            "rack_id": self._rack_id,
            "zona": self._zona,
            "es_expansion": self._es_expansion,
            "nivel": nivel,
            "posicion": posicion,
            "qr": tarima.codigo_qr,
            "peso_acumulado_kg": self._peso_actual_kg,
            "tarimas_ocupadas": self.tarimas_ocupadas,
        }

    def liberar_posicion(self, codigo_qr: str, peso_tarima_kg: float) -> None:
        """Libera la posicion de una tarima al salir a embarque."""
        qr_objetivo = codigo_qr.strip()
        clave_encontrada = None
        for clave, qr in self._posiciones.items():
            if qr == qr_objetivo:
                clave_encontrada = clave
                break

        if clave_encontrada is None:
            raise ValueError(f"El QR '{qr_objetivo}' no se encontro en el rack {self._rack_id}.")

        del self._posiciones[clave_encontrada]
        self._peso_actual_kg = max(0.0, self._peso_actual_kg - float(peso_tarima_kg))

    def to_dict(self) -> dict:
        return {
            "rack_id": self._rack_id,
            "sucursal_id": self._sucursal_id,
            "zona": self._zona,
            "frecuencia_dias": self._frecuencia_dias,
            "es_expansion": self._es_expansion,
            "altura_max_rack_m": self.ALTURA_MAX_RACK_M,
            "capacidad_max_kg": self.CAPACIDAD_MAX_KG,
            "peso_actual_kg": self._peso_actual_kg,
            "tarimas_ocupadas": self.tarimas_ocupadas,
            "capacidad_max_tarimas": self.CAPACIDAD_MAX_TARIMAS,
            "posiciones": [
                {"nivel": n, "posicion": p, "qr": qr}
                for (n, p), qr in sorted(self._posiciones.items())
            ],
        }


if __name__ == "__main__":
    rack_a1 = Almacenamiento(
        rack_id="RACK-A-01",
        sucursal_id=12,
        zona="A",
        frecuencia_dias=1,
        es_expansion=False,
    )
    t_ok = Tarima(
        codigo_qr="QR-CEDI-010",
        folio_factura="FAC-9900",
        sucursal_destino=12,
        peso_kg=950.0,
        alto_m=1.60,
    )
    print("Acomodo:", rack_a1.acomodar_tarima(t_ok))
    print("Estado rack:", rack_a1.to_dict())