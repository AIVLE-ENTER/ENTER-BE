from django.http import JsonResponse
from enter import models
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# 아이디 중복 체크 (중복시 사용불가, 중복되지 않을시 사용 가능 응답)
def check_id_duplicate(request):
    check_id = request.GET.get("id")
    is_available = not models.Users.objects.filter(user_id=check_id).exists()
    return JsonResponse({"is_available": is_available})
