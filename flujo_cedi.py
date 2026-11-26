import sys
from datetime import datetime
from pathlib import Path

RAIZ_PROYECTO = str(Path(__file__).resolve().parent)
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

from clases.agendamiento import Agendamiento
from clases.almacenamiento import Almacenamiento
from clases.embarque import Embarque
from clases.tarima import Tarima

def ejecutar_flujo_cedi() -> None:
    print("--- 1. Agendamiento de proveedor (Anden recibo 1-4) ---")
    cita = Agendamiento(
        codigo_cita="CITA-2026-010",
        proveedor="BIC",
        folio_orden="OC-7010",
        folio_factura="FAC-8820",
        fecha_hora_inicio=datetime(2026, 11, 25, 9, 0),
        fecha_hora_fin=datetime(2026, 11, 25, 10, 0),
        anden_recibo=1,
        origen_correo="pedidos@BIC.com",
        )
    cita.agregar_qr_esperado("QR-CEDI-101")
    cita.agregar_qr_esperado("QR-CEDI-102")
    print("Ventana", cita.validar_ventana_operativa())
    cita.cambiar_estado("en_anden")
    print("Estado cita:", cita.estado)

    print("\n--- 2. Recepcion / Control de incidencias ---")
    tarima_incidencia = Tarima(
        codigo_qr="QR-CEDI-101",
        folio_factura="FAC-8820",
        sucursal_destino=5,
        peso_kg=600.0,
        alto_m=1.90,
    )
    print("Altura tarima 101:", tarima_incidencia.validar_altura())
    tarima_incidencia.registrar_incidencia(
        "media", "Llego media tarima respecto a la factura"
    )
    print("Tarima 101 con incidencia:", tarima_incidencia.to_dict())

    tarima_valida = Tarima(
        codigo_qr="QR-CEDI-102",
        folio_factura="FAC-8820",
        sucursal_destino=5,
        peso_kg=1100.0,
        alto_m=1.65,
        estado="recibida",
    )
    print("Altura tarima 102:", tarima_valida.validar_altura())

    print("\n--- 3. ALMACENAMIENTO ZONAS (RACK 6m / 32,000 kg / 4x8) ---")
    rack_sucursal_5 = Almacenamiento(
        rack_id="RACK-A-05",
        sucursal_id=5,
        zona="A",
        frecuencia_dias=1,
        es_expansion=False,
    )
    resultado_acomodo = rack_sucursal_5.acomodar_tarima(tarima_valida)
    print("Acomodo exitoso:", resultado_acomodo)

    print("\n--- 4. EMBARQUE EN TORTON (MAX 12 TARIMAS / 12,000 kg) ---")
    embarque_suc_5 = Embarque(
        folio_embarque="EMB-2026-055",
        sucursal_destino=5,
        anden_embarque=1,
        tipo_unidad="Torton",
    )

    # Intento de cargar tarima con incidencia (debe bloquearse...) #
    revision_incidencia = embarque_suc_5.puede_cargar_tarima(tarima_incidencia)
    print("Intento con incidencia:", revision_incidencia)

    # Liberar rack de su tarima valida y subirla al Torton #
    rack_sucursal_5.liberar_posicion(
        tarima_valida.codigo_qr, tarima_valida.peso_kg
    )
    resultado_carga = embarque_suc_5.cargar_tarima(tarima_valida)
    print("Carga al Torton:", resultado_carga)

    relacion = embarque_suc_5.despachar()
    print("\n--- 5. RELACION DE EMBARQUE GENERADA ---")
    print(relacion)


if __name__ == "__main__":
    ejecutar_flujo_cedi()