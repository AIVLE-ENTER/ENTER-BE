from django.urls import path
from . import auth_views, signup_views, social_views

app_name = "account"

urlpatterns = [
    # signup_views.py (회원가입)
    path("signUp/checkId/", signup_views.check_id_duplicate, name="check-id"),
    path("signUp/company/", signup_views.company_list, name="company-list"),
    path("signUp/", signup_views.sign_up, name="sign-up"),
    # auth_views.py (로그인, 아이디 찾기, 비밀번호 변경, 회원 탈퇴)
    path("auth/checkId/", auth_views.check_id, name="check-id"),
    path("auth/signIn/", auth_views.sign_in, name="sign-in"),
    path("auth/findID/", auth_views.find_id, name="find-id"),
    path("auth/changePassword/", auth_views.change_password, name="chage-password"),
    path("auth/signOut/", auth_views.sign_out, name="sign-out"),
    path("auth/userInfo/", auth_views.user_info, name="user-info"),
    # social_views.py (소셜 연동)
    path("kakaoLogin/", social_views.kakao_login, name="kakao-login"),
    path("googleLogin/", social_views.google_login, name="google-login"),
    path("naverLogin/", social_views.naver_login, name="naver-login"),
]
