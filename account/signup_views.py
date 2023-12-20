from django.http import JsonResponse
from enter import models
from utils.views import send_email, save_email_auth
import json
import random
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# 아이디 중복 체크 (중복시 사용불가, 중복되지 않을시 사용 가능 응답)
def check_id_duplicate(request):
    check_id = request.GET.get("id")
    is_available = not models.Users.objects.filter(user_id=check_id).exists()
    return JsonResponse({"is_available": is_available})


# 이메일로 인증번호 전송
@csrf_exempt
@require_POST
def send_certification_number(request):
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    email = json_data.get("email")

    # 이메일 전송
    title = "[ENTER] 인증번호 발송"
    certification_number = random.randint(100000, 999999)
    content = f"이메일 인증번호 안내\n\n본 메일은 ENTER 사이트의 회원가입을 위한 이메일 인증입니다.\n아래의 [이메일 인증번호]를 입력하여 본인 확인을 해주시기 바랍니다.\n\n인증번호: {certification_number}"

    is_send = send_email(title, content, email)
    if not is_send["success"]:
        response_data = {
            "success": False,
            "message": f"이메일 전송에 실패했습니다. 오류 메시지: {is_send['message']}",
        }
        return JsonResponse(response_data, status=500)

    # 인증번호 저장
    is_save = save_email_auth(email, certification_number)
    print(is_save)
    if not is_save["success"]:
        response_data = {
            "success": False,
            "message": f"이메일 인증을 다시 시도해주세요. 오류 메시지: {is_save['message']}",
        }
        return JsonResponse(response_data, status=500)

    response_data = {"success": True, "message": "이메일 전송이 성공적으로 완료되었습니다."}
    return JsonResponse(response_data, status=200)
