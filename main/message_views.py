from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from utils.common import validate_token
from enter import models
import json


# 길이 유효성 검사
def validate_length(validations: list, max_length: list) -> (bool, dict):
    errors = []
    i = 0
    for target, value in validations:
        if len(value) > max_length[i]:
            errors.append(target)
        i += 1

    if errors:
        response_data = {
            "success": False,
            "message": "오류: 유효성 검사 (길이)",
            "errors": {"validation": errors},
        }
        return False, response_data
    else:
        return True, {}


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


# 자주쓰는 문구 생성
@csrf_exempt
@require_POST
def create_frequent_message(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    template_name = json_data.get("template_name")
    template_content = json_data.get("template_content")

    # 필수 데이터 누락
    if template_name is None or template_content is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 유효성 검사
    validations = [
        ("template_name", template_name),
        ("template_content", template_content),
    ]
    is_validate, response_data = validate_length(validations, [30, 100])
    if not is_validate:
        return JsonResponse(response_data, status=400)

    # 자주쓰는 문구 create
    models.Prompttemplates.objects.create(
        user=user, template_name=template_name, template_content=template_content
    )

    # 응답
    response_data = {"success": True, "message": "자주쓰는 문구를 생성하였습니다."}
    return JsonResponse(response_data, status=200)
