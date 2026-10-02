export interface PracticeCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  parentId: string | null;
}

export interface PracticeTag {
  id: string;
  name: string;
  slug: string;
}
