#!/usr/bin/env python3
"""
Servidor de desarrollo con auto-reload
Reinicia automáticamente cuando detecta cambios en archivos Python
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class DevServer:
    def __init__(self):
        self.process = None
        self.files_to_watch = [
            'server.py',
            'database.py'
        ]
        self.last_modified = {}
        
    def get_file_mtime(self, filepath):
        """Obtener tiempo de modificación de archivo"""
        try:
            return os.path.getmtime(filepath)
        except FileNotFoundError:
            return 0
    
    def check_for_changes(self):
        """Verificar si algún archivo ha cambiado"""
        for filepath in self.files_to_watch:
            current_mtime = self.get_file_mtime(filepath)
            
            if filepath not in self.last_modified:
                self.last_modified[filepath] = current_mtime
                continue
                
            if current_mtime > self.last_modified[filepath]:
                self.last_modified[filepath] = current_mtime
                return True
                
        return False
    
    def start_server(self):
        """Iniciar el servidor"""
        if self.process:
            self.stop_server()
            
        print("🚀 Iniciando servidor...")
        self.process = subprocess.Popen([
            sys.executable, 'server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Mostrar las primeras líneas de output
        for _ in range(5):
            line = self.process.stdout.readline()
            if line:
                print(line.strip())
            else:
                break
    
    def stop_server(self):
        """Detener el servidor"""
        if self.process:
            print("🛑 Deteniendo servidor...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
    
    def run(self):
        """Ejecutar el servidor de desarrollo"""
        print("🔧 Servidor de desarrollo iniciado")
        print("📁 Monitoreando archivos:", ', '.join(self.files_to_watch))
        print("⚡ Los cambios se aplicarán automáticamente")
        print("🛑 Presiona Ctrl+C para detener\n")
        
        # Inicializar timestamps
        for filepath in self.files_to_watch:
            self.last_modified[filepath] = self.get_file_mtime(filepath)
        
        # Iniciar servidor
        self.start_server()
        
        try:
            while True:
                time.sleep(1)
                
                if self.check_for_changes():
                    print("\n🔄 Cambios detectados - Reiniciando servidor...")
                    self.start_server()
                    
                # Verificar si el proceso sigue vivo
                if self.process and self.process.poll() is not None:
                    print("❌ El servidor se detuvo inesperadamente")
                    self.start_server()
                    
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servidor de desarrollo...")
            self.stop_server()
            print("✅ Servidor detenido")

if __name__ == '__main__':
    dev_server = DevServer()
    dev_server.run()