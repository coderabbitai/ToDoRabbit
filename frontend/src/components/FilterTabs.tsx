import { FILTERS, type TodoFilter } from '../filters';
import styles from './FilterTabs.module.css';

interface FilterTabsProps {
  value: TodoFilter;
  onChange: (filter: TodoFilter) => void;
}

export default function FilterTabs({ value, onChange }: FilterTabsProps) {
  return (
    <div className={styles.tabs} role="tablist" aria-label="Filter todos">
      {FILTERS.map((filter) => (
        <button
          key={filter.value}
          type="button"
          role="tab"
          aria-selected={filter.value === value}
          className={`${styles.tab} ${filter.value === value ? styles.active : ''}`}
          onClick={() => onChange(filter.value)}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}
