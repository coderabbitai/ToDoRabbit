import { useState, useEffect } from 'react';
import type { Todo, TodoCreate } from './types/todo';
import { fetchTodos, createTodo, updateTodo, deleteTodo } from './api/todos';
import { matchesFilter, toCompletedParam, type TodoFilter } from './filters';
import AddTodoForm from './components/AddTodoForm';
import FilterTabs from './components/FilterTabs';
import TodoList from './components/TodoList';
import styles from './App.module.css';

export default function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<TodoFilter>('all');

  const loadTodos = async (activeFilter: TodoFilter) => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTodos(toCompletedParam(activeFilter));
      setTodos(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load todos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTodos(filter);
  }, [filter]);

  const handleAddTodo = async (data: TodoCreate) => {
    try {
      const newTodo = await createTodo(data);
      if (matchesFilter(newTodo, filter)) {
        setTodos((prev) => [newTodo, ...prev]);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create todo');
      throw err;
    }
  };

  const handleToggleTodo = async (id: number, completed: boolean) => {
    try {
      const updatedTodo = await updateTodo(id, { completed });
      setTodos((prev) =>
        prev
          .map((todo) => (todo.id === id ? updatedTodo : todo))
          .filter((todo) => matchesFilter(todo, filter))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update todo');
      throw err;
    }
  };

  const handleDeleteTodo = async (id: number) => {
    try {
      await deleteTodo(id);
      setTodos((prev) => prev.filter((todo) => todo.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete todo');
      throw err;
    }
  };

  return (
    <div className={styles.app}>
      <div className={styles.container}>
        <header className={styles.header}>
          <h1 className={styles.title}>ToDoRabbit</h1>
          <p className={styles.subtitle}>A simple and elegant todo list</p>
        </header>

        <div className={styles.card}>
          <AddTodoForm onAdd={handleAddTodo} />
        </div>

        <div className={styles.card}>
          <FilterTabs value={filter} onChange={setFilter} />
          <TodoList
            todos={todos}
            loading={loading}
            error={error}
            onToggle={handleToggleTodo}
            onDelete={handleDeleteTodo}
          />
        </div>
      </div>
    </div>
  );
}
