export interface ResourceInterface {
  id: string;
  name: string;
  category: string;
  description: string;
  address: string;
  phone: string;
  hours: string;
}

export interface PlanStepInterface {
  resource: ResourceInterface;
  why: string;
  nextStep: string;
}

export interface PlanInterface {
  steps: PlanStepInterface[];
  followUpQuestions: string[];
}

export type ChatMessageRole = 'volunteer' | 'assistant';

export interface ChatMessageInterface {
  id: string;
  role: ChatMessageRole;
  text: string;
  plan?: PlanInterface;
}

export interface ApiErrorInterface {
  message: string;
  status: number;
}
