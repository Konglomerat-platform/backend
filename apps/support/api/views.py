from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.support.api.serializers import ComplaintSerializer
from apps.support.models import Complaint
from apps.support.services import create_complaint, delete_complaint, update_complaint
from apps.users.permissions import IsAdminRole
from core.utils import get_by_external


class ComplaintViewSet(ModelViewSet):
    serializer_class = ComplaintSerializer
    lookup_value_regex = r"[^/]+"

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        return Complaint.objects.select_related("from_company").prefetch_related("attachments")

    def get_object(self):
        complaint = get_by_external(Complaint, self.kwargs[self.lookup_field])
        if not complaint:
            raise NotFound()
        self.check_object_permissions(self.request, complaint)
        return complaint

    def create(self, request, *args, **kwargs):
        complaint = create_complaint(request.user, request.data)
        return Response(self.get_serializer(complaint).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        complaint = update_complaint(request.user, kwargs[self.lookup_field], request.data)
        return Response(self.get_serializer(complaint).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        delete_complaint(request.user, kwargs[self.lookup_field])
        return Response({"ok": True})
