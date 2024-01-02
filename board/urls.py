from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "board"

urlpatterns = [
    path("", views.post_list),  # 게시판에서 게시글 목록
    path("questionTypeList/", views.question_type_list),  # 질문 타입 목록
    path("<int:post_id>/", views.post_detail),  # 게시글 상세 페이지
    path("create/", views.post_create),  # 게시판에서 '글쓰기' 버튼 클릭 시
    path("<int:post_id>/delete/", views.post_delete),  # 게시글 상세 페이지에서 '삭제' 버튼 클릭 시
    path(
        "<int:post_id>/post_update_get/", views.post_update_get
    ),  # 게시글 상세 페이지에서 '수정' 버튼 클릭 시
    path(
        "<int:post_id>/post_update_post/", views.post_update_post
    ),  # 게시글을 수정하는 페이지에서 수정 후 '수정' 클릭 시
    path("<int:post_id>/answer", views.answer_detail),  # 문의글 상세 페이지
    path("<int:post_id>/answer_create", views.answer_create),  # 문의 답변 글 작성
    path("myinfo/", views.myinfo),  # 마이페이지
]

# MEDIA_URL로 들어오는 요청에 대해 MEDIA_ROOT 경로를 탐색한다.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
