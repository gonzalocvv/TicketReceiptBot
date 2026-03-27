# ⚙️ SETUP — Guía de configuración completa

Esta guía documenta el proceso completo para configurar TicketReceiptBot desde cero. Está escrita como un relato de lo que realmente hicimos, no como un tutorial genérico, así que vas a encontrar contexto sobre por qué tomamos cada decisión.

---

## Contexto y decisiones de arquitectura

El proyecto nació de una necesidad simple: sacar foto a un ticket del supermercado y que los datos queden guardados solos en algún lado. La idea inicial era usar Make o Zapier, pero decidimos construirlo nosotros para que sea replicable, personalizable y un proyecto personal real con documentación propia.

**¿Por qué Telegram y no WhatsApp?**
WhatsApp tiene una API oficial que es paga y burocrática. Telegram es gratuito, tiene una API excelente y @BotFather te permite crear un bot en 5 minutos.

**¿Por qué Claude y no Gemini?**
Empezamos con Gemini porque tiene un tier gratuito generoso (1500 requests por día). El problema fue que las cuentas de Google Workspace tienen el acceso a AI Studio bloqueado por el administrador de la organización, así que el `limit: 0` era permanente. Después de varias pruebas con distintas cuentas y modelos, cambiamos a la API de Claude de Anthropic. Con $5 de crédito procesás miles de tickets — cada imagen cuesta fracciones de centavo.

**¿Por qué Notion y no una base de datos?**
Notion tiene una API gratuita, es visual, permite hacer dashboards y filtros sin código, y cualquiera que quiera replicar el proyecto ya lo tiene o puede crearlo gratis. No necesitás saber SQL para ver tus gastos.

**¿Por qué Railway?**
El bot tiene que correr 24/7 para poder recibir mensajes en cualquier momento. Railway tiene un tier gratuito, se conecta a GitHub y cada vez que hacés `git push` redespliega automáticamente. Para uso personal es más que suficiente.

---

## Parte 1 — Crear el bot de Telegram

Esta parte es completamente gratuita y tarda menos de 5 minutos.

### 1.1 Crear el bot con @BotFather

Abrí Telegram (en el celular o en la web) y buscá **@BotFather** — tiene una tilde azul de verificación. Es el bot oficial de Telegram para crear y administrar bots.

Mandále el comando:
```
/newbot
```

Te va a pedir dos cosas:

**Nombre visible** — es lo que aparece en el encabezado del chat. Puede tener espacios y caracteres especiales. Ejemplo: `Recibo Gastos`

**Username** — tiene que ser único en Telegram y terminar obligatoriamente en `bot`. Ejemplo: `reciboGastos_bot`

Una vez creado, BotFather te manda un mensaje con el token. Tiene este formato:
```
8213716206:AAFJjW...
```

> ⚠️ Este token es como la contraseña de tu bot. Cualquiera que lo tenga puede controlarlo completamente. Nunca lo subas a GitHub ni lo compartas públicamente.

Guardalo en un lugar seguro — lo vas a necesitar más adelante.

---

## Parte 2 — Obtener la API Key de Claude (Anthropic)

### 2.1 Crear cuenta y cargar créditos

Entrá a **console.anthropic.com** y creá una cuenta si no tenés una.

Antes de poder usar la API necesitás cargar créditos. Con **$5** tenés para procesar miles de tickets — el costo por imagen es de aproximadamente $0.003, o sea menos de medio centavo uruguayo. No hay suscripción ni cobro automático: solo pagás cuando querés agregar más créditos.

Menú izquierdo → **Billing** → **Add credit**

### 2.2 Crear la API Key

Menú izquierdo → **API Keys** → **Create Key**

Ponele un nombre descriptivo, por ejemplo `recibobot`.

La key se muestra **una sola vez**. Tiene este formato:
```
sk-ant-api03-...
```

Copiala y guardala junto con el token de Telegram.

> ⚠️ Si la perdés tenés que crear una nueva. No hay forma de recuperarla.

---

## Parte 3 — Configurar Notion

Esta parte tiene varios pasos pero todos son gratuitos.

### 3.1 Duplicar la plantilla

La forma más fácil es usar la plantilla que ya está configurada con todas las tablas y columnas:

