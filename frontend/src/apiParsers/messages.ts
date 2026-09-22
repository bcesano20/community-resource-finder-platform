import type { ChatMessageInterface, ChatMessageRole, PlanInterface } from '@/types';
import { planParser, type PlanParser } from '@/apiParsers/plan';

// Raw shape expected by the backend's MessageRequestSerializer
export interface MessageRequestParser {
  question: string;
  history: { role: ChatMessageRole; text: string }[];
}

// Strips the frontend-only fields (id, plan) off each history entry — the
// backend's ChatHistoryEntrySerializer only reads role and text.
export const messageRequestParser = (
  question: string,
  history: ChatMessageInterface[],
): MessageRequestParser => {
  return {
    question,
    history: history.map(({ role, text }) => ({ role, text })),
  };
};

// Raw shape returned by the backend's MessageResponseSerializer
export interface MessageResponseParser {
  reply: string;
  plan: PlanParser | null;
}

export interface MessageResponse {
  reply: string;
  plan?: PlanInterface;
}

// Converts the backend's snake_case message response into the frontend's camelCase shape
export const messageResponseParser = (dto: MessageResponseParser): MessageResponse => {
  return {
    reply: dto.reply,
    plan: dto.plan ? planParser(dto.plan) : undefined,
  };
};
