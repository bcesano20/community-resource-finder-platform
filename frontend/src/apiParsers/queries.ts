import type { PlanInterface } from '@/types';
import { planParser, type PlanParser } from '@/apiParsers/plan';

// Raw shape returned by the backend's QueryResponseSerializer
export interface QueryResponseParser {
  transcript: string;
  plan: PlanParser;
}

export interface QueryResponse {
  transcript: string;
  plan: PlanInterface;
}

// Converts the backend's snake_case query response into the frontend's camelCase shape
export const queryResponseParser = (dto: QueryResponseParser): QueryResponse => {
  return {
    transcript: dto.transcript,
    plan: planParser(dto.plan),
  };
};
