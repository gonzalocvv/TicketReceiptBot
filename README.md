# 🧾 TicketReceiptBot

Bot de Telegram que procesa fotos de tickets de compra automáticamente usando IA y guarda los gastos en Notion.

## ¿Cómo funciona?

1. Le mandás una foto de un ticket al bot por Telegram
2. Gemini AI extrae los datos (tienda, fecha, productos, precios)
3. Los datos se guardan automáticamente en tu base de datos de Notion

También podés mandarle texto como `Transferencia a Juan $500 comida` y lo registra igual.

## Stack

- Python 3.13+
- python-telegram-bot
- Google Gemini API (gratuito)
- Notion API (gratuito)

## Configuración

### 1. Clonar el repo
```bash
git clone https://github.com/gonzalocvv/TicketReceiptBot.git
cd TicketReceiptBot
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copiá el archivo de ejemplo y completá con tus tokens:
```bash
cp .env.example .env
```

Editá el `.env` con tus valores:
```
TELEGRAM_TOKEN=tu_token_de_botfather
GEMINI_API_KEY=tu_api_key_de_google
NOTION_TOKEN=tu_token_de_notion
NOTION_TICKETS_DB=id_de_tu_base_tickets
NOTION_DETALLE_DB=id_de_tu_base_detalle
NOTION_INGRESOS_DB=id_de_tu_base_ingresos
```

### 4. Configurar Notion
- Crear una Integration en notion.so/profile/integrations
- Conectar la integration a tu página de ReciboBot
- Podes crear las tablas Tickets, Detalle e Ingresos (ver estructura abajo)
- También podes duplicar la plantilla directamente:

## 📋 Plantilla de Notion

👉 [Duplicar plantilla de Notion](https://www.notion.so/ReciboBot-320e548e6cdd8090b316c7b819d1cd5b?source=copy_link)

Incluye las tablas Tickets, Detalle e Ingresos ya configuradas con todas las columnas y relaciones.

### 5. Correr el bot
```bash
python3 bot.py
```

## Estructura de Notion

**Tabla Tickets:** Tienda (Title), Fecha (Date), Total (Number), Categoría (Select), Tipo (Select), Moneda (Select)

**Tabla Detalle:** Producto (Title), Precio (Number), Categoría (Select), Tickets (Relation)

**Tabla Ingresos:** Concepto (Title), Monto (Number), Fecha (Date), Fuente (Select), Moneda (Select)

## Uso

- **Foto de ticket** → mandá la imagen al bot
- **Gasto sin ticket** → escribí algo como `Uber $150 transporte`

## Deploy

Para correr el bot 24/7 sin tu computadora, podés desplegarlo en Railway o Render (ambos gratuitos para uso personal).