from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "board"

urlpatterns = [
    path("", views.post_list),
    path("<int:post_id>/", views.post_detail),
    path("create/", views.post_create),
    path("delete/", views.post_delete),
    path("<int:post_id>/delete/", views.post_delete),
]

# MEDIA_URL로 들어오는 요청에 대해 MEDIA_ROOT 경로를 탐색한다.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
