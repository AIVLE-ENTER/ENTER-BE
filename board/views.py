import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from enter.models import Qnaboard, Questiontype, Users
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

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


# 게시판 게시글 목록
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

    # 페이지 처리
    page = request.GET.get("page", 1)  # 기본값 1
    paginator = Paginator(posts, 3)  # 한 페이지에 보여질 게시물 수 설정

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
            "post_list": post_list,
            "keyword": keyword,
            "page": page,
            "type_list": type_list,
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 게시글 상세 페이지
def post_detail(request, post_id):

    post = get_object_or_404(Qnaboard, board_id=post_id)

    return JsonResponse(
        {
            "board_id": post.board_id,
            "question_type_title": post.question_type.question_type_title,
            "user_name": post.question_user.user_name,
            "question_datetime": post.question_datetime,
            "question_title": post.question_title,
            "question_content": post.question_content,
            "question_image_file": post.question_image_file,
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 게시글 작성
@login_required  # LOGIN_URL 설정 필요
@csrf_exempt
def post_create(request):
    # 유저 정보 확인
    session_user_id = request.session.get("user_id", None)
    if session_user_id is None:  # 로그인 페이지로 (로그인 페이지 링크로 수정해야함)
        msg = {"message": "로그인을 해주세요."}
        return JsonResponse(msg) # 프론트에서 redirect 처리
    
    if Users.objects.filter(user_id=session_user_id).exists():
        user = Users.objects.get(user_id=session_user_id)

    if request.method == "POST":
        
        question_type_id = request.POST["question_type_id"]
        question_type = Questiontype.objects.get(question_type_id=question_type_id)
        
        new_post = Qnaboard.objects.create(
            question_user=user.user_id,
            question_type=question_type,
            question_title=request.POST["question_title"],
            question_content=request.POST["question_content"],
            question_image_file=request.FILES["image"],
        )
        return redirect(f"/board/{new_post.board_id}")


# 게시글 삭제
def post_delete(request, post_id):
    
    post = get_object_or_404(Qnaboard, board_id=post_id)
    
    if request.session.get("user_id", None) == post.user.user_id:
        post.is_deleted = True
        post.save()
        msg = {"message": "게시글을 삭제하였습니다."}
    else:
        msg = {"message": "작성자만 삭제할 수 있습니다."}
        
    return JsonResponse(msg, json_dumps_params={"ensure_ascii": False},)


# 게시글 수정 페이지 화면
def post_update_get(request, post_id):
    
    post = get_object_or_404(Qnaboard, board_id=post_id)

    return JsonResponse(
        {
            "board_id": post.board_id,
            "question_type_title": post.question_type.question_type_title,
            "user_name": post.question_user.user_name,
            "question_datetime": post.question_datetime,
            "question_title": post.question_title,
            "question_content": post.question_content,
            "question_image_file": post.question_image_file,
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 게시글 DB 수정
@require_POST
def post_update_post(request, post_id):
    
    post = get_object_or_404(Qnaboard, board_id=post_id)
    
    # session_user_id = request.session.get("user_id", None)
    # user = Users.objects.get(user_id=session_user_id)
    
    if request.method == "POST":
        
        if request.session.get("user_id", None) == post.question_user.user_id:
            
            question_type_id = request.POST["question_type_id"]
            question_type = Questiontype.objects.get(question_type_id=question_type_id)

            post.question_type = question_type
            post.question_title = request.POST.get('question_title')
            post.question_content = request.POST.get('question_content')
            post.question_image_file = request.FILES['image']

            post.save()
            
            return redirect(f"/board/{post.board_id}") # 수정된 게시글의 상세 페이지로 리다이렉트
        
        else:
            msg = {"message": "작성자만 수정할 수 있습니다."}
            return JsonResponse(msg, json_dumps_params={"ensure_ascii": False},)