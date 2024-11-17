import { useState, useEffect } from "react";
import {
  Box,
  Button,
  Input,
  Typography,
  List,
  ListItem,
  FormControl,
  FormLabel,
  Checkbox,
} from "@mui/joy";

export const TodoForm = () => {
  const API_URL = "http://localhost:8000";
  const [todos, setTodos] = useState([]);
  const [task, setTask] = useState("");

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      const response = await fetch(`${API_URL}/api/todos`);
      const data = await response.json();

      setTodos(data);
    } catch (error) {
      console.error("Error al obtener tareas:", error);
    }
  };

  const handleInputChange = (event) => {
    setTask(event.target.value);
  };

  const handleAddTodo = async () => {
    if (task.trim()) {
      try {
        const newTodo = { todo: task, completed: false };
        const response = await fetch(`${API_URL}/api/todos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newTodo),
        });
        const savedTodo = await response.json();
        setTodos([...todos, savedTodo]);
        setTask("");
      } catch (error) {
        console.error("Error al agregar tarea:", error);
      }
    }
  };

  const toggleComplete = async (index) => {
    const updatedTodo = { ...todos[index], completed: !todos[index].completed };

    try {
      await fetch(`${API_URL}/api/todos/${updatedTodo.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedTodo),
      });
      const updatedTodos = todos.map((todo, i) =>
        i === index ? updatedTodo : todo
      );
      setTodos(updatedTodos);
    } catch (error) {
      console.error("Error al actualizar tarea:", error);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 400, margin: "auto", textAlign: "center" }}>
      <Typography level="h4" sx={{ mb: 2 }}>
        Crear Tarea
      </Typography>
      <FormControl sx={{ mb: 2, width: "100%" }}>
        <FormLabel>Nueva Tarea</FormLabel>
        <Input
          placeholder="Escribe una tarea..."
          value={task}
          onChange={handleInputChange}
          fullWidth
        />
      </FormControl>
      <Button
        onClick={handleAddTodo}
        variant="soft"
        color="warning"
        sx={{ mb: 2 }}
      >
        Agregar Tarea
      </Button>

      <List>
        {todos.map((todo, index) => (
          <ListItem key={index} sx={{ display: "flex", alignItems: "center" }}>
            <Checkbox
              checked={todo.completed}
              onChange={() => toggleComplete(index)}
              sx={{ mr: 2 }}
            />
            <Typography
              sx={{
                textDecoration: todo.completed ? "line-through" : "none",
                color: todo.completed ? "gray" : "inherit",
              }}
            >
              {todo.todo}
            </Typography>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};
