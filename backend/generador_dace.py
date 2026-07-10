import json
import random

carreras = ["Ingeniería Informática", "Administración", "Odontología", "Medicina", "Contaduría"]
estratos = ["Alto", "Medio", "Bajo", "Muy Bajo"]


materias_por_carrera = {
    "Ingeniería Informática": ["Programación I", "Cálculo I", "Estructuras de Datos", "Bases de Datos I"],
    "Medicina": ["Anatomía Humana", "Fisiología I", "Histología", "Bioquímica Médica"],
    "Odontología": ["Anatomía Dental", "Materiales Dentales", "Histología Bucal", "Patología General"],
    "Administración": ["Contabilidad I", "Teoría Administrativa", "Microeconomía", "Gerencia Estratégica"],
    "Contaduría": ["Contabilidad de Costos", "Auditoría I", "Derecho Tributario", "Análisis Financiero"]
}

estudiantes_mil = []

for i in range(1, 1001):
    carrera = random.choice(carreras)
    
    es_regular = random.choices([True, False], weights=[0.85, 0.15])[0]
    
    notas = []
    faltas = []
    
    if es_regular:
        
        materias_alumno = random.sample(materias_por_carrera[carrera], k=3)
        
        for materia in materias_alumno:
            nota = round(random.uniform(5.0, 20.0), 1)
            notas.append({
                "Materia": materia,
                "Semestre": 1,
                "Nota_Definitiva": nota,
                "Condicion": "Regular" if nota >= 10 else "Aplazado"
            })
            
            acumuladas = random.randint(0, 7)
            faltas.append({
                "Materia": materia,
                "Faltas_Acumuladas": acumuladas,
                "Limite_Faltas": 5
            })

    estudiante = {
        "Cedula": f"V-{random.randint(20000000, 35000000)}",
        "Nombres": f"Estudiante_{i}",
        "Apellidos": "Prueba",
        "Edad": random.randint(18, 30),
        "Genero": random.choice(["M", "F"]),
        "Carrera": carrera,
        "Estrato_Socioeconomico": random.choice(estratos),
        "Situacion_Laboral": random.choice([True, False]),
        "Es_Regular": es_regular,
        "Ultimo_Periodo": "2026-1",
        "Notas": notas,
        "Faltas": faltas
    }
    estudiantes_mil.append(estudiante)


ruta_json = "../frontend/lote_1000.json"
with open(ruta_json, "w", encoding="utf-8") as f:
    json.dump(estudiantes_mil, f, ensure_ascii=False, indent=2)

print(f"Archivo relacional generado con éxito en {ruta_json} con asignaturas distribuidas por facultad.")