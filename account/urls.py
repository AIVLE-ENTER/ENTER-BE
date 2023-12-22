from django.urls import path
from . import signup_views

app_name = "account"

urlpatterns = [
    # signup_views.py
    path("signUp/checkId/", signup_views.check_id_duplicate, name="check-id"),
    path("signUp/company/", signup_views.company_list, name="company-list"),
    path("signUp/", signup_views.sign_up, name="sign-up"),
]
