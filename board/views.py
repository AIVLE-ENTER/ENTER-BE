from django.http import JsonResponse
from enter.models import Qnaboard, Questiontype
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


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
        }
    )


def post_detail(request, post_id):
    post = Qnaboard.objects.get(board_id=post_id)

    return JsonResponse(
        {
            "board_id": post.board_id,
            "question_type_title": post.question_type.question_type_title,
            "user_name": post.question_user.user_name,
            "question_datetime": post.question_datetime,
            "question_title": post.question_title,
            "question_content": post.question_content,
            "question_file_name": post.question_file_name,
            "question_file_path": post.question_file_path,
        }
    )
