from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from utils.common import validate_token
from enter import models
import json


# 자주쓰는 문구 리스트
@csrf_exempt
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


# 자주쓰는 문구 상세
def frequent_message_detail(request, template_id):
    message = models.Prompttemplates.objects.filter(
        template_id=template_id, is_deleted=False
    )
    print(message)

    if message.exists():
        message_data = {
            "template_id": message[0].template_id,
            "template_name": message[0].template_name,
            "template_content": message[0].template_content,
            "created_datetime": message[0].created_datetime,
            "modified_datetime": message[0].modified_datetime,
        }
        response_data = {
            "success": True,
            "message": "자주쓰는 문구를 불러왔습니다.",
            "data": message_data,
        }
        return JsonResponse(response_data, status=200)
    else:
        response_data = {
            "success": False,
            "message": "존재하지 않는 문구입니다.",
        }
        return JsonResponse(response_data, status=400)


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
    if len(template_name) > 100:
        response_data = {
            "success": False,
            "message": "오류: template_name은 100글자를 넘을 수 없습니다.",
        }
        return JsonResponse(response_data, status=400)

    # 자주쓰는 문구 create
    models.Prompttemplates.objects.create(
        user=user, template_name=template_name, template_content=template_content
    )

    # 응답
    response_data = {"success": True, "message": "자주쓰는 문구를 생성하였습니다."}
    return JsonResponse(response_data, status=200)


# 자주쓰는 문구 수정
@csrf_exempt
@require_POST
def update_frequent_message(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    template_id = json_data.get("template_id")
    template_name = json_data.get("template_name")
    template_content = json_data.get("template_content")

    # 필수 데이터 누락
    if template_id is None or template_name is None or template_content is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 유효성 검사
    if len(template_name) > 100:
        response_data = {
            "success": False,
            "message": "오류: template_name은 100글자를 넘을 수 없습니다.",
        }
        return JsonResponse(response_data, status=400)

    message = models.Prompttemplates.objects.get(template_id=template_id)
    # 수정 권한
    if message.user != user:
        response_data = {"success": True, "message": "잘못된 요청입니다. (수정 권한은 작성자에게만 있습니다.)"}
        return JsonResponse(response_data, status=403)
    # 자주쓰는 문구 update
    message.template_name = template_name
    message.template_content = template_content
    message.save()

    # 응답
    response_data = {"success": True, "message": "자주쓰는 문구를 수정하였습니다."}
    return JsonResponse(response_data, status=200)


# 자주쓰는 문구 삭제
@csrf_exempt
@require_POST
def delete_frequent_message(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    template_id = json_data.get("template_id")

    # 필수 데이터 누락
    if template_id is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    message = models.Prompttemplates.objects.get(template_id=template_id)
    # 삭제 권한
    if message.user != user:
        response_data = {"success": True, "message": "잘못된 요청입니다. (삭제 권한은 작성자에게만 있습니다.)"}
        return JsonResponse(response_data, status=403)
    # 자주쓰는 문구 delete
    message.is_deleted = True
    message.save()

    # 응답
    response_data = {"success": True, "message": "자주쓰는 문구를 삭제하였습니다."}
    return JsonResponse(response_data, status=200)
