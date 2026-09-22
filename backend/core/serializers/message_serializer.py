from rest_framework import serializers

from core.serializers.query_serializer import PlanSerializer


class ChatHistoryEntrySerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["volunteer", "assistant"])
    text = serializers.CharField()


class MessageRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    history = ChatHistoryEntrySerializer(many=True, required=False, default=list)

    def to_internal_value(self, data: dict) -> dict:
        validated = super().to_internal_value(data)

        # plan_service.generate_followup_response expects history already in
        # Anthropic's {role: "user" | "assistant", content} shape, and a
        # follow_up_count — derived here since the backend is stateless
        # (README) and only ever sees the history the frontend resends.
        follow_up_count = sum(1 for entry in validated["history"] if entry["role"] == "assistant")
        anthropic_history = [
            {
                "role": "user" if entry["role"] == "volunteer" else "assistant",
                "content": entry["text"],
            }
            for entry in validated["history"]
        ]

        return {
            "question": validated["question"],
            "history": anthropic_history,
            "follow_up_count": follow_up_count,
        }


class MessageResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    plan = PlanSerializer(allow_null=True)
