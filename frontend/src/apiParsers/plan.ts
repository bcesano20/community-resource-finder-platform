import type { PlanInterface, ResourceInterface } from '@/types';

// Raw shape returned by the backend's PlanSerializer (snake_case)
interface PlanStepParser {
  resource: ResourceInterface;
  why: string;
  next_step: string;
}

export interface PlanParser {
  steps: PlanStepParser[];
  follow_up_questions: string[];
}

// Converts the backend's snake_case plan shape into the frontend's camelCase PlanInterface.
// Shared by the queries and messages parsers, since both endpoints return this same shape.
export const planParser = (dto: PlanParser): PlanInterface => {
  return {
    steps: dto.steps.map((step) => ({
      resource: step.resource,
      why: step.why,
      nextStep: step.next_step,
    })),
    followUpQuestions: dto.follow_up_questions,
  };
};
