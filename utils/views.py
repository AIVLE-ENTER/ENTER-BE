from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from enter import models
from utils.common import send_email, save_email_auth, is_valid_certification
import random
import json
from django.middleware.csrf import get_token


# 이메일로 인증번호 전송
@require_POST
@csrf_exempt
def send_certification_number(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    email = json_data.get("email")
    purpose = json_data.get("purpose")

    # 이메일 템플릿
    template = models.Emailtemplates.objects.filter(purpose=purpose)
    if not template.exists():
        response_data = {"success": False, "message": "오류: purpose 값이 잘못되었습니다."}
        return JsonResponse(response_data, status=400)
    title = template[0].title
    certification_number = random.randint(100000, 999999)
    content = template[0].content.format(certification_number=certification_number)

    # 비밀번호 찾기의 경우 회원 정보의 이메일과 일치할 경우에만 전송
    if purpose == "findPW":
        user_id = json_data.get("user_id")
        if not models.Users.objects.filter(user_email=email, user_id=user_id).exists():
            response_data = {"success": False, "message": "이메일이 회원정보와 일치하지 않습니다."}
            return JsonResponse(response_data, status=200)

    if send_email:
        # 이메일 전송
        is_send = send_email(title, content, email)
        if not is_send["success"]:
            response_data = {
                "success": False,
                "message": f"이메일 전송에 실패했습니다. 오류 메시지: {is_send['message']}",
            }
            return JsonResponse(response_data, status=500)

        # 인증번호 저장
        is_save = save_email_auth(email, certification_number, purpose)
        if not is_save["success"]:
            response_data = {
                "success": False,
                "message": f"이메일 인증을 다시 시도해주세요. 오류 메시지: {is_save['message']}",
            }
            return JsonResponse(response_data, status=500)

    response_data = {"success": True, "message": "이메일 전송이 성공적으로 완료되었습니다."}
    return JsonResponse(response_data, status=200)


# 인증번호 확인
@csrf_exempt
def check_certification_number(request):
    email = request.GET.get("email")
    certification_number = int(request.GET.get("certification_number"))
    purpose = request.GET.get("purpose")

    # 데이터 누락
    if email is None or certification_number is None or purpose is None:
        response_data = {"success": False, "message": "오류: 필수 데이터가 누락되었습니다."}
        return JsonResponse(response_data, status=400)

    # 인증번호 확인
    response_data = is_valid_certification(email, certification_number, purpose)
    return JsonResponse(response_data)
