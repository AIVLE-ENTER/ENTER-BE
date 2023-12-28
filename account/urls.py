from django.urls import path
from . import auth_views, signup_views

app_name = "account"

urlpatterns = [
    # signup_views.py (회원가입)
    path("signUp/checkId/", signup_views.check_id_duplicate, name="check-id"),
    path("signUp/company/", signup_views.company_list, name="company-list"),
    path("signUp/", signup_views.sign_up, name="sign-up"),
    # auth_views.py (로그인, 아이디/비번 찾기, 회원 탈퇴)
    path("auth/signIn/", auth_views.sign_in, name="sign-in"),
    # social_views.py (소셜 연동)
]
