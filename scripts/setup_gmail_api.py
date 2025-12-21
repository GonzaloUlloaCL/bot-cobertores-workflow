"""
Setup Gmail API Authentication
Genera el token de autenticación para acceder a Gmail API
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Alcance de permisos (read-only para correos)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'  # Para marcar como leído/aplicar etiquetas
]

def authenticate_gmail():
    """
    Autentica con Gmail API y guarda el token
    """
    creds = None
    token_path = 'token.json'
    credentials_path = 'credentials.json'
    
    print("=" * 60)
    print("SETUP GMAIL API - AUTENTICACIÓN")
    print("=" * 60)
    
    # Verificar que existe credentials.json
    if not os.path.exists(credentials_path):
        print("\n❌ ERROR: No se encuentra 'credentials.json'")
        print("\nPASOS PARA OBTENERLO:")
        print("1. Ve a: https://console.cloud.google.com/")
        print("2. Crea proyecto o selecciona uno existente")
        print("3. Habilita Gmail API")
        print("4. Crea credenciales OAuth 2.0 (Desktop app)")
        print("5. Descarga el JSON y guárdalo como 'credentials.json'")
        print("   en la raíz del proyecto")
        return None
    
    print("\n✅ Archivo credentials.json encontrado")
    
    # Verificar si ya existe un token válido
    if os.path.exists(token_path):
        print("✅ Token existente encontrado")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Si no hay token válido, generar uno nuevo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("⚠️ Token expirado, renovando...")
            creds.refresh(Request())
        else:
            print("\n🔐 Iniciando flujo de autenticación OAuth...")
            print("\n📌 Se abrirá tu navegador para autorizar la app")
            print("   1. Selecciona tu cuenta Gmail")
            print("   2. Click en 'Permitir' o 'Allow'")
            print("   3. Vuelve a esta ventana\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Guardar el token para futuros usos
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("✅ Token guardado en token.json")
    
    print("\n" + "=" * 60)
    print("TEST DE CONEXIÓN")
    print("=" * 60)
    
    try:
        # Crear servicio Gmail
        service = build('gmail', 'v1', credentials=creds)
        
        # Test: obtener perfil del usuario
        profile = service.users().getProfile(userId='me').execute()
        
        print(f"\n✅ Conexión exitosa!")
        print(f"   Email: {profile['emailAddress']}")
        print(f"   Total mensajes: {profile['messagesTotal']:,}")
        print(f"   Total threads: {profile['threadsTotal']:,}")
        
        # Test: listar etiquetas
        print("\n📋 Etiquetas disponibles en tu Gmail:")
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        if not labels:
            print("   No se encontraron etiquetas")
        else:
            for label in labels[:10]:  # Mostrar solo primeras 10
                print(f"   - {label['name']}")
        
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETADO CON ÉXITO")
        print("=" * 60)
        print("\n📌 PRÓXIMO PASO:")
        print("   1. Crea una etiqueta llamada 'bot-cobertores' en Gmail")
        print("   2. Envíate un correo de prueba con esa etiqueta")
        print("   3. Ejecuta el bot para procesar correos")
        
        return service
        
    except Exception as e:
        print(f"\n❌ ERROR al conectar con Gmail API:")
        print(f"   {str(e)}")
        return None

def create_label_if_not_exists(service, label_name='bot-cobertores'):
    """
    Crea la etiqueta en Gmail si no existe
    """
    try:
        # Verificar si la etiqueta ya existe
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                print(f"\n✅ Etiqueta '{label_name}' ya existe")
                print(f"   ID: {label['id']}")
                return label['id']
        
        # Crear etiqueta si no existe
        print(f"\n🏷️ Creando etiqueta '{label_name}'...")
        
        label_object = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        
        created_label = service.users().labels().create(
            userId='me',
            body=label_object
        ).execute()
        
        print(f"✅ Etiqueta creada exitosamente")
        print(f"   ID: {created_label['id']}")
        
        return created_label['id']
        
    except Exception as e:
        print(f"⚠️ Error al crear etiqueta: {str(e)}")
        return None

if __name__ == "__main__":
    print("\n🚀 Bot Cobertores - Setup Gmail API\n")
    
    # Autenticar
    service = authenticate_gmail()
    
    if service:
        # Crear etiqueta automáticamente
        print("\n" + "=" * 60)
        create_label_if_not_exists(service, 'bot-cobertores')
        
        print("\n" + "=" * 60)
        print("🎉 TODO LISTO PARA EMPEZAR")
        print("=" * 60)
        print("\nYa puedes ejecutar el bot principal")
    else:
        print("\n❌ Setup fallido. Revisa los errores arriba.")
    
    input("\nPresiona ENTER para salir...")