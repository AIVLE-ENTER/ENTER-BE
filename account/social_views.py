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


kakao_access_uri = "https://kauth.kakao.com/oauth/token"
kakao_profile_uri = "https://kapi.kakao.com/v2/user/me"
naver_token_uri = "https://nid.naver.com/oauth2.0/token"
naver_profile_uri = "https://openapi.naver.com/v1/nid/me"


# 회원 정보 요청 함수 (나중에 common.py로 옮기기)
def request_user_info(access_token, url):
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/x-www-form-urlencoded",
    }
    user_info_json = requests.get(url, headers=auth_headers).json()

    return user_info_json


# 카카오 로그인
@csrf_exempt
@require_POST
def kakao_login(request):
    # data 받아오기
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError as e:
        # JSON 디코딩 중에 오류가 발생한 경우
        response_data = {"success": False, "message": "Invalid JSON format"}
        return JsonResponse(response_data, status=400)
    if not data:
        response_data = {"success": False, "message": "data를 받아오지 못했습니다."}
        return JsonResponse(response_data, status=400)

    # code 추출
    code = data["code"]
    if not code:
        response_data = {"success": False, "message": "인가코드를 받아오지 못했습니다."}
        return JsonResponse(response_data, status=400)

    # access token 요청
    CLIENT_ID = get_env_variable("KAKAO_CLIENT_ID")
    CLIENT_SECRET = get_env_variable("KAKAO_CLIENT_SECRET")
    REDIRECT_URI = "http://localhost:5500/signin.html?type=kakao"
    token_url = f"{kakao_access_uri}?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}"
    token_req = requests.post(token_url)
    access_token = token_req.json().get("access_token")

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

    if not models.Users.objects.filter(kakao_id=kakao_id, user_status=0).exists():
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
    CLIENT_ID = get_env_variable("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = get_env_variable("GOOGLE_CLIENT_SECRET")

    # 클라이언트에서 받은 인가 코드
    json_data = json.loads(request.body.decode("utf-8"))
    authorization_code = json_data.get("code")

    # 로그인 토큰을 얻기 위한 요청 설정
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "http://localhost:5500/signin.html?type=google",
        "grant_type": "authorization_code",
    }

    # 로그인 토큰 요청
    token_response = requests.post(token_url, data=token_payload)

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

            if not models.Users.objects.filter(
                google_id=google_id, user_status=0
            ).exists():
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


# 네이버 로그인
@csrf_exempt
@require_POST
def naver_login(request):
    # data 받아오기
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError as e:
        # JSON 디코딩 중에 오류가 발생한 경우
        response_data = {"success": False, "message": "Invalid JSON format"}
        return JsonResponse(response_data, status=400)
    if not data:
        response_data = {"success": False, "message": "data를 받아오지 못했습니다."}
        return JsonResponse(response_data, status=400)

    # code 추출
    code = data["code"]
    if not code:
        response_data = {"success": False, "message": "인가코드를 받아오지 못했습니다."}
        return JsonResponse(response_data, status=400)

    # access token 요청
    CLIENT_ID = get_env_variable("NAVER_CLIENT_ID")
    CLIENT_SECRET = get_env_variable("NAVER_CLIENT_SECRET")
    REDIRECT_URI = "http://localhost:5500/signin.html?type=naver"

    token_url = f"{naver_token_uri}?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}"
    token_req = requests.post(token_url)
    access_token = token_req.json().get("access_token")

    # naver 회원정보 요청
    url = f"{naver_profile_uri}?access_token={access_token}"
    user_info_json = requests.get(url).json()
    if not user_info_json:
        response_data = {"success": False, "message": "유저 정보를 받아오지 못했습니다."}
        return JsonResponse(response_data, status=400)

    # 토큰 받아오기
    access_token = request.POST.get("access_token")

    # 회원가입 및 로그인
    naver_id = user_info_json.get("response").get("id")

    if not naver_id:
        response_data = {"success": False, "message": "네이버 계정을 받아오지 못했습니다."}
        return JsonResponse(response_data, status=400)

    if not models.Users.objects.filter(naver_id=naver_id, user_status=0).exists():
        response_data = {
            "success": True,
            "message": "not exists",
            "data": {"id": naver_id},
        }
        return JsonResponse(response_data, status=200)

    # jwt 토큰 발급하여 로그인
    user = models.Users.objects.get(naver_id=naver_id)
    token = create_token(user.user_id)

    response_data = {"success": True, "message": "exists", "data": {"token": token}}
    return JsonResponse(response_data, status=200)
