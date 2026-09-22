from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import SessionRequestSerializer, SessionResponseSerializer
from core.services.session_service import create_session


class SessionView(APIView):
    def post(self, request: Request) -> Response:
        request_serializer = SessionRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        session = create_session(request_serializer.validated_data["access_code"])

        response_serializer = SessionResponseSerializer(session)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
