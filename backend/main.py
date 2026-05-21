from fastapi import FastAPI

app = FastAPI(title="API de STAYLYTICS")

@app.get("/")
def ruta_raiz():
    return {"mensaje": "El motor de STAYLYTICS está en línea"}

@app.get("/api/estudiantes/prueba")
def obtener_estudiante_prueba():
    return {
        "id_estudiante": 1,
        "nombres": "Luis",
        "riesgo": "Alto",
        "probabilidad_desercion": 85.5
    }