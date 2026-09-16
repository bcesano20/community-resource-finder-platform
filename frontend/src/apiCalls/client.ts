import { API_BASE_URL, SESSION_TOKEN_STORAGE_KEY } from '@/helpers/constants';
import type { ApiErrorInterface } from '@/types';

interface RequestOptions {
  method?: 'GET' | 'POST';
  body?: unknown | FormData;
}

// General Api Call function
// The <TResponse> gives us a generic return type to avoid use any and can use different response types in each apiCall
export async function apiRequest<TResponse>(
  path: string,
  { method = 'GET', body }: RequestOptions = {},
): Promise<TResponse> {
  // Check the type of the body and the existance of the session token to know what kynd of header send
  const sessionToken = sessionStorage.getItem(SESSION_TOKEN_STORAGE_KEY);
  const isFormData = body instanceof FormData;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(sessionToken ? { Authorization: `Bearer ${sessionToken}` } : {}),
    },

    // When the body is a form it will send as is, else if the body exists it will send stringified as JSON, else send undefined, for example for a GET without body
    body: isFormData ? body : body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error: ApiErrorInterface = {
      message: response.statusText,
      status: response.status,
    };
    throw error;
  }

  return response.json() as Promise<TResponse>;
}
