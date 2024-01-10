from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from utils.common import validate_token
from enter import models
import json


# 길이 유효성 검사 (길이 전부 통일)
@csrf_exempt
def validate_length(validations: list, max_length: int) -> (bool, dict):
    errors = []

    for target, value in validations:
        if len(value) > max_length:
            errors.append(target)

    if errors:
        response_data = {
            "success": False,
            "message": f"{max_length}글자 이내로 입력해주세요.",
            "errors": {"validation": errors},
        }
        return False, response_data
    else:
        return True, {}


# 채팅방 리스트
@csrf_exempt
def chat_window_list(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 채팅창
    chats = models.Chatwindow.objects.filter(user=user, is_deleted=False)
    chat_list = []
    for chat in chats:
        chat_data = {
            "chat_window_id": chat.chat_window_id,
            "target_object": chat.target_object,
            "title": chat.title,
            "created_datetime": chat.created_datetime,
            "modified_datetime": chat.modified_datetime,
        }
        chat_list.append(chat_data)

    # 응답
    response_data = {
        "success": True,
        "message": "채팅창을 불러왔습니다.",
        "data": {"chat_list": chat_list},
    }
    return JsonResponse(response_data, status=200)


# 채팅방 생성
@require_POST
@csrf_exempt
def create_chat_window(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    target_object = json_data.get("target")
    title = json_data.get("title")

    # 필수 데이터 누락
    if target_object is None or title is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 유효성 검사
    validations = [("target", target_object), ("title", title)]
    is_validate, response_data = validate_length(validations, 20)
    if not is_validate:
        return JsonResponse(response_data, status=400)

    # target 중복 체크
    chat_params = {"target_object": target_object, "user": user}
    if models.Chatwindow.objects.filter(**chat_params).exists():
        response_data = {"success": False, "message": "중복된 주제입니다."}
        return JsonResponse(response_data, status=400)

    # 채팅방 create
    models.Chatwindow.objects.create(
        user=user, target_object=target_object, title=title
    )

    # 응답
    response_data = {"success": True, "message": "채팅방을 생성하였습니다."}
    return JsonResponse(response_data, status=200)


# 채팅방 수정
@csrf_exempt
@require_POST
def update_chat_window(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    chat_window_id = json_data.get("chat_window_id")
    title = json_data.get("title")

    # 필수 데이터 누락
    if chat_window_id is None or title is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 유효성 검사
    if len(title) > 20:
        response_data = {"success": False, "message": "20글자 이내로 입력해주세요."}
        return JsonResponse(response_data, status=400)

    chat = models.Chatwindow.objects.get(chat_window_id=chat_window_id)
    # 수정 권한
    if chat.user != user:
        response_data = {"success": True, "message": "잘못된 요청입니다. (수정 권한은 작성자에게만 있습니다.)"}
        return JsonResponse(response_data, status=403)
    # 채팅방 update
    chat.title = title
    chat.save()

    # 응답
    response_data = {"success": True, "message": "채팅방을 수정하였습니다."}
    return JsonResponse(response_data, status=200)


# 채팅방 삭제
@csrf_exempt
@require_POST
def delete_chat_window(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    chat_window_id = json_data.get("chat_window_id")

    # 필수 데이터 누락
    if chat_window_id is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    chat = models.Chatwindow.objects.get(chat_window_id=chat_window_id)
    # 삭제 권한
    if chat.user != user:
        response_data = {"success": True, "message": "잘못된 요청입니다. (삭제 권한은 작성자에게만 있습니다.)"}
        return JsonResponse(response_data, status=403)
    # 채팅방 delete
    chat.is_deleted = True
    chat.save()

    # 응답
    response_data = {"success": True, "message": "채팅방을 삭제하였습니다."}
    return JsonResponse(response_data, status=200)
