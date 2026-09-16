import { API_ROUTES } from '@/helpers/constants';
import type { ChatMessageInterface, PlanInterface } from '@/types';
import { apiRequest } from '@/api/client';

// Specific Response Type for that apiCall
interface SendMessageResponse {
  reply: string;
  plan?: PlanInterface;
}

// The text message to send to the AI with the chat history
export function sendMessagAPICall(
  question: string,
  history: ChatMessageInterface[],
): Promise<SendMessageResponse> {
  return apiRequest<SendMessageResponse>(API_ROUTES.messages, {
    method: 'POST',
    body: { question, history },
  });
}
