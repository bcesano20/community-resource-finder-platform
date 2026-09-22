from rest_framework import serializers


class QueryRequestSerializer(serializers.Serializer):
    audio = serializers.FileField()


class ResourceSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    category = serializers.CharField()
    description = serializers.CharField()
    address = serializers.CharField()
    phone = serializers.CharField()
    hours = serializers.CharField()


class PlanStepSerializer(serializers.Serializer):
    resource = ResourceSerializer()
    why = serializers.CharField()
    next_step = serializers.CharField()


class PlanSerializer(serializers.Serializer):
    steps = PlanStepSerializer(many=True)
    follow_up_questions = serializers.ListField(child=serializers.CharField())


class QueryResponseSerializer(serializers.Serializer):
    transcript = serializers.CharField()
    plan = PlanSerializer()
