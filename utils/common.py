# common.py
# 공통 함수 관리

from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from enter import models


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
def is_valid_certification(email: str, certification_number: int, purpose: str) -> dict:
    queryset = models.Emailauth.objects.filter(
        email=email, certification_number=certification_number, purpose=purpose
    )

    if not queryset.exists():
        return {"success": False, "message": "인증이 실패했습니다. 올바른 인증번호를 입력해주세요."}

    current_time = datetime.now()
    five_minutes_ago = current_time - timedelta(minutes=5)

    if not queryset.filter(created_datetime__gte=five_minutes_ago).exists():
        return {"success": False, "message": "시간이 초과하였습니다. 다시 시도해주세요."}

    return {"success": True, "message": "인증이 성공적으로 완료되었습니다."}
