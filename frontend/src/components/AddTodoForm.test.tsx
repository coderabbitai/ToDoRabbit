import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import AddTodoForm from './AddTodoForm';

describe('AddTodoForm', () => {
  it('renders the title and description inputs', () => {
    const html = renderToStaticMarkup(<AddTodoForm onAdd={async () => {}} />);
    expect(html).toContain('placeholder="What needs to be done?"');
    expect(html).toContain('placeholder="Description (optional)"');
  });

  it('disables the submit button until a title is entered', () => {
    const html = renderToStaticMarkup(<AddTodoForm onAdd={async () => {}} />);
    expect(html).toMatch(/<button[^>]*disabled[^>]*>Add Todo<\/button>/);
  });
});
