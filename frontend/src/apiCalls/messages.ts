import { API_ROUTES } from '@/helpers/constants';
import type { ChatMessageInterface } from '@/types';
import {
  messageRequestParser,
  messageResponseParser,
  type MessageResponse,
  type MessageResponseParser,
} from '@/apiParsers/messages';
import { apiRequest } from '@/api/client';

// The text message to send to the AI with the chat history
export async function sendMessagAPICall(
  question: string,
  history: ChatMessageInterface[],
): Promise<MessageResponse> {
  const response = await apiRequest<MessageResponseParser>(API_ROUTES.messages, {
    method: 'POST',
    body: messageRequestParser(question, history),
  });

  return messageResponseParser(response);
}
