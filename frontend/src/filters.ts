import type { Todo } from './types/todo';

export type TodoFilter = 'all' | 'active' | 'completed';

export const FILTERS: { value: TodoFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
];

/** Value for the API's `completed` query parameter, or undefined to fetch everything. */
export function toCompletedParam(filter: TodoFilter): boolean | undefined {
  if (filter === 'all') {
    return undefined;
  }
  return filter === 'completed';
}

export function matchesFilter(todo: Todo, filter: TodoFilter): boolean {
  const completed = toCompletedParam(filter);
  return completed === undefined || todo.completed === completed;
}
