import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import FilterTabs from './FilterTabs';

describe('FilterTabs', () => {
  it('renders a tab for each filter', () => {
    const html = renderToStaticMarkup(<FilterTabs value="all" onChange={() => {}} />);
    expect(html).toContain('>All</button>');
    expect(html).toContain('>Active</button>');
    expect(html).toContain('>Completed</button>');
  });

  it('marks only the selected tab as selected', () => {
    const html = renderToStaticMarkup(<FilterTabs value="active" onChange={() => {}} />);
    expect(html.match(/aria-selected="true"/g)).toHaveLength(1);
    expect(html).toMatch(/aria-selected="true"[^>]*>Active<\/button>/);
  });
});
