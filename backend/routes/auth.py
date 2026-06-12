from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from core.database import get_db
from core.security import obtener_password_hash, verificar_password, crear_token_acceso, SECRET_KEY, ALGORITHM
import models, schemas

router = APIRouter()

# El esquema que le dice a FastAPI dónde se piden los tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ---------------------------------------------------------
# EL GUARDIÁN (Dependencia para proteger endpoints)
# ---------------------------------------------------------
def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Verifica si el token enviado en la cabecera es matemáticamente válido y no ha expirado."""
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales o el token expiró",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo = payload.get("sub")
        if correo is None:
            raise credenciales_exception
    except JWTError:
        raise credenciales_exception
        
    usuario = db.query(models.UsuarioAdministrativo).filter(models.UsuarioAdministrativo.Correo == correo).first()
    if usuario is None:
        raise credenciales_exception
        
    return usuario

# ---------------------------------------------------------
# ENDPOINTS DE IDENTIDAD
# ---------------------------------------------------------
@router.post("/api/auth/registrar")
def registrar_admin(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Verificamos que el correo no esté tomado
    if db.query(models.UsuarioAdministrativo).filter(models.UsuarioAdministrativo.Correo == usuario.Correo).first():
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")
    
    # 2. Cifrado irreversible de la contraseña (NUNCA GUARDAR EN TEXTO PLANO)
    hashed_password = obtener_password_hash(usuario.Password)
    
    # 3. Guardado en la base de datos
    nuevo_usuario = models.UsuarioAdministrativo(
        Nombre_Completo=usuario.Nombre_Completo,
        Correo=usuario.Correo,
        Password_Hash=hashed_password,
        Rol=usuario.Rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {"mensaje": f"Usuario {nuevo_usuario.Nombre_Completo} registrado exitosamente. Ya puedes iniciar sesión."}


@router.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form_data.username se usa internamente por OAuth2, pero nosotros le pasaremos el correo
    usuario = db.query(models.UsuarioAdministrativo).filter(models.UsuarioAdministrativo.Correo == form_data.username).first()
    
    # Si el usuario no existe O la contraseña no coincide con el hash
    if not usuario or not verificar_password(form_data.password, str(usuario.Password_Hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Si sobrevive a la validación, le emitimos el token JWT
    access_token = crear_token_acceso(data={"sub": usuario.Correo})
    return {"access_token": access_token, "token_type": "bearer"}