from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
import models
from routes import estudiantes, registros, dashboard, auth

# Construcción de tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de STAYLYTICS - Arquitectura Modular")


origenes_permitidos = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://staylytics.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Registro de rutas
app.include_router(auth.router, tags=["Autenticación y Seguridad"])
app.include_router(estudiantes.router, tags=["Estudiantes y Análisis"])
app.include_router(registros.router, tags=["Control Académico (Notas y Faltas)"])
app.include_router(dashboard.router, tags=["Dashboard y Métricas"])