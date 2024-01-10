from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# 업로드 하는 파일에 대한 개수, 크기, 확장자 제한
FILE_COUNT_LIMIT = 3
# 업로드 하는 파일의 최대 사이즈 제한. 5MB : 5242880(5*1024*1024)
FILE_SIZE_LIMIT = 5242880
# 업로드 허용 확장자
WHITE_LIST_EXT = [
    ".jpg",
    ".jpeg",
    ".png",
]

def validate_file_count(value):
    # 파일 개수 제한 확인
    if len(value) > FILE_COUNT_LIMIT:
        raise ValidationError(_('최대 %s개까지만 업로드 가능합니다.') % FILE_COUNT_LIMIT)

def validate_file_size(value):
    # 파일 크기 제한 확인
    if value.size > FILE_SIZE_LIMIT:
        raise ValidationError(_('파일 크기는 최대 %s보다 작아야 합니다.') % FILE_SIZE_LIMIT)

def validate_file_extension(value):
    # 파일 확장자 제한 확인
    ext = os.path.splitext(value.name)[1]  # 파일 확장자 가져오기
    if not ext.lower() in WHITE_LIST_EXT:
        raise ValidationError(_('지원하지 않는 확장자입니다.'))


class Analysismemo(models.Model):
    id = models.AutoField(primary_key=True)
    memo_id = models.CharField(max_length=40)
    memo_content = models.CharField(max_length=700)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("Users", on_delete=models.CASCADE)

    class Meta:
        # managed = False
        db_table = "AnalysisMemo"


class Analysisresults(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    chat_window = models.ForeignKey("Chatwindow", on_delete=models.CASCADE)
    request_message = models.CharField(max_length=1000)
    request_datetime = models.DateTimeField()
    result_description = models.TextField()
    result_imagepaths = models.CharField(max_length=255, blank=True, null=True)
    result_datetime = models.DateTimeField()
    use_memo = models.IntegerField(
        default=0, blank=True, null=True
    )  # 메모사용여부 (0: 미사용, 1: 사용)

    class Meta:
        # managed = False
        db_table = "AnalysisResults"


class Chatwindow(models.Model):
    chat_window_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("Users", on_delete=models.CASCADE)
    target_object = models.CharField(max_length=20)
    title = models.CharField(max_length=20)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        # managed = False
        db_table = "ChatWindow"


class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=20)
    industry = models.CharField(max_length=20, blank=True, null=True)
    number_of_employees = models.IntegerField(blank=True, null=True)
    tot_sales = models.IntegerField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = "Company"


class Prompttemplates(models.Model):
    template_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("Users", on_delete=models.CASCADE)
    template_name = models.CharField(max_length=100)
    template_content = models.TextField()
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    is_deleted = models.IntegerField(default=0)  # 삭제여부 (0: 유지, 1: 삭제)

    class Meta:
        # managed = False
        db_table = "PromptTemplates"


class Qnaboard(models.Model):
    board_id = models.AutoField(primary_key=True)
    question_user = models.ForeignKey(
        "Users", on_delete=models.CASCADE, related_name="question_user_qnaboard_set"
    )
    question_type = models.ForeignKey("Questiontype", on_delete=models.CASCADE)
    question_title = models.CharField(max_length=30)
    question_content = models.CharField(max_length=100)
    question_image_file = models.ImageField(null=True, upload_to="", blank=True, validators=[validate_file_count, validate_file_size, validate_file_extension])
    question_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    answer_admin = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="answer_admin_qnaboard_set",
    )
    answer_content = models.CharField(max_length=255, blank=True, null=True)
    answer_datetime = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        # managed = True
        db_table = "QnABoard"


class Questiontype(models.Model):
    question_type_id = models.AutoField(primary_key=True)
    question_type_title = models.CharField(unique=True, max_length=20)
    question_type_content = models.CharField(max_length=20)

    class Meta:
        # managed = False
        db_table = "QuestionType"


class Users(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20)
    password = models.TextField()
    user_name = models.CharField(max_length=20)
    user_email = models.CharField(max_length=30)
    kakao_id = models.CharField(max_length=255, blank=True, null=True)
    naver_id = models.CharField(max_length=255, blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=5, default="user")  # admin: 관리자, user: 일반 사용자
    register_datetime = models.DateTimeField(auto_now_add=True)
    user_status = models.IntegerField(default=0)  # 0: 회원, 1: 탈퇴회원
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    privacy_agreement = models.BooleanField()  # 0: 미동의, 1: 동의

    class Meta:
        # managed = False
        db_table = "Users"


class Emailauth(models.Model):
    auth_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=30)
    certification_number = models.IntegerField()
    purpose = models.CharField(max_length=20)
    created_datetime = models.DateTimeField(auto_now_add=True)
    is_vertified = models.BooleanField(default=False)

    class Meta:
        # managed = False
        db_table = "EmailAuth"


class Emailtemplates(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    purpose = models.CharField(unique=True, max_length=20)

    class Meta:
        # managed = False
        db_table = "EmailTemplates"
