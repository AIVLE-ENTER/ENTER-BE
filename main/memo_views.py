from django.http import JsonResponse
from enter.models import Qnaboard, Analysismemo
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from utils.common import validate_token
import json


# 메모 불러오기
@csrf_exempt
def memo_detail(request):
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    memo_id = request.GET.get("memo_id")
    memo = Analysismemo.objects.filter(memo_id=memo_id)
    memo_info = {}
    if memo.exists():
        memo_info["memo_id"] = memo[0].memo_id
        memo_info["memo_content"] = memo[0].memo_content
        memo_info["created_datetime"] = memo[0].created_datetime
        memo_info["modified_datetime"] = memo[0].modified_datetime
        memo_info["user_id"] = user.user_id

    return JsonResponse(
        {
            "success": True,
            "message": "메모를 불러왔습니다.",
            "data": {
                "is_memo": memo.exists(),  # 메모 존재시:True, 미존재시:False
                "memo": memo_info,
            },
        },
        status=200,
        json_dumps_params={"ensure_ascii": False},
    )


# 메모 작성
@require_POST
@csrf_exempt
def memo_create(request):
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    json_data = json.loads(request.body.decode("utf-8"))
    memo_id = json_data.get("memo_id")
    memo_content = json_data.get("memo_content")

    memo = Analysismemo.objects.filter(memo_id=memo_id)

    # 받아온 memo_id 데이터 이미 존재하면 실패 응답
    if memo.exists():
        return JsonResponse(
            {"success": False, "message": "해당 질문에 대한 메모가 이미 존재합니다."},
            status=400,
            json_dumps_params={"ensure_ascii": False},
        )

    # memo_content가 비어있을 경우 필수 데이터 누락으로 처리
    if not memo_content:
        return JsonResponse(
            {"success": False, "message": "메모 내용이 작성되지 않았습니다."},
            status=400,
            json_dumps_params={"ensure_ascii": False},
        )

    # 메모내용이 700자를 초과하는지 확인
    if len(memo_content) > 700:
        return JsonResponse(
            {"success": False, "message": "메모 내용은 700자를 초과할 수 없습니다."},
            status=400,
            json_dumps_params={"ensure_ascii": False},
        )

    # 메모 작성
    new_memo = Analysismemo.objects.create(
        memo_id=memo_id, memo_content=memo_content, user=user
    )

    return JsonResponse(
        {
            "success": True,
            "message": "메모 작성이 완료되었습니다.",
        },
        json_dumps_params={"ensure_ascii": False},
        status=200,
    )


# 메모 수정
@require_POST
@csrf_exempt
def memo_update(request):
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    json_data = json.loads(request.body.decode("utf-8"))
    memo_id = json_data.get("memo_id")
    memo_content = json_data.get("memo_content")
    print(json_data)
    print(memo_id, memo_content)

    memo = Analysismemo.objects.filter(memo_id=memo_id)

    # 받아온 memo_id에 대한 메모가 존재하지 않을 경우
    if not memo.exists():
        return JsonResponse(
            {"success": False, "message": "수정할 메모가 존재하지 않습니다."}, status=400
        )

    # memo_content가 비어있을 경우 필수 데이터 누락으로 처리
    if not memo_content:
        return JsonResponse(
            {"success": False, "message": "메모 내용이 작성되지 않았습니다."}, status=400
        )

    # 메모내용이 700자를 초과하는지 확인
    if len(memo_content) > 700:
        return JsonResponse(
            {"success": False, "message": "메모 내용은 700자를 초과할 수 없습니다."}, status=400
        )

    if user.user_id == memo.first().user.user_id:
        memo_updated = memo[0]
        memo_updated.memo_content = memo_content
        memo_updated.save()

        return JsonResponse(
            {"success": True, "message": "메모를 수정하였습니다."},
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )

    else:
        return JsonResponse(
            {"success": False, "message": "잘못된 요청입니다. 수정 권한은 작성자에게만 있습니다."},
            json_dumps_params={"ensure_ascii": False},
            status=400,
        )


# 메모 삭제
@require_POST
@csrf_exempt
def memo_delete(request):
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    json_data = json.loads(request.body.decode("utf-8"))
    memo_id = json_data.get("memo_id")

    memo = Analysismemo.objects.filter(memo_id=memo_id)

    if user.user_id == memo.first().user.user_id:
        memo.delete()

        return JsonResponse(
            {"success": True, "message": "메모를 삭제하였습니다."},
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )

    else:
        return JsonResponse(
            {"success": False, "message": "잘못된 요청입니다. 삭제 권한은 작성자에게만 있습니다."},
            json_dumps_params={"ensure_ascii": False},
            status=403,
        )
