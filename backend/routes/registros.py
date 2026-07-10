from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func # IMPORTANTE: Importamos func para limpiar strings
from sqlalchemy.orm import Session
from core.database import get_db
import models, schemas
from services import ejecutar_recalculo_riesgo
from core.security import get_usuario_actual

router = APIRouter(dependencies=[Depends(get_usuario_actual)])

@router.post("/api/faltas/", response_model=schemas.FaltaResponse)
def registrar_falta(falta: schemas.FaltaCreate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.ID_Estudiante == falta.ID_Estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    
    # 1. Limpiamos la entrada del usuario (quitamos espacios extra y pasamos a minúsculas)
    materia_limpia = falta.Materia.strip().lower()

    # 2. Buscamos en la BD ignorando mayúsculas y espacios basura del JSON
    falta_existente = db.query(models.ControlFaltas).filter(
        models.ControlFaltas.ID_Estudiante == falta.ID_Estudiante,
        func.lower(func.trim(models.ControlFaltas.Materia)) == materia_limpia
    ).first()

    if falta_existente:
        falta_existente.Faltas_Acumuladas = falta.Faltas_Acumuladas # type: ignore
        falta_existente.Limite_Faltas = falta.Limite_Faltas # type: ignore
        registro_final = falta_existente
    else:
        falta.Materia = falta.Materia.strip() # Limpiamos antes de guardar nuevo
        nueva_falta = models.ControlFaltas(**falta.model_dump())
        db.add(nueva_falta)
        registro_final = nueva_falta

    db.commit()
    db.refresh(registro_final)
    
    ejecutar_recalculo_riesgo(falta.ID_Estudiante, db)
    return registro_final

@router.post("/api/historial/", response_model=schemas.HistorialResponse)
def registrar_nota(historial: schemas.HistorialCreate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.ID_Estudiante == historial.ID_Estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Error: Estudiante no existe.")
    
    # 1. Limpiamos la entrada del usuario
    materia_limpia = historial.Materia.strip().lower()

    # 2. Buscamos en la BD ignorando mayúsculas y espacios basura
    nota_existente = db.query(models.HistorialAcademico).filter(
        models.HistorialAcademico.ID_Estudiante == historial.ID_Estudiante,
        models.HistorialAcademico.Semestre == historial.Semestre,
        func.lower(func.trim(models.HistorialAcademico.Materia)) == materia_limpia
    ).first()

    if nota_existente:
        nota_existente.Nota_Definitiva = historial.Nota_Definitiva # type: ignore
        nota_existente.Condicion = historial.Condicion # type: ignore
        registro_final = nota_existente
    else:
        historial.Materia = historial.Materia.strip() # Limpiamos antes de guardar nuevo
        nuevo_registro = models.HistorialAcademico(**historial.model_dump())
        db.add(nuevo_registro)
        registro_final = nuevo_registro

    db.commit()
    db.refresh(registro_final)
    
    ejecutar_recalculo_riesgo(historial.ID_Estudiante, db)
    return registro_final