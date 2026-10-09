import { describe, expect, it } from 'vitest';
import { matchesFilter, toCompletedParam } from './filters';
import type { Todo } from './types/todo';

function makeTodo(completed: boolean): Todo {
  return {
    id: 1,
    title: 'Water the plants',
    description: null,
    completed,
    archived_at: null,
    created_at: '2026-01-05T09:00:00Z',
    updated_at: '2026-01-05T09:00:00Z',
  };
}

describe('toCompletedParam', () => {
  it('does not filter when showing all todos', () => {
    expect(toCompletedParam('all')).toBeUndefined();
  });

  it('maps active and completed to the API parameter', () => {
    expect(toCompletedParam('active')).toBe(false);
    expect(toCompletedParam('completed')).toBe(true);
  });
});

describe('matchesFilter', () => {
  it('matches every todo for the all filter', () => {
    expect(matchesFilter(makeTodo(true), 'all')).toBe(true);
    expect(matchesFilter(makeTodo(false), 'all')).toBe(true);
  });

  it('matches only open todos for the active filter', () => {
    expect(matchesFilter(makeTodo(false), 'active')).toBe(true);
    expect(matchesFilter(makeTodo(true), 'active')).toBe(false);
  });

  it('matches only finished todos for the completed filter', () => {
    expect(matchesFilter(makeTodo(true), 'completed')).toBe(true);
    expect(matchesFilter(makeTodo(false), 'completed')).toBe(false);
  });
});
