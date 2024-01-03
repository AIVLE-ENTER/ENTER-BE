from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from enter import models
import json
import requests
from django.conf import settings
from utils.common import create_token


kakao_profile_uri = "https://kapi.kakao.com/v2/user/me"


# 회원 정보 요청 함수 (나중에 common.py로 옮기기)
def request_user_info(access_token, url):
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/x-www-form-urlencoded",
    }
    user_info_json = requests.get(url, headers=auth_headers).json()

    return user_info_json


@csrf_exempt
@require_POST
def kakao_login(request):
    # 토큰 받아오기
    access_token = request.POST.get("access_token")

    # kakao 회원정보 요청
    user_info_json = request_user_info(access_token, kakao_profile_uri)
    if not user_info_json:
        error_message = {"message": "유저 정보를 받아오지 못했습니다."}
        return JsonResponse(error_message, status=400)
    print(user_info_json)

    # 회원가입 및 로그인
    kakao_id = user_info_json.get("id")

    if not kakao_id:
        response_data = {"success": False, "message": "카카오 계정을 받아오지 못했습니다."}
        return JsonResponse(response_data, status=400)

    if not models.Users.objects.filter(kakao_id=kakao_id).exists():
        response_data = {
            "success": True,
            "message": "not exists",
            "data": {"id": kakao_id},
        }
        return JsonResponse(response_data, status=200)

    # jwt 토큰 발급하여 로그인
    user = models.Users.objects.get(kakao_id=kakao_id)
    print(user.user_id)
    token = create_token(user.user_id)

    response_data = {"success": True, "message": "exists", "data": {"token": token}}
    return JsonResponse(response_data, status=200)
