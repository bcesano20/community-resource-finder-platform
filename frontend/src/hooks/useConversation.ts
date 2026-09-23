import { useCallback, useState } from 'react';

import { sendMessagAPICall } from '@/api/messages';
import { submitQueryAPICall } from '@/api/queries';
import { useFollowUpLimit } from '@/hooks/useFollowUpLimit';
import { ERROR_MESSAGES, PLAN_READY_MESSAGE, WELCOME_CHAT_MESSAGE } from '@/helpers/constants';
import type { ApiErrorInterface, ChatMessageInterface } from '@/types';

interface UseConversationOptions {
  // Called on a 401 from the backend (expired or invalid session token), so
  // the app can drop back to the unlock screen.
  onSessionExpired: () => void;
}

export function useConversation({ onSessionExpired }: UseConversationOptions) {
  const [messages, setMessages] = useState<ChatMessageInterface[]>([WELCOME_CHAT_MESSAGE]);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasPlan, setHasPlan] = useState<boolean>(false);

  const { hasReachedLimit, registerFollowUp } = useFollowUpLimit();

  const handleError = useCallback(
    (err: unknown) => {
      const apiError = err as Partial<ApiErrorInterface>;
      if (apiError?.status === 401) {
        onSessionExpired();
        return;
      }
      setError(ERROR_MESSAGES.GENERIC_ERROR);
    },
    [onSessionExpired],
  );

  // First turn: the recorded audio, transcribed and planned by /api/queries/.
  const submitRecording = useCallback(
    async (audio: Blob) => {
      setIsSending(true);
      setError(null);

      try {
        const { transcript, plan } = await submitQueryAPICall(audio);

        setMessages((current) => [
          ...current,
          { id: crypto.randomUUID(), role: 'volunteer', text: transcript },
          { id: crypto.randomUUID(), role: 'assistant', text: PLAN_READY_MESSAGE, plan },
        ]);
        setHasPlan(true);
      } catch (err) {
        handleError(err);
      } finally {
        setIsSending(false);
      }
    },
    [handleError],
  );

  // Later turns: typed follow-up questions sent to /api/messages/, along with
  // the conversation so far (excluding the static welcome bubble, which is a
  // frontend-only affordance and was never part of the real exchange).
  const submitFollowUp = useCallback(
    async (question: string) => {
      setIsSending(true);
      setError(null);

      const history = messages.filter((message) => message.id !== WELCOME_CHAT_MESSAGE.id);
      const volunteerMessage: ChatMessageInterface = {
        id: crypto.randomUUID(),
        role: 'volunteer',
        text: question,
      };
      setMessages((current) => [...current, volunteerMessage]);

      try {
        const { reply, plan } = await sendMessagAPICall(question, history);
        registerFollowUp();
        setMessages((current) => [
          ...current,
          { id: crypto.randomUUID(), role: 'assistant', text: reply, plan },
        ]);
      } catch (err) {
        handleError(err);
      } finally {
        setIsSending(false);
      }
    },
    [messages, handleError, registerFollowUp],
  );

  return {
    messages,
    isSending,
    error,
    canAskFollowUp: hasPlan && !hasReachedLimit,
    submitRecording,
    submitFollowUp,
  };
}
