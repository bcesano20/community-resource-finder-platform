from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import SessionTokenAuthentication
from core.serializers import QueryRequestSerializer, QueryResponseSerializer
from core.services.plan_service import generate_plan
from core.services.transcription_service import transcribe_audio


class QueryView(APIView):
    authentication_classes = [SessionTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        request_serializer = QueryRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        transcript = transcribe_audio(request_serializer.validated_data["audio"])
        plan = generate_plan(transcript)

        response_serializer = QueryResponseSerializer({"transcript": transcript, "plan": plan})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
