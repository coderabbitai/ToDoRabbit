export interface Todo {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  title: string;
  description?: string;
}
