from pydantic import BaseModel,EmailStr
from typing import Optional

# 1. ESQUEMA BASE
class EstudianteBase(BaseModel):
    Cedula: str
    Nombres: str
    Apellidos: str
    Edad: int
    Genero: str
    Carrera: str
    Estrato_Socioeconomico: str
    Situacion_Laboral: bool
    Es_Regular: bool = True
    Ultimo_Periodo: Optional[str] = None

class EstudianteCreate(EstudianteBase):
    pass 


class EstudianteResponse(EstudianteBase):
    ID_Estudiante: int
    Estatus_Actual: str
    Riesgo: str = "—"

    class Config:
        from_attributes = True

class FaltaCreate(BaseModel):
    ID_Estudiante: int
    Materia: str
    Faltas_Acumuladas: int
    Limite_Faltas: int

class FaltaResponse(BaseModel):
    ID_Falta: int
    ID_Estudiante: int
    Materia: str
    Faltas_Acumuladas: int
    Limite_Faltas: int

    class Config:
        from_attributes = True

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

class DashboardResumen(BaseModel):
    Bajo: int = 0
    Medio: int = 0
    Alto: int = 0
    Inactivo: int = 0
    Total_Activos: int = 0
    Mensaje_Inteligente: str = "Sin datos suficientes."
    Periodo_Actual: str = "2026-1"

class Token(BaseModel):
    access_token: str
    token_type: str

class UsuarioCreate(BaseModel):
    Nombre_Completo: str
    Correo: str
    Password: str
    Rol: str = "Coordinador"


class NotaDaceInbound(BaseModel):
    Materia: str
    Semestre: int
    Nota_Definitiva: float
    Condicion: str = "Regular"

class FaltaDaceInbound(BaseModel):
    Materia: str
    Faltas_Acumuladas: int
    Limite_Faltas: int


class EstudianteDaceSync(BaseModel):
    Cedula: str
    Nombres: str
    Apellidos: str
    Edad: int
    Genero: str
    Carrera: str
    Estrato_Socioeconomico: str
    Situacion_Laboral: bool
    Es_Regular: bool = True
    Ultimo_Periodo: str
    Notas: list[NotaDaceInbound] = []
    Faltas: list[FaltaDaceInbound] = []