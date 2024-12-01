from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv
from typing import Any, List, Optional
from pydantic import BaseModel

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir esto a dominios específicos si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verificar que las variables de entorno necesarias estén configuradas
REQUIRED_ENV_VARS = [
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
]

missing_env_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_env_vars:
    raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing_env_vars)}")

# Función para obtener una conexión a la base de datos
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
        )
        return conn
    except OperationalError as e:
        raise RuntimeError("No se pudo conectar a la base de datos. Verifica tu configuración.") from e

# Inicializar la base de datos (solo en producción)
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            todo TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

if os.getenv("TEST_ENV") != "true":  # Evitar inicializar la base de datos en el entorno de pruebas
    initialize_db()

# Modelo para los datos de entrada
class TodoIn(BaseModel):
    todo: str
    completed: bool = False

# Hello World Endpoint
@app.get("/")
def say_hello():
    return {"message": "Hello, World!"}

# Obtener todas las tareas
@app.get("/api/todos")
def get_todos():
    query = "SELECT id, todo, completed FROM todos"
    rows = execute_select_query(query)
    return [{"id": row[0], "todo": row[1], "completed": bool(row[2])} for row in rows]

# Agregar una nueva tarea
@app.post("/api/todos")
def add_todo(todo: TodoIn):
    query = "INSERT INTO todos (todo) VALUES (%s) RETURNING id"
    new_id = execute_select_query(query, [todo.todo])[0][0]
    return {"id": new_id, "todo": todo.todo}

# Actualizar una tarea existente
@app.put("/api/todos/{id}")
def update_todo(id: int, todo: TodoIn):
    query = "UPDATE todos SET todo = %s, completed = %s WHERE id = %s"
    execute_modify_query(query, [todo.todo, todo.completed, id])

    # Verificar si la tarea fue encontrada y actualizada
    updated_todo = execute_select_query("SELECT id, todo, completed FROM todos WHERE id = %s", [id])
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    return {"id": updated_todo[0][0], "todo": updated_todo[0][1], "completed": bool(updated_todo[0][2])}

# Ejecutar consultas SELECT
def execute_select_query(query: str, params: Optional[List[Any]] = None) -> List[Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        cursor.close()
    return result

# Ejecutar consultas INSERT, UPDATE, DELETE
def execute_modify_query(query: str, params: Optional[List[Any]] = None) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        conn.commit()
        cursor.close()
