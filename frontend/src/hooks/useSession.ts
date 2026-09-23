import { useCallback, useState } from 'react';

import { ERROR_MESSAGES, SESSION_TOKEN_STORAGE_KEY } from '@/helpers/constants';
import { createSessionAPICall } from '@/api/session';

export function useSession() {
  const [isUnlocked, setIsUnlocked] = useState<boolean>(
    () => sessionStorage.getItem(SESSION_TOKEN_STORAGE_KEY) !== null,
  );
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const unlock = useCallback(async (accessCode: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const { token } = await createSessionAPICall(accessCode);
      sessionStorage.setItem(SESSION_TOKEN_STORAGE_KEY, token);
      setIsUnlocked(true);
    } catch {
      setError(ERROR_MESSAGES.INVALID_ACCESS_CODE);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Drops back to the unlock screen — used both for an explicit sign-out and
  // for a 401 from the backend (session token expired or was never valid).
  const lock = useCallback((message?: string) => {
    sessionStorage.removeItem(SESSION_TOKEN_STORAGE_KEY);
    setIsUnlocked(false);
    setError(message ?? null);
  }, []);

  return { isUnlocked, isLoading, error, unlock, lock };
}
