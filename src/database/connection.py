"""
Gestión de Conexión a Base de Datos MySQL
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from .models import Base

# Cargar variables de entorno
load_dotenv()


class DatabaseManager:
    """Gestor de conexión a base de datos"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.Session = None
        
    def initialize(self):
        """Inicializa la conexión a la base de datos"""
        
        # Obtener credenciales desde .env
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'bot_cobertores')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '')
        
        # Construir URL de conexión
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        
        # Crear engine con pool de conexiones
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verificar conexión antes de usar
            echo=False  # True para debug SQL
        )
        
        # Crear session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        print(f"✅ Conexión a base de datos establecida: {db_name}")
        
        return self
    
    def get_session(self):
        """Obtiene una nueva sesión de base de datos"""
        if self.Session is None:
            self.initialize()
        return self.Session()
    
    def close_session(self, session):
        """Cierra una sesión de forma segura"""
        try:
            session.close()
        except Exception as e:
            print(f"⚠️ Error al cerrar sesión: {e}")
    
    def create_tables(self):
        """Crea todas las tablas si no existen"""
        Base.metadata.create_all(self.engine)
        print("✅ Tablas verificadas/creadas")
    
    def test_connection(self):
        """Prueba la conexión a la base de datos"""
        try:
            from sqlalchemy import text
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            print("✅ Test de conexión exitoso")
            return True
        except Exception as e:
            print(f"❌ Error en test de conexión: {e}")
            return False


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


def get_db_session():
    """Helper function para obtener sesión de BD"""
    return db_manager.get_session()


def init_database():
    """Inicializa la base de datos (llamar al inicio de la app)"""
    db_manager.initialize()
    db_manager.create_tables()
    return db_manager.test_connection()

# =============================================================================
# ADDITIONAL HELPERS
# =============================================================================

def get_engine():
    """
    Obtiene el engine de SQLAlchemy
    
    Returns:
        Engine: Engine de SQLAlchemy
    """
    if db_manager.engine is None:
        db_manager.initialize()
    return db_manager.engine


from contextlib import contextmanager

@contextmanager
def session_scope():
    """
    Context manager para manejar sesiones de forma segura.
    
    Usage:
        with session_scope() as session:
            user = session.query(User).first()
            session.add(new_object)
            # Commit automático al salir
    """
    session = db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def get_session():
    """
    Obtiene una nueva sesión de base de datos (alias para compatibilidad)
    
    Returns:
        Session: Nueva sesión de SQLAlchemy
    """
    return db_manager.get_session()