from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import SessionTokenAuthentication
from core.serializers import MessageRequestSerializer, MessageResponseSerializer
from core.services.plan_service import generate_followup_response


class MessageView(APIView):
    authentication_classes = [SessionTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        request_serializer = MessageRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        result = generate_followup_response(
            message=validated_data["question"],
            history=validated_data["history"],
            follow_up_count=validated_data["follow_up_count"],
        )

        response_serializer = MessageResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
