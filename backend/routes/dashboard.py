from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from core.database import get_db
import models, schemas
from core.security import get_usuario_actual

router = APIRouter(dependencies=[Depends(get_usuario_actual)])

@router.get("/api/dashboard/resumen", response_model=schemas.DashboardResumen)
def obtener_resumen_riesgo(carrera: Optional[str] = None, db: Session = Depends(get_db)):
    periodo_actual = "2026-1"

    subquery = db.query(
        func.max(models.AnalisisRiesgo.ID_Analisis).label("ultimo_analisis")
    ).group_by(models.AnalisisRiesgo.ID_Estudiante).subquery()

    query = db.query(
        models.AnalisisRiesgo.Nivel_Alerta,
        models.Estudiante.Carrera
    ).join(
        models.Estudiante, models.Estudiante.ID_Estudiante == models.AnalisisRiesgo.ID_Estudiante
    ).join(
        subquery, models.AnalisisRiesgo.ID_Analisis == subquery.c.ultimo_analisis
    ).filter(
        models.Estudiante.Ultimo_Periodo == periodo_actual
    )

    
    if carrera and carrera != "Todas":
        query = query.filter(models.Estudiante.Carrera == carrera)
    
    analisis_recientes = query.all()

    resumen = {"Bajo": 0, "Medio": 0, "Alto": 0, "Inactivo": 0}
    carreras_alto_riesgo = {}
    total_activos = 0

    for alerta, carrera_db in analisis_recientes:
        resumen[alerta] = resumen.get(alerta, 0) + 1
        if alerta != "Inactivo":
            total_activos += 1
        if alerta == "Alto":
            carreras_alto_riesgo[carrera_db] = carreras_alto_riesgo.get(carrera_db, 0) + 1

    
    if carrera and carrera != "Todas":
        mensaje = f"Análisis aislado para {carrera}. Total de alumnos regulares: {total_activos}."
        if carreras_alto_riesgo:
            mensaje += f" Casos de deserción inminente detectados: {carreras_alto_riesgo.get(carrera, 0)}."
    else:
        mensaje = "Análisis estable. No se detectan focos críticos de deserción."
        if carreras_alto_riesgo:
            carrera_critica = max(carreras_alto_riesgo, key=lambda k: carreras_alto_riesgo[k])
            cantidad_critica = carreras_alto_riesgo[carrera_critica]
            mensaje = f"Se analizaron {total_activos} perfiles regulares. El mayor foco de riesgo inminente se concentra en {carrera_critica} con {cantidad_critica} casos críticos."

    return {
        **resumen,
        "Total_Activos": total_activos,
        "Mensaje_Inteligente": mensaje,
        "Periodo_Actual": periodo_actual
    }