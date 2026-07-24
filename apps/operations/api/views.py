from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.ai.models import AiInteraction
from apps.catalog.models import Product
from apps.companies.models import Company
from apps.innovation.models import RndSubmission
from apps.operations.api.serializers import (
    ConferenceSerializer,
    ManagementModuleSerializer,
    ReportSerializer,
)
from apps.operations.models import Conference, ManagementModule
from apps.operations.services import create_conference, delete_conference, generate_report, join_conference, update_module
from apps.support.models import Complaint
from apps.users.permissions import IsAdminRole
from core.utils import get_by_external


class StatsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses=inline_serializer(
            name="StatsResponse",
            fields={
                "companies": serializers.IntegerField(),
                "aiRequests": serializers.IntegerField(),
                "startups": serializers.IntegerField(),
                "showrooms": serializers.IntegerField(),
                "complaints": serializers.IntegerField(),
                "conferences": serializers.IntegerField(),
            },
        )
    )
    def get(self, _request):
        # Every value here is a plain count of what is in the database. These
        # numbers are published on the public homepage, so they must not be
        # floored, padded or otherwise inflated: an empty platform has to be
        # able to report zero.
        return Response(
            {
                "companies": Company.objects.filter(active=True).count(),
                # One AiInteraction row is written per AI request, including
                # off-topic ones and those from signed-in users. AiUsage
                # .prompt_count is not usable here: it only tracks anonymous
                # on-topic requests and stops incrementing at the free limit.
                "aiRequests": AiInteraction.objects.count(),
                "startups": RndSubmission.objects.count(),
                "showrooms": Product.objects.count(),
                "complaints": Complaint.objects.filter(status=Complaint.Status.PENDING).count(),
                "conferences": Conference.objects.count(),
            }
        )


class ConferenceViewSet(ModelViewSet):
    serializer_class = ConferenceSerializer
    permission_classes = [AllowAny]
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        return Conference.objects.prefetch_related("attendances")

    def get_object(self):
        conference = get_by_external(Conference, self.kwargs[self.lookup_field])
        if not conference:
            raise NotFound()
        self.check_object_permissions(self.request, conference)
        return conference

    def create(self, request, *args, **kwargs):
        conference = create_conference(request.user, request.data)
        return Response(self.get_serializer(conference).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        delete_conference(request.user, kwargs[self.lookup_field])
        return Response({"ok": True})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, *args, **kwargs):
        conference = join_conference(request.user, kwargs[self.lookup_field])
        return Response(self.get_serializer(conference).data)


class ManagementModuleViewSet(GenericViewSet):
    serializer_class = ManagementModuleSerializer
    permission_classes = [IsAdminRole]
    lookup_field = "key"
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        return ManagementModule.objects.all()

    def list(self, request):
        return Response({module.key: module.enabled for module in self.get_queryset()})

    def update(self, request, *args, **kwargs):
        module = update_module(request.user, kwargs[self.lookup_field], bool(request.data.get("enabled")))
        return Response(self.get_serializer(module).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ReportGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OpenApiTypes.NONE, responses=ReportSerializer)
    def post(self, request):
        report = generate_report(request.user)
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
