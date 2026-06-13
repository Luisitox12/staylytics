from sqlalchemy.orm import Session
import models

def get_val(col):
    """Extrae el valor numérico puro de un objeto ColumnElement o lo retorna si ya es número."""
    # Si es una columna de SQLAlchemy, usamos ._value() o lo casteamos.
    # Para evitar errores, simplemente forzamos a float o int la representación string
    # o el valor directo si SQLAlchemy ya lo resolvió.
    try:
        if hasattr(col, 'expression'):
            # En SQLAlchemy 2.0 a veces los valores vienen envueltos
            return float(str(col))
        return float(col)
    except:
        return 0.0

def ejecutar_recalculo_riesgo(id_estudiante: int, db: Session):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.ID_Estudiante == id_estudiante).first()
    if not estudiante:
        return None

    # MÓDULO 1: Socioeconómico
    factor_socio = 0.0
    if estudiante.Situacion_Laboral == True:  # type: ignore
        factor_socio += 50.0
    if str(estudiante.Estrato_Socioeconomico).lower() in ["bajo", "muy bajo"]:
        factor_socio += 50.0

    # MÓDULO 2: Asistencia
    faltas = db.query(models.ControlFaltas).filter(models.ControlFaltas.ID_Estudiante == id_estudiante).all()
    factor_asistencia = 0.0
    if faltas:
        porcentajes = []
        for f in faltas:
            # Extraemos los valores puros
            acum = get_val(f.Faltas_Acumuladas)
            lim = get_val(f.Limite_Faltas)
            limite_seguro = lim if lim > 0 else 1.0
            porcentajes.append((acum / limite_seguro) * 100.0)
        factor_asistencia = min(max(porcentajes), 100.0)

    # MÓDULO 3: Académico
    historial = db.query(models.HistorialAcademico).filter(models.HistorialAcademico.ID_Estudiante == id_estudiante).all()
    factor_academico = 0.0
    if historial:
        materias_totales = len(historial)
        materias_reprobadas = 0
        suma_notas_20 = 0.0
        
        for registro in historial:
            # Extraemos el valor puro
            nota = get_val(registro.Nota_Definitiva)
            suma_notas_20 += nota
            if nota < 10.0: 
                materias_reprobadas += 1
        
        promedio_escala_20 = suma_notas_20 / float(materias_totales)
        promedio_oficial_10 = promedio_escala_20 / 2.0
        
        sub_promedio = ((10.0 - promedio_oficial_10) / 10.0) * 100.0
        sub_reprobacion = (float(materias_reprobadas) / float(materias_totales)) * 100.0
        factor_academico = (sub_promedio * 0.30) + (sub_reprobacion * 0.70)

    # --- MOTOR DE PESOS DINÁMICOS ---
    peso_socio = 0.20
    peso_asistencia = 0.45
    peso_academico = 0.35

    tiene_faltas = len(faltas) > 0
    tiene_historial = len(historial) > 0

    if not tiene_faltas and tiene_historial:
        peso_academico += peso_asistencia
        peso_asistencia = 0.0
    elif tiene_faltas and not tiene_historial:
        peso_asistencia += peso_academico
        peso_academico = 0.0
    elif not tiene_faltas and not tiene_historial:
        peso_socio = 1.0
        peso_asistencia = 0.0
        peso_academico = 0.0

    # FUSIÓN INTELIGENTE
    riesgo_total = (factor_asistencia * peso_asistencia) + (factor_academico * peso_academico) + (factor_socio * peso_socio)
    puntuacion_final = int(round(riesgo_total))

    # CLASIFICACIÓN
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