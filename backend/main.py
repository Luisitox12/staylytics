from fastapi import FastAPI
from core.database import engine
import models
from routes import estudiantes, registros, dashboard

# Construcción de tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de STAYLYTICS - Arquitectura Modular")

# Registro de rutas
app.include_router(estudiantes.router, tags=["Estudiantes y Análisis"])
app.include_router(registros.router, tags=["Control Académico (Notas y Faltas)"])
app.include_router(dashboard.router, tags=["Dashboard y Métricas"])