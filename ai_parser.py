import os
import asyncio
import json
import anthropic
from datetime import date
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def hoy():
    return date.today().strftime("%Y-%m-%d")

PROMPT_IMAGE = """
Analizá esta imagen de un ticket de compra y extraé los datos en formato JSON.
Devolvé SOLO el JSON, sin texto adicional, sin bloques de código.

El JSON debe tener esta estructura exacta:
{
  "data": {
    "tienda": "nombre del local",
    "fecha": "YYYY-MM-DD",
    "total": 123.45,
    "moneda": "UYU",
    "categoria": "Supermercado",
    "medio_pago": "Tarjeta de crédito",
    "productos": [
      {"producto": "nombre", "precio": 12.34, "categoria": "Frutas", "tipo": "Necesario"},
      {"producto": "nombre", "precio": 56.78, "categoria": "Otro", "tipo": "Innecesario"}
    ]
  },
  "aproximado": false
}

REGLAS:
- La moneda por defecto es UYU salvo que diga explícitamente USD o dólares
- Si el ticket no tiene detalle de productos (ej: ticket de POS), dejá productos como lista vacía []
- Si algún precio es aproximado o estimado, poné "aproximado": true
- Asigná "tipo" a cada producto: Necesario para comida básica, limpieza, higiene, medicamentos. Innecesario para snacks, golosinas, bebidas alcohólicas, artículos de lujo
- medio_pago: detectalo del ticket. Opciones: "Tarjeta de crédito", "Tarjeta de débito", "Efectivo", "Transferencia". Si no podés determinarlo, usá null
- Si el usuario manda información adicional en el caption, esa información tiene prioridad sobre lo que detectes visualmente
- Categorías para el ticket: Supermercado, Restaurante / Comida, Transporte, Farmacia, Entretenimiento, Ropa, Servicios, Otro
- Categorías para productos: Frutas, Verduras, Carnes, Lácteos, Limpieza, Bebidas, Otro
- Si no podés leer algún dato, usá null
"""

PROMPT_GASTO = """
El usuario describe un gasto en Uruguay. Extraé los datos en formato JSON.
Devolvé SOLO el JSON, sin texto adicional, sin bloques de código.

Texto: "{texto}"
Fecha de hoy: {hoy}

El JSON debe tener esta estructura exacta:
{{
  "data": {{
    "tienda": "nombre del local",
    "fecha": "{hoy}",
    "total": 123.45,
    "moneda": "UYU",
    "categoria": "categoria",
    "medio_pago": "Efectivo",
    "productos": [
      {{"producto": "nombre", "precio": 12.34, "categoria": "Otro", "tipo": "Necesario"}}
    ]
  }},
  "aproximado": false
}}

REGLAS:
- La moneda por defecto es SIEMPRE UYU salvo que diga explícitamente dólares o USD
- Si menciona cantidades (ej: "3 bidones a $120"), calculá el total del producto (3x120=360) y nombralo correctamente
- Si dice "hoy", usá la fecha de hoy: {hoy}
- Si el precio es aproximado ("creo que", "más o menos"), poné "aproximado": true
- Si el ticket es de POS o no tiene detalle de productos, dejá productos como lista vacía []
- Asigná "tipo" a cada producto: Necesario para comida básica, limpieza, higiene. Innecesario para snacks, golosinas, lujos
- medio_pago: detectalo del texto. Opciones: "Tarjeta de crédito", "Tarjeta de débito", "Efectivo", "Transferencia". Si no se menciona, usá "Efectivo" por defecto
- Categorías: Supermercado, Restaurante / Comida, Transporte, Farmacia, Entretenimiento, Ropa, Servicios, Otro
- Si el usuario escribe la fecha en formato DD/MM/YY o DD/MM/YYYY, convertila a YYYY-MM-DD
"""

PROMPT_INGRESO = """
El usuario describe un ingreso de dinero en Uruguay. Extraé los datos en formato JSON.
Devolvé SOLO el JSON, sin texto adicional, sin bloques de código.

Texto: "{texto}"
Fecha de hoy: {hoy}

El JSON debe tener esta estructura exacta:
{{
  "data": {{
    "concepto": "descripción del ingreso",
    "monto": 123.45,
    "fecha": "{hoy}",
    "moneda": "UYU",
    "fuente": "Mensualidad familia"
  }},
  "aproximado": false
}}

REGLAS:
- La moneda por defecto es SIEMPRE UYU salvo que diga explícitamente dólares o USD
- Si dice "hoy", usá la fecha de hoy: {hoy}
- Si el monto es aproximado, poné "aproximado": true
- Fuentes posibles: Mensualidad familia, Transferencia familia, Sueldo, Freelance, Otro
- Intentá detectar la fuente del contexto (ej: "me mandó plata papá" → "Mensualidad familia")
"""

def calcular_tipo_ticket(productos):
    if not productos:
        return "Necesario"
    
    monto_necesario = sum(p.get("precio") or 0 for p in productos if p.get("tipo") == "Necesario")
    monto_innecesario = sum(p.get("precio") or 0 for p in productos if p.get("tipo") == "Innecesario")
    count_necesario = sum(1 for p in productos if p.get("tipo") == "Necesario")
    count_innecesario = sum(1 for p in productos if p.get("tipo") == "Innecesario")

    if count_necesario > count_innecesario:
        return "Necesario"
    elif count_innecesario > count_necesario:
        return "Innecesario"
    else:
        return "Necesario" if monto_necesario >= monto_innecesario else "Innecesario"

async def parse_ticket_image(image_bytes: bytes, caption: str = ""):
    try:
        import base64
        image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
        
        prompt = PROMPT_IMAGE
        if caption:
            prompt += f"\n\nEl usuario agregó esta información adicional sobre el ticket: \"{caption}\". Usá estos datos para completar o corregir lo que no podés leer de la imagen. Tienen prioridad sobre lo que detectes visualmente."

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": prompt}
                ],
            }]
        )
        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        result["data"]["tipo"] = calcular_tipo_ticket(result["data"].get("productos", []))
        return result
    except Exception as e:
        print(f"Error parsing image: {e}")
        return None


async def parse_ticket_text(text: str):
    try:
        prompt = PROMPT_GASTO.format(texto=text, hoy=hoy())
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.content[0].text.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(result)
        parsed["data"]["tipo"] = calcular_tipo_ticket(parsed["data"].get("productos", []))
        return parsed
    except Exception as e:
        print(f"Error parsing text: {e}")
        return None

async def parse_ingreso_text(text: str):
    try:
        prompt = PROMPT_INGRESO.format(texto=text, hoy=hoy())
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.content[0].text.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result)
    except Exception as e:
        print(f"Error parsing ingreso: {e}")
        return None