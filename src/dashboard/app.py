"""
Dashboard Web - Flask Application
Visualización de emails procesados y tareas creadas
"""

import sys
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import EmailProcesado, Tarea, Alerta
from database.connection import session_scope

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'dev-secret-key-change-in-production')


@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('dashboard.html')


@app.route('/api/stats')
def get_stats():
    """Estadísticas generales"""
    try:
        with session_scope() as session:
            # Contadores
            total_emails = session.query(EmailProcesado).count()
            total_tareas = session.query(Tarea).count()
            tareas_pendientes = session.query(Tarea).filter(Tarea.estado == 'pendiente').count()
            tareas_completadas = session.query(Tarea).filter(Tarea.estado == 'completada').count()
            
            # Tareas por prioridad
            alta_prioridad = session.query(Tarea).filter(Tarea.prioridad == 'alta').count()
            normal_prioridad = session.query(Tarea).filter(Tarea.prioridad == 'normal').count()
            baja_prioridad = session.query(Tarea).filter(Tarea.prioridad == 'baja').count()
            
            stats = {
                'total_emails': total_emails,
                'total_tareas': total_tareas,
                'tareas_pendientes': tareas_pendientes,
                'tareas_completadas': tareas_completadas,
                'alta_prioridad': alta_prioridad,
                'normal_prioridad': normal_prioridad,
                'baja_prioridad': baja_prioridad
            }
            
            return jsonify(stats)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/emails')
def get_emails():
    """Lista de emails procesados"""
    try:
        with session_scope() as session:
            emails = session.query(EmailProcesado).order_by(
                EmailProcesado.received_date.desc()
            ).limit(50).all()
            
            emails_data = [{
                'id': email.id,
                'gmail_id': email.gmail_id,
                'subject': email.subject,
                'sender_email': email.sender_email,
                'sender_name': email.sender_name,
                'received_date': email.received_date.isoformat() if email.received_date else None,
                'processed_date': email.processed_date.isoformat() if email.processed_date else None,
                'status': email.status,
                'has_attachments': email.has_attachments,
                'attachment_count': email.attachment_count,
                'priority': email.priority
            } for email in emails]
            
            return jsonify(emails_data)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tareas')
def get_tareas():
    """Lista de tareas creadas"""
    try:
        estado_filter = request.args.get('estado')
        prioridad_filter = request.args.get('prioridad')
        
        with session_scope() as session:
            query = session.query(Tarea)
            
            # Aplicar filtros
            if estado_filter:
                query = query.filter(Tarea.estado == estado_filter)
            if prioridad_filter:
                query = query.filter(Tarea.prioridad == prioridad_filter)
            
            tareas = query.order_by(Tarea.fecha_solicitud.desc()).limit(100).all()
            
            tareas_data = [{
                'id': tarea.id,
                'email_id': tarea.email_id,
                'codigo_cobertor': tarea.codigo_cobertor,
                'cuartel': tarea.cuartel,
                'hileras': tarea.hileras,
                'largo_metros': float(tarea.largo_metros) if tarea.largo_metros else None,
                'prioridad': tarea.prioridad,
                'estado': tarea.estado,
                'fecha_solicitud': tarea.fecha_solicitud.isoformat() if tarea.fecha_solicitud else None,
                'fecha_requerida': tarea.fecha_requerida.isoformat() if tarea.fecha_requerida else None,
                'observaciones': tarea.observaciones
            } for tarea in tareas]
            
            return jsonify(tareas_data)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/<int:email_id>')
def get_email_detail(email_id):
    """Detalle de un email específico con sus tareas"""
    try:
        with session_scope() as session:
            email = session.query(EmailProcesado).filter(
                EmailProcesado.id == email_id
            ).first()
            
            if not email:
                return jsonify({'error': 'Email no encontrado'}), 404
            
            # Obtener tareas asociadas
            tareas = session.query(Tarea).filter(Tarea.email_id == email_id).all()
            
            email_data = {
                'id': email.id,
                'gmail_id': email.gmail_id,
                'subject': email.subject,
                'sender_email': email.sender_email,
                'sender_name': email.sender_name,
                'body_text': email.body_text,
                'received_date': email.received_date.isoformat() if email.received_date else None,
                'processed_date': email.processed_date.isoformat() if email.processed_date else None,
                'status': email.status,
                'tareas': [{
                    'id': t.id,
                    'codigo_cobertor': t.codigo_cobertor,
                    'cuartel': t.cuartel,
                    'hileras': t.hileras,
                    'largo_metros': float(t.largo_metros) if t.largo_metros else None,
                    'prioridad': t.prioridad,
                    'estado': t.estado
                } for t in tareas]
            }
            
            return jsonify(email_data)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tarea/<int:tarea_id>/update', methods=['POST'])
def update_tarea(tarea_id):
    """Actualizar estado de una tarea"""
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        if nuevo_estado not in ['pendiente', 'en_proceso', 'completada', 'cancelada']:
            return jsonify({'error': 'Estado inválido'}), 400
        
        with session_scope() as session:
            tarea = session.query(Tarea).filter(Tarea.id == tarea_id).first()
            
            if not tarea:
                return jsonify({'error': 'Tarea no encontrada'}), 404
            
            tarea.estado = nuevo_estado
            
            if nuevo_estado == 'completada':
                tarea.fecha_completada = datetime.now()
            
            return jsonify({'success': True, 'estado': nuevo_estado})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🌐 Iniciando Dashboard...")
    print("📊 Accede a: http://localhost:5000")
    print("🔄 Presiona Ctrl+C para detener")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )