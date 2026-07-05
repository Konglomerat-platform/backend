from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api.serializers import UserPayloadSerializer


def user_payload(user) -> dict:
    return UserPayloadSerializer(user).data


def _token_pair(user):
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["name"] = user.public_name
    access = refresh.access_token
    access["role"] = user.role
    access["name"] = user.public_name
    return refresh, access


def _set_refresh_cookie(response: Response, refresh: RefreshToken) -> None:
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        str(refresh),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path="/api/auth/",
    )


def login_response(request, username: str, password: str) -> Response:
    user = authenticate(request, username=username.strip(), password=password)
    if not user:
        return Response({"error": "invalid_credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    refresh, access = _token_pair(user)
    response = Response({"access": str(access), "token": str(access), "user": user_payload(user)})
    _set_refresh_cookie(response, refresh)
    return response


def refresh_response(raw_refresh: str | None) -> Response:
    if not raw_refresh:
        return Response({"error": "no_refresh"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        old = RefreshToken(raw_refresh)
        user = get_user_model().objects.get(pk=old["user_id"], is_active=True)
        old.blacklist()
        refresh, access = _token_pair(user)
    except (TokenError, get_user_model().DoesNotExist, KeyError):
        return Response({"error": "invalid_refresh"}, status=status.HTTP_401_UNAUTHORIZED)
    response = Response({"access": str(access), "token": str(access), "user": user_payload(user)})
    _set_refresh_cookie(response, refresh)
    return response


def logout_response(raw_refresh: str | None) -> Response:
    if raw_refresh:
        try:
            RefreshToken(raw_refresh).blacklist()
        except TokenError:
            pass
    response = Response({"ok": True})
    response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME, path="/api/auth/")
    return response
