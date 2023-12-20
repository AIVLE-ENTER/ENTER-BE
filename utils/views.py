from django.http import JsonResponse
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


# 인증번호 확인
def check_certification_number(request):
    email = request.GET.get("email")
    certification_number = request.GET.get("certification_number")
    type = request.GET.get("type")

    # 데이터 누락
    if email is None or certification_number is None or type is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=500)

    # 인증번호 확인
    response_data = is_valid_certification(email, certification_number, type)
    return JsonResponse(response_data)


# 인증번호 확인 함수
def is_valid_certification(email: str, certification_number: int, type: str) -> dict:
    queryset = models.Emailauth.objects.filter(
        email=email, certification_number=certification_number, type=type
    )

    if not queryset.exists():
        return {"success": False, "message": "인증이 실패했습니다. 올바른 인증번호를 입력해주세요."}

    current_time = datetime.now()
    five_minutes_ago = current_time - timedelta(minutes=5)

    if not queryset.filter(created_datetime__gte=five_minutes_ago).exists():
        return {"success": False, "message": "시간이 초과하였습니다. 다시 시도해주세요."}

    return {"success": True, "message": "인증이 성공적으로 완료되었습니다."}
