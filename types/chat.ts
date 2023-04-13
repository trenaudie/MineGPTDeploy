import { OpenAIModel } from './openai';

export interface Message {
  role: Role;
  source: boolean;
  title: string;
  content: string;
}


export type Role = 'assistant' | 'user';

export interface ChatBody {
  prompt: string;
}

export interface Conversation {
  id: string;
  name: string;
  messages: Message[];
  model: OpenAIModel;
  prompt: string;
  folderId: string | null;
}
