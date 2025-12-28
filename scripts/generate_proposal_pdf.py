from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date
import os

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "propuesta_bot_cobertores.pdf")

def generate_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 80, "Automatización de Procesos Operacionales")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 130, "Cliente: Empresa Logística")
    c.drawString(50, height - 160, f"Fecha: {date.today()}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 220, "Problema")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 250, "- Correos operacionales procesados manualmente")
    c.drawString(50, height - 270, "- Pérdida de 10+ horas semanales")
    c.drawString(50, height - 290, "- Riesgo de errores humanos")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 340, "Solución")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 370, "- Bot Python + IA que clasifica y prioriza correos")
    c.drawString(50, height - 390, "- Dashboard centralizado")
    c.drawString(50, height - 410, "- Reportes automáticos")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 460, "Inversión")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 490, "Setup inicial: USD 2.500")
    c.drawString(50, height - 510, "Soporte mensual opcional: USD 200")

    c.save()
    print(f"✅ PDF generado correctamente en: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_pdf()
