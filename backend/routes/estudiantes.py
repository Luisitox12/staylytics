from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlalchemy.orm import Session
from core.database import get_db
import models, schemas
from services import ejecutar_recalculo_riesgo
from core.security import get_usuario_actual
from typing import Optional

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

    analisis = ejecutar_recalculo_riesgo(nuevo_estudiante.ID_Estudiante, db) # type: ignore

    est_dict = {c.name: getattr(nuevo_estudiante, c.name) for c in nuevo_estudiante.__table__.columns}
    est_dict["Riesgo"] = analisis.Nivel_Alerta if analisis else "—"
    
    return est_dict


@router.get("/api/estudiantes/", response_model=list[schemas.EstudianteResponse])
def obtener_estudiantes(
    carrera: Optional[str] = None, 
    periodo: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 2000, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Estudiante)
    
    if carrera and carrera != "Todas":
        query = query.filter(models.Estudiante.Carrera == carrera)
    if periodo and periodo != "Todos":
        query = query.filter(models.Estudiante.Ultimo_Periodo == periodo)
        
    estudiantes = query.offset(skip).limit(limit).all()
    
    lista_respuesta = []
    for est in estudiantes:
        ultimo_riesgo = db.query(models.AnalisisRiesgo).filter(
            models.AnalisisRiesgo.ID_Estudiante == est.ID_Estudiante
        ).order_by(models.AnalisisRiesgo.ID_Analisis.desc()).first()
        
        est_dict = {c.name: getattr(est, c.name) for c in est.__table__.columns}
        est_dict["Riesgo"] = ultimo_riesgo.Nivel_Alerta if ultimo_riesgo else "—"
        lista_respuesta.append(est_dict)
        
    return lista_respuesta


@router.get("/api/estudiantes/{id_estudiante}", response_model=schemas.EstudianteResponse)
def obtener_estudiante_por_id(
    id_estudiante: int = Path(..., title="ID del estudiante a buscar"), 
    db: Session = Depends(get_db)
):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.ID_Estudiante == id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado en la base de datos.")
    
    ultimo_riesgo = db.query(models.AnalisisRiesgo).filter(
        models.AnalisisRiesgo.ID_Estudiante == id_estudiante
    ).order_by(models.AnalisisRiesgo.ID_Analisis.desc()).first()
    
    est_dict = {c.name: getattr(estudiante, c.name) for c in estudiante.__table__.columns}
    est_dict["Riesgo"] = ultimo_riesgo.Nivel_Alerta if ultimo_riesgo else "—"
    
    return est_dict


@router.get("/api/estudiantes/riesgo/{nivel_alerta}", response_model=list[schemas.EstudianteResponse])
def obtener_estudiantes_por_riesgo(
    nivel_alerta: str = Path(..., title="Nivel de alerta a filtrar (Bajo, Medio, Alto)"),
    db: Session = Depends(get_db)
):
    nivel_formateado = nivel_alerta.capitalize()
    if nivel_formateado not in ["Bajo", "Medio", "Alto"]:
        raise HTTPException(
            status_code=400, 
            detail="Parámetro inválido. Los niveles de alerta permitidos son: Bajo, Medio o Alto."
        )

    subquery = db.query(
        func.max(models.AnalisisRiesgo.ID_Analisis).label("ultimo_analisis")
    ).group_by(models.AnalisisRiesgo.ID_Estudiante).subquery()

    estudiantes = db.query(models.Estudiante).join(
        models.AnalisisRiesgo, models.Estudiante.ID_Estudiante == models.AnalisisRiesgo.ID_Estudiante
    ).join(
        subquery, models.AnalisisRiesgo.ID_Analisis == subquery.c.ultimo_analisis
    ).filter(
        models.AnalisisRiesgo.Nivel_Alerta == nivel_formateado
    ).all()

    return estudiantes


@router.get("/api/estudiantes/{id_estudiante}/expediente")
def obtener_expediente(id_estudiante: int, db: Session = Depends(get_db)):
    notas = db.query(models.HistorialAcademico).filter(models.HistorialAcademico.ID_Estudiante == id_estudiante).all()
    faltas = db.query(models.ControlFaltas).filter(models.ControlFaltas.ID_Estudiante == id_estudiante).all()
    
    return {
        "notas": [{col.name: getattr(nota, col.name) for col in nota.__table__.columns} for nota in notas],
        "faltas": [{col.name: getattr(falta, col.name) for col in falta.__table__.columns} for falta in faltas]
    }


@router.post("/api/estudiantes/dace-webhook")
def sincronizar_dace_lote(payload: list[schemas.EstudianteDaceSync], db: Session = Depends(get_db)):
    """
    WEBHOOK INDUSTRIAL: Procesa registros demográficos y académicos en masa.
    Modo relacional: Inyecta notas y faltas directamente desde el JSON central.
    """
    from services import ejecutar_recalculo_riesgo
    procesados = 0
    
    for est_data in payload:
        db_est = db.query(models.Estudiante).filter(models.Estudiante.Cedula == est_data.Cedula).first()
        
        notas_inbound = est_data.Notas
        faltas_inbound = est_data.Faltas
        est_dict = est_data.model_dump(exclude={"Notas", "Faltas"})
        
        if not db_est:
            db_est = models.Estudiante(**est_dict)
            db.add(db_est)
            db.commit()
            db.refresh(db_est)
        else:
            db_est.Ultimo_Periodo = est_data.Ultimo_Periodo  # type: ignore
            db_est.Es_Regular = est_data.Es_Regular          # type: ignore
            db_est.Carrera = est_data.Carrera                # type: ignore
            db.commit()

        # Limpieza de seguridad: borrar notas previas del mismo semestre para no duplicar
        db.query(models.HistorialAcademico).filter(
            models.HistorialAcademico.ID_Estudiante == db_est.ID_Estudiante,
            models.HistorialAcademico.Semestre == (est_data.Notas[0].Semestre if est_data.Notas else 1)
        ).delete()
        
        db.query(models.ControlFaltas).filter(models.ControlFaltas.ID_Estudiante == db_est.ID_Estudiante).delete()

        # Ingesta Transaccional de Notas
        if notas_inbound:
            for n in notas_inbound:
                nueva_nota = models.HistorialAcademico(
                    ID_Estudiante=db_est.ID_Estudiante,
                    Materia=n.Materia,
                    Semestre=n.Semestre,
                    Nota_Definitiva=n.Nota_Definitiva,
                    Condicion=n.Condicion
                )
                db.add(nueva_nota)

        # Ingesta Transaccional de Faltas
        if faltas_inbound:
            for f in faltas_inbound:
                nueva_falta = models.ControlFaltas(
                    ID_Estudiante=db_est.ID_Estudiante,
                    Materia=f.Materia,
                    Faltas_Acumuladas=f.Faltas_Acumuladas,
                    Limite_Faltas=f.Limite_Faltas
                )
                db.add(nueva_falta)
            
        db.commit()

        ejecutar_recalculo_riesgo(db_est.ID_Estudiante, db) # type: ignore
        procesados += 1

    return {"mensaje": f"Sincronización DACE Relacional completa. {procesados} expedientes integrados con notas y faltas."}