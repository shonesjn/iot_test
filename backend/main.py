import os
from dotenv import load_dotenv
import psycopg2
import time
import random
import threading
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load env
load_dotenv()

# ==============================
# FASTAPI INIT (IMPORTANT)
# ==============================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# DATABASE CONNECTION
# ==============================
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "water_monitoring"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )

# ==============================
# CREATE TABLES
# ==============================
def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id SERIAL PRIMARY KEY,
        distance FLOAT,
        temperature FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id SERIAL PRIMARY KEY,
        distance FLOAT,
        temperature FLOAT,
        prediction VARCHAR(50),
        confidence FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ==============================
# SENSOR DATA GENERATOR
# ==============================
def generate_test_data():
    return {
        "distance": round(90 + random.uniform(-10, 10), 1),
        "temperature": round(20 + random.uniform(-2, 2), 1),
        "created_at": datetime.now()
    }

# ==============================
# BACKGROUND SENSOR COLLECTOR
# ==============================
def sensor_collector():
    print("Sensor Collector Started")

    while True:
        try:
            data = generate_test_data()

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
            INSERT INTO sensor_data (distance, temperature, created_at)
            VALUES (%s,%s,%s)
            """, (data["distance"], data["temperature"], data["created_at"]))

            conn.commit()
            cur.close()
            conn.close()

            print("Inserted:", data)

        except Exception as e:
            print("Error:", e)

        time.sleep(5)

# ==============================
# GET SENSOR DATA API
# ==============================
@app.get("/sensor-data")
def get_sensor_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, distance, temperature, created_at
    FROM sensor_data
    ORDER BY id DESC
    LIMIT 50
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "distance": r[1],
            "temperature": r[2],
            "created_at": r[3]
        }
        for r in rows
    ]

# ==============================
# 🔥 DUMMY PREDICTION MODEL (NO ERRORS)
# ==============================
@app.post("/api/v1/predict")
def predict_water_activity(data: dict):

    distance = float(data["distance"])
    temperature = float(data["temperature"])

    # Simple logic (for demo)
    if distance < 30:
        prediction = "shower"
        confidence = 0.92
    elif distance < 60:
        prediction = "faucet"
        confidence = 0.85
    elif distance < 80:
        prediction = "toilet"
        confidence = 0.78
    else:
        prediction = "no_activity"
        confidence = 0.70

    # Save prediction
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO predictions (distance, temperature, prediction, confidence)
    VALUES (%s,%s,%s,%s)
    """, (distance, temperature, prediction, confidence))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "prediction": prediction,
        "confidence": confidence
    }

# ==============================
# STARTUP EVENT
# ==============================
@app.on_event("startup")
def startup():
    create_tables()

    thread = threading.Thread(target=sensor_collector)
    thread.daemon = True
    thread.start()

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)