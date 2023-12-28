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
    params = {"user_id": user_id, "password": password, "user_status": 0}
    if not models.Users.objects.filter(**params).exists():
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
    params = {"user_name": user_name, "user_email": email, "user_status": 0}
    users = models.Users.objects.filter(**params)
    id_list = [user.user_id for user in users]

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
        return JsonResponse(response_data, status=400)


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


# 회원 탈퇴
@csrf_exempt
@require_POST
def sign_out(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    user_id = json_data.get("user_id")
    password = json_data.get("password")

    # 사용자 확인
    user_params = {"user_id": user_id, "user_status": 0}
    if not models.Users.objects.filter(**user_params).exists():
        response_data = {"success": False, "message": "존재하지 않는 아이디입니다."}
        return JsonResponse(response_data, status=400)
    user = models.Users.objects.filter(**user_params)[0]
    if user.password != encode_sha256(password):
        response_data = {"success": False, "message": "비밀번호가 일치하지 않습니다."}
        return JsonResponse(response_data, status=400)

    # 탈퇴
    user.user_status = 1
    user.save()
    response_data = {"success": True, "message": "회원 탈퇴에 성공하였습니다."}
    return JsonResponse(response_data, status=200)


# 사용자 정보
def user_info(request):
    # 헤더에서 토큰 받아오기
    auth_header = json.loads(request.headers.get("common"))["Authorization"]
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer ") :]
        user_data = validate_token(token)

        # 토큰 부적격
        if not user_data["succes"]:
            if user_data["message"] == "Invalid":
                response_data = {"success": False, "message": "유효하지 않은 토큰입니다."}
                return JsonResponse(response_data, status=400)
            elif user_data["message"] == "Expired":
                response_data = {"success": False, "message": "기간이 만료된 토큰입니다."}
                return JsonResponse(response_data, status=400)

        # 존재하지 않는 아이디
        user_params = {"user_id": user_data["user_id"], "user_status": 0}
        if not models.Users.objects.filter(**user_params).exists():
            response_data = {"success": False, "message": "존재하지 않는 아이디입니다."}
            return JsonResponse(response_data, status=400)

        # 유저 정보
        user = models.Users.objects.filter(**user_params)[0]
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
    else:
        response_data = {"success": False, "message": "HTTP 헤더 정보가 올바르지 않습니다."}
        return JsonResponse(response_data, status=400)
