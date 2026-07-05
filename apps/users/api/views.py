from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services import login_response, logout_response, refresh_response, user_payload


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return login_response(
            request,
            str(request.data.get("username", "")),
            request.data.get("password", ""),
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME) or request.data.get("refresh")
        return refresh_response(raw_refresh)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME) or request.data.get("refresh")
        return logout_response(raw_refresh)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": user_payload(request.user)})
