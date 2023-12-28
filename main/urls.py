from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    # 채팅방
    path("", views.chat_window_list),
    path("chatWindow/create/", views.create_chat_window),
    path("chatWindow/update/", views.update_chat_window),
    path("chatWindow/delete/", views.delete_chat_window),
    # 자주 쓰는 문구
    # path("frequentMessage/", views.frequent_message_list),
    # path("frequentMessage/create/", views.create_frequent_message),
    # path("frequentMessage/update/", views.update_frequent_message),
    # path("frequentMessage/delete/", views.delete_frequent_message),
]
