from django.urls import path
from . import views

app_name = "utils"

urlpatterns = [
    path(
        "checkCertificationNumber/",
        views.check_certification_number,
        name="check-certification-number",
    ),
]
