from rest_framework.routers import DefaultRouter

from apps.communications.api.views import ChatMessageViewSet

router = DefaultRouter()
router.register("chat/messages", ChatMessageViewSet, basename="chat-message")

urlpatterns = router.urls
