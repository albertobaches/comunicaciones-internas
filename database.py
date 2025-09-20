#!/usr/bin/env python3
"""
Base de datos SQLite para usuarios - Sincronización real entre navegadores
"""

import sqlite3
import json
import os
from datetime import datetime

class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla de comunicados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                destinatario TEXT NOT NULL,
                prioridad TEXT NOT NULL DEFAULT 'normal',
                remitente TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hora TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar usuarios por defecto si no existen
        default_users = [
            ('admin', 'admin123', 'admin'),
            ('usuario1', 'pass123', 'user')
        ]
        
        for username, password, role in default_users:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, password, role))
        
        conn.commit()
        conn.close()
        print(f"✅ Base de datos inicializada: {self.db_path}")
    
    def get_all_users(self):
        """Obtiene todos los usuarios de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password, role, created_at, updated_at
            FROM users ORDER BY id
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'role': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        conn.close()
        return users
    
    def add_user(self, username, password, role='user'):
        """Añade un nuevo usuario a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, password, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Usuario añadido: {username} (ID: {user_id})")
            return {'success': True, 'id': user_id, 'message': f'Usuario {username} creado'}
            
        except sqlite3.IntegrityError:
            conn.close()
            return {'success': False, 'message': f'El usuario {username} ya existe'}
    
    def update_user(self, user_id, username=None, password=None, role=None):
        """Actualiza un usuario existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if username is not None and username.strip() != '':
            updates.append("username = ?")
            params.append(username)
        if password is not None and password.strip() != '':
            updates.append("password = ?")
            params.append(password)
        if role is not None and role.strip() != '':
            updates.append("role = ?")
            params.append(role)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Usuario actualizado'}
            else:
                conn.close()
                return {'success': False, 'message': 'Usuario no encontrado'}
        
        conn.close()
        return {'success': False, 'message': 'No hay datos para actualizar'}
    
    def delete_user(self, user_id):
        """Elimina un usuario de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Usuario eliminado'}
        else:
            conn.close()
            return {'success': False, 'message': 'Usuario no encontrado'}
    
    def authenticate_user(self, username, password):
        """Autentica un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, role FROM users 
            WHERE username = ? AND password = ?
        ''', (username, password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2]
                }
            }
        else:
            return {'success': False, 'message': 'Credenciales incorrectas'}
    
    def add_communication(self, titulo, mensaje, destinatario, prioridad, remitente, hora):
        """Añade un nuevo comunicado a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO communications (titulo, mensaje, destinatario, prioridad, remitente, hora)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (titulo, mensaje, destinatario, prioridad, remitente, hora))
            
            comm_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Comunicado añadido: {titulo} (ID: {comm_id})")
            return {'success': True, 'id': comm_id, 'message': 'Comunicado enviado exitosamente'}
            
        except Exception as e:
            conn.close()
            print(f"❌ Error al guardar comunicado: {e}")
            return {'success': False, 'message': f'Error al guardar comunicado: {str(e)}'}
    
    def get_communications_by_sender(self, remitente):
        """Obtiene todos los comunicados enviados por un usuario específico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, titulo, mensaje, destinatario, prioridad, remitente, fecha, hora, created_at
            FROM communications 
            WHERE remitente = ?
            ORDER BY created_at DESC
        ''', (remitente,))
        
        communications = []
        for row in cursor.fetchall():
            communications.append({
                'id': row[0],
                'titulo': row[1],
                'mensaje': row[2],
                'destinatario': row[3],
                'prioridad': row[4],
                'remitente': row[5],
                'fecha': row[6],
                'hora': row[7],
                'created_at': row[8]
            })
        
        conn.close()
        return communications
    
    def get_all_communications(self):
        """Obtiene todos los comunicados de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, titulo, mensaje, destinatario, prioridad, remitente, fecha, hora, created_at
            FROM communications 
            ORDER BY created_at DESC
        ''')
        
        communications = []
        for row in cursor.fetchall():
            communications.append({
                'id': row[0],
                'titulo': row[1],
                'mensaje': row[2],
                'destinatario': row[3],
                'prioridad': row[4],
                'remitente': row[5],
                'fecha': row[6],
                'hora': row[7],
                'created_at': row[8]
            })
        
        conn.close()
        return communications
    
    def delete_communication(self, comm_id, remitente):
        """Elimina un comunicado específico si pertenece al remitente o si remitente es None (admin)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if remitente is None:
                # Administrador puede eliminar cualquier comunicado
                cursor.execute('''
                    SELECT id FROM communications WHERE id = ?
                ''', (comm_id,))
                
                if cursor.fetchone() is None:
                    conn.close()
                    return {'success': False, 'message': 'Comunicado no encontrado'}
                
                cursor.execute('''
                    DELETE FROM communications WHERE id = ?
                ''', (comm_id,))
            else:
                # Usuario regular solo puede eliminar sus propios comunicados
                cursor.execute('''
                    SELECT id FROM communications 
                    WHERE id = ? AND remitente = ?
                ''', (comm_id, remitente))
                
                if cursor.fetchone() is None:
                    conn.close()
                    return {'success': False, 'message': 'Comunicado no encontrado o no autorizado'}
                
                cursor.execute('''
                    DELETE FROM communications 
                    WHERE id = ? AND remitente = ?
                ''', (comm_id, remitente))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Comunicado eliminado: ID {comm_id}")
            return {'success': True, 'message': 'Comunicado eliminado exitosamente'}
            
        except Exception as e:
            conn.close()
            print(f"❌ Error al eliminar comunicado: {e}")
            return {'success': False, 'message': f'Error al eliminar comunicado: {str(e)}'}

    def get_communications_by_recipient(self, destinatario):
        """Obtiene todos los comunicados recibidos por un usuario específico (bandeja de entrada)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, titulo, mensaje, destinatario, prioridad, remitente, fecha, hora, created_at
            FROM communications 
            WHERE destinatario = ? OR destinatario = 'todos'
            ORDER BY created_at DESC
        ''', (destinatario,))
        
        communications = []
        for row in cursor.fetchall():
            communications.append({
                'id': row[0],
                'titulo': row[1],
                'mensaje': row[2],
                'destinatario': row[3],
                'prioridad': row[4],
                'remitente': row[5],
                'fecha': row[6],
                'hora': row[7],
                'created_at': row[8]
            })
        
        conn.close()
        return communications

if __name__ == "__main__":
    # Prueba de la base de datos
    db = UserDatabase()
    print("🔍 Usuarios en la base de datos:")
    users = db.get_all_users()
    for user in users:
        print(f"  - {user['username']} ({user['role']}) - ID: {user['id']}")