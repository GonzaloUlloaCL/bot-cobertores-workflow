🤖 OpsMail AI – Intelligent Email-to-Workflow Automation

Sistema de automatización operacional que transforma correos electrónicos no estructurados en flujos de trabajo, combinando aprendizaje histórico, reglas dinámicas e IA como fallback inteligente.

Stack: Python · Flask · Google Gemini · MySQL

📋 Descripción

OpsMail AI es una plataforma diseñada para organizaciones que reciben solicitudes operativas por correo electrónico en formatos libres y poco estructurados.

El sistema analiza correos históricos para aprender patrones reales de operación, genera reglas automáticas con scoring de confianza y luego procesa nuevos correos de forma autónoma, reduciendo tiempo operativo, errores manuales y dependencia de IA generativa.

Proyecto desarrollado como demo técnica y de portafolio, validado en escenarios simulados que replican flujos operativos reales (producción, logística, servicios).

❗ Problema

Muchas áreas operativas reciben solicitudes por email sin estructura estándar:

Formatos variables

Información incompleta

Prioridades poco claras

Procesamiento manual (10–15 hrs/semana)

Alto riesgo de errores

✅ Solución

OpsMail AI automatiza el proceso completo:

📧 Captura emails desde Gmail mediante etiquetas
🧠 Aprende patrones históricos de operación
⚙️ Genera reglas automáticas con scoring de confianza
🤖 Usa IA (Gemini) solo cuando es necesario
📊 Procesa adjuntos Excel/PDF
💾 Almacena resultados en base de datos
📈 Dashboard web para seguimiento y control

🧠 Sistema de Aprendizaje – Fase 0 (Diferenciador clave)

Antes de operar, el sistema ejecuta una fase de aprendizaje histórico:

python src/learning/historical_scraper.py --months 6

¿Qué aprende?

👥 Perfiles de remitentes

⚠️ Patrones de urgencia y prioridad

🔁 Tipos recurrentes de solicitudes

⚙️ Reglas automáticas con scoring de confianza

🧵 Patrones de hilos y escalamiento

📌 El objetivo es que el sistema aprenda el “lenguaje operacional” propio de cada organización antes de automatizar.

⚙️ Fase 1 – Operación Inteligente

Cuando llega un email nuevo:

Consulta reglas aprendidas

Si confianza > 75% → aplica regla directa

Si confianza < 75% → fallback a IA (Gemini)

Si confianza < 50% → revisión humana

Beneficios

⚡ Procesamiento rápido
💰 Menor costo en llamadas a IA
🎯 Mayor precisión contextual
🔍 Clasificación explicable
📊 Visibilidad completa

🎯 Ejemplo de Caso de Uso (Genérico)

Asunto: Solicitud urgente de producción
Contenido:

Área: Planta Norte

Ítem: Producto X

Cantidad: 1.200 unidades

Fecha requerida: 48 hrs

Resultado:

Tarea creada en BD

Prioridad detectada automáticamente

Score de confianza

Alerta si requiere revisión humana

📊 Resultados de Prueba

Escenario de validación técnica:

📧 266 emails analizados

👥 26 perfiles de remitentes

⚙️ 16 reglas automáticas generadas

🎯 Confianza promedio: 85%

⏱️ < 3 segundos por email

💸 ~$0.0002 USD por email (cuando usa IA)

🏗️ Arquitectura
Fase 0: Aprendizaje Histórico          Fase 1: Operación
┌─────────────────────────────┐    ┌──────────────────────────┐
│ Emails históricos           │    │ Emails nuevos            │
│ ↓                           │    │ ↓                        │
│ historical_scraper.py       │    │ email_processor.py       │
│ ↓                           │    │ ↓                        │
│ Análisis de patrones        │    │ rules_engine.py          │
│ Reglas automáticas          │────┤ ¿Regla conocida?         │
│ Base de conocimiento        │    │ ├─ Sí → Regla            │
└─────────────────────────────┘    │ └─ No → IA (Gemini)      │
                                   └──────────────────────────┘

🗄️ Base de Datos

15 tablas en total

8 operativas (emails, tareas, alertas, logs)

7 de conocimiento (perfiles, reglas, patrones, feedback)

🚀 Aplicaciones Comerciales

OpsMail AI es aplicable a cualquier industria que gestione solicitudes por email:

🏭 Manufactura

📦 Logística

🏗️ Construcción

🛒 Retail

🌾 Agricultura

💼 Servicios

Valor diferencial: el sistema aprende de la operación específica del cliente, no usa reglas genéricas.

🔮 Roadmap

Confirmaciones automáticas por email

Notificaciones Slack / Discord

Integración Google Calendar

API REST

Multi-tenant SaaS

Deploy cloud (AWS / GCP)

👤 Autor

Gonzalo Ulloa
Desarrollador Python | Automatización Operacional con IA

GitHub: @GonzaloUlloaCL
LinkedIn: Gonzalo Ulloa

💬 ¿Próximo paso?

Este proyecto está listo para:

Adaptarse a una operación real

Prototiparse con datos del cliente

Evolucionar a producto interno o SaaS
