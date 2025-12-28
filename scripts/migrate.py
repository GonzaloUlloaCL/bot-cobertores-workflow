"""
Script de migración usando SQLAlchemy (ya instalado)
Agrega tablas de aprendizaje a bot_cobertores existente
"""

import sys
import os
from pathlib import Path

# Agregar root del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Ejecuta migración SQL"""
    
    # Construir connection string
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'bot_cobertores')
    
    connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print(f"🔗 Conectando a: {db_host}:{db_port}/{db_name}")
    
    try:
        engine = create_engine(connection_string, echo=False)
        
        # Leer archivo SQL
        sql_file = project_root / 'migration_add_learning.sql'
        
        if not sql_file.exists():
            print(f"❌ No se encuentra: {sql_file}")
            print("💡 Coloca migration_add_learning.sql en la raíz del proyecto")
            return False
        
        print(f"📄 Leyendo: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Separar statements (evitar problemas con delimiters)
        statements = []
        current_statement = []
        in_delimiter = False
        
        for line in sql_content.split('\n'):
            line_stripped = line.strip()
            
            # Skip comments
            if line_stripped.startswith('--') or line_stripped.startswith('/*'):
                continue
            
            # Handle DELIMITER changes
            if 'DELIMITER' in line_stripped.upper():
                if '//' in line_stripped:
                    in_delimiter = True
                else:
                    in_delimiter = False
                continue
            
            # Accumulate statement
            if line_stripped:
                current_statement.append(line)
            
            # End of statement
            if not in_delimiter and line_stripped.endswith(';'):
                stmt = '\n'.join(current_statement)
                if stmt.strip():
                    statements.append(stmt)
                current_statement = []
        
        print(f"📊 Ejecutando {len(statements)} statements...")
        
        with engine.connect() as conn:
            executed = 0
            errors = 0
            
            for idx, statement in enumerate(statements, 1):
                try:
                    # Skip empty or comment-only statements
                    stmt_clean = statement.strip()
                    if not stmt_clean or stmt_clean.startswith('--'):
                        continue
                    
                    conn.execute(text(statement))
                    executed += 1
                    
                    if executed % 5 == 0:
                        print(f"   ✓ Ejecutados: {executed}/{len(statements)}")
                
                except Exception as e:
                    error_msg = str(e)
                    
                    # Ignorar errores de "ya existe"
                    if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                        print(f"   ⚠️ Statement {idx}: Ya existe (ignorado)")
                        continue
                    
                    errors += 1
                    print(f"   ❌ Error en statement {idx}:")
                    print(f"      {error_msg}")
                    
                    # Mostrar statement problemático
                    if len(statement) < 200:
                        print(f"      SQL: {statement[:200]}...")
            
            conn.commit()
        
        print("\n" + "="*60)
        if errors == 0:
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        else:
            print(f"⚠️ MIGRACIÓN COMPLETADA CON {errors} ERRORES")
        print("="*60)
        print(f"📊 Statements ejecutados: {executed}")
        print(f"❌ Errores: {errors}")
        print("="*60)
        
        # Verificar tablas creadas
        print("\n🔍 Verificando estructura...")
        verify_migration(engine)
        
        return errors == 0
    
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {str(e)}")
        return False


def verify_migration(engine):
    """Verifica que las tablas se crearon correctamente"""
    
    expected_tables = [
        'sender_profiles',
        'internal_author_profiles', 
        'thread_patterns',
        'learned_rules',
        'learning_sessions',
        'keyword_patterns',
        'file_reviews'
    ]
    
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        existing_tables = [row[0] for row in result]
        
        print("\n📋 TABLAS EN BASE DE DATOS:")
        print("-" * 60)
        
        for table in existing_tables:
            if table in expected_tables:
                emoji = "🆕"
            else:
                emoji = "📦"
            print(f"{emoji} {table}")
        
        print("-" * 60)
        
        # Check new tables
        missing = set(expected_tables) - set(existing_tables)
        if missing:
            print(f"\n⚠️ TABLAS FALTANTES: {', '.join(missing)}")
        else:
            print(f"\n✅ Todas las tablas de aprendizaje creadas ({len(expected_tables)})")
        
        # Check modified columns in existing tables
        print("\n🔧 Verificando columnas agregadas a tablas existentes...")
        
        try:
            result = conn.execute(text("DESCRIBE tareas"))
            columns = [row[0] for row in result]
            
            new_columns = [
                'confianza_clasificacion',
                'metodo_clasificacion', 
                'requiere_revision_humana',
                'razon_revision'
            ]
            
            for col in new_columns:
                if col in columns:
                    print(f"   ✓ tareas.{col}")
                else:
                    print(f"   ❌ tareas.{col} - FALTA")
        
        except Exception as e:
            print(f"   ⚠️ No se pudo verificar tabla tareas: {e}")


if __name__ == "__main__":
    print("="*60)
    print("🚀 MIGRACIÓN: Sistema de Aprendizaje")
    print("="*60)
    print()
    
    success = run_migration()
    
    if success:
        print("\n✅ Migración exitosa. Siguiente paso:")
        print("   python src/learning/historical_scraper.py --months 3")
        sys.exit(0)
    else:
        print("\n❌ Migración falló. Revisa los errores arriba.")
        sys.exit(1)