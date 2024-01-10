import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from enter.models import Qnaboard, Questiontype
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from utils.common import validate_token, mask_name
import json
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from os.path import splitext



# Create your views here.

# 업로드 하는 파일에 대한 개수, 크기, 확장자 제한
FILE_COUNT_LIMIT = 3
# 업로드 하는 파일의 최대 사이즈 제한. 5MB : 5242880(5*1024*1024)
FILE_SIZE_LIMIT = 5242880
# 업로드 허용 확장자
WHITE_LIST_EXT = [
    ".jpg",
    ".jpeg",
    ".png",
]


# Question Type 리스트
@csrf_exempt
def question_type_list(request):
    types = Questiontype.objects.all()
    type_list = []
    for type in types:
        type_info = {
            "question_type_id": type.question_type_id,
            "question_type_title": type.question_type_title,
        }
        type_list.append(type_info)
    return JsonResponse({"type_list": type_list})


# 게시판 게시글 목록
@csrf_exempt
def post_list(request):
    # 문의 유형 드롭 다운 리스트
    type_qr = Questiontype.objects.all()
    type_list = []
    for type in type_qr:
        type_dict = {
            "question_type_id": type.question_type_id,
            "question_type_title": type.question_type_title,
        }
        type_list.append(type_dict)

    # 검색 키워드 및 문의 유형
    keyword = request.GET.get("keyword", "")
    type = request.GET.get("type", None)
    posts = (
        Qnaboard.objects.filter(
            question_title__icontains=keyword,
            is_deleted=False,
            question_type_id=int(type) if type and type.isdigit() else Q(),
        )
        .order_by("-question_datetime")
        .all()
    )
    tot_post = len(posts)

    # 페이지 처리
    page = request.GET.get("page", 1)  # 기본값 1
    paginator = Paginator(posts, 10)  # 한 페이지에 보여질 게시물 수 설정

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(1)

    # 게시글 목록
    post_number = paginator.count - paginator.per_page * (posts.number - 1)

    post_list = []
    for post in posts:
        post_dict = {
            "number": post_number,
            "question_type_title": post.question_type.question_type_title,
            "board_id": post.board_id,
            "question_title": post.question_title,
            "user_name": post.question_user.user_name,
            "question_datetime": post.question_datetime,
        }
        post_list.append(post_dict)
        post_number -= 1

    return JsonResponse(
        {
            "tot_post": tot_post,
            "post_list": post_list,
            "keyword": keyword,
            "page": page,
            "type_list": type_list,
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 게시글 상세 페이지
@csrf_exempt
def post_detail(request, post_id):
    post = get_object_or_404(Qnaboard, board_id=post_id)

    if post.question_image_file:  # 이미지 파일이 있는 경우
        question_image_url = post.question_image_file.url
    else:  # 이미지 파일이 없는 경우
        question_image_url = None

    return JsonResponse(
        {
            "success": True,
            "board_id": post.board_id,
            "question_type_title": post.question_type.question_type_title,
            "user_name": post.question_user.user_name,
            "user_id": post.question_user.user_id,
            "question_datetime": post.question_datetime,
            "question_title": post.question_title,
            "question_content": post.question_content,
            "answer_content": post.answer_content,
            "answer_admin_name": None if post.answer_admin is None else post.answer_admin.user_name,
            "answer_datetime": post.answer_datetime,
            "question_image_file": ("http://localhost:8000/board" + question_image_url)
            if question_image_url
            else None,
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 게시글 작성
@csrf_exempt
def post_create(request):
    user, response = validate_token(request)

    if not response["success"]:
        return JsonResponse(response, status=400)

    if request.method == "POST":
        question_type_id = request.POST["question_type_id"]
        question_type = Questiontype.objects.get(question_type_id=question_type_id)

        # 이미지 파일 처리
        if "image" in request.FILES:
            question_image_file = request.FILES["image"]
            
            # 파일명에서 확장자 추출
            file_extension = splitext(question_image_file.name)[1].lower()

            # 원하는 확장자가 아닌 경우 None 할당
            if file_extension not in WHITE_LIST_EXT:
                question_image_file = None
                
        else:
            # 이미지 파일이 전송되지 않은 경우, 기본값 또는 None으로 설정할 수 있음
            question_image_file = None

        new_post = Qnaboard.objects.create(
            question_user=user,
            question_type=question_type,
            question_title=request.POST["question_title"],
            question_content=request.POST["question_content"],
            question_image_file=question_image_file,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "게시글 작성이 완료되었습니다.",
                "board_id": new_post.board_id,
            },
            status=200,
            json_dumps_params={"ensure_ascii": False},
        )


# 게시글 삭제
@csrf_exempt
def post_delete(request, post_id):
    user, response = validate_token(request)

    if not response["success"]:
        return JsonResponse(response, status=400)

    post = get_object_or_404(Qnaboard, board_id=post_id)

    if user.user_id == post.question_user.user_id or user.role == "admin":
        post.is_deleted = True
        post.save()
        return JsonResponse(
            {"success": True, "message": "게시글 삭제 완료"},
            status=200,
            json_dumps_params={"ensure_ascii": False},
        )

    else:
        return JsonResponse(
            {"success": False, "message": "게시글 삭제 권한이 없습니다."},
            status=403,
            json_dumps_params={"ensure_ascii": False},
        )


# 게시글 수정 페이지 화면
@csrf_exempt
def post_update_get(request, post_id):
    user, response = validate_token(request)
    if not response["success"]:
        return JsonResponse(response, status=400)

    post = get_object_or_404(Qnaboard, board_id=post_id)

    if user.user_id == post.question_user.user_id:
        if post.question_image_file:  # 이미지 파일이 있는 경우
            question_image_url = post.question_image_file.url
        else:  # 이미지 파일이 없는 경우
            question_image_url = None

        response_data = {
            "success": True,
            "board_id": post.board_id,
            "question_type_title": post.question_type.question_type_title,
            "user_name": post.question_user.user_name,
            "question_datetime": post.question_datetime,
            "question_title": post.question_title,
            "question_content": post.question_content,
            "question_image_file": ("http://localhost:8000/board" + question_image_url)
            if question_image_url
            else None,
        }

        print(response_data)

        return JsonResponse(
            response_data,
            status=200,
            json_dumps_params={"ensure_ascii": False},
        )
    else:
        return JsonResponse(
            {"success": False, "message": "게시글 수정 권한이 없습니다."},
            status=403,
            json_dumps_params={"ensure_ascii": False},
        )


# 게시글 DB 수정
@csrf_exempt
@require_POST
def post_update_post(request, post_id):
    user, response = validate_token(request)

    if not response["success"]:
        return JsonResponse(response, status=400)

    post = get_object_or_404(Qnaboard, board_id=post_id)

    if user.user_id == post.question_user.user_id:
        question_type_id = request.POST["question_type_id"]
        question_type = Questiontype.objects.get(question_type_id=question_type_id)
        post.question_type = question_type
        post.question_title = request.POST.get("question_title")
        post.question_content = request.POST.get("question_content")
        
        if "image" in request.FILES:
            post.question_image_file = request.FILES["image"]

        post.save()

        return JsonResponse(
            {"success": True, "message": "수정하였습니다."},
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )

    else:
        return JsonResponse(
            {"success": False, "message": "게시글 수정 권한이 없습니다."},
            status=403,
            json_dumps_params={"ensure_ascii": False},
        )


# 문의 답변 작성
@csrf_exempt
@require_POST
def answer_create(request, post_id):
    user, response = validate_token(request)
    # 데이터 받아오기
    json_data = json.loads(request.body.decode("utf-8"))
    answer_content = json_data.get("answer_content")

    if not response["success"]:
        return JsonResponse(response, status=400)

    if user.role == "admin":
        post = get_object_or_404(Qnaboard, board_id=post_id)

        post.answer_content = answer_content
        post.answer_datetime = timezone.now()
        post.answer_admin = user
        post.save()
        return JsonResponse(
            {"success": True, "message": "답변이 작성되었습니다."},
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )

    else:
        msg = {"message": "관리자만 작성할 수 있습니다."}
        return JsonResponse(
            {"success": False, "message": "권한이 없습니다."},
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


# 문의 답변글 상세 페이지
@csrf_exempt
def answer_detail(request, post_id):
    post = get_object_or_404(Qnaboard, board_id=post_id)

    return JsonResponse(
        {
            "answer_title": "[답변]" + post.question_title,
            "answer_content": post.answer_content,
            "board_id": post.board_id,
            "question_type_title": post.question_type.question_type_title,
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 마이페이지
@csrf_exempt
def myinfo(request):
    user, response = validate_token(request)

    if not response["success"]:
        return JsonResponse(response, status=400)

    return JsonResponse(
        {
            "user_id": user.user_id,
            "password": "*******",
            "user_name": mask_name(user.user_name),
            "user_email": user.user_email,
            "role": user.role,
        },
        json_dumps_params={"ensure_ascii": False},
    )
