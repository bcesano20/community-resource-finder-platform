import type { ChatMessageRole } from '@/types';

interface ChatBubbleProps {
  role: ChatMessageRole;
  text: string;
}

export function ChatBubble({ role, text }: ChatBubbleProps) {
  // This is the volunteer chat message interaction
  const isVolunteer = role === 'volunteer';

  return (
    <div className={`flex ${isVolunteer ? 'justify-end' : 'justify-start'}`}>
      <p
        className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
          isVolunteer ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
        }`}
      >
        {text}
      </p>
    </div>
  );
}
