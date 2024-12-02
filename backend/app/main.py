from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv
from typing import Any, List, Optional
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from pydantic import BaseModel, Field, ValidationError, field_validator
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
# Load environment variables
load_dotenv()

# Initialize Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        _experiments={
            "continuous_profiling_auto_start": True,
        },
        traces_sample_rate=1.0,
        environment=os.getenv("ENVIRONMENT", "development"),
    )

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Log the validation error in Sentry
    sentry_sdk.capture_exception(exc)

    # Serialize the error details for JSONResponse
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),  # Serialize the validation errors
            "body": str(exc.body),  # Include the request body for debugging
        },
    )
# Add Sentry middleware
if SENTRY_DSN:
    app.add_middleware(SentryAsgiMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verify required environment variables
REQUIRED_ENV_VARS = [
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
]

missing_env_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_env_vars:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing_env_vars)}")


# Function to get a database connection
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
        sentry_sdk.capture_exception(e)  # Capture exception in Sentry
        raise RuntimeError("Could not connect to the database. Check your configuration.") from e


# Initialize the database (only in production)
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


if os.getenv("TEST_ENV") != "true":  # Avoid initializing the database in the test environment
    initialize_db()


# Model for input data

# Model for input data with validations

class TodoIn(BaseModel):
    todo: str = Field(..., min_length=1, max_length=200, description="The task description")
    completed: bool = Field(default=False, description="Whether the task is completed")

    # Use field_validator for specific field validation
    @field_validator('todo')
    def no_weird_characters(cls, value: str) -> str:
        if any(char in value for char in ["$", "@", "#", "%"]):
            raise ValueError("The task description contains invalid characters: $, @, #, %")
        return value


# Hello World Endpoint
@app.get("/")
def say_hello():
    return {"message": "Hello, World!"}


# Get all tasks
@app.get("/api/todos")
def get_todos():
    try:
        query = "SELECT id, todo, completed FROM todos"
        rows = execute_select_query(query)
        return [{"id": row[0], "todo": row[1], "completed": bool(row[2])} for row in rows]
    except Exception as e:

        sentry_sdk.capture_exception(e)  # Capture exception in Sentry
        raise ValueError(e)



# Add a new task
@app.post("/api/todos")
def add_todo(todo: TodoIn):
    try:
        query = "INSERT INTO todos (todo) VALUES (%s) RETURNING id"
        new_id = execute_select_query(query, [todo.todo])[0][0]
        return {"id": new_id, "todo": todo.todo}
    except Exception as e:
        sentry_sdk.capture_exception(e)  # Log unexpected errors to Sentry
        raise HTTPException(status_code=500, detail="Unexpected server error")

# Update an existing task
@app.put("/api/todos/{id}")
def update_todo(id: int, todo: TodoIn):

    try:
        query = "UPDATE todos SET todo = %s, completed = %s WHERE id = %s"
        execute_modify_query(query, [todo.todo, todo.completed, id])

        # Verify if the task was found and updated
        updated_todo = execute_select_query("SELECT id, todo, completed FROM todos WHERE id = %s", [id])
        if not updated_todo:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"id": updated_todo[0][0], "todo": updated_todo[0][1], "completed": bool(updated_todo[0][2])}
    except Exception as e:
        sentry_sdk.capture_exception(e)  # Capture exception in Sentry
        raise ValueError(e)


# Execute SELECT queries
def execute_select_query(query: str, params: Optional[List[Any]] = None) -> List[Any]:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            result = cursor.fetchall()
            cursor.close()
        return result
    except Exception as e:
        sentry_sdk.capture_exception(e)  # Capture exception in Sentry
        raise ValueError(e)


# Execute INSERT, UPDATE, DELETE queries
def execute_modify_query(query: str, params: Optional[List[Any]] = None) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            conn.commit()
            cursor.close()
    except Exception as e:
        sentry_sdk.capture_exception(e)  # Capture exception in Sentry
        raise ValueError(e)

