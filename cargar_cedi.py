import psycopg

HOST = "aws-1-us-west-2.pooler.supabase.com"
PORT = 5432
DBNAME = "postgres"
USER = "postgres.ncdifwgcujdwsjcyftqk"
PASSWORD = "ApexLogic*12"


def cargar_datos_cedi(conn):
    with conn.cursor() as cur:
        # 1. Orden de compra (ejemplo: proveedor 1 ya existe en datos iniciales)
        cur.execute(
            """
            INSERT INTO orden_compra (folio_oc, id_proveedor, fecha_emision)
            VALUES (%s, %s, %s)
            ON CONFLICT (folio_oc) DO NOTHING
            RETURNING id_oc
            """,
            ("OC-2026-0099", 1, "2026-11-25"),
        )
        row = cur.fetchone()
        if row:
            id_oc = row[0]
        else:
            cur.execute("SELECT id_oc FROM orden_compra WHERE folio_oc = %s", ("OC-2026-0099",))
            id_oc = cur.fetchone()[0]

        # 2. Detalle de OC (sku e id_sucursal deben existir en producto y sucursal)
        detalles = [
            (id_oc, "SKU-1001", 1, 120),
            (id_oc, "SKU-1002", 1, 80),
        ]
        for det in detalles:
            cur.execute(
                """
                INSERT INTO oc_detalle (id_oc, sku, id_sucursal, piezas_solicitadas)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id_oc, sku, id_sucursal) DO NOTHING
                """,
                det,
            )

        # 3. Factura (1 factura por OC)
        cur.execute(
            """
            INSERT INTO factura (folio_factura, id_oc, fecha)
            VALUES (%s, %s, %s)
            ON CONFLICT (folio_factura) DO NOTHING
            RETURNING id_factura
            """,
            ("FAC-2026-0099", id_oc, "2026-11-25"),
        )
        f_row = cur.fetchone()
        if f_row:
            id_factura = f_row[0]
        else:
            cur.execute("SELECT id_factura FROM factura WHERE id_oc = %s", (id_oc,))
            id_factura = cur.fetchone()[0]

        # 4. Bultos declarados (altura/peso/volumen/piezas > 0)
        bultos = [
            ("QR-B-900001", id_factura, "SKU-1001", 1, 120, 122.5, 0.18),
            ("QR-B-900002", id_factura, "SKU-1002", 1, 80, 82.0, 0.14),
        ]
        for b in bultos:
            cur.execute(
                """
                INSERT INTO bulto (codigo_qr, id_factura, sku, id_sucursal, piezas, peso_kg, volumen_m3)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (codigo_qr) DO NOTHING
                """,
                b,
            )

    conn.commit()
    print("Carga completada correctamente.")


if __name__ == "__main__":
    with psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        sslmode="require",
    ) as conn:
        cargar_datos_cedi(conn)