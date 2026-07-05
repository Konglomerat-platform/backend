from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.innovation.api.serializers import RndSubmissionSerializer
from apps.innovation.models import RndSubmission
from apps.innovation.services import create_submission, submissions_for_user, update_submission
from core.utils import get_by_external


class RndSubmissionViewSet(ModelViewSet):
    serializer_class = RndSubmissionSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r"[^/]+"
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_queryset(self):
        return submissions_for_user(self.request.user, self.request.query_params.get("company"))

    def get_object(self):
        submission = get_by_external(RndSubmission, self.kwargs[self.lookup_field])
        if not submission:
            raise NotFound()
        self.check_object_permissions(self.request, submission)
        return submission

    def create(self, request, *args, **kwargs):
        item = create_submission(request.user, request.data)
        return Response(self.get_serializer(item).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        item = update_submission(request.user, kwargs[self.lookup_field], request.data)
        return Response(self.get_serializer(item).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
