import { API_ROUTES } from '@/helpers/constants';
import { apiRequest } from '@/api/client';

// Specific Response Type for this apiCall
interface CreateSessionResponse {
  token: string;
}

export function createSessionAPICall(accessCode: string): Promise<CreateSessionResponse> {
  return apiRequest<CreateSessionResponse>(API_ROUTES.session, {
    method: 'POST',
    body: { accessCode },
  });
}
