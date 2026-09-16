import { API_ROUTES } from '@/helpers/constants';
import type { PlanInterface } from '@/types';
import { apiRequest } from '@/api/client';

// Specific Response Type for this apiCall
interface SubmitQueryResponse {
  transcript: string;
  plan: PlanInterface;
}

// Send the audio message to the AI model
export function submitQueryAPICall(audio: Blob): Promise<SubmitQueryResponse> {
  const formData = new FormData();
  formData.append('audio', audio);

  return apiRequest<SubmitQueryResponse>(API_ROUTES.queries, {
    method: 'POST',
    body: formData,
  });
}
