# common.py
# 공통 함수 관리
from django.http import HttpResponse
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from enter import models
import hashlib
import jwt
from pytz import timezone
import datetime
from django.conf import settings

SECRET_PRE = settings.SECRET_PRE


# 메일 전송
def send_email(title: str, content: str, to_email: str):
    try:
        email = EmailMessage(
            title,
            content,
            to=[to_email],
        )
        email.content_subtype = "html"  # Content Type을 "html"로 설정
        email.send()
        return {"success": True}
    except Exception as e:
        print(f"Error creating Emailauth instance: {e}")
        return {"success": False, "message": e}


# 인증번호 DB 저장
def save_email_auth(email: str, certification_number: int, purpose: str):
    try:
        models.Emailauth.objects.create(
            email=email, certification_number=certification_number, purpose=purpose
        )
        return {"success": True}
    except Exception as e:
        print(f"Error creating Emailauth instance: {e}")
        return {"success": False, "message": e}


# 인증번호 확인 함수
def is_valid_certification(email: str, input_number: int, purpose: str) -> dict:
    queryset = models.Emailauth.objects.filter(email=email, purpose=purpose).order_by(
        "-auth_id"
    )[0]
    certification_number = queryset.certification_number

    if certification_number != input_number:
        return {"success": False, "message": "인증이 실패했습니다. 올바른 인증번호를 입력해주세요."}

    current_time = datetime.now()
    five_minutes_ago = current_time - timedelta(minutes=5)

    if queryset.created_datetime < five_minutes_ago:
        return {"success": False, "message": "시간이 초과하였습니다. 다시 시도해주세요."}

    # 인증 완료시 is_verified 값 바꾸기
    queryset.is_verified = True
    queryset.save()

    return {"success": True, "message": "인증이 성공적으로 완료되었습니다."}


# sha256 암호화
def encode_sha256(str: str) -> str:
    result = ""
    for s in str:
        result += hashlib.sha256(s.encode()).hexdigest() + "\n"
    return result


# sha256 복호화
def decode_sha256(str: str) -> str:
    for i in range(len(str)):
        str = str.replace(hashlib.sha256(chr(i).encode()).hexdigest(), chr(i))
    return str.replace("\n", "")


# jwt 토큰 생성
def create_token(user_id: str) -> str:
    data = {
        "exp": datetime.datetime.now(timezone("Asia/Seoul"))
        + datetime.timedelta(seconds=60 * 60 * 24),  # 24시간
        "user_id": user_id,
    }
    token = jwt.encode(data, SECRET_PRE, algorithm="HS256")
    return token


# jwt 토큰 검증
def validate_token(token: str) -> str:
    try:
        decoded = jwt.decode(token, SECRET_PRE, algorithms="HS256")
    except jwt.ExpiredSignatureError:
        return HttpResponse("Unauthorized", status=401)
    except jwt.InvalidTokenError:
        return HttpResponse("Unauthorized", status=401)
    else:
        return decoded["user_id"]