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

    def get(self, _request):
        return Response(
            {
                "companies": max(30, Company.objects.filter(active=True).count()),
                "aiRequests": max(4820, AiInteraction.objects.count()),
                "startups": RndSubmission.objects.count() + 10,
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

    def post(self, request):
        report = generate_report(request.user)
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
