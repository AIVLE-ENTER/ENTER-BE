from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from enter import models
import json
from utils.common import encode_sha256
from django.conf import settings
from utils.common import create_token, validate_token
from datetime import datetime, timedelta
import re


# 로그인
@csrf_exempt
@require_POST
def sign_in(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_id = json_data.get("user_id")
    password = encode_sha256(json_data.get("password"))

    # 필수 데이터 누락
    if user_id is None or password is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

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

    # 필수 데이터 누락
    if user_name is None or email is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 유저 찾기
    users = models.Users.objects.filter(user_name=user_name, user_email=email)
    id_list = [user.user_id for user in users]

    # 응답
    response_data = {"success": True, "message": "아이디 찾기에 성공하였습니다.", "id_list": id_list}
    return JsonResponse(response_data, status=200)


# 비밀번호 변경
@csrf_exempt
@require_POST
def chage_password(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_id = json_data.get("user_id")
    email = json_data.get("email")
    certification_number = json_data.get("certification_number")
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
    user = models.Users.objects.filter(user_id=user_id)[0]
    if not models.Users.objects.filter(user_id=user_id).exists():  # 존재하지 않는 아이디
        response_data = {"success": False, "message": "존재하지 않는 아이디 입니다."}
        return JsonResponse(response_data, status=400)
    if email != user.user_email:  # 이메일 일치X
        response_data = {"success": False, "message": "이메일이 일치하지 않습니다."}
        return JsonResponse(response_data, status=400)

    # 인증번호 관련 - 부적절, 시간초과
    params = {"email": email, "purpose": "findPW"}
    auth = models.Emailauth.objects.filter(**params).order_by("-auth_id")[0]
    is_certificate = (
        auth.is_verified is True and auth.certification_number == certification_number
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
