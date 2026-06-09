from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
import models, schemas

router = APIRouter()

@router.get("/api/dashboard/resumen", response_model=schemas.DashboardResumen)
def obtener_resumen_riesgo(db: Session = Depends(get_db)):
    # 1. SUBCONSULTA: Extraemos el ID del último análisis de cada estudiante
    # Al usar func.max() con el ID autoincremental, garantizamos obtener el evento más reciente.
    subquery = db.query(
        func.max(models.AnalisisRiesgo.ID_Analisis).label("ultimo_analisis")
    ).group_by(models.AnalisisRiesgo.ID_Estudiante).subquery()

    # 2. CONSULTA PRINCIPAL: Contamos los niveles de alerta cruzando datos solo con la subconsulta
    conteo = db.query(
        models.AnalisisRiesgo.Nivel_Alerta,
        func.count(models.AnalisisRiesgo.ID_Analisis).label("cantidad")
    ).join(
        subquery, models.AnalisisRiesgo.ID_Analisis == subquery.c.ultimo_analisis
    ).group_by(models.AnalisisRiesgo.Nivel_Alerta).all()

    # 3. CONSTRUCCIÓN DE RESPUESTA: Inicializamos en 0 para evitar errores si no hay datos
    resumen = {"Bajo": 0, "Medio": 0, "Alto": 0}
    
    # Mapeamos los resultados de la base de datos al diccionario
    for nivel, cantidad in conteo:
        resumen[nivel] = cantidad

    return resumen