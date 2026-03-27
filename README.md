# 🧾 TicketReceiptBot

Bot de Telegram que procesa fotos de tickets de compra automáticamente usando IA y guarda los gastos en Notion. También registra gastos sin ticket y ingresos por texto.

## ¿Cómo funciona?

1. Le mandás una foto de un ticket al bot por Telegram
2. Claude AI lee la imagen y extrae tienda, fecha, productos, precios y categorías
3. Los datos se guardan automáticamente en tu Notion — un registro por ticket y uno por cada producto

Si no tenés ticket, escribís `/gasto almacén $350 tarjeta de débito` y queda registrado igual. También podés mandar una foto con caption para agregar info que no aparece en el ticket, como el medio de pago o si fue necesario o no.

## Stack

| Herramienta | Rol | Costo |
|---|---|---|
| Python 3.13+ | Cerebro que conecta todo | Gratis |
| python-telegram-bot | Interfaz con Telegram | Gratis |
| Claude API (Anthropic) | Lee imágenes y extrae datos | ~$0.003 por ticket |
| Notion API | Base de datos visual | Gratis |
| Railway | Servidor 24/7 | Gratis (trial) / $5/mes |

## Contexto y decisiones de arquitectura

El proyecto nació de una necesidad simple: sacar foto a un ticket del supermercado y que los datos queden guardados solos en algún lado. La idea inicial era usar Make o Zapier, pero decidimos construirlo nosotros para que sea replicable, personalizable y un proyecto personal real con documentación propia.

**¿Por qué Telegram y no WhatsApp?**
WhatsApp tiene una API oficial que es paga y burocrática. Telegram es gratuito, tiene una API excelente y @BotFather te permite crear un bot en 5 minutos.

**¿Por qué Claude y no Gemini?**
Empezamos con Gemini porque tiene un tier gratuito generoso (1500 requests por día). El problema fue que las cuentas de Google Workspace tienen el acceso a AI Studio bloqueado por el administrador de la organización, así que el `limit: 0` era permanente. Después de varias pruebas con distintas cuentas y modelos, cambiamos a la API de Claude de Anthropic. Con $5 de crédito procesás miles de tickets — cada imagen cuesta fracciones de centavo.

**¿Por qué Notion y no una base de datos?**
Notion tiene una API gratuita, es visual, permite hacer dashboards y filtros sin código, y cualquiera que quiera replicar el proyecto ya lo tiene o puede crearlo gratis.

**¿Por qué Railway?**
El bot tiene que correr 24/7 para poder recibir mensajes en cualquier momento. Railway tiene un tier gratuito, se conecta a GitHub y cada vez que hacés `git push` redespliega automáticamente. Para uso personal es más que suficiente.

## Plantilla de Notion

¿No querés configurar las tablas desde cero? Duplicá la plantilla con un click:

👉 [Duplicar plantilla de Notion](https://flicker-baker-e2f.notion.site/ReciboBot-Template-330e548e6cdd80aba23df6c3f4e8e857?source=copy_link)

Incluye las tablas Tickets, Detalle e Ingresos ya configuradas con todas las columnas, relaciones y opciones de Select.

## Uso

### Foto de ticket
Mandá cualquier foto de ticket al bot. Si el ticket no muestra el medio de pago o querés aclarar algo, agregá un caption:
```
[foto] + "efectivo, innecesario"
[foto] + "tarjeta de débito"
[foto] + "crédito, necesario"
```

### Registrar un gasto sin ticket
```
/gasto almacén Don Jorge $350 hoy tarjeta de débito
/gasto Uber $180 hoy, necesario
/gasto 3 bidones de agua $120 cada uno, efectivo
```

### Registrar un ingreso
```
/ingreso mensualidad de papá $5000
/ingreso cobré sueldo $25000 hoy
/ingreso me transfirieron $1500 de Juan
```

## Deploy

El bot corre 24/7 en Railway sin necesidad de tener tu computadora encendida. Cada vez que hacés `git push` a GitHub, Railway detecta el cambio y redespliega automáticamente en 2-3 minutos.

Para configurar tu propio deploy seguí las instrucciones en [SETUP.md](SETUP.md).