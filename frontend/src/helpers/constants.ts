import type { ChatMessageInterface } from '@/types';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export const API_ROUTES = {
  session: '/api/session/',
  queries: '/api/queries/',
  messages: '/api/messages/',
} as const;

export const MAX_FOLLOW_UP_QUESTIONS = 2;

export const SESSION_TOKEN_STORAGE_KEY = 'communityResourceFinder.sessionToken';

export const ERROR_MESSAGES = {
  INVALID_ACCESS_CODE: 'That access code is not valid. Please try again.',
  EMPTY_CODE: 'Please, enter the code.',
  NETWORK_ERROR: 'Something went wrong. Please check your connection and try again.',
  GENERIC_ERROR: 'Something went wrong. Please try again.',
  SESSION_EXPIRED: 'Your session expired. Please enter the access code again.',
  EMPTY_FOLLOW_UP: 'Please, type a question before sending.',
} as const;

export const WELCOME_CHAT_MESSAGE: ChatMessageInterface = {
  id: 'welcome',
  role: 'assistant',
  text: "Record what the person shares about their situation, and I'll help put together an action plan using community resources in this area.",
};

// /api/queries/ only returns a transcript + plan, no conversational reply text
export const PLAN_READY_MESSAGE = "Here's a plan based on what you shared:";

// like /api/messages/ does, so this is the assistant bubble shown alongside it.
export const FOLLOW_UP_INPUT_PLACEHOLDER = 'Ask a follow-up question…';
