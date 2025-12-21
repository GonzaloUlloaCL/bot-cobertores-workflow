# 🤖 Bot de Cobertores - Automatización con IA

Sistema inteligente de procesamiento de emails operacionales con extracción automática de datos usando IA.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)](https://ai.google.dev/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)](https://www.mysql.com/)

## 📋 Descripción

Proyecto de automatización operacional que procesa correos electrónicos de solicitudes de producción, extrae datos estructurados usando IA (Google Gemini), y genera un dashboard de gestión de tareas.

**Problema resuelto:** Empresas agrícolas/manufactureras reciben solicitudes de producción por email en formatos no estructurados. La entrada manual de datos consume 10-15 horas/semana y genera errores.

**Solución:** Bot que automáticamente:
- 📧 Captura emails de Gmail con etiqueta específica
- 🤖 Extrae datos usando IA (códigos, dimensiones, prioridades)
- 📊 Procesa adjuntos Excel/PDF
- 💾 Almacena en base de datos MySQL
- 📈 Genera dashboard web para seguimiento

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
- ✅ Tarea creada en BD
- ✅ Prioridad detectada (ALTA)
- ✅ Alerta generada
- ✅ Email marcado como procesado

## 🏗️ Arquitectura
```
Gmail API → Python Processor → Gemini IA → MySQL → Flask Dashboard
```

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Captura de Emails** | Gmail API (OAuth 2.0) | Scraping seguro de emails |
| **IA Processing** | Google Gemini 2.5 Flash | Extracción inteligente de datos |
| **Procesamiento de Archivos** | Pandas, OpenPyXL, PyPDF2 | Lectura de Excel/PDF |
| **Base de Datos** | MySQL 8.0 + SQLAlchemy | Almacenamiento persistente |
| **Dashboard** | Flask + HTML/CSS/JS | Visualización web |
| **Infraestructura** | Python 3.13, Virtual Env | Entorno de desarrollo |

## 📊 Resultados y Métricas

![Dashboard - Tareas](docs/screenshots/dashboard-tareas.png)

**Métricas de la demo:**
- ✅ **7 emails procesados** automáticamente
- ✅ **7 tareas creadas** (100% de conversión)
- ✅ **< 3 segundos** por email procesado
- ✅ **$0.0002 USD** costo por email (Gemini API)
- ✅ **Detección automática** de prioridad alta en emails urgentes

**Ahorro estimado para cliente real:**
- 10-15 horas/semana en entrada manual
- 95%+ reducción de errores
- Visibilidad completa de solicitudes

## 🚀 Instalación

### Prerrequisitos

- Python 3.13+
- MySQL 8.0+
- Cuenta de Google (Gmail API)
- API Key de Google Gemini

### Configuración

1. **Clonar repositorio**
```bash
git clone https://github.com/tu-usuario/bot-cobertores-workflow.git
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
```

5. **Configurar Gmail API**
- Ir a [Google Cloud Console](https://console.cloud.google.com/)
- Crear proyecto y habilitar Gmail API
- Descargar `credentials.json` y colocar en la raíz

6. **Crear base de datos**
```bash
mysql -u root -p
CREATE DATABASE bot_cobertores;
```

7. **Inicializar base de datos**
```bash
python scripts/init_database.py
```

## 💻 Uso

### Procesar Emails
```bash
python src/data_processing/email_processor.py
```

### Iniciar Dashboard
```bash
python src/dashboard/app.py
```

Acceder a: `http://localhost:5000`

## 📁 Estructura del Proyecto
```
bot-cobertores-workflow/
├── src/
│   ├── gmail_capture/          # Captura de emails
│   │   └── gmail_client.py
│   ├── data_processing/        # Procesamiento con IA
│   │   ├── gpt_parser.py       # Parser Gemini
│   │   ├── attachment_processor.py  # Excel/PDF
│   │   └── email_processor.py  # Orquestador principal
│   ├── database/               # Modelos y conexión
│   │   ├── models.py
│   │   └── connection.py
│   └── dashboard/              # Web dashboard
│       ├── app.py
│       └── templates/
├── data/
│   └── attachments/            # Archivos descargados
├── docs/
│   └── screenshots/            # Capturas de pantalla
├── credentials.json            # Gmail OAuth (gitignored)
├── .env                        # Variables de entorno (gitignored)
└── requirements.txt
```

## 🎨 Características

### ✅ Implementadas

- [x] Captura automática de emails con Gmail API
- [x] Extracción de datos con Gemini IA
- [x] Procesamiento de adjuntos Excel/PDF
- [x] Base de datos MySQL con 8 tablas
- [x] Dashboard web responsive
- [x] Sistema de alertas para tareas urgentes
- [x] Manejo de rate limiting de API
- [x] Fallback para emails sin datos estructurados
- [x] Logging completo de operaciones

### 🔮 Roadmap Futuro

- [ ] Envío automático de confirmaciones por email
- [ ] Notificaciones en tiempo real (Slack/Discord)
- [ ] Integración con Google Calendar
- [ ] Auto-aprendizaje del modelo con feedback
- [ ] API REST para integraciones
- [ ] Deploy en cloud (AWS/GCP)

## 🤝 Aplicaciones Comerciales

Este sistema es aplicable a cualquier industria que procese solicitudes por email:

- 🏭 **Manufactura:** Órdenes de producción
- 📦 **Logística:** Solicitudes de despacho
- 🏗️ **Construcción:** Pedidos de materiales
- 🛒 **Retail:** Órdenes de compra
- 🌾 **Agricultura:** Planificación de cultivos

**Valor para clientes:** Proyectos desde $2,000 - $5,000 USD

## 📝 Licencia

MIT License - Ver archivo [LICENSE](LICENSE)

## 👤 Autor

**Gonzalo Ulloa**
- GitHub: [@GonzaloUlloaCL](https://github.com/GonzaloUlloaCL)
- LinkedIn: [GonzaloUlloa](https://www.linkedin.com/in/gonzalo-ulloa-g/)
- Email: gonzalo.ulloa@usach.cl

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub