import { Layout } from './Layout';

import { Footer } from './components';
import { ChatScreen } from './pages/ChatScreen';
import { UnlockScreen } from './pages/UnlockScreen';
import { useSession } from './hooks/useSession';

export function App() {
  const { isUnlocked, isLoading, error, unlock, lock } = useSession();

  return (
    <Layout>
      {isUnlocked ? (
        <ChatScreen onSessionExpired={lock} />
      ) : (
        <UnlockScreen isLoading={isLoading} error={error} onUnlock={unlock} />
      )}
      <Footer />
    </Layout>
  );
}
