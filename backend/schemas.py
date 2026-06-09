from pydantic import BaseModel

# 1. ESQUEMA BASE
class EstudianteBase(BaseModel):
    Cedula: str
    Nombres: str
    Apellidos: str
    Edad: int
    Estrato_Socioeconomico: str
    Situacion_Laboral: bool

# 2. ESQUEMA DE CREACIÓN
class EstudianteCreate(EstudianteBase):
    pass 

# 3. ESQUEMAS DE RESPUESTA BLINDADOS
class EstudianteResponse(EstudianteBase):
    ID_Estudiante: int
    Estatus_Actual: str

    class Config:
        from_attributes = True

class FaltaCreate(BaseModel):
    ID_Estudiante: int
    Materia: str
    Faltas_Acumuladas: int
    Limite_Faltas: int

class AnalisisRiesgoResponse(BaseModel):
    ID_Analisis: int
    Puntuacion_Riesgo: int
    Nivel_Alerta: str

    class Config:
        from_attributes = True

class HistorialCreate(BaseModel):
    ID_Estudiante: int
    Materia: str
    Semestre: int
    Nota_Definitiva: float
    Condicion: str = "Regular"

class HistorialResponse(BaseModel):
    ID_Historial: int 
    ID_Estudiante: int
    Materia: str
    Semestre: int
    Nota_Definitiva: float
    Condicion: str

    class Config:
        from_attributes = True