import { useState } from 'react';

import { Layout } from './Layout';

import { ChatScreen } from './pages/ChatScreen';
import { UnlockScreen } from './pages/UnlockScreen';
import { WELCOME_CHAT_MESSAGE } from './helpers/constants';

export function App() {
  const [isUnlocked, setIsUnlocked] = useState<boolean>(false);

  return (
    <Layout>
      {isUnlocked ? (
        <ChatScreen messages={[WELCOME_CHAT_MESSAGE]} />
      ) : (
        <UnlockScreen onUnlock={() => setIsUnlocked(true)} />
      )}
    </Layout>
  );
}
