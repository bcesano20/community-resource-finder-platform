import { useCallback, useState } from 'react';

import { MAX_FOLLOW_UP_QUESTIONS } from '@/helpers/constants';

export function useFollowUpLimit() {
  const [count, setCount] = useState<number>(0);

  const registerFollowUp = useCallback(() => {
    setCount((current) => Math.min(current + 1, MAX_FOLLOW_UP_QUESTIONS));
  }, []);

  const hasReachedLimit = count >= MAX_FOLLOW_UP_QUESTIONS;
  const remaining = MAX_FOLLOW_UP_QUESTIONS - count;

  return { count, remaining, hasReachedLimit, registerFollowUp };
}
