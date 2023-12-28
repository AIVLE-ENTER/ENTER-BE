from django.urls import path
from . import chat_views, message_views

app_name = "main"

urlpatterns = [
    # 채팅방
    path("", chat_views.chat_window_list),
    path("chatWindow/create/", chat_views.create_chat_window),
    path("chatWindow/update/", chat_views.update_chat_window),
    path("chatWindow/delete/", chat_views.delete_chat_window),
    # 자주 쓰는 문구
    path("frequentMessage/", message_views.frequent_message_list),
    # path("frequentMessage/create/", views.create_frequent_message),
    # path("frequentMessage/update/", views.update_frequent_message),
    # path("frequentMessage/delete/", views.delete_frequent_message),
]
