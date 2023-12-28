from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.chat_window_list),
]
