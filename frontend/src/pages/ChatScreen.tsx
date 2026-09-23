import { useState } from 'react';

import type { ChatMessageRole } from '@/types';
import { ERROR_MESSAGES, FOLLOW_UP_INPUT_PLACEHOLDER } from '@/helpers/constants';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { useConversation } from '@/hooks/useConversation';
import { ChatBubble, PlanCard } from '@/components';

const ASSISTANT_ROLE: ChatMessageRole = 'assistant';

interface ChatScreenProps {
  onSessionExpired: () => void;
}

export function ChatScreen({ onSessionExpired }: ChatScreenProps) {
  const { isRecording, startRecording, stopRecording } = useAudioRecorder();
  const { messages, isSending, error, canAskFollowUp, submitRecording, submitFollowUp } =
    useConversation({ onSessionExpired });
  const [followUpText, setFollowUpText] = useState<string>('');
  const [followUpError, setFollowUpError] = useState<string | null>(null);

  const handleMicClick = async () => {
    if (isRecording) {
      const audio = await stopRecording();
      void submitRecording(audio);
      return;
    }

    await startRecording();
  };

  const handleFollowUpSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (!followUpText.trim()) {
      setFollowUpError(ERROR_MESSAGES.EMPTY_FOLLOW_UP);
      return;
    }

    setFollowUpError(null);
    void submitFollowUp(followUpText.trim());
    setFollowUpText('');
  };

  return (
    <div className="flex flex-1 flex-col p-6 bg-gradient-to-br from-blue-700 via-blue-500 to-blue-300">
      <div className="flex-1 space-y-3 overflow-y-auto p-4 bg-gray-100 rounded-2xl">
        {messages.map((message) => (
          <div key={message.id} className="space-y-2">
            <ChatBubble role={message.role} text={message.text} />
            {message.plan?.steps.map((step) => (
              <PlanCard key={step.resource.id} step={step} />
            ))}
            {message.plan?.followUpQuestions.length ? (
              <ul className="ml-2 list-disc space-y-1 text-sm text-gray-600">
                {message.plan.followUpQuestions.map((question) => (
                  <li key={question}>{question}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ))}
        {isSending ? <ChatBubble role={ASSISTANT_ROLE} text="Thinking…" /> : null}
      </div>

      {error ? <p className="px-4 text-sm font-bold text-red-700">{error}</p> : null}

      {canAskFollowUp ? (
        <form onSubmit={handleFollowUpSubmit} className="flex gap-2 px-4 pb-2">
          <input
            type="text"
            aria-label="Follow-up question"
            placeholder={FOLLOW_UP_INPUT_PLACEHOLDER}
            value={followUpText}
            onChange={(event) => setFollowUpText(event.target.value)}
            disabled={isSending}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-base disabled:opacity-50"
          />
          <button
            type="submit"
            aria-label="Send"
            disabled={isSending}
            className="rounded-lg bg-blue-800 px-4 py-2 font-medium text-white disabled:opacity-50"
          >
            <span aria-hidden="true">📨</span>
          </button>
        </form>
      ) : null}
      {followUpError ? (
        <p className="px-4 text-sm font-bold text-red-700">{followUpError}</p>
      ) : null}

      <div className="flex justify-center p-4">
        <button
          type="button"
          aria-label={isRecording ? 'Stop recording' : 'Start recording'}
          onClick={() => void handleMicClick()}
          disabled={isSending}
          className={`flex h-16 w-16 items-center justify-center rounded-full text-2xl disabled:opacity-50 ${
            isRecording ? 'bg-red-600' : 'bg-blue-600'
          }`}
        >
          <span aria-hidden="true">🎤</span>
        </button>
      </div>
    </div>
  );
}
