-- ============================================
-- MIGRACIÓN: Agregar sistema de aprendizaje
-- Base de datos: bot_cobertores (EXISTENTE)
-- Fecha: 2024-12-27
-- ============================================

USE bot_cobertores;

-- ============================================
-- PRIMERO: Verificar y agregar columnas faltantes
-- ============================================

-- Agregar columnas a tareas (con manejo de errores)
SET @sql = 'ALTER TABLE tareas ADD COLUMN confianza_clasificacion FLOAT DEFAULT NULL';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = 'ALTER TABLE tareas ADD COLUMN metodo_clasificacion VARCHAR(50) DEFAULT "manual"';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = 'ALTER TABLE tareas ADD COLUMN requiere_revision_humana BOOLEAN DEFAULT FALSE';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = 'ALTER TABLE tareas ADD COLUMN razon_revision VARCHAR(255) DEFAULT NULL';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar columnas a archivos_adjuntos
SET @sql = 'ALTER TABLE archivos_adjuntos ADD COLUMN confidence_score FLOAT DEFAULT 0.0';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = 'ALTER TABLE archivos_adjuntos ADD COLUMN requires_review BOOLEAN DEFAULT FALSE';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = 'ALTER TABLE archivos_adjuntos ADD COLUMN review_reason VARCHAR(255) DEFAULT NULL';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================
-- NUEVAS TABLAS: Sistema de aprendizaje
-- ============================================

CREATE TABLE IF NOT EXISTS sender_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(255),
    empresa VARCHAR(255),
    domain VARCHAR(255),
    category ENUM('cliente','proveedor','interno','gobierno','otro') DEFAULT 'otro',
    inferred_intent ENUM('cotizacion','orden_compra','reclamo','soporte','consulta','seguimiento','informativo','urgente','otro') DEFAULT 'otro',
    typical_action ENUM('crear_tarea','escalar','solo_informar','requiere_respuesta','archivar') DEFAULT 'crear_tarea',
    typical_urgency ENUM('baja','media','alta','critica') DEFAULT 'media',
    avg_response_time_hours INT,
    emails_analyzed INT DEFAULT 0,
    confidence_score FLOAT DEFAULT 0.0,
    last_seen DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_category (category),
    INDEX idx_confidence (confidence_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS internal_author_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(255),
    role ENUM('operaciones','ventas','logistica','compras','management','soporte','otro') DEFAULT 'otro',
    seniority ENUM('junior','mid','senior','lead','manager') DEFAULT 'mid',
    avg_response_minutes INT,
    avg_emails_per_day FLOAT,
    escalation_weight FLOAT DEFAULT 1.0,
    tends_to_forward BOOLEAN DEFAULT FALSE,
    tends_to_assign BOOLEAN DEFAULT FALSE,
    tends_to_cc_multiple BOOLEAN DEFAULT FALSE,
    work_hours_start TIME DEFAULT '09:00:00',
    work_hours_end TIME DEFAULT '18:00:00',
    works_weekends BOOLEAN DEFAULT FALSE,
    emails_analyzed INT DEFAULT 0,
    threads_participated INT DEFAULT 0,
    last_seen DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS thread_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    thread_id VARCHAR(255) UNIQUE,
    subject VARCHAR(500),
    total_messages INT,
    internal_participants INT,
    external_participants INT,
    has_forward BOOLEAN DEFAULT FALSE,
    has_reply_all BOOLEAN DEFAULT FALSE,
    has_cc BOOLEAN DEFAULT FALSE,
    has_attachments BOOLEAN DEFAULT FALSE,
    inferred_complexity ENUM('baja','media','alta') DEFAULT 'media',
    inferred_risk ENUM('bajo','medio','alto') DEFAULT 'medio',
    time_to_resolution_hours INT,
    status ENUM('abierto','cerrado','abandonado') DEFAULT 'cerrado',
    started_at DATETIME,
    closed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_thread (thread_id),
    INDEX idx_complexity (inferred_complexity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS learned_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(255),
    rule_type ENUM('sender','internal_author','keyword','thread_pattern','time_based') NOT NULL,
    trigger_condition TEXT,
    action ENUM('crear_tarea','escalar','notificar','asignar_automatico','solicitar_info','archivar') NOT NULL,
    urgency ENUM('baja','media','alta','critica') DEFAULT 'media',
    assigned_role VARCHAR(50),
    times_triggered INT DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    confidence FLOAT DEFAULT 0.0,
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (rule_type),
    INDEX idx_active (active),
    INDEX idx_confidence (confidence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS learning_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_type ENUM('initial','retrain','incremental') DEFAULT 'initial',
    emails_scanned INT,
    date_range_start DATE,
    date_range_end DATE,
    senders_identified INT,
    internal_authors_identified INT,
    rules_generated INT,
    sequences_identified INT,
    roles_analyzed INT,
    status ENUM('running','completed','failed','cancelled') DEFAULT 'running',
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    duration_minutes INT,
    created_by VARCHAR(255),
    INDEX idx_status (status),
    INDEX idx_type (session_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS keyword_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(255),
    category ENUM('urgencia','cotizacion','reclamo','seguimiento','aprobacion','otro'),
    weight FLOAT DEFAULT 1.0,
    times_found INT DEFAULT 0,
    accuracy_rate FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS file_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    archivo_id INT,
    reviewed_by VARCHAR(255),
    original_data JSON,
    corrected_data JSON,
    confidence_before FLOAT,
    was_correct BOOLEAN,
    reviewed_at DATETIME,
    FOREIGN KEY (archivo_id) REFERENCES archivos_adjuntos(id) ON DELETE CASCADE,
    INDEX idx_archivo (archivo_id),
    INDEX idx_was_correct (was_correct)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- DATOS INICIALES
-- ============================================

INSERT IGNORE INTO keyword_patterns (keyword, category, weight) VALUES
('urgente', 'urgencia', 2.0),
('emergencia', 'urgencia', 2.5),
('inmediato', 'urgencia', 2.0),
('hoy', 'urgencia', 1.5),
('ahora', 'urgencia', 1.8),
('asap', 'urgencia', 1.7),
('prioritario', 'urgencia', 1.5),
('importante', 'urgencia', 1.2),
('cotización', 'cotizacion', 1.5),
('presupuesto', 'cotizacion', 1.5),
('precio', 'cotizacion', 1.3),
('reclamo', 'reclamo', 2.0),
('problema', 'reclamo', 1.7),
('error', 'reclamo', 1.5),
('seguimiento', 'seguimiento', 1.0),
('estado', 'seguimiento', 0.8),
('avance', 'seguimiento', 0.8);