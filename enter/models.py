from django.db import models


class Analysismemo(models.Model):
    memo_id = models.AutoField(primary_key=True)
    analysis = models.ForeignKey("Analysisresults", on_delete=models.CASCADE)
    memo_content = models.CharField(max_length=255)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    is_deleted = models.IntegerField(default=0)  # 삭제여부 (0: 유지, 1: 삭제)

    class Meta:
        managed = False
        db_table = "AnalysisMemo"


class Analysisresults(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    chat_window = models.ForeignKey("Chatwindow", on_delete=models.CASCADE)
    request_message = models.CharField(max_length=1000)
    request_datetime = models.DateTimeField()
    result_description = models.CharField()
    result_imagepaths = models.CharField(max_length=255, blank=True, null=True)
    result_datetime = models.DateTimeField()
    use_memo = models.IntegerField(blank=True, null=True)  # 메모사용여부 (0: 미사용, 1: 사용)

    class Meta:
        managed = False
        db_table = "AnalysisResults"


class Chatwindow(models.Model):
    chat_window_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("Users", on_delete=models.CASCADE)
    target_object = models.CharField(max_length=20)
    title = models.CharField(max_length=20)
    crawling_text = models.CharField(max_length=1000, blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "ChatWindow"


class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=20)
    industry = models.CharField(max_length=20, blank=True, null=True)
    number_of_employees = models.IntegerField(blank=True, null=True)
    tot_sales = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Company"


class Prompttemplates(models.Model):
    template_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("Users", on_delete=models.CASCADE)
    template_name = models.CharField(max_length=30)
    template_content = models.CharField(max_length=50)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    is_deleted = models.IntegerField(default=0)  # 삭제여부 (0: 유지, 1: 삭제)

    class Meta:
        managed = False
        db_table = "PromptTemplates"


class Qnaboard(models.Model):
    board_id = models.AutoField(primary_key=True)
    question_user = models.ForeignKey("Users", on_delete=models.CASCADE)
    question_type = models.ForeignKey("Questiontype", on_delete=models.CASCADE)
    question_title = models.CharField(max_length=30)
    question_content = models.CharField(max_length=100)
    question_file_name = models.CharField(max_length=255, blank=True, null=True)
    question_file_path = models.CharField(max_length=255, blank=True, null=True)
    question_datetime = models.DateTimeField()
    answer_admin = models.ForeignKey(
        "Users", on_delete=models.CASCADE, blank=True, null=True
    )
    answer_content = models.CharField(max_length=255, blank=True, null=True)
    answer_datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "QnABoard"


class Questiontype(models.Model):
    question_type_id = models.AutoField(primary_key=True)
    question_type_title = models.CharField(unique=True, max_length=20)
    question_type_content = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = "QuestionType"


class Users(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(max_length=20)
    user_name = models.CharField(max_length=20)
    user_email = models.CharField(max_length=30)
    kakao_id = models.CharField(max_length=255, blank=True, null=True)
    naver_id = models.CharField(max_length=255, blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=5, db_comment="admin: 관리자, user: 일반 사용자")
    register_datetime = models.DateTimeField()
    user_status = models.IntegerField(db_comment="0: 회원, 1: 탈퇴회원")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "Users"


class Emailauth(models.Model):
    auth_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=30)
    certification_number = models.IntegerField()
    created_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "emailAuth"