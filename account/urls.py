from django.urls import path
from . import signup_views

app_name = "account"

urlpatterns = [
    # signup_views.py
    path("signUp/checkId/", signup_views.check_id_duplicate, name="check-id"),
    path(
        "signUp/email/",
        signup_views.send_certification_number,
        name="send-certification",
    ),
]
