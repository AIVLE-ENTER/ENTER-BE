from django.urls import path
from . import signup_views

app_name = "account"

urlpatterns = [
    # signup_views.py
    path("signup/check-id/", signup_views.check_id_duplicate, name="check-id"),
    path(
        "signup/email/",
        signup_views.send_certification_number,
        name="send-certification",
    ),
]
