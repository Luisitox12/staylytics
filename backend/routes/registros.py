from fastapi import APIRouter, Depends, HTTPException
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
    
    nueva_falta = models.ControlFaltas(**falta.model_dump())
    db.add(nueva_falta)
    db.commit()
    db.refresh(nueva_falta)
    
    ejecutar_recalculo_riesgo(falta.ID_Estudiante, db)
    return nueva_falta

@router.post("/api/historial/", response_model=schemas.HistorialResponse)
def registrar_nota(historial: schemas.HistorialCreate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.ID_Estudiante == historial.ID_Estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Error: Estudiante no existe.")
    
    nuevo_registro = models.HistorialAcademico(**historial.model_dump())
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    ejecutar_recalculo_riesgo(historial.ID_Estudiante, db)
    return nuevo_registro