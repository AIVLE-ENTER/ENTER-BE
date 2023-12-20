from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path("signup/check-id/", views.check_id_duplicate, name="check-id"),
]