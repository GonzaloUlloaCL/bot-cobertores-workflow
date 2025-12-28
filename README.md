<div align="center">

# 🤖 Sistema de Automatización con IA

### Demo técnico de procesamiento inteligente de emails operacionales

**Basado en procesos reales del sector agroindustrial chileno**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)](https://ai.google.dev/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Demo](#-demo) • [Features](#-características) • [Arquitectura](#-arquitectura) • [Instalación](#-instalación) • [Contacto](#-contacto)

</div>

---

## 💡 El Problema

**Contexto real:** Empresas manufactureras/agrícolas reciben solicitudes de producción por email en formatos no estructurados.

```
📧 10-15 horas/semana perdidas en entrada manual
❌ Errores de transcripción en datos críticos  
📊 Falta de visibilidad de solicitudes pendientes
⏱️ Retrasos en procesamiento de urgencias
```

**Impacto:** Tiempo desperdiciado, errores costosos, falta de trazabilidad.

---

## ✨ La Solución

Sistema inteligente que **aprende de emails históricos** y automatiza el procesamiento de solicitudes operacionales.

### 🎯 Enfoque Dual

<div align="center">

```
┌──────────────────────────────────┐    ┌────────────────────────────┐
│   FASE 0: APRENDIZAJE (one-time) │    │  FASE 1: OPERACIÓN (24/7)  │
├──────────────────────────────────┤    ├────────────────────────────┤
│  📧 Analiza emails históricos    │───▶│  📧 Email nuevo            │
│  🧠 Identifica patrones          │    │  🔍 Consulta reglas        │
│  ⚙️  Genera reglas automáticas   │    │  ✅ Aplica o usa IA        │
│  💾 Guarda en BD                 │    │  📊 Crea tarea + scoring   │
└──────────────────────────────────┘    └────────────────────────────┘
```

</div>

---

## 🚀 Features Principales

### 🧠 Sistema de Aprendizaje Automático

```bash
python src/learning/historical_scraper.py --months 6
```

**Qué hace:**
- 📊 Analiza emails históricos (1-12 meses configurables)
- 👥 Identifica perfiles de remitentes
- ⚙️ Genera reglas automáticas con scoring de confianza
- 🎯 Detecta patrones de urgencia y tipo de solicitud

**Resultados demo (1 mes de análisis):**
```
✅ 266 emails procesados
✅ 26 remitentes identificados  
✅ 16 reglas automáticas generadas
✅ 85% confianza promedio
```

### ⚡ Motor de Decisión Inteligente

El sistema decide **cómo clasificar** cada email nuevo:

| Confianza | Acción | Beneficio |
|-----------|--------|-----------|
| **> 75%** | Aplica regla directa | ⚡ Rápido + 💰 Gratis |
| **50-75%** | Regla + revisión | 🎯 Balanceado |
| **< 50%** | Fallback a Gemini IA | 🤖 Preciso pero con costo |

**Ventajas:**
- Menor dependencia de APIs de IA (ahorro de costos)
- Respuestas más rápidas en casos conocidos
- Sistema que mejora con el tiempo

### 📊 Procesamiento Completo

- 📧 **Captura:** Gmail API con OAuth 2.0
- 🤖 **Extracción:** Google Gemini 2.5 Flash (cuando necesario)
- 📎 **Adjuntos:** Procesa Excel/PDF con scoring de confianza
- 💾 **Almacenamiento:** MySQL con 15 tablas
- 📈 **Dashboard:** Flask responsive con métricas en tiempo real
- ⚠️ **Alertas:** Notifica casos que requieren revisión humana

---

## 🏗️ Arquitectura Técnica

### Stack Completo

```python
{
    "backend": ["Python 3.13", "Flask", "SQLAlchemy"],
    "ai": ["Google Gemini 2.5 Flash"],
    "apis": ["Gmail API (OAuth 2.0)"],
    "data_processing": ["Pandas", "OpenPyXL", "PyPDF2"],
    "database": ["MySQL 8.0"],
    "frontend": ["HTML5", "CSS3", "JavaScript vanilla"],
    "deployment": ["Local / Cloud-ready"]
}
```

### Base de Datos (15 tablas)

**Operativas (8):**
- `emails_procesados`, `tareas`, `archivos_adjuntos`, `alertas`, `configuracion`, `log_sistema`
- Vistas SQL optimizadas

**Conocimiento (7):**
- `sender_profiles`: Patrones por remitente
- `learned_rules`: Reglas generadas automáticamente
- `internal_author_profiles`: Comportamiento de usuarios internos
- `thread_patterns`: Análisis de hilos
- `learning_sessions`: Historial de entrenamientos
- `keyword_patterns`: Keywords por categoría
- `file_reviews`: Feedback loop

---

## 📊 Resultados y Métricas

### Demo Técnica (7 emails procesados)

| Métrica | Resultado |
|---------|-----------|
| Emails procesados | 7/7 (100%) |
| Tiempo por email | < 3 segundos |
| Costo por email | $0.0002 USD |
| Tareas creadas | 7 automáticas |

### Sistema de Aprendizaje (266 emails analizados)

| Métrica | Resultado |
|---------|-----------|
| Remitentes identificados | 26 |
| Reglas generadas | 16 |
| Confianza promedio | 85% |
| Hilos analizados | 7 |

### Impacto Estimado (Caso Real)

```
⏱️  Ahorro: 10-15 horas/semana
💰 ROI: 3-6 meses
📉 Reducción errores: 95%+
⚡ Procesamiento: 60% sin IA (reglas directas)
```

---

## 🎯 Caso de Uso: Solicitud de Cobertor

**Email entrante:**
```
De: produccion@empresa.cl
Asunto: Solicitud Cobertor - URGENTE

Necesito cobertor para:
- Cuartel: 15
- Hileras: 8  
- Largo: 120 metros
- Código: COB-001
- Prioridad: ALTA
```

**Procesamiento automático:**

1. 🔍 **Rules Engine** consulta: ¿Email de `produccion@empresa.cl`?
2. ✅ **Regla encontrada:** "Emails de producción → Alta urgencia (confianza: 92%)"
3. 📊 **Gemini extrae datos:** Código, dimensiones, especificaciones
4. 💾 **Crea tarea en BD** con toda la información
5. ⚠️ **Genera alerta** automática por urgencia alta
6. ✅ **Email marcado** como procesado

**Resultado:** Tarea lista en 2.8 segundos, sin intervención humana.

---

## 🚀 Instalación

### Prerrequisitos

```bash
✅ Python 3.13+
✅ MySQL 8.0+
✅ Cuenta Google (Gmail API)
✅ API Key Google Gemini
```

### Quick Start

```bash
# 1. Clonar repositorio
git clone https://github.com/GonzaloUlloaCL/bot-cobertores-workflow.git
cd bot-cobertores-workflow

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env (ver sección abajo)

# 5. Configurar Gmail API
# - Ir a Google Cloud Console
# - Crear proyecto y habilitar Gmail API
# - Descargar credentials.json

# 6. Crear base de datos
mysql -u root -p
CREATE DATABASE bot_cobertores;

# 7. Ejecutar migraciones
python scripts/migrate.py

# 8. Fase de aprendizaje
python src/learning/historical_scraper.py --months 6

# 9. Procesar emails nuevos
python src/data_processing/email_processor.py

# 10. Iniciar dashboard
python src/dashboard/app.py
# Acceder a: http://localhost:5000
```

### Configuración .env

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

---

## 📁 Estructura del Proyecto

```
bot-cobertores-workflow/
├── src/
│   ├── gmail_capture/          # Gmail API client
│   ├── data_processing/        # Procesamiento de emails
│   │   ├── gpt_parser.py       # Parser Gemini (fallback)
│   │   ├── attachment_processor.py
│   │   └── email_processor.py
│   ├── learning/               # 🆕 Sistema de aprendizaje
│   │   └── historical_scraper.py
│   ├── database/
│   │   ├── models.py           # 15 modelos SQLAlchemy
│   │   └── connection.py
│   └── dashboard/
│       ├── app.py              # Flask server
│       └── templates/
├── scripts/
│   ├── migrate.py              # 🆕 Migraciones automatizadas
│   └── generate_proposal_pdf.py
├── migration_add_learning.sql  # 🆕 SQL tablas aprendizaje
├── docs/
│   └── propuesta_onepager.html # Propuesta para clientes
├── .env                        # Variables de entorno
├── requirements.txt
└── README.md
```

---

## 🎨 Características Implementadas

### ✅ Core

- [x] Captura automática Gmail con OAuth 2.0
- [x] Extracción de datos con Gemini IA
- [x] Procesamiento de adjuntos Excel/PDF
- [x] Base de datos MySQL con 15 tablas
- [x] Dashboard web responsive

### ✅ Sistema de Aprendizaje

- [x] Análisis histórico de emails (1-12 meses)
- [x] Generación automática de reglas con scoring
- [x] Motor de decisión: reglas → IA fallback
- [x] Scoring de confianza por clasificación
- [x] Sistema de alertas para revisión humana
- [x] Feedback loop para mejora continua

### ✅ Otros

- [x] Manejo de rate limiting
- [x] Fallback inteligente
- [x] Logging completo
- [x] Propuesta comercial automatizada

---

## 🔮 Roadmap Futuro

### v3.0 - Mejoras Operativas

- [ ] Email automático de confirmación
- [ ] Notificaciones Slack/Discord
- [ ] Integración Google Calendar
- [ ] Tests automatizados (pytest)

### v4.0 - Análisis Avanzado

- [ ] Descriptores de cargo automáticos
- [ ] Análisis de flujos de trabajo
- [ ] Patrones de escalamiento
- [ ] Optimización de procesos

### v5.0 - Producto Escalable

- [ ] API REST para integraciones
- [ ] Multi-tenant SaaS
- [ ] Deploy cloud (AWS/GCP)
- [ ] Autenticación y roles

---

## 💼 Aplicaciones Comerciales

Este sistema es aplicable a cualquier industria que procese solicitudes por email:

| Industria | Caso de Uso | Ahorro Estimado |
|-----------|-------------|-----------------|
| 🏭 **Manufactura** | Órdenes de producción | 12-18h/semana |
| 📦 **Logística** | Solicitudes de despacho | 10-15h/semana |
| 🏗️ **Construcción** | Pedidos de materiales | 8-12h/semana |
| 🛒 **Retail** | Órdenes de compra | 10-15h/semana |
| 🌾 **Agricultura** | Planificación de cultivos | 10-15h/semana |

**Diferenciador clave:** Sistema que aprende de TU operación específica.

**Propuesta de valor:**
- Setup: $2,000 - $4,000 USD
- Soporte mensual: $150 - $300 USD  
- ROI: 3-6 meses

---

## 📝 Licencia

MIT License - Ver archivo [LICENSE](LICENSE)

---

## 👤 Autor

**Gonzalo Ulloa González**

Ingeniero Industrial (USACH) con especialización en Python y automatización con IA.

- 💼 **LinkedIn:** [gonzalo-ulloa-g](https://www.linkedin.com/in/gonzalo-ulloa-g/)
- 📧 **Email:** gonzalo.ulloa@usach.cl
- 🐙 **GitHub:** [@GonzaloUlloaCL](https://github.com/GonzaloUlloaCL)
- 📍 **Ubicación:** Santiago, Chile

---

## 📫 Contacto

### ¿Interesado en implementar esto en tu empresa?

**Servicios freelance:**
- 🤖 Automatización de procesos operativos
- 📧 Procesamiento inteligente de emails/documentos
- 🧠 Integración de IA en workflows existentes
- 📊 Análisis de datos y optimización de procesos

**📞 Agenda una consulta gratuita:** [gonzalo.ulloa@usach.cl](mailto:gonzalo.ulloa@usach.cl)

---

<div align="center">

### 💡 "Automatiza lo repetitivo. Enfócate en lo estratégico."

![Profile Views](https://komarev.com/ghpvc/?username=GonzaloUlloaCL&color=blue&style=flat-square)

⭐ **¿Te gustó este proyecto? Dale una estrella en GitHub**

[⬆ Volver arriba](#-sistema-de-automatización-con-ia)

</div>