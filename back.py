import os
import time
from datetime import datetime
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from pathlib import Path

# Conexión MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
try:
    client.server_info()
    db = client["db_idealista"]
    collection = db["historico_predicciones"]
    print("MongoDB: conexión establecida.")
except Exception as e:
    print(f"No se pudo conectar a MongoDB: {e}")
    collection = None

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier front acceda (para desarrollo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# 3. Ruta de previsión
@app.post("/prever")
def predecir_precio(datos: DatosInmueble):
    payload = datos.model_dump()
    # Guardamos una copia del input tal como vino
    input_payload = payload.copy()
    zona_nombre = input_payload.pop("zona").strip().lower()

    if zona_nombre not in ZONAS_CODE_MAP:
        zonas_validas = ", ".join(sorted(ZONAS_CODE_MAP.keys()))
        raise HTTPException(status_code=400, detail=f"Zona no válida: {zona_nombre}. Usa una de estas: {zonas_validas}")

    # Codificamos la zona para el modelo
    input_payload["zona_codificada"] = ZONAS_CODE_MAP[zona_nombre]
    df = pd.DataFrame([input_payload])

    # Orden exacto que espera el modelo
    orden_modelo = [
        "metros", "habitaciones", "baños", "zona_codificada",
        "ascensor_S", "es_exterior", "planta_num",
        "extra_piscina", "extra_terraza", "extra_garaje",
        "extra_reformado", "metros_por_hab", "ratio_banos"
    ]

    try:
        df = df[orden_modelo]
    except KeyError:
        raise HTTPException(status_code=400, detail="Faltan columnas en el JSON enviado.")
    
    # Predicción (medimos tiempo de inferencia)
    start = time.perf_counter()
    prediccion = model.predict(df)
    inference_ms = (time.perf_counter() - start) * 1000.0
    precio = float(prediccion[0])

    # Registro en MongoDB
    if collection is not None:
        doc = {
            "input": datos.model_dump(),
            "prediction": precio,
            "model": "XGBoost_v1",
            "timestamp": datetime.utcnow(),
            "inference_ms": round(inference_ms, 2)
        }
        try:
            collection.insert_one(doc)
        except Exception as e:
            print(f"Error al guardar en MongoDB: {e}")

    return {"Precio estimado": precio}

@app.get("/", response_class=HTMLResponse)
def leer_front():
    try:
        # Busca el archivo index.html en la misma carpeta
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: No se encontró el archivo index.html</h1>"

# Endpoint para historial de predicciones
@app.get("/historico")
async def obtener_historico():
    if collection is None:
        return {"error": "MongoDB no está conectado."}
    try:
        # Recuperar historial
        resultados = list(collection.find({}, {"_id": 0}))
        return {"historial": resultados}
    except Exception as e:
        return {"error": str(e)}