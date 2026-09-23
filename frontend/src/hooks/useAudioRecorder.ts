import { useCallback, useRef, useState } from 'react';

export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const stopResolveRef = useRef<((blob: Blob) => void) | null>(null);

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    chunksRef.current = [];

    mediaRecorder.ondataavailable = (event) => {
      chunksRef.current.push(event.data);
    };
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      setAudioBlob(blob);

      // release the mic so the browser's recording indicator turns off
      stream.getTracks().forEach((track) => track.stop());

      stopResolveRef.current?.(blob);
      stopResolveRef.current = null;
    };

    mediaRecorder.start();
    mediaRecorderRef.current = mediaRecorder;
    setIsRecording(true);
  }, []);

  // Returns a promise instead of relying on the `audioBlob` state, since the
  // blob is only assembled asynchronously inside `onstop` — callers that need
  // the recording right after stopping (e.g. to submit it) can await this.
  const stopRecording = useCallback((): Promise<Blob> => {
    setIsRecording(false);

    return new Promise((resolve) => {
      stopResolveRef.current = resolve;
      mediaRecorderRef.current?.stop();
    });
  }, []);

  return { isRecording, audioBlob, startRecording, stopRecording };
}
