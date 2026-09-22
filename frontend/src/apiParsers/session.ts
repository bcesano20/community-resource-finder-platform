// Raw shape expected by the backend's SessionRequestSerializer (snake_case)
export interface SessionRequestParser {
  access_code: string;
}

// Converts the frontend's camelCase access code into the backend's snake_case request shape
export const sessionRequestParser = (accessCode: string): SessionRequestParser => {
  return { access_code: accessCode };
};
