#!/usr/bin/env python3
"""
Base de datos PostgreSQL para usuarios - Compatible con Render.com
"""

import os
import json
from datetime import datetime
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    # Fallback a SQLite para desarrollo local
    import sqlite3

class UserDatabase:
    def __init__(self):
        self.use_postgres = POSTGRES_AVAILABLE and os.environ.get('DATABASE_URL')
        
        if self.use_postgres:
            self.database_url = os.environ.get('DATABASE_URL')
            print("🐘 Usando PostgreSQL (Render)")
        else:
            self.db_path = "users.db"
            print("🗃️ Usando SQLite (desarrollo local)")
        
        self.init_database()
    
    def get_connection(self):
        """Obtiene conexión a la base de datos"""
        if self.use_postgres:
            return psycopg2.connect(self.database_url)
        else:
            return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            # PostgreSQL syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS communications (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(255) NOT NULL,
                    mensaje TEXT NOT NULL,
                    destinatario VARCHAR(255) NOT NULL,
                    prioridad VARCHAR(50) NOT NULL DEFAULT 'normal',
                    remitente VARCHAR(255) NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hora VARCHAR(10) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            # SQLite syntax (desarrollo local)
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
            ('usuario1', 'pass123', 'user'),
            ('usuario2', 'pass456', 'user'),
            ('gerente', 'gerente123', 'manager')
        ]
        
        for username, password, role in default_users:
            try:
                if self.use_postgres:
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) ON CONFLICT (username) DO NOTHING",
                        (username, password, role)
                    )
                else:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                        (username, password, role)
                    )
            except Exception as e:
                print(f"Error insertando usuario {username}: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    
    def authenticate_user(self, username, password):
        """Autentica un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute("SELECT username, role FROM users WHERE username = %s AND password = %s", (username, password))
        else:
            cursor.execute("SELECT username, role FROM users WHERE username = ? AND password = ?", (username, password))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'username': result[0],
                'role': result[1]
            }
        return None
    
    def get_all_users(self):
        """Obtiene todos los usuarios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY username")
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'role': row[2],
                'created_at': str(row[3]) if row[3] else None
            })
        
        conn.close()
        return users
    
    def add_user(self, username, password, role='user'):
        """Agrega un nuevo usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.use_postgres:
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING id",
                    (username, password, role)
                )
                user_id = cursor.fetchone()[0]
            else:
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password, role)
                )
                user_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return user_id
        except Exception as e:
            conn.close()
            raise e
    
    def update_user(self, user_id, username=None, password=None, role=None):
        """Actualiza un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if username:
            updates.append("username = %s" if self.use_postgres else "username = ?")
            params.append(username)
        if password:
            updates.append("password = %s" if self.use_postgres else "password = ?")
            params.append(password)
        if role:
            updates.append("role = %s" if self.use_postgres else "role = ?")
            params.append(role)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = {'%s' if self.use_postgres else '?'}"
            cursor.execute(query, params)
            
            conn.commit()
        
        conn.close()
    
    def delete_user(self, user_id):
        """Elimina un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
    
    def add_communication(self, titulo, mensaje, destinatario, prioridad, remitente, hora):
        """Agrega una nueva comunicación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute(
                "INSERT INTO communications (titulo, mensaje, destinatario, prioridad, remitente, hora) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (titulo, mensaje, destinatario, prioridad, remitente, hora)
            )
            comm_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                "INSERT INTO communications (titulo, mensaje, destinatario, prioridad, remitente, hora) VALUES (?, ?, ?, ?, ?, ?)",
                (titulo, mensaje, destinatario, prioridad, remitente, hora)
            )
            comm_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return comm_id
    
    def get_communications(self, limit=50):
        """Obtiene todas las comunicaciones"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, titulo, mensaje, destinatario, prioridad, remitente, fecha, hora FROM communications ORDER BY fecha DESC LIMIT %s" if self.use_postgres else "SELECT id, titulo, mensaje, destinatario, prioridad, remitente, fecha, hora FROM communications ORDER BY fecha DESC LIMIT ?",
            (limit,)
        )
        
        communications = []
        for row in cursor.fetchall():
            communications.append({
                'id': row[0],
                'titulo': row[1],
                'mensaje': row[2],
                'destinatario': row[3],
                'prioridad': row[4],
                'remitente': row[5],
                'fecha': str(row[6]) if row[6] else None,
                'hora': row[7]
            })
        
        conn.close()
        return communications
    
    def get_user_communications(self, username, limit=50):
        """Obtiene comunicaciones para un usuario específico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute(
                "SELECT id, titulo, mensaje, destinatario, prioridad, remitente, fecha, hora FROM communications WHERE destinatario = %s OR destinatario = 'todos' ORDER BY fecha DESC LIMIT %s",
                (username, limit)
            )
        else:
            cursor.execute(
                "SELECT id, titulo, mensaje, destinatario, prioridad, remitente, fecha, hora FROM communications WHERE destinatario = ? OR destinatario = 'todos' ORDER BY fecha DESC LIMIT ?",
                (username, limit)
            )
        
        communications = []
        for row in cursor.fetchall():
            communications.append({
                'id': row[0],
                'titulo': row[1],
                'mensaje': row[2],
                'destinatario': row[3],
                'prioridad': row[4],
                'remitente': row[5],
                'fecha': str(row[6]) if row[6] else None,
                'hora': row[7]
            })
        
        conn.close()
        return communications
    
    def delete_communication(self, comm_id):
        """Elimina una comunicación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute("DELETE FROM communications WHERE id = %s", (comm_id,))
        else:
            cursor.execute("DELETE FROM communications WHERE id = ?", (comm_id,))
        
        conn.commit()
        conn.close()