👉 [Duplicar plantilla de Notion](https://www.notion.so/ReciboBot-320e548e6cdd8090b316c7b819d1cd5b?source=copy_link)

Click en **Duplicate** y se crea una copia en tu Notion con las tres tablas listas: Tickets, Detalle e Ingresos.

Si preferís crear las tablas desde cero, la estructura es la siguiente:

**Tabla Tickets:**
| Columna | Tipo |
|---|---|
| Tienda | Title |
| Fecha | Date |
| Total | Number |
| Categoría | Select |
| Tipo | Select (Necesario / Innecesario) |
| Moneda | Select (UYU / USD) |
| Medio de pago | Select (Tarjeta de crédito / Tarjeta de débito / Efectivo / Transferencia) |

**Tabla Detalle:**
| Columna | Tipo |
|---|---|
| Producto | Title |
| Precio | Number |
| Categoría | Select |
| Tipo | Select (Necesario / Innecesario) |
| Tickets | Relation → Tickets |

**Tabla Ingresos:**
| Columna | Tipo |
|---|---|
| Concepto | Title |
| Monto | Number |
| Fecha | Date |
| Fuente | Select |
| Moneda | Select (UYU / USD) |

### 3.2 Crear la Integration

Para que el bot pueda escribir en tu Notion necesitás crear una "Integration" — es básicamente una app con permiso de acceso a tu workspace.

Entrá a **notion.so/profile/integrations** → click en **Internal integrations** → **New integration**

- **Nombre:** ReciboBot
- **Associated workspace:** seleccioná tu workspace
- Click en **Create**

Te aparece el **Internal Integration Token** que empieza con `ntn_` (antes empezaban con `secret_`, ambos formatos funcionan igual).

Guardalo junto con los otros tokens.

### 3.3 Conectar la Integration a tu página

La integration no tiene acceso a nada por defecto. Tenés que conectarla explícitamente a tu página de ReciboBot.

En la pestaña **Content access** dentro de la Integration, buscá y seleccioná la página **ReciboBot**. Así el bot va a poder leer y escribir en tus tablas.

### 3.4 Obtener los Database IDs

Cada tabla en Notion tiene un ID único que el bot necesita para saber dónde escribir. Lo encontrás en la URL cuando abrís la tabla:
```
https://notion.so/NombreDeLaTabla-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...
```

La parte entre el último `-` y el `?` son 32 caracteres — ese es el Database ID.

Necesitás el ID de las tres tablas: **Tickets**, **Detalle** e **Ingresos**.

> No los compartas públicamente. Son únicos para tu workspace.

---

## Parte 4 — Clonar el repositorio

### 4.1 Requisitos previos

- **Python 3.11+** — descargalo desde python.org si no lo tenés. En Mac, al instalar asegurate de que quede accesible como `python3` en la Terminal.
- **Git** — viene instalado en Mac por defecto.
- **VS Code** (recomendado) — para editar los archivos de configuración.

### 4.2 Clonar el repo
```bash
git clone https://github.com/gonzalocvv/TicketReceiptBot.git
cd TicketReceiptBot
```

### 4.3 Crear el entorno virtual e instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

El entorno virtual (`venv`) aísla las librerías del proyecto del resto de tu sistema. Cada vez que abras una Terminal nueva y quieras correr el bot, tenés que activarlo con `source venv/bin/activate`.

---

## Parte 5 — Configurar las variables de entorno

Copiá el archivo de ejemplo:
```bash
cp .env.example .env
```

Abrí el `.env` en VS Code y completá con tus valores:
```
# Telegram
TELEGRAM_TOKEN=8213716206:AAFJjWhp...

# Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Notion
NOTION_TOKEN=ntn_...
NOTION_TICKETS_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DETALLE_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_INGRESOS_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ El archivo `.env` está en el `.gitignore` — nunca se sube a GitHub. Cada persona que clone el repo tiene que crear el suyo propio con sus propias keys.

---

## Parte 6 — Correr el bot localmente

Con el entorno virtual activo:
```bash
python3 bot.py
```

Deberías ver:
```
🤖 Bot corriendo...
```

Abrí Telegram, buscá tu bot y mandále una foto de un ticket. Si todo está bien configurado, en unos segundos el bot te confirma el gasto y aparece una nueva fila en tu tabla de Notion.

> ⚠️ Nunca corras el bot localmente y en Railway al mismo tiempo. Telegram no permite dos instancias del mismo bot corriendo en paralelo y vas a ver un error de `Conflict`.

---

## Parte 7 — Deploy en Railway (24/7)

Cuando el bot corre localmente solo funciona mientras tenés la computadora encendida. Para que funcione siempre, lo deployamos en Railway.

### 7.1 Crear cuenta en Railway

Entrá a **railway.app** y creá una cuenta con GitHub. Aceptá los términos de uso — el bot no viola ninguno.

### 7.2 Crear el proyecto

Click en **New Project** → **Deploy from GitHub repo** → seleccioná **TicketReceiptBot**

Railway detecta automáticamente el `Procfile` y sabe que tiene que correr `python3 bot.py`.

### 7.3 Configurar las variables de entorno en Railway

El `.env` nunca se sube a GitHub, así que tenés que cargar las variables manualmente en Railway.

Click en el servicio **worker** → pestaña **Variables** → agregá cada variable con su valor:
```
TELEGRAM_TOKEN
ANTHROPIC_API_KEY
NOTION_TOKEN
NOTION_TICKETS_DB
NOTION_DETALLE_DB
NOTION_INGRESOS_DB
```

Una vez cargadas todas, Railway hace un redeploy automático y el bot queda corriendo 24/7.

### 7.4 Deploys automáticos

A partir de ahora, cada vez que hacés cambios en el código y los subís a GitHub:
```bash
git add .
git commit -m "descripción del cambio"
git push origin main
```

Railway detecta el push y redespliega automáticamente en 2-3 minutos. No tenés que hacer nada más.

---

## Resumen de tokens necesarios

| Variable | Dónde se obtiene | Costo |
|---|---|---|
| `TELEGRAM_TOKEN` | @BotFather en Telegram | Gratis |
| `ANTHROPIC_API_KEY` | console.anthropic.com | $5 mínimo (dura meses) |
| `NOTION_TOKEN` | notion.so/profile/integrations | Gratis |
| `NOTION_TICKETS_DB` | URL de la tabla en Notion | Gratis |
| `NOTION_DETALLE_DB` | URL de la tabla en Notion | Gratis |
| `NOTION_INGRESOS_DB` | URL de la tabla en Notion | Gratis |