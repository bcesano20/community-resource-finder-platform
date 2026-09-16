import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { useAudioRecorder } from '../useAudioRecorder';

class MockMediaRecorder {
  static instances: MockMediaRecorder[] = [];

  ondataavailable: ((event: BlobEvent) => void) | null = null;
  onstop: (() => void) | null = null;

  start = vi.fn();
  stop = vi.fn(() => {
    this.onstop?.();
  });

  public constructor() {
    MockMediaRecorder.instances.push(this);
  }
}

describe('useAudioRecorder', () => {
  let stopTrackSpy: ReturnType<typeof vi.fn>;
  let getUserMediaMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    stopTrackSpy = vi.fn();
    const fakeStream = { getTracks: () => [{ stop: stopTrackSpy }] } as unknown as MediaStream;
    getUserMediaMock = vi.fn().mockResolvedValue(fakeStream);

    Object.defineProperty(navigator, 'mediaDevices', {
      value: { getUserMedia: getUserMediaMock },
      configurable: true,
    });
    vi.stubGlobal('MediaRecorder', MockMediaRecorder);
  });

  afterEach(() => {
    MockMediaRecorder.instances = [];
    vi.unstubAllGlobals();
  });

  it('starts with no recording and no audio yet', () => {
    const { result } = renderHook(() => useAudioRecorder());

    expect(result.current.isRecording).toBe(false);
    expect(result.current.audioBlob).toBeNull();
  });

  it('requests the mic and flips isRecording on startRecording', async () => {
    const { result } = renderHook(() => useAudioRecorder());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(getUserMediaMock).toHaveBeenCalledWith({ audio: true });
    expect(result.current.isRecording).toBe(true);
  });

  it('assembles the recorded chunks into a blob and releases the mic on stop', async () => {
    const { result } = renderHook(() => useAudioRecorder());

    await act(async () => {
      await result.current.startRecording();
    });

    const recorderInstance = MockMediaRecorder.instances.at(-1);
    act(() => {
      recorderInstance?.ondataavailable?.({ data: new Blob(['chunk']) } as BlobEvent);
    });

    act(() => {
      result.current.stopRecording();
    });

    expect(result.current.isRecording).toBe(false);
    expect(result.current.audioBlob).toBeInstanceOf(Blob);
    expect(result.current.audioBlob?.type).toBe('audio/webm');
    expect(stopTrackSpy).toHaveBeenCalledTimes(1);
  });
});
