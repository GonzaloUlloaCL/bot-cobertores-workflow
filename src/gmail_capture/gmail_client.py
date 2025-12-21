"""
Cliente Gmail API - Captura de correos con etiqueta específica
"""

import os
import base64
from datetime import datetime
from email.utils import parsedate_to_datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailClient:
    """Cliente para interactuar con Gmail API"""
    
    def __init__(self):
        self.service = None
        self.label_name = os.getenv('GMAIL_LABEL', 'bot-cobertores')
        self.label_id = None
        
    def authenticate(self):
        """Autentica con Gmail API"""
        creds = None
        token_path = 'token.json'
        credentials_path = 'credentials.json'
        
        # Cargar token existente
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Renovar o crear nuevo token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Guardar token
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Crear servicio
        self.service = build('gmail', 'v1', credentials=creds)
        
        # Obtener ID de la etiqueta
        self.label_id = self._get_label_id()
        
        print(f"✅ Autenticado con Gmail API")
        print(f"✅ Etiqueta '{self.label_name}' ID: {self.label_id}")
        
        return self
    
    def _get_label_id(self):
        """Obtiene el ID de la etiqueta configurada"""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'].lower() == self.label_name.lower():
                    return label['id']
            
            print(f"⚠️ Etiqueta '{self.label_name}' no encontrada")
            return None
            
        except HttpError as error:
            print(f"❌ Error al obtener etiquetas: {error}")
            return None
    
    def get_unread_emails(self, max_results=50):
        """
        Obtiene correos no leídos con la etiqueta específica
        
        Args:
            max_results: Máximo de correos a obtener
            
        Returns:
            Lista de diccionarios con información de correos
        """
        if not self.label_id:
            print("❌ No se puede obtener correos sin ID de etiqueta")
            return []
        
        try:
            # Buscar correos con la etiqueta y sin leer
            query = f"label:{self.label_name} is:unread"
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print(f"📭 No hay correos nuevos con etiqueta '{self.label_name}'")
                return []
            
            print(f"📬 {len(messages)} correos nuevos encontrados")
            
            # Obtener detalles completos de cada correo
            emails_data = []
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails_data.append(email_data)
            
            return emails_data
            
        except HttpError as error:
            print(f"❌ Error al obtener correos: {error}")
            return []
    
    def _get_email_details(self, msg_id):
        """
        Obtiene detalles completos de un correo
        
        Args:
            msg_id: ID del mensaje en Gmail
            
        Returns:
            Diccionario con datos del correo
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extraer headers
            headers = message['payload']['headers']
            headers_dict = {h['name']: h['value'] for h in headers}
            
            # Fecha del correo
            date_str = headers_dict.get('Date', '')
            try:
                received_date = parsedate_to_datetime(date_str)
            except:
                received_date = datetime.now()
            
            # Cuerpo del correo
            body_text = self._extract_body(message['payload'], 'text/plain')
            body_html = self._extract_body(message['payload'], 'text/html')
            
            # Verificar adjuntos
            has_attachments = False
            attachment_count = 0
            
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('filename'):
                        has_attachments = True
                        attachment_count += 1
            
            email_data = {
                'gmail_id': msg_id,
                'thread_id': message['threadId'],
                'sender_email': headers_dict.get('From', ''),
                'sender_name': self._extract_name(headers_dict.get('From', '')),
                'subject': headers_dict.get('Subject', ''),
                'body_text': body_text,
                'body_html': body_html,
                'received_date': received_date,
                'has_attachments': has_attachments,
                'attachment_count': attachment_count,
                'labels': message.get('labelIds', []),
                'raw_message': message  # Guardar mensaje completo para procesamiento posterior
            }
            
            return email_data
            
        except HttpError as error:
            print(f"❌ Error al obtener detalles del correo {msg_id}: {error}")
            return None
    
    def _extract_body(self, payload, mime_type):
        """Extrae el cuerpo del correo según mime type"""
        
        # Si el payload tiene body directamente
        if payload.get('mimeType') == mime_type and 'data' in payload.get('body', {}):
            data = payload['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        # Si tiene partes, buscar recursivamente
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == mime_type and 'data' in part.get('body', {}):
                    data = part['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
                # Buscar en sub-partes
                if 'parts' in part:
                    result = self._extract_body(part, mime_type)
                    if result:
                        return result
        
        return ""
    
    def _extract_name(self, from_field):
        """Extrae el nombre del campo From"""
        if '<' in from_field:
            name = from_field.split('<')[0].strip()
            return name.strip('"').strip("'")
        return from_field
    
    def mark_as_read(self, msg_id):
        """Marca un correo como leído"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f"⚠️ Error al marcar correo como leído: {error}")
            return False
    
    def download_attachment(self, msg_id, attachment_id, filename, save_path='data/attachments/'):
        """
        Descarga un archivo adjunto
        
        Args:
            msg_id: ID del mensaje
            attachment_id: ID del adjunto
            filename: Nombre del archivo
            save_path: Ruta donde guardar el archivo
            
        Returns:
            Ruta completa del archivo guardado o None si falla
        """
        try:
            # Crear directorio si no existe
            os.makedirs(save_path, exist_ok=True)
            
            # Obtener adjunto
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=msg_id,
                id=attachment_id
            ).execute()
            
            # Decodificar y guardar
            file_data = base64.urlsafe_b64decode(attachment['data'])
            file_path = os.path.join(save_path, filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            print(f"✅ Adjunto guardado: {file_path}")
            return file_path
            
        except HttpError as error:
            print(f"❌ Error al descargar adjunto: {error}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    print("🚀 Test de Gmail Client\n")
    
    # Crear cliente y autenticar
    client = GmailClient()
    client.authenticate()
    
    # Obtener correos
    emails = client.get_unread_emails(max_results=5)
    
    print(f"\n📊 Total de correos capturados: {len(emails)}")
    
    # Mostrar info de cada correo
    for i, email in enumerate(emails, 1):
        print(f"\n--- Correo {i} ---")
        print(f"De: {email['sender_name']} <{email['sender_email']}>")
        print(f"Asunto: {email['subject']}")
        print(f"Fecha: {email['received_date']}")
        print(f"Adjuntos: {email['attachment_count']}")
        print(f"Texto (preview): {email['body_text'][:100]}...")