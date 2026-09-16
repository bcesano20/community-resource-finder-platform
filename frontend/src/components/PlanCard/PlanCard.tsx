import type { PlanStepInterface } from '@/types';

interface PlanCardProps {
  step: PlanStepInterface;
}

export function PlanCard({ step }: PlanCardProps) {
  const { resource, nextStep } = step;

  // Just show the info from the response in a card format
  return (
    <div className="rounded-xl border border-gray-200 p-4 shadow-sm">
      <h3 className="font-semibold text-gray-900">{resource.name}</h3>
      <p className="text-sm text-gray-600">{resource.category}</p>
      <p className="mt-2 text-sm text-gray-700">{resource.address}</p>
      <p className="text-sm text-gray-700">{resource.phone}</p>
      <p className="text-sm text-gray-700">{resource.hours}</p>
      <p className="mt-3 text-sm font-medium text-blue-700">Next step: {nextStep}</p>
    </div>
  );
}
