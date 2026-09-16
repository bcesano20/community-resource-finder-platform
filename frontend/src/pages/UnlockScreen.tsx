import { useState } from 'react';

import { ERROR_MESSAGES } from '@/helpers/constants';
import { useSession } from '@/hooks/useSession';

interface UnlockScreenProps {
  onUnlock: () => void;
}

export function UnlockScreen({ onUnlock }: UnlockScreenProps) {
  const [accessCode, setAccessCode] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // TODO: export 'unlock' from the hook when the backend be ready, currently is the flow bypass that auth
  const { isLoading, error } = useSession();

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (!accessCode.trim()) {
      setErrorMsg(ERROR_MESSAGES.EMPTY_CODE);
      return;
    }

    setErrorMsg(null);

    // TODO (testing only, remove once /api/session/ exists): any non-empty code unlocks without calling the backend
    // void unlock(accessCode);
    onUnlock();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-1 flex-col justify-center gap-4 bg-gradient-to-br from-blue-700 via-blue-500 to-blue-300 p-6"
    >
      <h1 className="text-xl font-semibold text-white">Enter access code</h1>
      <input
        type="text"
        inputMode="text"
        aria-label="Access code"
        value={accessCode}
        onChange={(event) => setAccessCode(event.target.value)}
        className="rounded-lg border border-gray-300 px-4 py-3 text-base"
      />
      {errorMsg ? (
        <p className="text-sm text-gray-800 font-bold">{errorMsg}</p>
      ) : error ? (
        <p className="text-sm text-gray-800 font-bold">{error}</p>
      ) : null}
      <button
        type="submit"
        disabled={isLoading}
        className="rounded-lg bg-blue-800 px-4 py-3 font-medium text-white disabled:opacity-50"
      >
        {isLoading ? 'Checking...' : 'Continue'}
      </button>
    </form>
  );
}
