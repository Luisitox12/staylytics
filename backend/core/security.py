from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# CONFIGURACIÓN CRIPTOGRÁFICA STRICTA
# En producción, estos valores se extraen de variables de entorno (.env)
SECRET_KEY = "STAYLYTICS_ULTRA_SECRET_KEY_FOR_JWT_SIGNING_DONT_LEAK_THIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Motor de hashing usando el algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        
    # Inyectamos la fecha de expiración en el cuerpo (payload) del token
    to_encode.update({"exp": expire})
    
    # Firmamos el token con nuestra clave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt