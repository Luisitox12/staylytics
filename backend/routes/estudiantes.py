from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from core.database import get_db
import models, schemas
from services import ejecutar_recalculo_riesgo

router = APIRouter()

@router.post("/api/estudiantes/", response_model=schemas.EstudianteResponse)
def crear_estudiante(estudiante: schemas.EstudianteCreate, db: Session = Depends(get_db)):
    db_estudiante = db.query(models.Estudiante).filter(models.Estudiante.Cedula == estudiante.Cedula).first()
    if db_estudiante:
        raise HTTPException(status_code=400, detail="Error: La cédula ya está registrada.")
    
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

@router.post("/api/estudiantes/{id_estudiante}/analisis", response_model=schemas.AnalisisRiesgoResponse)
def calcular_riesgo_estudiante(
    id_estudiante: int = Path(..., title="ID del estudiante a evaluar"),
    db: Session = Depends(get_db)
):
    resultado = ejecutar_recalculo_riesgo(id_estudiante, db)
    if not resultado:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado en la base de datos.")
    return resultado