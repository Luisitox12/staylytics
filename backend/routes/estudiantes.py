from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlalchemy.orm import Session
from core.database import get_db
import models, schemas
from services import ejecutar_recalculo_riesgo
from core.security import get_usuario_actual

router = APIRouter(dependencies=[Depends(get_usuario_actual)])

@router.post("/api/estudiantes/", response_model=schemas.EstudianteResponse)
def crear_estudiante(estudiante: schemas.EstudianteCreate, db: Session = Depends(get_db)):
    db_estudiante = db.query(models.Estudiante).filter(models.Estudiante.Cedula == estudiante.Cedula).first()
    if db_estudiante:
        raise HTTPException(status_code=400, detail="Error: La cédula ya está registrada en el sistema.")
    
    nuevo_estudiante = models.Estudiante(**estudiante.model_dump())
    db.add(nuevo_estudiante)
    db.commit() 
    db.refresh(nuevo_estudiante) 
    return nuevo_estudiante


@router.get("/api/estudiantes/", response_model=list[schemas.EstudianteResponse])
def obtener_estudiantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    estudiantes = db.query(models.Estudiante).offset(skip).limit(limit).all()
    return estudiantes


@router.get("/api/estudiantes/{id_estudiante}", response_model=schemas.EstudianteResponse)
def obtener_estudiante_por_id(
    id_estudiante: int = Path(..., title="ID del estudiante a buscar"), 
    db: Session = Depends(get_db)
):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.ID_Estudiante == id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado en la base de datos.")
    return estudiante


# =========================================================
# NUEVO ENDPOINT: FILTRADO LONGITUDINAL POR RIESGO (DRILL-DOWN)
# =========================================================
@router.get("/api/estudiantes/riesgo/{nivel_alerta}", response_model=list[schemas.EstudianteResponse])
def obtener_estudiantes_por_riesgo(
    nivel_alerta: str = Path(..., title="Nivel de alerta a filtrar (Bajo, Medio, Alto)"),
    db: Session = Depends(get_db)
):
    """
    Extrae la lista de estudiantes cuyo ÚLTIMO cálculo de riesgo coincida 
    exactamente con el nivel de alerta solicitado. Evita la duplicidad histórica.
    """
    # 1. Normalización y Validación estricta del parámetro de entrada
    nivel_formateado = nivel_alerta.capitalize()
    if nivel_formateado not in ["Bajo", "Medio", "Alto"]:
        raise HTTPException(
            status_code=400, 
            detail="Parámetro inválido. Los niveles de alerta permitidos son: Bajo, Medio o Alto."
        )

    # 2. SUBCONSULTA: Identifica el ID del cálculo más reciente para cada estudiante
    subquery = db.query(
        func.max(models.AnalisisRiesgo.ID_Analisis).label("ultimo_analisis")
    ).group_by(models.AnalisisRiesgo.ID_Estudiante).subquery()

    # 3. CONSULTA MAESTRA (Doble JOIN):
    # Cruzamos Estudiantes con sus Riesgos, y luego filtramos usando solo los IDs de la subconsulta
    estudiantes = db.query(models.Estudiante).join(
        models.AnalisisRiesgo, models.Estudiante.ID_Estudiante == models.AnalisisRiesgo.ID_Estudiante
    ).join(
        subquery, models.AnalisisRiesgo.ID_Analisis == subquery.c.ultimo_analisis
    ).filter(
        models.AnalisisRiesgo.Nivel_Alerta == nivel_formateado
    ).all()

    return estudiantes