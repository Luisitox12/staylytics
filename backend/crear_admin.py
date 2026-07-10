import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from core.security import obtener_password_hash 
import models

def sembrar_administrador():
    db = SessionLocal()
    email_admin = "admin@staylytics.com"
    password_admin = "admin123"

    try:
        
        usuario_existente = db.query(models.UsuarioAdministrativo).filter(
            models.UsuarioAdministrativo.Correo == email_admin
        ).first()
        
        if not usuario_existente:
            print("⏳ Creando administrador maestro...")
            
            
            nuevo_admin = models.UsuarioAdministrativo(
                Nombre_Completo="Administrador Principal",
                Correo=email_admin,
                Password_Hash=obtener_password_hash(password_admin),
                Rol="Admin",
                Estatus=True
            )
            
            db.add(nuevo_admin)
            db.commit()
            print(f" ÉXITO: Administrador inyectado.")
            print(f" Usuario: {email_admin}")
            print(f" Clave: {password_admin}")
        else:
            print(" El administrador ya existe en la base de datos.")
            
    except Exception as e:
        print(f" Error crítico al inyectar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sembrar_administrador()