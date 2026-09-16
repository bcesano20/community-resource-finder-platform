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
} as const;

export const WELCOME_CHAT_MESSAGE: ChatMessageInterface = {
  id: 'welcome',
  role: 'assistant',
  text: "Record what the person shares about their situation, and I'll help put together an action plan using community resources in this area.",
};
