class Tarima:
    ALTURA_MAX_M = 1.85
    LARGO_BASE_M = 1.12
    ANCHO_BASE_M = 1.15
    ESTADOS_VALIDOS = {"en_camino", "recibida", "incidencia", "acomodada", "embarcada"}
    INCIDENCIAS_VALIDAS = {"ninguna", "cambio", "media", "faltante", "sobrante"}

    def __init__(
        self,
        codigo_qr: str,
        folio_factura: str,
        sucursal_destino: int,
        peso_kg: float,
        alto_m: float,
        estado: str = "en_camino",
        incidencia: str = "ninguna",
    ):
        if not 1 <= sucursal_destino <= 32:
            raise ValueError("La sucursal destino debe estar entre 1 y 32")
        if peso_kg <= 0:
            raise ValueError("El peso debe ser mayor a 0")
        if alto_m <= 0:
            raise ValueError("La altura debe ser mayor que 0")

        self._codigo_qr = codigo_qr.strip()
        self._folio_factura = folio_factura.strip()
        self._sucursal_destino = sucursal_destino
        self._peso_kg = float(peso_kg)
        self._alto_m = float(alto_m)
        self._estado = estado if estado in self.ESTADOS_VALIDOS else "en_camino"
        self._incidencia = (
            incidencia if incidencia in self.INCIDENCIAS_VALIDAS else "ninguna"
        )
        self._nota_incidencia = ""

    @property
    def codigo_qr(self) -> str:
        return self._codigo_qr

    @property
    def folio_factura(self) -> str:
        return self._folio_factura

    @property
    def sucursal_destino(self) -> int:
        return self._sucursal_destino

    @property
    def peso_kg(self) -> float:
        return self._peso_kg

    @property
    def alto_m(self) -> float:
        return self._alto_m

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def incidencia(self) -> str:
        return self._incidencia

    @property
    def nota_incidencia(self) -> str:
        return self._nota_incidencia

    # METODOS PUBLICOS CON LAS REGLAS DEL CEDI
    def validar_altura(self) -> dict:
        excede = self._alto_m > self.ALTURA_MAX_M
        return {
            "qr": self._codigo_qr,
            "alto_m": self._alto_m,
            "max_permitido_m": self.ALTURA_MAX_M,
            "excede_altura": excede,
        }

    def registrar_incidencia(self, tipo: str, nota: str = "") -> None:
        tipo_limpio = tipo.strip().lower()
        if tipo_limpio not in self.INCIDENCIAS_VALIDAS or tipo_limpio == "ninguna":
            raise ValueError(
                f"Incidencia no valida '{tipo}'. Usa: cambio, media, faltante o sobrante."
            )
        self._incidencia = tipo_limpio
        self._nota_incidencia = nota.strip()
        self._estado = "incidencia"

    def cambiar_estado(self, nuevo_estado: str) -> None:
        estado_limpio = nuevo_estado.strip().lower()
        if estado_limpio not in self.ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado no valido '{nuevo_estado}'. Usa: {', '.join(sorted(self.ESTADOS_VALIDOS))}."
            )

        # BLOQUEO DE EMBARCACION SI HAY INCIDENCIA
        if estado_limpio == "embarcada" and self._incidencia != "ninguna":
            raise RuntimeError(
                f"No se puede embarcar la tarima {self._codigo_qr} con incidencia '{self._incidencia}' activa."
            )
        self._estado = estado_limpio

    def to_dict(self) -> dict:
        """Se puede mandar este objeto a JSON en su RedAPI o guardarlo en BD."""
        return {
            "codigo_qr": self._codigo_qr,
            "folio_factura": self._folio_factura,
            "sucursal_destino": self._sucursal_destino,
            "peso_kg": self._peso_kg,
            "alto_m": self._alto_m,
            "estado": self._estado,
            "incidencia": self._incidencia,
            "nota_incidencia": self._nota_incidencia,
        }


if __name__ == "__main__":
    t1 = Tarima(
        codigo_qr="QR-CEDI-001",
        folio_factura="AFC-9841",
        sucursal_destino=12,
        peso_kg=850.0,
        alto_m=1.92,
    )
    print("Revision de altura:", t1.validar_altura())
    t1.registrar_incidencia("media", "Llego media tarima respecto a la orden")
    print("Estado actual:", t1.to_dict())
    