"""
Sistema de Aprendizaje Histórico - FASE 0
Analiza Gmail histórico para extraer patrones operativos

Uso:
    python historical_scraper.py --months 6 --mode full
    python historical_scraper.py --months 3 --mode senders-only
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from collections import defaultdict, Counter
import json

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gmail_capture.gmail_client import GmailClient
from database.connection import get_session
from database.models import (
    SenderProfile, InternalAuthorProfile, ThreadPattern,
    LearnedRule, LearningSession, KeywordPattern
)

from sqlalchemy import func
from dotenv import load_dotenv

load_dotenv()


class HistoricalScraper:
    """Scraper de Gmail histórico para fase de aprendizaje"""
    
    # Palabras clave por categoría
    URGENCY_KEYWORDS = {
        'critica': ['urgente', 'emergencia', 'inmediato', 'hoy mismo', 'ahora', 'ya'],
        'alta': ['pronto', 'prioritario', 'importante', 'necesario', 'asap'],
        'media': ['cuando puedas', 'esta semana', 'revisar'],
        'baja': ['info', 'informativo', 'fyi', 'para conocimiento']
    }
    
    INTENT_KEYWORDS = {
        'cotizacion': ['cotización', 'cotizar', 'precio', 'cuánto cuesta', 'presupuesto'],
        'orden_compra': ['orden de compra', 'oc', 'pedido', 'comprar'],
        'reclamo': ['reclamo', 'problema', 'error', 'mal', 'incorrecto', 'queja'],
        'soporte': ['ayuda', 'soporte', 'apoyo', 'consulta', 'duda'],
        'seguimiento': ['seguimiento', 'estado', 'avance', 'progreso', '¿cómo va?'],
        'urgente': ['urgente', 'emergencia', 'inmediato', 'crítico']
    }
    
    ACTION_KEYWORDS = {
        'crear_tarea': ['por favor', 'necesito', 'podrían', 'solicito'],
        'escalar': ['urgente', 'gerencia', 'dirección', 'prioritario'],
        'requiere_respuesta': ['¿', 'consulta', 'pregunta', 'confirmar']
    }
    
    def __init__(self, months: int = 6):
        """
        Args:
            months: Meses hacia atrás a analizar
        """
        self.gmail = GmailClient()
        # Inicializar servicio explícitamente
        if not hasattr(self.gmail, 'service') or self.gmail.service is None:
            print("⚠️ Inicializando Gmail API...")
            self.gmail.authenticate()
        self.session = get_session()
        self.months = months
        self.stats = {
            'emails_analyzed': 0,
            'senders_identified': 0,
            'internal_authors_identified': 0,
            'threads_analyzed': 0,
            'rules_generated': 0
        }
        
        # Cache en memoria
        self.sender_stats = defaultdict(lambda: {
            'total': 0,
            'urgency_counts': Counter(),
            'intent_counts': Counter(),
            'action_counts': Counter(),
            'response_times': [],
            'subjects': [],
            'has_attachments': 0
        })
        
        self.internal_stats = defaultdict(lambda: {
            'total': 0,
            'forwarded': 0,
            'replied': 0,
            'cc_count': 0,
            'response_times': [],
            'roles_detected': Counter()
        })
        
        self.thread_stats = defaultdict(lambda: {
            'messages': 0,
            'participants': set(),
            'internal_count': 0,
            'external_count': 0,
            'has_forward': False,
            'has_cc': False,
            'has_attachments': False,
            'start_time': None,
            'end_time': None
        })
        
    def run_full_analysis(self) -> Dict:
        """Ejecuta análisis completo"""
        
        print("🚀 Iniciando análisis histórico de Gmail...")
        print(f"📅 Analizando últimos {self.months} meses")
        
        # Crear sesión de aprendizaje
        learning_session = LearningSession(
            session_type='initial',
            started_at=datetime.now(),
            status='running'
        )
        self.session.add(learning_session)
        self.session.commit()
        
        try:
            # 1. Obtener emails históricos
            print("\n📥 Obteniendo emails históricos...")
            emails = self._fetch_historical_emails()
            self.stats['emails_analyzed'] = len(emails)
            print(f"✅ {len(emails)} emails obtenidos")
            
            # 2. Analizar patrones
            print("\n🔍 Analizando patrones...")
            self._analyze_emails(emails)
            
            # 3. Guardar perfiles de remitentes
            print("\n💾 Guardando perfiles de remitentes...")
            self._save_sender_profiles()
            
            # 4. Guardar perfiles internos
            print("\n💾 Guardando perfiles internos...")
            self._save_internal_profiles()
            
            # 5. Guardar patrones de hilos
            print("\n💾 Guardando patrones de hilos...")
            self._save_thread_patterns()
            
            # 6. Generar reglas
            print("\n⚙️ Generando reglas automáticas...")
            self._generate_rules()
            
            # 7. Guardar palabras clave
            print("\n📝 Guardando palabras clave...")
            self._save_keywords()
            
            # Actualizar sesión
            learning_session.status = 'completed'
            learning_session.completed_at = datetime.now()
            learning_session.emails_scanned = self.stats['emails_analyzed']
            learning_session.senders_identified = self.stats['senders_identified']
            learning_session.internal_authors_identified = self.stats['internal_authors_identified']
            learning_session.rules_generated = self.stats['rules_generated']
            learning_session.duration_minutes = (
                (datetime.now() - learning_session.started_at).seconds // 60
            )
            self.session.commit()
            
            print("\n✅ Análisis completado exitosamente!")
            self._print_summary()
            
            return self.stats
            
        except Exception as e:
            learning_session.status = 'failed'
            learning_session.error_message = str(e)
            learning_session.completed_at = datetime.now()
            self.session.commit()
            
            print(f"\n❌ Error en análisis: {str(e)}")
            raise
    
    def _fetch_historical_emails(self) -> List[Dict]:
        """Obtiene emails históricos de Gmail"""
        
        date_limit = datetime.now() - timedelta(days=30 * self.months)
        query = f"after:{date_limit.strftime('%Y/%m/%d')}"
        
        try:
            messages = self.gmail.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=500  # Límite por seguridad, ajustar según necesidad
            ).execute()
            
            emails = []
            
            if 'messages' in messages:
                total = len(messages['messages'])
                print(f"📊 Procesando {total} mensajes...")
                
                for idx, msg in enumerate(messages['messages'], 1):
                    if idx % 50 == 0:
                        print(f"   Procesados: {idx}/{total}")
                    
                    email_data = self._get_email_details(msg['id'])
                    if email_data:
                        emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"❌ Error obteniendo emails: {str(e)}")
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict]:
        """Obtiene detalles completos de un email"""
        
        try:
            message = self.gmail.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'cc': headers.get('Cc', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'in_reply_to': headers.get('In-Reply-To', ''),
                'references': headers.get('References', ''),
                'labels': message.get('labelIds', []),
                'has_attachments': 'parts' in message['payload'] and 
                                   any(p.get('filename') for p in message['payload'].get('parts', []))
            }
            
        except Exception as e:
            return None
    
    def _analyze_emails(self, emails: List[Dict]):
        """Analiza todos los emails y extrae patrones"""
        
        internal_domain = os.getenv('INTERNAL_DOMAIN', '@usach.cl')  # Ajustar según empresa
        
        for email in emails:
            # Extraer email del remitente
            sender_match = re.search(r'<(.+?)>', email['from'])
            sender_email = sender_match.group(1) if sender_match else email['from']
            
            is_internal = internal_domain in sender_email
            
            # Analizar remitente externo
            if not is_internal:
                self._analyze_sender(sender_email, email)
            else:
                # Analizar autor interno
                self._analyze_internal_author(sender_email, email)
            
            # Analizar hilo
            self._analyze_thread(email['thread_id'], email, is_internal)
    
    def _analyze_sender(self, sender_email: str, email: Dict):
        """Analiza patrones de un remitente externo"""
        
        stats = self.sender_stats[sender_email]
        stats['total'] += 1
        
        subject = email['subject'].lower()
        
        # Detectar urgencia
        urgency = self._detect_urgency(subject)
        stats['urgency_counts'][urgency] += 1
        
        # Detectar intención
        intent = self._detect_intent(subject)
        stats['intent_counts'][intent] += 1
        
        # Detectar acción
        action = self._detect_action(subject)
        stats['action_counts'][action] += 1
        
        # Attachments
        if email['has_attachments']:
            stats['has_attachments'] += 1
        
        stats['subjects'].append(subject)
    
    def _analyze_internal_author(self, author_email: str, email: Dict):
        """Analiza patrones de autor interno"""
        
        stats = self.internal_stats[author_email]
        stats['total'] += 1
        
        # Detectar forwards
        if email['in_reply_to'] or 'fwd' in email['subject'].lower():
            stats['forwarded'] += 1
        
        # Detectar replies
        if email['in_reply_to']:
            stats['replied'] += 1
        
        # Contar CCs
        if email['cc']:
            stats['cc_count'] += len(email['cc'].split(','))
        
        # Detectar rol por keywords en subject
        subject_lower = email['subject'].lower()
        if any(kw in subject_lower for kw in ['venta', 'cliente', 'comercial']):
            stats['roles_detected']['ventas'] += 1
        elif any(kw in subject_lower for kw in ['operacion', 'produccion', 'logistica']):
            stats['roles_detected']['operaciones'] += 1
        elif any(kw in subject_lower for kw in ['compra', 'proveedor']):
            stats['roles_detected']['compras'] += 1
    
    def _analyze_thread(self, thread_id: str, email: Dict, is_internal: bool):
        """Analiza patrones de un hilo"""
        
        stats = self.thread_stats[thread_id]
        stats['messages'] += 1
        
        sender_match = re.search(r'<(.+?)>', email['from'])
        sender = sender_match.group(1) if sender_match else email['from']
        stats['participants'].add(sender)
        
        if is_internal:
            stats['internal_count'] += 1
        else:
            stats['external_count'] += 1
        
        if 'fwd' in email['subject'].lower():
            stats['has_forward'] = True
        
        if email['cc']:
            stats['has_cc'] = True
        
        if email['has_attachments']:
            stats['has_attachments'] = True
    
    def _detect_urgency(self, text: str) -> str:
        """Detecta nivel de urgencia por keywords"""
        
        for level, keywords in self.URGENCY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return level
        return 'media'
    
    def _detect_intent(self, text: str) -> str:
        """Detecta intención por keywords"""
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return intent
        return 'otro'
    
    def _detect_action(self, text: str) -> str:
        """Detecta acción requerida"""
        
        for action, keywords in self.ACTION_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return action
        return 'crear_tarea'
    
    def _save_sender_profiles(self):
        """Guarda perfiles de remitentes en BD"""
    
        # Rollback por si hay error previo
        self.session.rollback()
    
        for sender_email, stats in self.sender_stats.items():
            if stats['total'] < 3:  # Mínimo 3 emails para crear perfil
                continue
            
            # Calcular promedios
            most_common_urgency = stats['urgency_counts'].most_common(1)[0][0]
            most_common_intent = stats['intent_counts'].most_common(1)[0][0]
            most_common_action = stats['action_counts'].most_common(1)[0][0]
            
            # Calcular confianza (basado en volumen y consistencia)
            urgency_confidence = stats['urgency_counts'][most_common_urgency] / stats['total']
            confidence = min(urgency_confidence * (stats['total'] / 10), 1.0)
            
            # Extraer dominio y empresa
            domain = sender_email.split('@')[1] if '@' in sender_email else ''
            empresa = domain.split('.')[0].title() if domain else ''
            
            profile = SenderProfile(
                email=sender_email,
                domain=domain,
                empresa=empresa,
                category='proveedor' if 'proveedor' in empresa.lower() else 'cliente',
                inferred_intent=most_common_intent,
                typical_action=most_common_action,
                typical_urgency=most_common_urgency,
                emails_analyzed=stats['total'],
                confidence_score=confidence,
                last_seen=datetime.now()
            )
            
            self.session.merge(profile)
            self.stats['senders_identified'] += 1
        
        self.session.commit()
    
    def _save_internal_profiles(self):
        """Guarda perfiles de autores internos"""
        
        for author_email, stats in self.internal_stats.items():
            if stats['total'] < 3:
                continue
            
            # Inferir rol
            most_common_role = stats['roles_detected'].most_common(1)
            role = most_common_role[0][0] if most_common_role else 'otro'
            
            profile = InternalAuthorProfile(
                email=author_email,
                role=role,
                tends_to_forward=stats['forwarded'] / stats['total'] > 0.3,
                tends_to_cc_multiple=stats['cc_count'] / stats['total'] > 2,
                emails_analyzed=stats['total'],
                last_seen=datetime.now()
            )
            
            self.session.merge(profile)
            self.stats['internal_authors_identified'] += 1
        
        self.session.commit()
    
    def _save_thread_patterns(self):
        """Guarda patrones de hilos"""
        
        for thread_id, stats in self.thread_stats.items():
            if stats['messages'] < 2:  # Solo hilos con múltiples mensajes
                continue
            
            # Calcular complejidad
            if stats['messages'] > 10 or len(stats['participants']) > 5:
                complexity = 'alta'
            elif stats['messages'] > 5 or len(stats['participants']) > 3:
                complexity = 'media'
            else:
                complexity = 'baja'
            
            pattern = ThreadPattern(
                thread_id=thread_id,
                total_messages=stats['messages'],
                internal_participants=stats['internal_count'],
                external_participants=stats['external_count'],
                has_forward=stats['has_forward'],
                has_cc=stats['has_cc'],
                has_attachments=stats['has_attachments'],
                inferred_complexity=complexity
            )
            
            self.session.merge(pattern)
            self.stats['threads_analyzed'] += 1
        
        self.session.commit()
    
    def _generate_rules(self):
        """Genera reglas automáticas basadas en patrones"""
        
        # Reglas por remitente
        for sender_email, stats in self.sender_stats.items():
            if stats['total'] < 5:
                continue
            
            most_common_urgency = stats['urgency_counts'].most_common(1)[0][0]
            most_common_action = stats['action_counts'].most_common(1)[0][0]
            
            if stats['urgency_counts'][most_common_urgency] / stats['total'] > 0.7:
                rule = LearnedRule(
                    rule_name=f"Auto: {sender_email}",
                    rule_type='sender',
                    trigger_condition=json.dumps({'sender': sender_email}),
                    action=most_common_action,
                    urgency=most_common_urgency,
                    confidence=stats['urgency_counts'][most_common_urgency] / stats['total'],
                    times_triggered=0
                )
                
                self.session.merge(rule)
                self.stats['rules_generated'] += 1
        
        self.session.commit()
    
    def _save_keywords(self):
        """Guarda palabras clave encontradas"""
        
        # Contar todas las palabras en subjects
        all_words = Counter()
        
        for stats in self.sender_stats.values():
            for subject in stats['subjects']:
                words = re.findall(r'\w+', subject.lower())
                all_words.update(words)
        
        # Guardar top keywords
        for word, count in all_words.most_common(50):
            if len(word) < 3 or word in ['de', 'la', 'el', 'en', 'para']:
                continue
            
            keyword = KeywordPattern(
                keyword=word,
                category='otro',
                times_found=count
            )
            
            self.session.merge(keyword)
        
        self.session.commit()
    
    def _print_summary(self):
        """Imprime resumen de análisis"""
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE ANÁLISIS")
        print("="*60)
        print(f"📧 Emails analizados: {self.stats['emails_analyzed']}")
        print(f"👥 Remitentes identificados: {self.stats['senders_identified']}")
        print(f"🏢 Autores internos: {self.stats['internal_authors_identified']}")
        print(f"🔗 Hilos analizados: {self.stats['threads_analyzed']}")
        print(f"⚙️  Reglas generadas: {self.stats['rules_generated']}")
        print("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis histórico de Gmail')
    parser.add_argument('--months', type=int, default=6, help='Meses a analizar')
    parser.add_argument('--mode', choices=['full', 'senders-only'], default='full')
    
    args = parser.parse_args()
    
    scraper = HistoricalScraper(months=args.months)
    
    try:
        stats = scraper.run_full_analysis()
        print("\n✅ Proceso completado exitosamente")
        print(f"📊 Ver resultados en base de datos: sender_profiles, learned_rules")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)