from sqlalchemy.orm import Session
import models

def ejecutar_recalculo_riesgo(id_estudiante: int, db: Session):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.ID_Estudiante == id_estudiante).first()
    if not estudiante:
        return None

    # MÓDULO 1: Socioeconómico
    factor_socio = 0
    if bool(estudiante.Situacion_Laboral):
        factor_socio += 50
    if estudiante.Estrato_Socioeconomico.lower() in ["bajo", "muy bajo"]:
        factor_socio += 50

    # MÓDULO 2: Asistencia
    faltas = db.query(models.ControlFaltas).filter(models.ControlFaltas.ID_Estudiante == id_estudiante).all()
    factor_asistencia = 0
    if faltas:
        peor_porcentaje = max([((float(falta.Faltas_Acumuladas) / float(falta.Limite_Faltas)) * 100) for falta in faltas])
        factor_asistencia = min(peor_porcentaje, 100.0)

    # MÓDULO 3: Académico
    historial = db.query(models.HistorialAcademico).filter(models.HistorialAcademico.ID_Estudiante == id_estudiante).all()
    factor_academico = 0
    
    if historial:
        materias_totales = len(historial)
        materias_reprobadas = 0
        suma_notas_20 = 0
        
        for registro in historial:
            nota = float(registro.Nota_Definitiva)
            suma_notas_20 += nota
            if nota < 10.0: 
                materias_reprobadas += 1
        
        promedio_escala_20 = suma_notas_20 / materias_totales
        promedio_oficial_10 = promedio_escala_20 / 2.0
        
        sub_promedio = ((10.0 - promedio_oficial_10) / 10.0) * 100
        sub_reprobacion = (materias_reprobadas / materias_totales) * 100
        factor_academico = (sub_promedio * 0.30) + (sub_reprobacion * 0.70)

    # FUSIÓN
    riesgo_total = (factor_asistencia * 0.45) + (factor_academico * 0.35) + (factor_socio * 0.20)
    puntuacion_final = int(round(riesgo_total))

    if puntuacion_final <= 30:
        alerta = "Bajo"
    elif puntuacion_final <= 70:
        alerta = "Medio"
    else:
        alerta = "Alto"

    nuevo_analisis = models.AnalisisRiesgo(
        ID_Estudiante=id_estudiante,
        Puntuacion_Riesgo=puntuacion_final,
        Nivel_Alerta=alerta
    )
    db.add(nuevo_analisis)
    db.commit()
    db.refresh(nuevo_analisis)
    
    return nuevo_analisis