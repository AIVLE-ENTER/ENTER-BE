from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from enter import models
import json
import re
from datetime import datetime, timedelta
from utils.common import encode_sha256


# 아이디 중복 체크 (중복시 사용불가, 중복되지 않을시 사용 가능 응답)
def check_id_duplicate(request):
    check_id = request.GET.get("id")
    is_available = not models.Users.objects.filter(user_id=check_id).exists()
    return JsonResponse({"is_available": is_available})


# 회사 리스트
def company_list(request):
    companys = models.Company.objects.all()
    company_list = []
    for company in companys:
        company_info = {
            "company_id": company.company_id,
            "company_name": company.company_name,
        }
        company_list.append(company_info)
    return JsonResponse({"company_list": company_list})


# 회원가입
@require_POST
@csrf_exempt
def sign_up(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    company_id = json_data.get("company_id")
    password = json_data.get("password")
    certification_number = int(json_data.get("certification_number"))
    type = json_data.get("type")

    # 회원가입 데이터
    data = {
        "user_id": json_data.get("user_id"),
        "password": encode_sha256(password),  # 비밀번호 암호화
        "user_name": json_data.get("user_name"),
        "user_email": json_data.get("user_email"),
        "privacy_agreement": json_data.get("privacy_agreement"),
    }

    # 유효성 검사
    status = 400
    success = False
    message = "오류가 발생했습니다. 다시 시도해주세요."
    errors, user_data = {}, {}
    reg_id_pw = re.compile(r"^[a-zA-Z0-9]{4,12}$")

    if not data["privacy_agreement"]:
        errors["privacy"] = "(필수) 개인정보 수집 및 이용에 동의하지 않았습니다."
    if data["user_name"] == "" or data["user_name"] is None:
        errors["name"] = "유저명을 입력하지 않았습니다."
    if models.Users.objects.filter(user_id=data["user_id"]).exists():
        errors["duplicate"] = "중복된 ID 입니다."
    if not reg_id_pw.match(data["user_id"]):
        errors["id"] = "ID 형식이 올바르지 않습니다."
    if not reg_id_pw.match(password):
        errors["password"] = "패스워드 형식이 올바르지 않습니다."
    if not models.Company.objects.filter(company_id=company_id).exists():
        errors["company"] = "존재하지 않는 회사아이디 입니다."

    # 유효성 검사 - 이메일
    reg_mail = re.compile(
        r"^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$"
    )
    queryset = models.Emailauth.objects.filter(
        email=data["user_email"], purpose="signup"
    ).order_by("-auth_id")[0]
    is_certificate = (
        queryset.is_vertified is True
        and queryset.certification_number == certification_number
    )
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    if not reg_mail.match(data["user_email"]):
        errors["email"] = "이메일 형식이 올바르지 않습니다."
    elif not is_certificate:
        errors["email_auth"] = "이메일 인증이 부적절하게 진행되었습니다. 다시 시도해주세요."
    elif queryset.created_datetime < ten_minutes_ago:
        errors["email_auth"] = "이메일 인증 후 시간이 10분이상 초과되었습니다. 다시 시도해주세요."

    # 소셜 연동
    if type:
        social_id = json_data.get("social_id")
        if type == "kakao":
            data["kakao_id"] = social_id
        elif type == "google":
            data["google_id"] = social_id
        elif type == "naver":
            data["naver_id"] = social_id

    # 에러가 없으면 회원가입
    if errors == {}:
        status = 200
        success = True
        message = "회원가입이 성공적으로 완료되었습니다."
        data["company"] = models.Company.objects.get(company_id=company_id)
        models.Users.objects.create(**data)
        user_data = {
            "user_id": data["user_id"],
            "user_name": data["user_name"],
            "user_email": data["user_email"],
        }

    # 응답
    response_data = {
        "success": success,
        "message": message,
        "data": user_data,
        "errors": errors,
    }
    return JsonResponse(response_data, status=status)
