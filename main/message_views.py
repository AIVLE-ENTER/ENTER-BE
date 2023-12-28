from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from utils.common import validate_token
from enter import models
import json


# 자주쓰는 문구 리스트
def frequent_message_list(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 문구
    messages = models.Prompttemplates.objects.filter(user=user, is_deleted=False)
    message_list = []
    for message in messages:
        message_data = {
            "template_id": message.template_id,
            "template_name": message.template_name,
            "template_content": message.template_content,
            "created_datetime": message.created_datetime,
            "modified_datetime": message.modified_datetime,
        }
        message_list.append(message_data)

    # 응답
    response_data = {
        "success": True,
        "message": "자주쓰는 문구를 불러왔습니다.",
        "data": {"message_list": message_list},
    }
    return JsonResponse(response_data, status=200)
