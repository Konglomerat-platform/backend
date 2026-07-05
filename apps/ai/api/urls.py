from django.urls import path

from apps.ai.api.views import AiChatView, AiLetterView, AiUsageView

urlpatterns = [
    path("ai/usage/", AiUsageView.as_view(), name="ai-usage"),
    path("ai/chat/", AiChatView.as_view(), name="ai-chat"),
    path("ai/letter/", AiLetterView.as_view(), name="ai-letter"),
]
