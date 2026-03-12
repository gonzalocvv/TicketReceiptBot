import os
import asyncio
import json
from google import genai
from datetime import date
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = """
Analizá esta imagen de un ticket de compra y extraé los datos en formato JSON.
Devolvé SOLO el JSON, sin texto adicional, sin bloques de código.

El JSON debe tener esta estructura exacta:
{
  "tienda": "nombre del local",
  "fecha": "YYYY-MM-DD",
  "total": 123.45,
  "moneda": "UYU",
  "categoria": "Supermercado",
  "tipo": "Necesario",
  "productos": [
    {"producto": "nombre", "precio": 12.34, "categoria": "Frutas"},
    {"producto": "nombre", "precio": 56.78, "categoria": "Carnes"}
  ]
}

Categorías posibles para el ticket: Supermercado, Restaurante / Comida, Transporte, Farmacia, Entretenimiento, Ropa, Servicios, Otro
Categorías posibles para productos: Frutas, Verduras, Carnes, Lácteos, Limpieza, Bebidas, Otro
Tipo: Necesario o Innecesario
Si no podés leer algún dato, usá null.
"""

PROMPT_TEXT = """
El usuario describe un gasto con texto. Extraé los datos en formato JSON.
Devolvé SOLO el JSON, sin texto adicional, sin bloques de código.

Texto del usuario: "{texto}"

El JSON debe tener esta estructura exacta:
{{
  "tienda": "nombre del local o persona",
  "fecha": "{hoy}",
  "total": 123.45,
  "moneda": "UYU",
  "categoria": "categoria del gasto",
  "tipo": "Necesario",
  "productos": []
}}

Categorías posibles: Supermercado, Restaurante / Comida, Transporte, Farmacia, Entretenimiento, Ropa, Servicios, Otro
Tipo: Necesario o Innecesario
Si no podés determinar algún dato, usá null.
"""

async def parse_ticket_image(image_bytes: bytes):
    try:
        from google.genai import types
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.0-flash-lite",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                PROMPT
            ]
        )
        text = response.text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"Error parsing image: {e}")
        return None

async def parse_ticket_text(text: str):
    try:
        hoy = date.today().strftime("%Y-%m-%d")
        prompt = PROMPT_TEXT.format(texto=text, hoy=hoy)
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        result = response.text.strip()
        return json.loads(result)
    except Exception as e:
        print(f"Error parsing text: {e}")
        return None