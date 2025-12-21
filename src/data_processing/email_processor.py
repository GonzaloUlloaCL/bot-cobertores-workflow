"""
Email Processor - Integrador completo del pipeline
Orquesta: Gmail → Parser IA/Excel → MySQL
"""

import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Añadir path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gmail_capture.gmail_client import GmailClient
from data_processing.gpt_parser import GeminiParser
from data_processing.attachment_processor import AttachmentProcessor
from database.models import EmailProcesado, Tarea, ArchivoAdjunto, Alerta, session_scope

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


class EmailProcessor:
    """Procesador completo de emails con IA"""
    
    def __init__(self):
        """Inicializa todos los componentes"""
        logger.info("🚀 Inicializando EmailProcessor...")
        
        try:
            self.gmail_client = GmailClient()
            self.gmail_client.authenticate()
            self.gmail_client._get_label_id()
            self.gpt_parser = GeminiParser()
            self.attachment_processor = AttachmentProcessor()
            
            logger.info("✅ EmailProcessor inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando EmailProcessor: {e}")
            raise
    
    def process_new_emails(self, max_emails: int = 50) -> Dict:
        """
        Procesa emails nuevos del Gmail
        
        Args:
            max_emails: Máximo número de emails a procesar
        
        Returns:
            Dict con estadísticas del procesamiento
        """
        logger.info(f"📧 Buscando emails nuevos (máx: {max_emails})...")
        
        stats = {
            'emails_procesados': 0,
            'tareas_creadas': 0,
            'adjuntos_procesados': 0,
            'errores': 0,
            'timestamp': datetime.now()
        }
        
        try:
            # Capturar emails
            emails = self.gmail_client.get_unread_emails(max_results=max_emails)
            
            if not emails:
                logger.info("📭 No hay emails nuevos para procesar")
                return stats
            
            logger.info(f"📬 {len(emails)} emails capturados, procesando...")
            
            # Procesar cada email
            for email_data in emails:
                try:
                    result = self._process_single_email(email_data)
                    
                    if result['success']:
                        stats['emails_procesados'] += 1
                        stats['tareas_creadas'] += result['tareas_creadas']
                        stats['adjuntos_procesados'] += result['adjuntos_procesados']
                    else:
                        stats['errores'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error procesando email: {e}")
                    stats['errores'] += 1
                    continue
            
            # Resumen
            logger.info(f"""
╔══════════════════════════════════════════════════════╗
║           RESUMEN DE PROCESAMIENTO                   ║
╠══════════════════════════════════════════════════════╣
║  📧 Emails procesados:    {stats['emails_procesados']:3d}                       ║
║  ✅ Tareas creadas:       {stats['tareas_creadas']:3d}                       ║
║  📎 Adjuntos procesados:  {stats['adjuntos_procesados']:3d}                       ║
║  ❌ Errores:              {stats['errores']:3d}                       ║
╚══════════════════════════════════════════════════════╝
            """)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error en process_new_emails: {e}")
            return stats
    
    def _process_single_email(self, email_data: Dict) -> Dict:
        """
        Procesa un email individual
        
        Args:
            email_data: Dict con datos del email de Gmail
        
        Returns:
            Dict con resultado del procesamiento
        """
        result = {
            'success': False,
            'tareas_creadas': 0,
            'adjuntos_procesados': 0
        }
        
        gmail_id = email_data.get('gmail_id')
        subject = email_data.get('subject', 'Sin asunto')
        sender = email_data.get('sender_email', 'Desconocido')
        
        logger.info(f"📨 Procesando: {subject[:50]}...")
        
        try:
            with session_scope() as session:
                # 1. Guardar email en BD
                email_obj = EmailProcesado(
                    gmail_id=gmail_id,
                    thread_id=email_data.get('thread_id'),
                    sender_email=sender,
                    sender_name=email_data.get('sender_name'),
                    subject=subject,
                    body_text=email_data.get('body_text', ''),
                    body_html=email_data.get('body_html', ''),
                    received_date=email_data.get('received_date', datetime.now()),
                    has_attachments=email_data.get('has_attachments', False),
                    attachment_count=email_data.get('attachment_count', 0),
                    status='processing'
                )
                session.add(email_obj)
                session.flush()  # Para obtener el ID
                
                tareas_creadas = []
                
                # 2. Procesar adjuntos (si existen)
                attachments = email_data.get('attachments', [])
                if attachments:
                    logger.info(f"   📎 {len(attachments)} adjuntos encontrados")
                    
                    for attachment in attachments:
                        try:
                            attachment_data = self._process_attachment(
                                email_obj.id,
                                attachment,
                                session
                            )
                            
                            if attachment_data:
                                tareas_creadas.extend(attachment_data)
                                result['adjuntos_procesados'] += 1
                                
                        except Exception as e:
                            logger.error(f"   ❌ Error procesando adjunto: {e}")
                            continue
                
                # 3. Procesar texto del email con IA (si no hay adjuntos o como complemento)
                body_text = email_data.get('body_text', '').strip()
                if body_text and len(body_text) > 20:  # Solo si hay contenido relevante
                    logger.info("   🤖 Procesando texto con IA...")
                    
                    parsed_data = self.gpt_parser.parse_email_text(body_text, subject)
                    
                    if parsed_data:
                        tareas_creadas.append(parsed_data)
                    else:
                        # Crear tarea genérica si la IA no pudo extraer datos
                        logger.info("   📝 Creando tarea genérica de revisión...")
                        tarea_generica = {
                            'codigo_cobertor': None,
                            'cuartel': None,
                            'hileras': None,
                            'largo_metros': None,
                            'prioridad': 'normal',
                            'descripcion': f'Revisar email: {subject[:80]}',
                            'notas': f'Email requiere revisión manual. Contenido: {body_text[:200]}...',
                            'urgente': 'urgente' in subject.lower() or 'crítico' in subject.lower(),
                            'origen': 'fallback_revision'
                        }
                        tareas_creadas.append(tarea_generica)
                                
                # 4. Crear tareas en BD
                if tareas_creadas:
                    for tarea_data in tareas_creadas:
                        tarea = Tarea(
                            email_id=email_obj.id,
                            codigo_cobertor=tarea_data.get('codigo_cobertor'),
                            cuartel=tarea_data.get('cuartel'),
                            hileras=tarea_data.get('hileras'),
                            largo_metros=tarea_data.get('largo_metros'),
                            prioridad=tarea_data.get('prioridad', 'normal'),
                            observaciones=tarea_data.get('descripcion'),
                            estado='pendiente',
                            fecha_solicitud=datetime.now()
                        )
                        session.add(tarea)
                        result['tareas_creadas'] += 1
                    
                    logger.info(f"   ✅ {result['tareas_creadas']} tarea(s) creada(s)")
                
                # 5. Actualizar status del email
                email_obj.status = 'processed' if result['tareas_creadas'] > 0 else 'no_data'
                email_obj.processed_date = datetime.now()
                
                # 6. Crear alerta si hay tareas urgentes
                if any(t.get('urgente') for t in tareas_creadas):
                    alerta = Alerta(
                        tipo='tarea_urgente',
                        titulo=f"Tarea urgente: {subject[:50]}",
                        descripcion=f"{result['tareas_creadas']} tarea(s) urgente(s) detectada(s)",
                        severidad='alta',
                        leida=False
                    )
                    session.add(alerta)
                    logger.info("   🚨 Alerta de urgencia creada")
                
                # 7. Marcar email como leído en Gmail
                try:
                    self.gmail_client.mark_as_read(gmail_id)
                except Exception as e:
                    logger.warning(f"   ⚠️ No se pudo marcar como leído: {e}")
                
                result['success'] = True
                
        except Exception as e:
            logger.error(f"❌ Error procesando email {gmail_id}: {e}")
            
            # Intentar guardar error en BD
            try:
                with session_scope() as err_session:
                    alerta = Alerta(
                        tipo='error_procesamiento',
                        titulo=f"Error procesando: {subject[:50]}",
                        descripcion=str(e),
                        severidad='media',
                        leida=False
                    )
                    err_session.add(alerta)
            except:
                pass
        
        return result
    
    def _process_attachment(self, email_id: int, attachment: Dict, session) -> Optional[List[Dict]]:
        """
        Procesa un adjunto individual
        
        Args:
            email_id: ID del email en BD
            attachment: Dict con datos del adjunto
            session: Sesión de SQLAlchemy
        
        Returns:
            Lista de diccionarios con datos extraídos
        """
        filename = attachment.get('filename', 'unknown')
        file_path = attachment.get('path')
        
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"   ⚠️ Archivo no encontrado: {filename}")
            return None
        
        logger.info(f"   📂 Procesando adjunto: {filename}")
        
        try:
            # Procesar archivo según tipo
            extracted_data = self.attachment_processor.process_file(file_path)
            
            if not extracted_data:
                logger.warning(f"   ⚠️ No se extrajeron datos de: {filename}")
                return None
            
            # Guardar metadata del adjunto
            adjunto_obj = ArchivoAdjunto(
                email_id=email_id,
                filename=filename,
                file_path=file_path,
                mime_type=attachment.get('mime_type'),
                size_bytes=attachment.get('size', 0),
                extracted_data=str(extracted_data)[:5000]  # Limitar tamaño
            )
            session.add(adjunto_obj)
            
            logger.info(f"   ✅ {len(extracted_data)} registro(s) extraído(s) de {filename}")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"   ❌ Error procesando adjunto {filename}: {e}")
            return None
    
    def process_by_id(self, gmail_id: str) -> bool:
        """
        Procesa un email específico por su Gmail ID
        
        Args:
            gmail_id: ID del email en Gmail
        
        Returns:
            True si se procesó exitosamente
        """
        try:
            email_data = self.gmail_client.get_email(gmail_id)
            
            if not email_data:
                logger.error(f"❌ Email {gmail_id} no encontrado")
                return False
            
            result = self._process_single_email(email_data)
            return result['success']
            
        except Exception as e:
            logger.error(f"❌ Error procesando email {gmail_id}: {e}")
            return False


def run_processor(max_emails: int = 50):
    """
    Función helper para ejecutar el procesador
    
    Usage:
        from data_processing.email_processor import run_processor
        run_processor(max_emails=10)
    """
    processor = EmailProcessor()
    return processor.process_new_emails(max_emails)


if __name__ == "__main__":
    print("🤖 Bot de Cobertores - Procesador de Emails\n")
    
    # Ejecutar procesamiento
    processor = EmailProcessor()
    stats = processor.process_new_emails(max_emails=10)
    
    print(f"\n🎉 Procesamiento completado!")
    print(f"Timestamp: {stats['timestamp']}")