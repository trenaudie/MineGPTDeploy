
export interface Docsource {
  id: number;
  file_id : string;
  name: string;
  description: string;
  source: string; //actual source website
  folderId: string | null;
}
