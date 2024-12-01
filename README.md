# Proyecto de Integración Continua y Contenedores

Este proyecto tiene como objetivo demostrar la integración de herramientas para el desarrollo y despliegue de software utilizando contenedores Docker, integración continua con Jenkins, monitoreo de errores con Sentry, y cobertura de código con Codecov.

## Tecnologías Utilizadas

- **Docker**: Para la creación de contenedores y la administración del entorno.
- **Jenkins**: Para la automatización de la integración continua y el despliegue.
- **Codecov**: Para la medición y análisis de la cobertura del código.
- **Sentry**: Para el monitoreo y la captura de errores en producción.
- **Jira/Zenhub**: Para la gestión de tareas y seguimiento de proyectos.

---

## Estructura del Proyecto

El proyecto se encuentra estructurado de la siguiente manera:

/SG19B01-INTEGRACION-CONTINUA.git│ 

├── backend # Proyecto del backend │

├── frontend # Proyecto del frontend │ 

├── docker-compose.yml # Configuración de Docker para contenedores

├── Integrantes.txt # Información de los integrantes del equipo 

├── Jenkinsfile # Configuración de Jenkins para CI/CD


## Instrucciones para Ejecutar el Proyecto

### Requisitos Previos

- Docker y Docker Compose deben estar instalados en tu máquina.
- Tener acceso al repositorio de GitHub.
- Configuración de herramientas de CI/CD Jenkins

### Instalación

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/Jrecos/SG19B01-INTEGRACION-CONTINUA.git
   cd SG19B01-INTEGRACION-CONTINUA.git
    ```
  
Configurar y ejecutar los contenedores con Docker:
  ```bash
    docker-compose up --build
 ```

La aplicación estará accesible en la URL ```bash http://localhost:3000 ```

Ejecutar pruebas locales:

```bash
npm test
```

O si utilizas yarn:

```bash
yarn test
```


### Estructura de Ramas

El flujo de trabajo de ramas sigue esta estructura:

main: Rama principal para la versión estable.

dev: Rama de desarrollo donde se integran las nuevas características.

feature/[nombre]: Ramas para características o correcciones específicas. Estas ramas se crean desde dev y se fusionan nuevamente en dev una vez terminadas.
