import type { ChatMessageInterface } from '@/types';
import { ChatBubble, PlanCard } from '@/components';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';

interface ChatScreenProps {
  messages: ChatMessageInterface[];
}

export function ChatScreen({ messages }: ChatScreenProps) {
  const { isRecording, startRecording, stopRecording } = useAudioRecorder();

  return (
    <div className="flex flex-1 flex-col p-10">
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.map((message) => (
          <div key={message.id} className="space-y-2">
            <ChatBubble role={message.role} text={message.text} />
            {message.plan?.steps.map((step) => (
              <PlanCard key={step.resource.id} step={step} />
            ))}
          </div>
        ))}
      </div>
      <div className="flex justify-center p-4">
        <button
          type="button"
          aria-label={isRecording ? 'Stop recording' : 'Start recording'}
          onClick={() => (isRecording ? stopRecording() : void startRecording())}
          className={`flex h-16 w-16 items-center justify-center rounded-full text-2xl ${
            isRecording ? 'bg-red-600' : 'bg-blue-600'
          }`}
        >
          <span aria-hidden="true">🎤</span>
        </button>
      </div>
    </div>
  );
}
