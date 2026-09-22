from rest_framework import serializers


class SessionRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField()


class SessionResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
