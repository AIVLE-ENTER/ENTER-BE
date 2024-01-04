from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import redirect
from enter import models
import json
import requests
from django.conf import settings
from utils.common import create_token
from enter.settings import get_env_variable


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
    token = create_token(user.user_id)

    response_data = {"success": True, "message": "exists", "data": {"token": token}}
    return JsonResponse(response_data, status=200)


# 구글 로그인
@csrf_exempt
@require_POST
def google_login(request):
    CLIENT_ID = get_env_variable("CLIENT_ID")
    CLIENT_SECRET = get_env_variable("CLIENT_SECRET")

    # 클라이언트에서 받은 인가 코드
    json_data = json.loads(request.body.decode("utf-8"))
    authorization_code = json_data.get("code")

    # 로그인 토큰을 얻기 위한 요청 설정
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "http://localhost:5500/signin_test.html?type=google",
        "grant_type": "authorization_code",
    }

    # 로그인 토큰 요청
    token_response = requests.post(token_url, data=token_payload)
    print(token_response.json())

    if token_response.status_code == 200:
        access_token = token_response.json().get("access_token")

        # 구글 사용자 정보 요청
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        user_info_response = requests.get(
            user_info_url, headers=headers
        )  # 여기까지가 response 받아오는 코드.

        if user_info_response.status_code == 200:
            google_id = user_info_response.json()["id"]

            if not google_id:
                response_data = {"success": False, "message": "구글 계정을 받아오지 못했습니다."}
                return JsonResponse(response_data, status=400)

            if not models.Users.objects.filter(google_id=google_id).exists():
                response_data = {
                    "success": True,
                    "message": "not exists",
                    "data": {"id": google_id},
                }
                return JsonResponse(response_data, status=200)

            # jwt 토큰 프론트로 전달
            user = models.Users.objects.get(google_id=google_id)
            token = create_token(user.user_id)
            response_data = {
                "success": True,
                "message": "exists",
                "data": {"token": token},
            }
            return JsonResponse(response_data, status=200)

        else:
            return JsonResponse(
                {"success": False, "message": "Failed to fetch user info from Google"},
                status=500,
            )

    else:
        return JsonResponse(
            {"success": False, "message": "access token을 받아오는데 실패했습니다."},
            status=500,
            json_dumps_params={"ensure_ascii": False},
        )
