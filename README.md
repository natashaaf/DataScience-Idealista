# ProphetAI — Predicción de Precios Inmobiliarios (Madrid) 

[English version below](#english)

ProphetAI es una herramienta interactiva diseñada para estimar el precio de venta de inmuebles en la ciudad de Madrid. Utiliza un modelo de Machine Learning (XGBoost) entrenado con datos reales del mercado para ofrecer predicciones precisas basadas en características como los metros cuadrados, la zona, el número de habitaciones y extras (piscina, garaje, etc.).

Este proyecto fue desarrollado como parte de un Trabajo de Fin de Año por un equipo de estudiantes de DAW, integrando un stack tecnológico moderno y despliegue mediante contenedores.

##  Instalación y Uso

Gracias a Docker, puedes desplegar todo el entorno (Backend, Frontend y Base de Datos) con un solo comando.

### Requisitos previos
- Tener instalado [Docker](https://www.docker.com/get-started) y [Docker Compose](https://docs.docker.com/compose/install/).
- Clonar este repositorio.

### Pasos para arrancar
1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
   cd nombre-del-repo

### Como ejecutar

Una vez completados los pasos anteriores y estando poscionados en la carpeta del proyecto
lanzamos la aplicación con: 

docker compose up -d

### Accede a la aplicación:

Frontend: Abre tu navegador en http://localhost:8000.

API (FastAPI Docs): Si quieres probar los endpoints manualmente, ve a http://localhost:8000/historico

Esto último refleja las consultas realizadas en la aplicación par asu posterior uso como datos para su posible análisis.

-------------------------------------------------------
### Stack Tecnológico
Lenguaje: Python 3.12

Modelo: XGBoost (entrenado con Scikit-learn)

Backend: FastAPI

Base de Datos: MongoDB (para el histórico de consultas)

Contenedores: Docker & Docker Compose

Frontend: HTML5, CSS3 y JavaScript Vanilla.


------------------------ ENGLISH INSTRUCTIONS ---------------------------

ProphetAI — Real Estate Price Prediction (Madrid) 
ProphetAI is an interactive tool designed to estimate property sale prices in Madrid. It uses a Machine Learning model (XGBoost) trained on real market data to provide accurate predictions based on features such as square footage, neighborhood, number of rooms, and extras (swimming pool, garage, etc.).

This project was developed as part of a Final Degree Project, integrating a modern tech stack and containerized deployment.

##  Installation and Usage
Thanks to Docker, you can deploy the entire environment (Backend, Frontend, and Database) with a single command.

### Prerequisites
Have Docker and Docker Compose installed.
[Docker](https://www.docker.com/get-started) y [Docker Compose](https://docs.docker.com/compose/install/).


### Getting Started
Clone the repository:

Bash
git clone [https://github.com/your-username/repo-name.git](https://github.com/your-username/repo-name.git)
cd repo-name


### Start the services:
Run the following command in the project root:

Bash
docker compose up -d

### Access the application:

Frontend: Open your browser at http://localhost:8000.

API (FastAPI Docs): To test endpoints manually, go to http://localhost:8000/historico.

------------------------------------------------

## Tech Stack
Language: Python 3.12

Model: XGBoost (trained with Scikit-learn)

Backend: FastAPI

Database: MongoDB (for search history)

Containers: Docker & Docker Compose

Frontend: HTML5, CSS3, and Vanilla JavaScript.