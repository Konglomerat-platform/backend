from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.models import AiInteraction, AiUsage
from apps.ai.services import ai_letter, ai_reply, on_topic
from apps.catalog.models import Product
from apps.content.models import NewsArticle
from apps.innovation.models import RndSubmission
from apps.operations.models import Conference
from apps.support.models import Complaint


class AiUsageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        visitor = request.query_params.get("visitor") or ""
        usage = AiUsage.objects.filter(visitor_id=visitor).first()
        used = usage.prompt_count if usage else 0
        return Response({"used": used, "remaining": max(0, 3 - used), "locked": used >= 3})


class AiChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = str(request.data.get("message") or "")
        lang = request.data.get("lang") or "ru"
        topic = on_topic(message)
        user = request.user if request.user.is_authenticated else None

        if user:
            if not topic:
                AiInteraction.objects.create(user=user, prompt=message, lang=lang, off_topic=True)
                return Response({"offtopic": True, "reply": None, "remaining": None, "locked": False})
            reply = _reply(message, lang)
            AiInteraction.objects.create(user=user, prompt=message, reply=reply, lang=lang)
            return Response({"offtopic": False, "reply": reply, "remaining": None, "locked": False})

        visitor = request.data.get("visitor") or ""
        if not visitor:
            return Response({"error": "no_visitor"}, status=400)
        usage, _ = AiUsage.objects.get_or_create(visitor_id=visitor)
        if usage.prompt_count >= 3:
            return Response({"locked": True, "remaining": 0, "reply": None, "offtopic": False})
        if not topic:
            AiInteraction.objects.create(visitor_id=visitor, prompt=message, lang=lang, off_topic=True)
            return Response(
                {
                    "offtopic": True,
                    "reply": None,
                    "remaining": max(0, 3 - usage.prompt_count),
                    "locked": False,
                }
            )
        usage.prompt_count += 1
        usage.save(update_fields=["prompt_count", "updated_at"])
        reply = _reply(message, lang)
        AiInteraction.objects.create(visitor_id=visitor, prompt=message, reply=reply, lang=lang)
        return Response(
            {
                "offtopic": False,
                "reply": reply,
                "remaining": max(0, 3 - usage.prompt_count),
                "locked": usage.prompt_count >= 3,
            }
        )


class AiLetterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company_name = request.user.company.name if request.user.company_id else request.user.public_name
        return Response(
            ai_letter(
                str(request.data.get("message") or ""),
                request.data.get("lang") or "ru",
                company_name,
                request.data.get("attachments") or [],
            )
        )


def _reply(message: str, lang: str) -> str:
    return ai_reply(
        message,
        lang,
        products=Product.objects.select_related("company"),
        news=NewsArticle.objects.all(),
        conferences=Conference.objects.all(),
        complaints=Complaint.objects.all(),
        rnd=RndSubmission.objects.all(),
    )
