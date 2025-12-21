"""
Test de captura de correos Gmail y guardado en base de datos
"""

import sys
sys.path.append('.')

from datetime import datetime
from src.gmail_capture.gmail_client import GmailClient
from src.database.connection import init_database, get_db_session
from src.database.models import EmailProcesado

def test_gmail_to_database():
    """
    Test completo: Captura correos de Gmail y los guarda en MySQL
    """
    print("=" * 70)
    print("TEST: GMAIL → BASE DE DATOS")
    print("=" * 70)
    
    # 1. Inicializar base de datos
    print("\n[1/4] Inicializando base de datos...")
    if not init_database():
        print("❌ Error al conectar con base de datos")
        return
    
    # 2. Autenticar con Gmail
    print("\n[2/4] Autenticando con Gmail API...")
    client = GmailClient()
    client.authenticate()
    
    # 3. Capturar correos
    print("\n[3/4] Capturando correos con etiqueta 'bot-cobertores'...")
    emails = client.get_unread_emails(max_results=10)
    
    if not emails:
        print("\n⚠️ No hay correos nuevos para procesar")
        print("\n💡 PARA PROBAR:")
        print("1. Envíate un correo a ti mismo")
        print("2. Ponle la etiqueta 'bot-cobertores'")
        print("3. Ejecuta este script nuevamente")
        return
    
    # 4. Guardar en base de datos
    print(f"\n[4/4] Guardando {len(emails)} correos en base de datos...")
    
    session = get_db_session()
    emails_guardados = 0
    emails_duplicados = 0
    
    try:
        for email_data in emails:
            # Verificar si ya existe
            existe = session.query(EmailProcesado).filter_by(
                gmail_id=email_data['gmail_id']
            ).first()
            
            if existe:
                print(f"⚠️ Correo ya existe: {email_data['subject'][:50]}...")
                emails_duplicados += 1
                continue
            
            # Crear nuevo registro
            email_record = EmailProcesado(
                gmail_id=email_data['gmail_id'],
                thread_id=email_data['thread_id'],
                sender_email=email_data['sender_email'],
                sender_name=email_data['sender_name'],
                subject=email_data['subject'],
                body_text=email_data['body_text'],
                body_html=email_data['body_html'],
                received_date=email_data['received_date'],
                has_attachments=email_data['has_attachments'],
                attachment_count=email_data['attachment_count'],
                status='pending',
                priority='normal'
            )
            
            session.add(email_record)
            emails_guardados += 1
            
            print(f"✅ Guardado: {email_data['subject'][:50]}...")
            
            # Marcar como leído en Gmail (opcional)
            # client.mark_as_read(email_data['gmail_id'])
        
        session.commit()
        
        print("\n" + "=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"✅ Correos guardados: {emails_guardados}")
        print(f"⚠️ Correos duplicados (ya existían): {emails_duplicados}")
        print(f"📊 Total procesados: {len(emails)}")
        
        # Mostrar últimos 5 correos en BD
        print("\n" + "=" * 70)
        print("ÚLTIMOS 5 CORREOS EN BASE DE DATOS")
        print("=" * 70)
        
        ultimos = session.query(EmailProcesado).order_by(
            EmailProcesado.received_date.desc()
        ).limit(5).all()
        
        for i, email in enumerate(ultimos, 1):
            print(f"\n{i}. ID: {email.id}")
            print(f"   De: {email.sender_name} <{email.sender_email}>")
            print(f"   Asunto: {email.subject}")
            print(f"   Fecha: {email.received_date}")
            print(f"   Estado: {email.status}")
            print(f"   Adjuntos: {email.attachment_count}")
        
    except Exception as e:
        print(f"\n❌ Error al guardar en base de datos: {e}")
        session.rollback()
    
    finally:
        session.close()
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETADO")
    print("=" * 70)


if __name__ == "__main__":
    test_gmail_to_database()
    input("\nPresiona ENTER para salir...")