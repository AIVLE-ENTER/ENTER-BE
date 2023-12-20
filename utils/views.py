from django.core.mail import EmailMessage
from enter import models


# 메일 전송
def send_email(title: str, content: str, to_email: str):
    try:
        email = EmailMessage(
            title,
            content,
            to=[to_email],
        )
        email.send()
        return {"success": True}
    except Exception as e:
        print(f"Error creating Emailauth instance: {e}")
        return {"success": False, "message": e}


# 인증번호 DB 저장
def save_email_auth(email: str, certification_number: int, type: str):
    try:
        models.Emailauth.objects.create(
            email=email, certification_number=certification_number, type=type
        )
        return {"success": True}
    except Exception as e:
        print(f"Error creating Emailauth instance: {e}")
        return {"success": False, "message": e}
