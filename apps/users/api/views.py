from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services import login_response, logout_response, refresh_response, user_payload


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="LoginRequest",
            fields={
                "username": serializers.CharField(),
                "password": serializers.CharField(write_only=True),
            },
        ),
        responses=OpenApiTypes.OBJECT,
    )
    def post(self, request):
        return login_response(
            request,
            str(request.data.get("username", "")),
            request.data.get("password", ""),
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="RefreshRequest",
            fields={"refresh": serializers.CharField(required=False, allow_blank=True)},
        ),
        responses=OpenApiTypes.OBJECT,
    )
    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME) or request.data.get("refresh")
        return refresh_response(raw_refresh)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="LogoutRequest",
            fields={"refresh": serializers.CharField(required=False, allow_blank=True)},
        ),
        responses=OpenApiTypes.OBJECT,
    )
    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME) or request.data.get("refresh")
        return logout_response(raw_refresh)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response({"user": user_payload(request.user)})
