from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# CONFIGURACIÓN CRIPTOGRÁFICA STRICTA
SECRET_KEY = "STAYLYTICS_ULTRA_SECRET_KEY_FOR_JWT_SIGNING_DONT_LEAK_THIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Motor de hashing usando el algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Le decimos a FastAPI dónde está la ruta para conseguir el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ---------------------------------------------------------
# SERVICIOS DE CONTRASEÑAS (Hashing)
# ---------------------------------------------------------
def obtener_password_hash(password: str) -> str:
    """Convierte una contraseña en texto plano en un hash irreversible."""
    return pwd_context.hash(password)

def verificar_password(password_plana: str, password_hasheada: str) -> bool:
    """Compara una contraseña entrante con el hash guardado en la base de datos."""
    return pwd_context.verify(password_plana, password_hasheada)

# ---------------------------------------------------------
# SERVICIOS DE TOKENS (JWT)
# ---------------------------------------------------------
def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """ Genera un token JWT firmado criptográficamente con tiempo de expiración. """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------------------------------------------------
# EL GUARDIA DE SEGURIDAD (Decodificador)
# ---------------------------------------------------------
def get_usuario_actual(token: str = Depends(oauth2_scheme)):
    """Intercepta el token de la cabecera, lo desencripta y valida la identidad."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Desencriptamos usando la misma llave secreta y algoritmo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
        return correo
    except JWTError:
        raise credentials_exception