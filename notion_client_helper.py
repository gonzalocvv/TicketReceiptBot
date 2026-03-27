import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))

TICKETS_DB = os.getenv("NOTION_TICKETS_DB")
DETALLE_DB = os.getenv("NOTION_DETALLE_DB")
INGRESOS_DB = os.getenv("NOTION_INGRESOS_DB")

async def save_ticket(data: dict):
    try:
        ticket_page = notion.pages.create(
            parent={"database_id": TICKETS_DB},
            properties={
                "Tienda": {"title": [{"text": {"content": data.get("tienda") or "Sin nombre"}}]},
                "Fecha": {"date": {"start": data.get("fecha")} if data.get("fecha") else None},
                "Total": {"number": data.get("total")},
                "Categoría": {"select": {"name": data.get("categoria") or "Otro"}},
                "Tipo": {"select": {"name": data.get("tipo") or "Necesario"}},
                "Moneda": {"select": {"name": data.get("moneda") or "UYU"}},
                "Medio de pago": {"select": {"name": data.get("medio_pago")} if data.get("medio_pago") else None},
            }
        )
        ticket_id = ticket_page["id"]
        for p in data.get("productos") or []:
            notion.pages.create(
                parent={"database_id": DETALLE_DB},
                properties={
                    "Producto": {"title": [{"text": {"content": p.get("producto") or "Sin nombre"}}]},
                    "Precio": {"number": p.get("precio")},
                    "Categoría": {"select": {"name": p.get("categoria") or "Otro"}},
                    "Tipo": {"select": {"name": p.get("tipo") or "Necesario"}},
                    "Tickets": {"relation": [{"id": ticket_id}]},
                }
            )
        print(f"✅ Ticket guardado: {data.get('tienda')}")
    except Exception as e:
        print(f"❌ Error guardando ticket: {e}")

async def save_ingreso(data: dict):
    try:
        notion.pages.create(
            parent={"database_id": INGRESOS_DB},
            properties={
                "Concepto": {"title": [{"text": {"content": data.get("concepto") or "Sin concepto"}}]},
                "Monto": {"number": data.get("monto")},
                "Fecha": {"date": {"start": data.get("fecha")} if data.get("fecha") else None},
                "Moneda": {"select": {"name": data.get("moneda") or "UYU"}},
                "Fuente": {"select": {"name": data.get("fuente") or "Otro"}},
            }
        )
        print(f"✅ Ingreso guardado: {data.get('concepto')}")
    except Exception as e:
        print(f"❌ Error guardando ingreso: {e}")