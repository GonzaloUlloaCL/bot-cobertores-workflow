"""
GPT Parser - Extracción inteligente de datos desde emails
Usa Google Gemini API para procesar texto y extraer datos estructurados
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class GeminiParser:
    """Parser que usa Gemini para extraer datos estructurados de emails"""
    
    def __init__(self):
        """Inicializa el cliente de Gemini"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en .env")
        
        # Configurar cliente con nueva API
        self.client = genai.Client(api_key=api_key)
        logger.info("✅ Gemini Parser inicializado correctamente")
    
    def parse_email_text(self, email_text: str, email_subject: str = "") -> Optional[Dict]:
        """
        Extrae datos estructurados del texto de un email
        
        Args:
            email_text: Cuerpo del email
            email_subject: Asunto del email (opcional)
        
        Returns:
            Dict con datos extraídos o None si falla
        """
        try:
            # Construir prompt optimizado
            prompt = self._build_prompt(email_text, email_subject)
            
            # Llamar a Gemini con nuevo modelo
            logger.info("🤖 Enviando texto a Gemini para procesamiento...")
            
            response = self.client.models.generate_content(
                model='models/gemini-2.5-flash',
                contents=prompt
            )
            
            # Extraer texto de respuesta
            response_text = response.text.strip()
            logger.debug(f"Respuesta raw de Gemini: {response_text[:200]}...")
            
            # Limpiar markdown si existe
            json_text = self._extract_json(response_text)
            
            # Parsear JSON
            data = json.loads(json_text)
            
            # Validar y normalizar
            normalized_data = self._normalize_data(data)
            
            logger.info(f"✅ Datos extraídos exitosamente: {normalized_data.get('codigo_cobertor', 'N/A')}")
            return normalized_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parseando JSON de Gemini: {e}")
            logger.error(f"Respuesta problemática: {response_text if 'response_text' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"❌ Error en parse_email_text: {e}")
            return None
    
    def parse_batch(self, emails: List[Dict]) -> List[Dict]:
        """
        Procesa múltiples emails en batch
        
        Args:
            emails: Lista de dicts con 'body_text' y 'subject'
        
        Returns:
            Lista de dicts con datos extraídos
        """
        results = []
        for i, email in enumerate(emails, 1):
            logger.info(f"📧 Procesando email {i}/{len(emails)}")
            
            body = email.get('body_text', '')
            subject = email.get('subject', '')
            
            parsed = self.parse_email_text(body, subject)
            if parsed:
                parsed['email_index'] = i
                parsed['original_subject'] = subject
                results.append(parsed)
        
        logger.info(f"✅ Batch completado: {len(results)}/{len(emails)} emails procesados exitosamente")
        return results
    
    def _build_prompt(self, email_text: str, email_subject: str) -> str:
        """Construye el prompt optimizado para Gemini"""
        
        # LIMPIEZA MEJORADA: Extraer contenido después de "Forwarded message"
        cleaned_text = email_text
        
        # Si es un forward, tomar el contenido del mensaje original
        forward_markers = [
            '---------- Forwarded message ---------',
            '-----Original Message-----',
            'Begin forwarded message:',
            '-------- Mensaje reenviado --------'
        ]
        
        for marker in forward_markers:
            if marker in cleaned_text:
                parts = cleaned_text.split(marker, 1)
                if len(parts) > 1:
                    cleaned_text = parts[1]  # Tomar la parte DESPUÉS del marker
                    break
        
        # Remover firmas comunes (solo las primeras líneas de firma)
        signature_markers = [
            'Enviado desde mi',
            'Sent from my',
            'Get Outlook for',
            'Descargue Outlook para'
        ]
        
        for marker in signature_markers:
            if marker in cleaned_text:
                cleaned_text = cleaned_text.split(marker)[0]
                break
        
        # Limitar tamaño pero ser generoso
        text_to_analyze = cleaned_text[:3000]  # Aumentado de 2000 a 3000
        
        prompt = f"""Eres un experto en extraer información de emails operacionales del sector agrícola chileno.

**CONTEXTO:**
Este es un email sobre cobertores, mallas, o trabajos agrícolas. Puede contener:
- Solicitudes de producción
- Confirmaciones de pedidos
- Reportes de trabajos realizados
- Cotizaciones o proformas

**ASUNTO:**
{email_subject}

**CONTENIDO DEL EMAIL:**
{text_to_analyze}

**TU TAREA:**
Extrae TODA la información operacional relevante que encuentres.

**CAMPOS A BUSCAR:**
1. **codigo_cobertor**: Cualquier código alfanumérico (COB-XXX, C00000XXX, pedido #XXX, OC-XXX)
2. **cuartel**: Número o nombre de cuartel/sector/campo (ej: "15", "Cuartel 22", "Manantiales")
3. **hileras**: Cantidad de hileras/filas (número entero)
4. **largo_metros**: Largo en metros (número decimal, puede estar como "120m", "120 metros", "120 mts")
5. **prioridad**: 
   - "alta" si ves: URGENTE, CRÍTICO, PRIORITARIO, INMEDIATO, ALTA
   - "baja" si ves: BAJA, NO URGENTE
   - "normal" en cualquier otro caso
6. **descripcion**: Resumen de QUÉ se está solicitando/reportando (máx 100 chars)
7. **notas**: Información adicional relevante (empresa, contacto, observaciones)

**REGLAS IMPORTANTES:**
- Si NO encuentras un dato específico, usa null (no inventes)
- Si encuentras información parcial, úsala (es mejor que null)
- Para emails sobre "trabajos realizados" o "confirmaciones", también extrae los datos
- Si el email menciona múltiples items, extrae datos del primero o más importante
- Números sin unidad cerca de "metro" son metros
- Busca en TODO el texto, no solo al inicio

**EJEMPLOS DE CÓDIGOS VÁLIDOS:**
- "COB-001", "C0000019127", "OC-2025-001", "Pedido #12345"

**FORMATO DE SALIDA (SOLO JSON, SIN ```json ni explicaciones):**
{{
  "codigo_cobertor": "código encontrado o null",
  "cuartel": "nombre o número de cuartel",
  "hileras": número_entero_o_null,
  "largo_metros": número_decimal_o_null,
  "prioridad": "alta|normal|baja",
  "descripcion": "Breve resumen de la solicitud/reporte",
  "notas": "Información adicional relevante"
}}

Responde ÚNICAMENTE con el objeto JSON, sin bloques de código ni explicaciones."""

        return prompt
    
    def _extract_json(self, text: str) -> str:
        """Extrae JSON limpio de la respuesta de Gemini"""
        
        # Eliminar bloques de markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        # Limpiar espacios
        text = text.strip()
        
        # Si no empieza con {, buscar el primer {
        if not text.startswith('{'):
            start = text.find('{')
            if start != -1:
                text = text[start:]
        
        # Si no termina con }, buscar el último }
        if not text.endswith('}'):
            end = text.rfind('}')
            if end != -1:
                text = text[:end+1]
        
        return text
    
    def _normalize_data(self, data: Dict) -> Dict:
        """Normaliza y valida los datos extraídos"""
        
        normalized = {
            'codigo_cobertor': self._normalize_string(data.get('codigo_cobertor')),
            'cuartel': self._normalize_string(data.get('cuartel')),
            'hileras': self._normalize_int(data.get('hileras')),
            'largo_metros': self._normalize_float(data.get('largo_metros')),
            'prioridad': self._normalize_priority(data.get('prioridad')),
            'descripcion': self._normalize_string(data.get('descripcion', ''))[:100],
            'notas': self._normalize_string(data.get('notas', ''))[:500],
            'urgente': data.get('prioridad', '').lower() == 'alta',
            'origen': 'texto_email'
        }
        
        return normalized
    
    def _normalize_string(self, value) -> Optional[str]:
        """Normaliza strings"""
        if value is None or value == 'null':
            return None
        return str(value).strip() or None
    
    def _normalize_int(self, value) -> Optional[int]:
        """Normaliza enteros"""
        if value is None or value == 'null':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _normalize_float(self, value) -> Optional[float]:
        """Normaliza floats"""
        if value is None or value == 'null':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _normalize_priority(self, value) -> str:
        """Normaliza prioridad"""
        if not value:
            return 'normal'
        
        value_lower = str(value).lower()
        if value_lower in ['alta', 'high', 'urgente', 'critico']:
            return 'alta'
        elif value_lower in ['baja', 'low']:
            return 'baja'
        else:
            return 'normal'


# Función helper para uso rápido
def parse_email(email_text: str, email_subject: str = "") -> Optional[Dict]:
    """
    Función helper para parsear un email rápidamente
    
    Usage:
        from data_processing.gpt_parser import parse_email
        data = parse_email(email_body, email_subject)
    """
    parser = GeminiParser()
    return parser.parse_email_text(email_text, email_subject)


if __name__ == "__main__":
    # Test del parser
    print("🧪 Testing Gemini Parser...")
    
    # Email de prueba
    test_email = """
    Necesito cobertor para:
    - Cuartel: 15
    - Hileras: 8  
    - Largo: 120 metros
    - Código: COB-001
    - Prioridad: ALTA
    
    Favor confirmar fecha de entrega.
    """
    
    test_subject = "Solicitud Cobertor - URGENTE"
    
    try:
        parser = GeminiParser()
        result = parser.parse_email_text(test_email, test_subject)
        
        if result:
            print("\n✅ TEST EXITOSO!")
            print("\nDatos extraídos:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("\n❌ TEST FALLIDO - No se pudieron extraer datos")
            
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()