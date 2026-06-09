from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base 

# 1. ENTIDAD DE SEGURIDAD
class UsuarioAdministrativo(Base):
    __tablename__ = "Usuarios_Administrativos"
    ID_Usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Nombre_Completo = Column(String(100), nullable=False)
    Correo = Column(String(100), unique=True, nullable=False)
    Password_Hash = Column(String(255), nullable=False)
    Rol = Column(String(50), nullable=False)
    Estatus = Column(Boolean, default=True)
    Fecha_Registro = Column(TIMESTAMP, server_default=func.now())

# 2. ENTIDAD NÚCLEO (Estudiantes)
class Estudiante(Base):
    __tablename__ = "Estudiantes"
    ID_Estudiante = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Cedula = Column(String(15), unique=True, nullable=False)
    Nombres = Column(String(50), nullable=False)
    Apellidos = Column(String(50), nullable=False)
    Edad = Column(Integer, nullable=False)
    Estrato_Socioeconomico = Column(String(20), nullable=False)
    Situacion_Laboral = Column(Boolean, nullable=False)
    Estatus_Actual = Column(String(20), default='Activo')

    historial = relationship("HistorialAcademico", back_populates="estudiante", cascade="all, delete-orphan")
    faltas = relationship("ControlFaltas", back_populates="estudiante", cascade="all, delete-orphan")
    riesgos = relationship("AnalisisRiesgo", back_populates="estudiante", cascade="all, delete-orphan")
    deserciones = relationship("RegistroDesercion", back_populates="estudiante", cascade="all, delete-orphan")

# 3. ENTIDADES DINÁMICAS
class HistorialAcademico(Base):
    __tablename__ = "Historial_Academico"
    ID_Historial = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_Estudiante = Column(Integer, ForeignKey("Estudiantes.ID_Estudiante", ondelete="CASCADE"), nullable=False)
    Materia = Column(String(50), nullable=False)
    Semestre = Column(Integer, nullable=False)
    Nota_Definitiva = Column(Numeric(4, 2))
    Condicion = Column(String(20), nullable=False)
    estudiante = relationship("Estudiante", back_populates="historial")

class ControlFaltas(Base):
    __tablename__ = "Control_Faltas"
    ID_Falta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_Estudiante = Column(Integer, ForeignKey("Estudiantes.ID_Estudiante", ondelete="CASCADE"), nullable=False)
    Materia = Column(String(50), nullable=False)
    Faltas_Acumuladas = Column(Integer, default=0)
    Limite_Faltas = Column(Integer, nullable=False)
    estudiante = relationship("Estudiante", back_populates="faltas")

class AnalisisRiesgo(Base):
    __tablename__ = "Analisis_Riesgo"
    ID_Analisis = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_Estudiante = Column(Integer, ForeignKey("Estudiantes.ID_Estudiante", ondelete="CASCADE"), nullable=False)
    Puntuacion_Riesgo = Column(Integer, nullable=False)
    Nivel_Alerta = Column(String(20), nullable=False)
    Fecha_Calculo = Column(TIMESTAMP, server_default=func.now())
    estudiante = relationship("Estudiante", back_populates="riesgos")

class RegistroDesercion(Base):
    __tablename__ = "Registro_Desercion"
    ID_Desercion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_Estudiante = Column(Integer, ForeignKey("Estudiantes.ID_Estudiante", ondelete="CASCADE"), nullable=False)
    Fecha_Desercion = Column(Date, nullable=False)
    Motivo = Column(String(50), nullable=False)
    Observaciones = Column(Text)
    estudiante = relationship("Estudiante", back_populates="deserciones")