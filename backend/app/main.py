from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# Set up CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL
        );
        INSERT INTO messages (content)
        VALUES ('Hello from the Database!')
        ON CONFLICT DO NOTHING;
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Initialize the database when the application starts
initialize_db()

@app.get("/api/data")
async def get_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM messages LIMIT 1;")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"message": result[0]}