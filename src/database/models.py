"""
Modelos de Base de Datos - SQLAlchemy ORM
Define las tablas como clases Python para fácil manejo
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Enum, DECIMAL, ForeignKey, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class EmailProcesado(Base):
    """Correos capturados y procesados desde Gmail"""
    
    __tablename__ = 'emails_procesados'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    gmail_id = Column(String(255), unique=True, nullable=False)
    thread_id = Column(String(255))
    sender_email = Column(String(255), nullable=False)
    sender_name = Column(String(255))
    subject = Column(Text)
    body_text = Column(Text)
    body_html = Column(Text)
    received_date = Column(DateTime, nullable=False)
    processed_date = Column(DateTime, default=datetime.now)
    has_attachments = Column(Boolean, default=False)
    attachment_count = Column(Integer, default=0)
    priority = Column(String(50), default='normal')
    status = Column(
        Enum('pending', 'processed', 'error', name='email_status'),
        default='pending'
    )
    error_message = Column(Text)
    
    # Relaciones
    tareas = relationship('Tarea', back_populates='email', cascade='all, delete-orphan')
    adjuntos = relationship('ArchivoAdjunto', back_populates='email', cascade='all, delete-orphan')
    alertas = relationship('Alerta', back_populates='email')
    
    # Índices
    __table_args__ = (
        Index('idx_gmail_id', 'gmail_id'),
        Index('idx_received_date', 'received_date'),
        Index('idx_status', 'status'),
        Index('idx_priority', 'priority'),
    )
    
    def __repr__(self):
        return f"<EmailProcesado(id={self.id}, subject='{self.subject[:30]}...', status='{self.status}')>"


class Tarea(Base):
    """Tareas operacionales extraídas de los correos"""
    
    __tablename__ = 'tareas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('emails_procesados.id', ondelete='CASCADE'), nullable=False)
    
    # Información del cobertor
    codigo_cobertor = Column(String(100))
    cuartel = Column(String(50))
    hileras = Column(Integer)
    largo_metros = Column(DECIMAL(10, 2))
    cantidad = Column(Integer, default=1)
    
    # Especificaciones técnicas
    tipo_cobertor = Column(String(100))
    perforacion = Column(String(50))
    color = Column(String(50))
    observaciones = Column(Text)
    
    # Gestión de la tarea
    prioridad = Column(
        Enum('baja', 'normal', 'alta', 'urgente', name='prioridad_enum'),
        default='normal'
    )
    estado = Column(
        Enum('pendiente', 'en_proceso', 'completada', 'cancelada', name='estado_enum'),
        default='pendiente'
    )
    fecha_solicitud = Column(DateTime, nullable=False)
    fecha_requerida = Column(DateTime)
    fecha_estimada_produccion = Column(DateTime)
    fecha_completada = Column(DateTime)
    
    # Cliente/Solicitante
    solicitante_nombre = Column(String(255))
    solicitante_email = Column(String(255))
    area_solicitante = Column(String(100))
    
    # Tracking
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    email = relationship('EmailProcesado', back_populates='tareas')
    alertas = relationship('Alerta', back_populates='tarea')
    
    # Índices
    __table_args__ = (
        Index('idx_estado', 'estado'),
        Index('idx_prioridad', 'prioridad'),
        Index('idx_fecha_requerida', 'fecha_requerida'),
        Index('idx_codigo', 'codigo_cobertor'),
    )
    
    def __repr__(self):
        return f"<Tarea(id={self.id}, codigo='{self.codigo_cobertor}', estado='{self.estado}')>"


class ArchivoAdjunto(Base):
    """Archivos adjuntos procesados"""
    
    __tablename__ = 'archivos_adjuntos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('emails_procesados.id', ondelete='CASCADE'), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100))
    size_bytes = Column(Integer)
    file_path = Column(String(500))
    extracted_data = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relaciones
    email = relationship('EmailProcesado', back_populates='adjuntos')
    
    # Índices
    __table_args__ = (
        Index('idx_email_id', 'email_id'),
        Index('idx_processed', 'processed'),
    )
    
    def __repr__(self):
        return f"<ArchivoAdjunto(id={self.id}, filename='{self.filename}')>"


class Alerta(Base):
    """Alertas y notificaciones del sistema"""
    
    __tablename__ = 'alertas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(
        Enum('conflicto', 'urgente', 'vencimiento', 'informativa', name='tipo_alerta_enum'),
        nullable=False
    )
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tarea_id = Column(Integer, ForeignKey('tareas.id', ondelete='SET NULL'))
    email_id = Column(Integer, ForeignKey('emails_procesados.id', ondelete='SET NULL'))
    severidad = Column(
        Enum('baja', 'media', 'alta', 'critica', name='severidad_enum'),
        default='media'
    )
    leida = Column(Boolean, default=False)
    fecha_alerta = Column(DateTime, default=datetime.now)
    
    # Relaciones
    tarea = relationship('Tarea', back_populates='alertas')
    email = relationship('EmailProcesado', back_populates='alertas')
    
    # Índices
    __table_args__ = (
        Index('idx_leida', 'leida'),
        Index('idx_tipo', 'tipo'),
        Index('idx_fecha', 'fecha_alerta'),
    )
    
    def __repr__(self):
        return f"<Alerta(id={self.id}, tipo='{self.tipo}', titulo='{self.titulo}')>"


class Configuracion(Base):
    """Configuración dinámica del sistema"""
    
    __tablename__ = 'configuracion'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    tipo = Column(
        Enum('string', 'number', 'boolean', 'json', name='tipo_config_enum'),
        default='string'
    )
    descripcion = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Configuracion(clave='{self.clave}', valor='{self.valor}')>"


class LogSistema(Base):
    """Log de operaciones del bot"""
    
    __tablename__ = 'log_sistema'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    nivel = Column(
        Enum('debug', 'info', 'warning', 'error', 'critical', name='nivel_log_enum'),
        default='info'
    )
    modulo = Column(String(100))
    mensaje = Column(Text)
    detalles = Column(JSON)
    
    # Índices
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_nivel', 'nivel'),
        Index('idx_modulo', 'modulo'),
    )
    
    def __repr__(self):
        return f"<LogSistema(nivel='{self.nivel}', modulo='{self.modulo}', mensaje='{self.mensaje[:50]}...')>"

# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from .connection import get_engine

# Crear session factory
Session = sessionmaker(bind=get_engine())


@contextmanager
def session_scope():
    """
    Context manager para manejar sesiones de SQLAlchemy de forma segura.
    
    Usage:
        with session_scope() as session:
            user = session.query(User).first()
            session.add(new_object)
            # Commit automático al salir
    """
    session = Session()
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
    Obtiene una nueva sesión de base de datos.
    Recuerda cerrarla manualmente después de usarla.
    
    Returns:
        Session: Nueva sesión de SQLAlchemy
    """
    return Session()

# =============================================================================
# IMPORT SESSION SCOPE FROM CONNECTION
# =============================================================================

from .connection import session_scope

# Exportar para que esté disponible al importar desde models
__all__ = ['Base', 'EmailProcesado', 'Tarea', 'ArchivoAdjunto', 'Alerta', 'session_scope']