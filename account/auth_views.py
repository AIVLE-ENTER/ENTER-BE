from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from enter import models
import json
import jwt
from pytz import timezone
import datetime
from utils.common import encode_sha256
from django.conf import settings

SECRET_PRE = settings.SECRET_PRE


# jwt 토큰 생성
def create_token(user_id: str) -> str:
    data = {
        "exp": datetime.datetime.now(timezone("Asia/Seoul"))
        + datetime.timedelta(seconds=300),
        "user_id": user_id,
    }
    token = jwt.encode(data, SECRET_PRE, algorithm="HS256")
    return token


# 로그인
@csrf_exempt
@require_POST
def login(request):
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
