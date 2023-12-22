from django.http import JsonResponse
from enter import models
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


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
        company_list.append({"company_id": company.company_id, "company_name": company.company_name})
    return JsonResponse({"company_list": company_list})