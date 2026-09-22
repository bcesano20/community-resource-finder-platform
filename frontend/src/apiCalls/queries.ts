import { API_ROUTES } from '@/helpers/constants';
import {
  queryResponseParser,
  type QueryResponse,
  type QueryResponseParser,
} from '@/apiParsers/queries';
import { apiRequest } from '@/api/client';

// Send the audio message to the AI model
export async function submitQueryAPICall(audio: Blob): Promise<QueryResponse> {
  const formData = new FormData();
  formData.append('audio', audio);

  const response = await apiRequest<QueryResponseParser>(API_ROUTES.queries, {
    method: 'POST',
    body: formData,
  });

  return queryResponseParser(response);
}
