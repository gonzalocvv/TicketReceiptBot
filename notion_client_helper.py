import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))

TICKETS_DB = os.getenv("NOTION_TICKETS_DB")
DETALLE_DB = os.getenv("NOTION_DETALLE_DB")

async def save_ticket(data: dict):
    try:
        # Crear fila en Tickets
        ticket_page = notion.pages.create(
            parent={"database_id": TICKETS_DB},
            properties={
                "Tienda": {
                    "title": [{"text": {"content": data.get("tienda") or "Sin nombre"}}]
                },
                "Fecha": {
                    "date": {"start": data.get("fecha")} if data.get("fecha") else None
                },
                "Total": {
                    "number": data.get("total")
                },
                "Categoría": {
                    "select": {"name": data.get("categoria") or "Otro"}
                },
                "Tipo": {
                    "select": {"name": data.get("tipo") or "Necesario"}
                },
                "Moneda": {
                    "select": {"name": data.get("moneda") or "UYU"}
                },
            }
        )

        ticket_id = ticket_page["id"]

        # Crear filas en Detalle por cada producto
        productos = data.get("productos") or []
        for p in productos:
            notion.pages.create(
                parent={"database_id": DETALLE_DB},
                properties={
                    "Producto": {
                        "title": [{"text": {"content": p.get("producto") or "Sin nombre"}}]
                    },
                    "Precio": {
                        "number": p.get("precio")
                    },
                    "Categoría": {
                        "select": {"name": p.get("categoria") or "Otro"}
                    },
                    "Tickets": {
                        "relation": [{"id": ticket_id}]
                    },
                }
            )

        print(f"✅ Ticket guardado: {data.get('tienda')}")

    except Exception as e:
        print(f"❌ Error guardando en Notion: {e}")