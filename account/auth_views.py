from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from enter import models
import json
from utils.common import encode_sha256
from django.conf import settings
from utils.common import create_token, validate_token, mask_name
from datetime import datetime, timedelta
import re


# 로그인
@require_POST
@csrf_exempt
def sign_in(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_id = json_data.get("user_id")
    password = encode_sha256(json_data.get("password"))
    type = json_data.get("type")

    # 필수 데이터 누락
    if user_id is None or password is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 계정 확인 및 로그인
    params = {"user_id": user_id, "password": password, "user_status": 0}
    if not models.Users.objects.filter(**params).exists():
        response_data = {"success": False, "message": "로그인에 실패하였습니다."}
        return JsonResponse(response_data, status=200)
    else:
        # 소셜 연동
        if type != "":
            social_id = json_data.get("social_id")
            user = models.Users.objects.get(user_id=user_id)
            if type == "kakao":
                user.kakao_id = social_id
            elif type == "google":
                user.google_id = social_id
            elif type == "naver":
                user.naver_id = social_id
            user.save()
        # jwt 토큰 발급
        token = create_token(user_id)
        # 응답
        response_data = {
            "success": True,
            "message": "로그인에 성공하였습니다.",
            "data": {"user_id": user_id, "token": token},
        }
        return JsonResponse(response_data, status=200)


# 아이디 존재여부 확인
def check_id(request):
    check_id = request.GET.get("id")
    is_exist = models.Users.objects.filter(user_id=check_id).exists()
    return JsonResponse({"is_exist": is_exist})


# 아이디 찾기
@csrf_exempt
@require_POST
def find_id(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_name = json_data.get("user_name")
    email = json_data.get("email")

    # 필수 데이터 누락
    if user_name is None or email is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 유저 찾기
    params = {"user_name": user_name, "user_email": email, "user_status": 0}
    users = models.Users.objects.filter(**params).order_by("register_datetime")
    id_list = [
        {
            "id": user.user_id,
            "register_date": user.register_datetime.strftime("%Y-%m-%d"),
        }
        for user in users
    ]

    # 응답
    if len(id_list) > 0:
        response_data = {
            "success": True,
            "message": "아이디 찾기에 성공하였습니다.",
            "id_list": id_list,
        }
        return JsonResponse(response_data, status=200)
    else:
        response_data = {
            "success": False,
            "message": "해당하는 계정을 찾을 수 없습니다.",
            "id_list": id_list,
        }
        return JsonResponse(response_data, status=200)


# 비밀번호 변경
@require_POST
@csrf_exempt
def change_password(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_id = json_data.get("user_id")
    email = json_data.get("email")
    certification_number = int(json_data.get("certification_number"))
    password = json_data.get("password")

    # 필수 데이터 누락
    if (
        user_id is None
        or email is None
        or certification_number is None
        or password is None
    ):
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 사용자
    user_params = {"user_id": user_id, "user_status": 0}
    if not models.Users.objects.filter(**user_params).exists():  # 존재하지 않는 아이디
        response_data = {"success": False, "message": "존재하지 않는 아이디 입니다."}
        return JsonResponse(response_data, status=400)
    user = models.Users.objects.filter(**user_params)[0]
    if email != user.user_email:  # 이메일 일치X
        response_data = {"success": False, "message": "이메일이 일치하지 않습니다."}
        return JsonResponse(response_data, status=400)

    # 인증번호 관련 - 부적절, 시간초과
    auth_params = {"email": email, "purpose": "findPW"}
    auth = models.Emailauth.objects.filter(**auth_params).order_by("-auth_id")[0]
    is_certificate = (
        auth.is_vertified is True and auth.certification_number == certification_number
    )
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    if not is_certificate:
        response_data = {"success": False, "message": "이메일 인증이 부적절하게 진행되었습니다."}
        return JsonResponse(response_data, status=400)
    elif auth.created_datetime < ten_minutes_ago:
        response_data = {"success": False, "message": "이메일 인증 후 시간이 10분이상 초과되었습니다."}
        return JsonResponse(response_data, status=400)

    # 새 비밀번호 유효성 검사
    reg_pw = re.compile(r"^[a-zA-Z0-9]{4,12}$")
    if not reg_pw.match(password):
        response_data = {"success": False, "message": "비밀번호 형식이 올바르지 않습니다."}
        return JsonResponse(response_data, status=400)

    # 비밀번호 변경
    user.password = encode_sha256(password)
    user.save()

    response_data = {"success": True, "message": "비밀번호 변경에 성공하였습니다."}
    return JsonResponse(response_data, status=200)


# 회원 탈퇴
@require_POST
@csrf_exempt
def sign_out(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_id = json_data.get("user_id")
    password = json_data.get("password")

    # 필수 데이터 누락
    if user_id is None or password is None:
        response_data = {"success": False, "message": "오류: 필수 데이터 누락"}
        return JsonResponse(response_data, status=400)

    # 사용자 확인
    user_params = {"user_id": user_id, "user_status": 0}
    if not models.Users.objects.filter(**user_params).exists():
        response_data = {"success": False, "message": "존재하지 않는 아이디입니다."}
        return JsonResponse(response_data, status=400)
    user = models.Users.objects.filter(**user_params)[0]
    if user.password != encode_sha256(password):
        response_data = {"success": False, "message": "비밀번호가 일치하지 않습니다."}
        return JsonResponse(response_data, status=200)

    # 탈퇴 권한
    if user_id != user.user_id:
        response_data = {
            "success": False,
            "message": "잘못된 요청입니다. (로그인한 유저와 탈퇴하려는 유저가 다릅니다.)",
        }
        return JsonResponse(response_data, status=200)

    # 탈퇴
    user.user_status = 1
    user.save()
    response_data = {"success": True, "message": "회원 탈퇴에 성공하였습니다."}
    return JsonResponse(response_data, status=200)


# 사용자 정보
def user_info(request):
    # 토큰 검증
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    # 유저 정보
    response_data = {
        "success": True,
        "message": "유저 정보 받기에 성공하였습니다.",
        "data": {
            "user_id": user.user_id,
            "user_name": mask_name(user.user_name),
            "role": user.role,
        },
    }
    return JsonResponse(response_data, status=200)
