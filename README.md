        # 🤖 Bot de Cobertores - Sistema de Automatización con IA

Sistema inteligente de procesamiento de emails operacionales con **aprendizaje automático de patrones** y extracción de datos usando IA.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)](https://ai.google.dev/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)](https://www.mysql.com/)

## 📋 Descripción

Proyecto de automatización operacional que **aprende de tu operación** para procesar correos electrónicos de solicitudes de producción. El sistema extrae datos estructurados usando IA, genera reglas automáticas basadas en patrones históricos, y provee un dashboard de gestión inteligente.

**Problema resuelto:** Empresas agrícolas/manufactureras reciben solicitudes por email en formatos no estructurados. La entrada manual consume 10-15 horas/semana y genera errores.

**Solución:** Sistema inteligente que:

* 📧 Captura emails de Gmail con etiqueta específica
* 🧠 **Aprende patrones de emails históricos** (remitentes, urgencias, tipos de solicitud)
* ⚙️ **Genera reglas automáticas** basadas en comportamiento real
* 🤖 Extrae datos usando IA (Google Gemini) con fallback inteligente
* 📊 Procesa adjuntos Excel/PDF con scoring de confianza
* 💾 Almacena en base de datos MySQL
* 📈 Dashboard web para seguimiento y revisión

## 🎯 Caso de Uso Real

Basado en operaciones reales del área de Cobertores en Agrosystems (2024-2025). El sistema procesa solicitudes como:

```
Asunto: Solicitud Cobertor - URGENTE
De: produccion@empresa.cl

Necesito cobertor para:
- Cuartel: 15
- Hileras: 8
- Largo: 120 metros
- Código: COB-001
- Prioridad: ALTA
```

**Output automatizado:**

* ✅ Tarea creada en BD
* ✅ Prioridad detectada automáticamente (por reglas aprendidas o IA)
* ✅ Scoring de confianza en la clasificación
* ✅ Alerta si requiere revisión humana
* ✅ Email marcado como procesado

## 🏗️ Arquitectura

```
        Fase 0: Aprendizaje              Fase 1: Operación
┌─────────────────────────────┐    ┌──────────────────────────┐
│  Gmail Histórico (1-12m)    │    │   Gmail (emails nuevos)  │
│            ↓                │    │           ↓              │
│  historical_scraper.py      │    │   email_processor.py     │
│            ↓                │    │           ↓              │
│  Análisis de patrones       │    │   rules_engine.py        │
│  - Remitentes               │    │           ↓              │
│  - Urgencias                │    │   ¿Regla conocida?       │
│  - Tipos de solicitud       │    │   ├─ Sí → Aplicar regla  │
│            ↓                │    │   └─ No → Usar Gemini    │
│  Base de Conocimiento       │────┤           ↓              │
│  - sender_profiles          │    │   Tarea en BD            │
│  - learned_rules (16)       │    │   + Score confianza      │
└─────────────────────────────┘    └──────────────────────────┘
```

### Stack Tecnológico

| Componente | Tecnología | Propósito |
| --- | --- | --- |
| **Captura de Emails** | Gmail API (OAuth 2.0) | Scraping seguro de emails |
| **Aprendizaje Automático** | Python + SQLAlchemy | Análisis de patrones históricos |
| **IA Processing** | Google Gemini 2.5 Flash | Extracción inteligente de datos (fallback) |
| **Motor de Reglas** | Python (rules_engine.py) | Clasificación basada en conocimiento |
| **Procesamiento de Archivos** | Pandas, OpenPyXL, PyPDF2 | Lectura de Excel/PDF con scoring |
| **Base de Datos** | MySQL 8.0 + SQLAlchemy | 15 tablas (operación + conocimiento) |
| **Dashboard** | Flask + HTML/CSS/JS | Visualización web responsive |
| **Infraestructura** | Python 3.13, Virtual Env | Entorno de desarrollo |

## 🧠 Sistema de Aprendizaje (Nuevo)

### Fase 0: Análisis Histórico

El sistema analiza emails pasados para aprender patrones operativos:

```bash
python src/learning/historical_scraper.py --months 6
```

**Qué aprende:**

* **Perfiles de remitentes:** Identifica quién envía qué tipo de solicitudes
* **Patrones de urgencia:** Detecta keywords y comportamiento asociado a prioridad
* **Reglas automáticas:** Genera reglas con scoring de confianza (ej: "emails de proveedor X siempre son urgentes")
* **Hilos de conversación:** Analiza patrones de escalamiento y coordinación

**Resultados de prueba (1 mes de emails):**

* 📧 **266 emails** analizados
* 👥 **26 remitentes** identificados
* ⚙️ **16 reglas** automáticas generadas
* 🎯 **Confianza promedio:** 85%

### Fase 1: Operación Inteligente

Cuando llega un email nuevo:

1. **Rules Engine** consulta conocimiento aprendido
2. Si confianza > 75% → **Aplica regla directa** (sin usar IA, más rápido, gratis)
3. Si confianza < 75% → **Fallback a Gemini IA**
4. Si confianza < 50% → **Marca para revisión humana**

**Beneficios:**

* ⚡ **Respuesta más rápida** (reglas vs llamadas API)
* 💰 **Menor costo** (menos llamadas a Gemini)
* 🎯 **Mayor precisión** (aprende de tu operación específica)
* 🔍 **Explicabilidad** ("clasificado por regla X con 92% confianza")

## 📊 Resultados y Métricas

**Demo Técnica (7 emails procesados):**

* ✅ **7 tareas creadas** (100% de conversión)
* ✅ **< 3 segundos** por email procesado
* ✅ **$0.0002 USD** costo por email (cuando usa Gemini)

**Sistema de Aprendizaje (266 emails históricos):**

* ✅ **26 perfiles** de remitentes creados
* ✅ **16 reglas** automáticas con 70-100% confianza
* ✅ **0 falsos positivos** en clasificación de urgencia
* ✅ **Sistema autónomo** para emails recurrentes

**Ahorro estimado para cliente real:**

* 10-15 horas/semana en entrada manual
* 95%+ reducción de errores
* 60% reducción en llamadas a API de IA
* Visibilidad completa de solicitudes

## 🚀 Instalación

### Prerrequisitos

* Python 3.13+
* MySQL 8.0+
* Cuenta de Google (Gmail API)
* API Key de Google Gemini

### Configuración

1. **Clonar repositorio**

```bash
git clone https://github.com/GonzaloUlloaCL/bot-cobertores-workflow.git
cd bot-cobertores-workflow
```

2. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Crear archivo `.env` en la raíz:

```env
# Gmail API
GMAIL_CLIENT_ID=tu_client_id
GMAIL_CLIENT_SECRET=tu_client_secret
GMAIL_LABEL=bot-cobertores

# Gemini AI
GEMINI_API_KEY=tu_gemini_api_key

# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bot_cobertores
DB_USER=root
DB_PASSWORD=tu_password

# Dominio interno (para identificar autores internos)
INTERNAL_DOMAIN=@tuempresa.com
```

5. **Configurar Gmail API**

* Ir a [Google Cloud Console](https://console.cloud.google.com/)
* Crear proyecto y habilitar Gmail API
* Descargar `credentials.json` y colocar en la raíz

6. **Crear base de datos**

```bash
mysql -u root -p
CREATE DATABASE bot_cobertores;
```

7. **Ejecutar migraciones**

```bash
python scripts/migrate.py
```

Esto crea **15 tablas**:

* 8 tablas operativas (emails, tareas, alertas, etc.)
* 7 tablas de conocimiento (sender_profiles, learned_rules, etc.)

## 💻 Uso

### 1. Fase de Aprendizaje (Primera vez)

Analiza emails históricos para aprender patrones:

```bash
python src/learning/historical_scraper.py --months 6
```

**Opciones:**

* `--months N`: Analizar últimos N meses (default: 6)
* `--mode full`: Análisis completo (default)
* `--mode senders-only`: Solo perfiles de remitentes

**Output:**

```
🚀 Iniciando análisis histórico de Gmail...
📧 Emails analizados: 450
👥 Remitentes identificados: 45
⚙️  Reglas generadas: 28
🔗 Hilos analizados: 120
```

### 2. Procesar Emails Nuevos

```bash
python src/data_processing/email_processor.py
```

El sistema:

1. Captura emails con etiqueta `bot-cobertores`
2. Consulta reglas aprendidas
3. Clasifica (regla o IA según confianza)
4. Crea tareas en BD
5. Genera alertas si requiere revisión

### 3. Iniciar Dashboard

```bash
python src/dashboard/app.py
```

Acceder a: `http://localhost:5000`

**Dashboard muestra:**

* Tareas pendientes con prioridad
* Score de confianza por tarea
* Alertas de revisión humana
* Reglas aplicadas

## 📁 Estructura del Proyecto

```
bot-cobertores-workflow/
├── src/
│   ├── gmail_capture/          # Captura de emails
│   │   └── gmail_client.py
│   ├── data_processing/        # Procesamiento
│   │   ├── gpt_parser.py       # Parser Gemini (fallback)
│   │   ├── attachment_processor.py  # Excel/PDF
│   │   └── email_processor.py  # Orquestador principal
│   ├── learning/               # Sistema de aprendizaje (NUEVO)
│   │   └── historical_scraper.py   # Análisis histórico
│   ├── database/               # Modelos y conexión
│   │   ├── models.py           # 15 modelos (8 operación + 7 conocimiento)
│   │   └── connection.py
│   └── dashboard/              # Web dashboard
│       ├── app.py
│       └── templates/
├── scripts/
│   ├── migrate.py              # Migraciones automatizadas (NUEVO)
│   └── generate_proposal_pdf.py
├── migration_add_learning.sql  # SQL para tablas de aprendizaje (NUEVO)
├── data/
│   └── attachments/            # Archivos descargados
├── credentials.json            # Gmail OAuth (gitignored)
├── .env                        # Variables de entorno (gitignored)
└── requirements.txt
```

## 🗄️ Base de Datos

### Tablas Operativas (8)

* `emails_procesados`: Emails capturados
* `tareas`: Tareas extraídas (con `confianza_clasificacion`)
* `archivos_adjuntos`: Attachments (con `confidence_score`)
* `alertas`: Notificaciones
* `configuracion`: Settings dinámicos
* `log_sistema`: Logs de operaciones
* Vistas SQL optimizadas

### Tablas de Conocimiento (7 - NUEVO)

* `sender_profiles`: Perfiles de remitentes aprendidos
* `internal_author_profiles`: Comportamiento de autores internos
* `thread_patterns`: Análisis de hilos
* `learned_rules`: Reglas generadas automáticamente
* `learning_sessions`: Historial de aprendizaje
* `keyword_patterns`: Keywords por categoría
* `file_reviews`: Feedback loop para mejora continua

## 🎨 Características

### ✅ Implementadas

**Core:**

* Captura automática de emails con Gmail API
* Extracción de datos con Gemini IA
* Procesamiento de adjuntos Excel/PDF
* Base de datos MySQL con 15 tablas
* Dashboard web responsive

**Sistema de Aprendizaje (NUEVO):**

* 🧠 Análisis histórico de emails (1-12 meses configurables)
* ⚙️ Generación automática de reglas con scoring
* 🎯 Motor de decisión: reglas → IA fallback
* 📊 Scoring de confianza por clasificación
* ⚠️ Sistema de alertas para revisión humana
* 📈 Feedback loop para mejora continua

**Otros:**

* Sistema de alertas para tareas urgentes
* Manejo de rate limiting de API
* Fallback inteligente para emails no estructurados
* Logging completo de operaciones

### 🔮 Roadmap Futuro

* Envío automático de confirmaciones por email
* Notificaciones en tiempo real (Slack/Discord)
* Integración con Google Calendar
* Auto-entrenamiento con feedback de usuarios
* Descriptores de cargo automáticos (análisis de roles)
* API REST para integraciones
* Deploy en cloud (AWS/GCP)
* Multi-tenant para SaaS

## 🤝 Aplicaciones Comerciales

Este sistema es aplicable a cualquier industria que procese solicitudes por email:

* 🏭 **Manufactura:** Órdenes de producción
* 📦 **Logística:** Solicitudes de despacho
* 🏗️ **Construcción:** Pedidos de materiales
* 🛒 **Retail:** Órdenes de compra
* 🌾 **Agricultura:** Planificación de cultivos
* 💼 **Servicios:** Gestión de tickets

**Diferenciador clave:** Sistema que aprende de TU operación específica, no solo procesa.

**Valor para clientes:** 

* Setup: $2,000 - $4,000 USD
* Soporte mensual: $150 - $300 USD
* ROI: 3-6 meses

## 📈 Roadmap de Producto

### v1.0 - Sistema Base (✅ Completado)

* Captura y procesamiento de emails
* Extracción con IA
* Dashboard básico

### v2.0 - Sistema de Aprendizaje (✅ Completado)

* Análisis histórico
* Reglas automáticas
* Motor de decisión inteligente
* Scoring de confianza

### v3.0 - Mejoras Operativas (En desarrollo)

* Email automático de confirmación
* Notificaciones Slack/Discord
* Integración Google Calendar
* Tests automatizados

### v4.0 - Análisis Avanzado (Planeado)

* Descriptores de cargo
* Análisis de flujos de trabajo
* Patrones de escalamiento
* Optimización de procesos

## 📝 Licencia

MIT License - Ver archivo LICENSE

## 👤 Autor

**Gonzalo Ulloa**

* GitHub: [@GonzaloUlloaCL](https://github.com/GonzaloUlloaCL)
* LinkedIn: [Gonzalo Ulloa](https://www.linkedin.com/in/gonzalo-ulloa-g/)
* Email: gonzalo.ulloa@usach.cl

**Desarrollador Python** en transición a freelance, especializado en automatización operacional con IA.

---

⭐ **Si este proyecto te fue útil, considera darle una estrella en GitHub**

💼 **¿Interesado en implementar esto en tu empresa?** [Contáctame](mailto:gonzalo.ulloa@usach.cl)
