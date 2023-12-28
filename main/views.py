from django.http import JsonResponse
from utils.common import validate_token
from enter import models


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
