#  Staylytics: Sistema de Prevención de Deserción Académica

**Staylytics** es una plataforma de análisis predictivo diseñada para la gestión académica, orientada a la identificación temprana de factores de riesgo de deserción estudiantil. Desarrollado con una arquitectura desacoplada para garantizar escalabilidad y rendimiento en entornos universitarios.

---

##  Stack Tecnológico

La arquitectura está construida sobre bases sólidas:

| Capa | Tecnología |
| :--- | :--- |
| **Backend** | Python 3.12, FastAPI |
| **Base de Datos** | MySQL 8.0, SQLAlchemy ORM |
| **Contenedores** | Docker & Docker Compose |
| **Servidor Web** | Nginx |
| **Seguridad** | JWT, Bcrypt, Middleware CORS |

---

##  Arquitectura del Sistema

El sistema utiliza una arquitectura basada en contenedores para garantizar que el entorno de desarrollo sea idéntico al de producción.

- **Backend:** API RESTful que centraliza la lógica de negocio, autenticación y análisis de riesgo mediante un motor predictivo.
- **Base de Datos:** Instancia persistente aislada que gestiona el historial académico y las alertas tempranas.
- **Frontend:** Interfaz web estática optimizada para renderizado eficiente de grandes volúmenes de datos.

---

##  Instalación y Despliegue

Este proyecto está diseñado para desplegarse mediante orquestación de contenedores, facilitando la instalación en cualquier servidor institucional.

### Prerrequisitos
* [Docker](https://www.docker.com/products/docker-desktop/) instalado y en ejecución.

### Pasos para iniciar
1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/staylytics.git](https://github.com/tu-usuario/staylytics.git)
   cd staylytics

2. **Levantar el ecosistema completo:**
    ```bash
    docker-compose up -d --build

3. **Acceso:**
    Una vez que los contenedores estén activos, accede a la plataforma en:
    http://localhost

#### Funcionalidades Clave

* Análisis Predictivo: Algoritmos internos para identificar estudiantes en riesgo (Alertas tempranas).

* Gestión DACE: Ingesta de datos masivos (Webhooks) para el procesamiento de historial académico.

* Seguridad: Autenticación robusta basada en tokens JWT y hashing de contraseñas con Bcrypt.

* Dashboard: Visualización interactiva con Chart.js para métricas de deserción y rendimiento.

##### Consideraciones de Seguridad

El sistema implementa políticas de CORS restrictivas y manejo de variables de entorno para evitar la exposición de credenciales (DATABASE_URL, SECRET_KEY). El despliegue en producción debe asegurar el uso de protocolos HTTPS y la rotación frecuente de claves secretas.