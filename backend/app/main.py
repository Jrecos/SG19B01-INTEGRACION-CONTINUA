from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv
from typing import Any, List, Optional
from pydantic import BaseModel

load_dotenv()

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
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            todo TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Initialize the database when the application starts
initialize_db()

class TodoIn(BaseModel):
    todo: str
    completed: bool = False

# Endpoint para obtener todas las tareas
@app.get("/api/todos")
def get_todos():
    query = "SELECT id, todo, completed FROM todos"
    rows = execute_select_query(query)
    print(rows)
    return [{"id": row[0], "todo": row[1], "completed": bool(row[2])} for row in rows]

# Endpoint para agregar una nueva tarea
@app.post("/api/todos")
def add_todo(todo: TodoIn):
    query = "INSERT INTO todos (todo) VALUES (%s) RETURNING id"
    new_id = execute_select_query(query, [todo.todo])[0]
    return {"id": new_id, "todo": todo.todo}

# Endpoint para actualizar una tarea existente
@app.put("/api/todos/{id}")
def update_todo(id: int, todo: TodoIn):
    query = "UPDATE todos SET todo = %s, completed = %s WHERE id = %s"
    execute_modify_query(query, [todo.todo, todo.completed, id])
    
    # Verificar si la tarea fue encontrada y actualizada
    updated_todo = execute_select_query("SELECT id, todo, completed FROM todos WHERE id = %s", [id])
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return {"id": updated_todo[0][0], "todo": updated_todo[0][1], "completed": bool(updated_todo[0][2])}


# Función para ejecutar consultas que devuelven datos (SELECT)
def execute_select_query(query: str, params: Optional[List[Any]] = None) -> List[Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        cursor.close()
    return result

# Función para ejecutar consultas que modifican datos (INSERT, UPDATE, DELETE)
def execute_modify_query(query: str, params: Optional[List[Any]] = None) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        conn.commit()
        cursor.close()