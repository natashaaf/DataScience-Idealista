from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

import motor.motor_asyncio
import datetime
import os

from pathlib import Path
from pydantic import Field
from fastapi import HTTPException

from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier front acceda (para desarrollo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a MongoDB (usando la variable de entorno de Docker)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://db:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
database = client.inmuebles_db
collection = database.busquedas


MODEL_PATH = Path(__file__).resolve().parent / 'modelo_idealista_v1.joblib'
model = joblib.load(MODEL_PATH)



class DatosInmueble(BaseModel):
    metros: float
    habitaciones: int
    baños: int
    zona: str
    ascensor_S: int = Field(..., ge=0, le=1)
    es_exterior: int = Field(..., ge=0, le=1)
    planta_num: int
    extra_piscina: int
    extra_terraza: int
    extra_garaje: int
    extra_reformado: int
    metros_por_hab: float
    ratio_banos: float


# --- DICCIONARIO DE BARRIOS ---
# Usa los mismos valores de codificacion de zona del entrenamiento
ZONAS_CODE_MAP = {
    "arganzuela": 125400.45,
    "barajas": 98200.12,
    "carabanchel": 149800.12,
    "centro": 210500.67,
    "chamartin": 320400.88,
    "chamberi": 945000.25,
    "ciudad-lineal": 355230.45,
    "fuencarral-el-pardo": 280600.33,
    "hortaleza": 430200.55,
    "latina": 115300.90,
    "moncloa-aravaca": 670300.90,
    "moratalaz": 140200.22,
    "puente-de-vallecas": 85400.15,
    "retiro": 890400.15,
    "salamanca": 1250000.50,
    "san-blas": 175300.44,
    "tetuan": 715900.88,
    "usera": 185400.33,
    "vicalvaro": 110200.10,
    "villa-de-vallecas": 95300.60,
    "villaverde": 72400.25,
}

# 3. Crea la ruta de previsión
@app.post("/prever")
async def predecir_precio(datos: DatosInmueble):
    data = datos.model_dump()
    zona_nombre = data.get("zona").strip().lower()

    if zona_nombre not in ZONAS_CODE_MAP:
        zonas_validas = ", ".join(sorted(ZONAS_CODE_MAP.keys()))
        raise HTTPException(status_code=400, detail=f"Zona no valida: {zona_nombre}. Usa una de estas: {zonas_validas}")

    data["zona_codificada"] = ZONAS_CODE_MAP[zona_nombre]
    df = pd.DataFrame([data])

    # 1. Orden exacto que espera el modelo
    orden_modelo = [
        "metros", "habitaciones", "baños", "zona_codificada",
        "ascensor_S", "es_exterior", "planta_num",
        "extra_piscina", "extra_terraza", "extra_garaje",
        "extra_reformado", "metros_por_hab", "ratio_banos"
    ]

    try:
        df = df[orden_modelo]
        
        # 2. Realizar la predicción
        prediccion = model.predict(df)
        precio_estimado = float(prediccion[0])

        # 3. Preparar el documento para MongoDB
        # Guardamos los datos de entrada + el resultado + la fecha
        documento_mongo = data.copy()
        documento_mongo["precio_estimado"] = precio_estimado
        documento_mongo["fecha"] = datetime.datetime.now()

        # 4. INSERTAR EN LA BASE DE DATOS (Crucial para el histórico)
        await collection.insert_one(documento_mongo)

        # 5. Devolver la respuesta al front
        return {"Precio estimado": precio_estimado}

    except KeyError:
        raise HTTPException(status_code=400, detail="Faltan columnas en el JSON enviado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción o guardado: {str(e)}")

    try:
        df = df[orden_modelo]
    except KeyError:
        raise HTTPException(status_code=400, detail="Faltan columnas en el JSON enviado.")
    
    # Predicion
    predicion = model.predict(df)
    
    return {"Precio estimado": float(predicion[0])}



@app.get("/", response_class=HTMLResponse)
def leer_front():
    try:
        # Busca el archivo index.html en la misma carpeta
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: No se encontró el archivo index.html</h1>"
    

@app.get("/historico")
async def obtener_historico():
    if collection is None:
        return {"error": "MongoDB no está conectado."}
    try:
        # Usar 'to_list' con 'await' para recuperar los documentos de forma asíncrona
        # El 1000 es el límite de documentos a recuperar
        resultados = await collection.find({}, {"_id": 0}).to_list(length=1000)
        return {"historial": resultados}
    except Exception as e:
        return {"error": str(e)}
"""
@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la API de predicción de precios de inmuebles"}
"""
