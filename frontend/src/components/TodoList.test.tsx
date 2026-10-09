import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import type { Todo } from '../types/todo';
import TodoList from './TodoList';

const noop = async () => {};

function makeTodo(overrides: Partial<Todo> = {}): Todo {
  return {
    id: 1,
    title: 'Write release notes',
    description: null,
    completed: false,
    archived_at: null,
    created_at: '2026-01-05T09:00:00Z',
    updated_at: '2026-01-05T09:00:00Z',
    ...overrides,
  };
}

function render(props: Partial<Parameters<typeof TodoList>[0]> = {}) {
  return renderToStaticMarkup(
    <TodoList
      todos={[]}
      loading={false}
      error={null}
      onToggle={noop}
      onDelete={noop}
      {...props}
    />
  );
}

describe('TodoList', () => {
  it('shows a loading message while todos are being fetched', () => {
    expect(render({ loading: true })).toContain('Loading todos...');
  });

  it('shows the error message when loading fails', () => {
    expect(render({ error: 'Network down' })).toContain('Error: Network down');
  });

  it('shows the empty state when there are no todos', () => {
    expect(render()).toContain('No todos yet. Add one above to get started!');
  });

  it('renders a row for every todo', () => {
    const html = render({
      todos: [
        makeTodo({ id: 1, title: 'Write release notes' }),
        makeTodo({ id: 2, title: 'Review open pull requests' }),
      ],
    });
    expect(html).toContain('Write release notes');
    expect(html).toContain('Review open pull requests');
  });
});
