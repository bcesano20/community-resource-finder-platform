import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { MAX_FOLLOW_UP_QUESTIONS } from '@/helpers/constants';
import { useFollowUpLimit } from '../useFollowUpLimit';

describe('useFollowUpLimit', () => {
  it('starts at zero, under the limit', () => {
    const { result } = renderHook(() => useFollowUpLimit());

    expect(result.current.count).toBe(0);
    expect(result.current.remaining).toBe(MAX_FOLLOW_UP_QUESTIONS);
    expect(result.current.hasReachedLimit).toBe(false);
  });

  it('increments count and decreases remaining without reaching the limit', () => {
    const { result } = renderHook(() => useFollowUpLimit());

    act(() => {
      result.current.registerFollowUp();
    });

    expect(result.current.count).toBe(1);
    expect(result.current.remaining).toBe(MAX_FOLLOW_UP_QUESTIONS - 1);
    expect(result.current.hasReachedLimit).toBe(false);
  });

  it('flags hasReachedLimit once the count hits the max', () => {
    const { result } = renderHook(() => useFollowUpLimit());

    act(() => {
      for (let i = 0; i < MAX_FOLLOW_UP_QUESTIONS; i += 1) {
        result.current.registerFollowUp();
      }
    });

    expect(result.current.count).toBe(MAX_FOLLOW_UP_QUESTIONS);
    expect(result.current.remaining).toBe(0);
    expect(result.current.hasReachedLimit).toBe(true);
  });

  it('caps the count at the max even if registerFollowUp is called past the limit', () => {
    const { result } = renderHook(() => useFollowUpLimit());

    act(() => {
      result.current.registerFollowUp();
      result.current.registerFollowUp();
      result.current.registerFollowUp();
    });

    expect(result.current.count).toBe(MAX_FOLLOW_UP_QUESTIONS);
    expect(result.current.hasReachedLimit).toBe(true);
  });
});
