from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
import models
from routes import estudiantes, registros, dashboard, auth

# Construcción de tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de STAYLYTICS - Arquitectura Modular")

# =========================================================
# CONFIGURACIÓN DE CORS (Defensa del Perímetro)
# =========================================================
# Define estrictamente quién tiene permiso de consumir esta API.
# Ajusta los puertos según lo que use tu frontend (3000 para React/Next, 5173 para Vite).
origenes_permitidos = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"], # Fundamental permitir todo aquí para el futuro token de Autorización
)

# Registro de rutas
app.include_router(auth.router, tags=["Autenticación y Seguridad"])
app.include_router(estudiantes.router, tags=["Estudiantes y Análisis"])
app.include_router(registros.router, tags=["Control Académico (Notas y Faltas)"])
app.include_router(dashboard.router, tags=["Dashboard y Métricas"])