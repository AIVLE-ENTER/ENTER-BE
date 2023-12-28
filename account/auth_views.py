from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from enter import models
import json
from utils.common import encode_sha256
from django.conf import settings
from utils.common import create_token, validate_token


# 로그인
@csrf_exempt
@require_POST
def sign_in(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_id = json_data.get("user_id")
    password = encode_sha256(json_data.get("password"))

    # 계정 확인 및 로그인
    if not models.Users.objects.filter(user_id=user_id, password=password).exists():
        response_data = {"success": False, "message": "로그인에 실패하였습니다."}
        return JsonResponse(response_data, status=401)
    else:
        token = create_token(user_id)
        response_data = {
            "success": True,
            "message": "로그인에 성공하였습니다.",
            "data": {"user_id": user_id, "token": token},
        }
        return JsonResponse(response_data, status=200)


# 아이디 찾기
@csrf_exempt
@require_POST
def find_id(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_name = json_data.get("user_name")
    email = json_data.get("email")

    # 유저 찾기
    users = models.Users.objects.filter(user_name=user_name, user_email=email)
    id_list = [user.user_id for user in users]

    # 응답
    response_data = {"success": True, "message": "아이디 찾기에 성공하였습니다.", "id_list": id_list}
    return JsonResponse(response_data, status=200)
