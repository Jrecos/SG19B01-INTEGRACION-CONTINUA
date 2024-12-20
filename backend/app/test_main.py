import pytest
from fastapi.testclient import TestClient
from main import app, get_db_connection, initialize_db, execute_select_query, execute_modify_query
from unittest.mock import patch, MagicMock
import os

# Usamos TestClient para interactuar con la aplicación FastAPI
client = TestClient(app)

# Verificar que las variables de entorno necesarias estén configuradas
@pytest.mark.parametrize(
    "env_var, expected_result",
    [
        ("POSTGRES_DB", True),
        ("POSTGRES_USER", True),
        ("POSTGRES_PASSWORD", True),
        ("POSTGRES_HOST", True),
        ("POSTGRES_PORT", True),
    ]
)
def test_required_env_vars(env_var, expected_result):
    result = os.getenv(env_var)
    assert (result is not None) == expected_result, f"Variable de entorno {env_var} no está configurada correctamente."

# Verificar que la conexión a la base de datos se pueda realizar correctamente
def test_db_connection():
    with patch("main.psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        conn = get_db_connection()
        assert conn is not None

# Verificar el endpoint "GET /api/todos"
def test_get_todos():
    # Simulamos la base de datos
    mock_rows = [(1, "Tarea 1", True), (2, "Tarea 2", False)]
    with patch("main.execute_select_query") as mock_execute_select:
        mock_execute_select.return_value = mock_rows
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.json() == [{"id": 1, "todo": "Tarea 1", "completed": True},
                                   {"id": 2, "todo": "Tarea 2", "completed": False}]

# Verificar el endpoint "POST /api/todos"
def test_add_todo():
    new_todo = {"todo": "Nueva tarea", "completed": False}
    mock_new_id = 1
    with patch("main.execute_select_query") as mock_execute_select:
        mock_execute_select.return_value = [(mock_new_id,)]
        response = client.post("/api/todos", json=new_todo)
        assert response.status_code == 200
        assert response.json() == {"id": mock_new_id, "todo": new_todo["todo"]}

# Verificar el endpoint "PUT /api/todos/{id}" para actualizar una tarea
def test_update_todo():
    todo_to_update = {"todo": "Tarea actualizada", "completed": True}
    mock_updated_row = [(1, "Tarea actualizada", True)]
    with patch("main.execute_modify_query") as mock_execute_modify, patch("main.execute_select_query") as mock_execute_select:
        mock_execute_select.return_value = mock_updated_row
        response = client.put("/api/todos/1", json=todo_to_update)
        assert response.status_code == 200
        assert response.json() == {"id": 1, "todo": "Tarea actualizada", "completed": True}

# Test the Hello World endpoint
def test_say_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

# Test validation error handling
def test_validation_error_handling():
    invalid_todo_data = {"todo": ""}
    response = client.post("/api/todos", json=invalid_todo_data)
    assert response.status_code == 422

# Test the initialization of the database (only in production)
def test_initialize_db():
    with patch("main.get_db_connection") as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        initialize_db()

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()