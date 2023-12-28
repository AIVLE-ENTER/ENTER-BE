from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from utils.common import validate_token
from enter import models
import json


# 채팅방 리스트
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
            "crawling_text": chat.crawling_text,
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
@csrf_exempt
@require_POST
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
    if len(target_object) > 20 or len(title) > 20:
        errors = []
        if len(target_object) > 20:
            errors.append("target")
        if len(title) > 20:
            errors.append("title")
        response_data = {
            "success": False,
            "message": "오류: 유효성 검사 (20글자 초과)",
            "errors": {"validation": errors},
        }
        return JsonResponse(response_data, status=400)

    # 채팅방 create
    models.Chatwindow.objects.create(
        user=user, target_object=target_object, title=title
    )

    # 응답
    response_data = {"success": True, "message": "채팅방을 생성하였습니다."}
    return JsonResponse(response_data, status=200)
