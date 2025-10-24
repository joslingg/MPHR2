from django.db import models


# --- Danh mục Khoa/Phòng ---
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên khoa/phòng")

    class Meta:
        verbose_name = "Khoa/Phòng"
        verbose_name_plural = "Danh mục Khoa/Phòng"
        ordering = ["name"]

    def __str__(self):
        return self.name


# --- Danh mục Loại khám ---
class ExaminationType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Loại khám")

    class Meta:
        verbose_name = "Loại khám"
        verbose_name_plural = "Danh mục Loại khám"
        ordering = ["name"]

    def __str__(self):
        return self.name


# --- Danh mục Phân loại sức khỏe ---
class HealthClassification(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Phân loại (I, II, III, IV...)")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả chi tiết")

    class Meta:
        verbose_name = "Phân loại sức khỏe"
        verbose_name_plural = "Danh mục Phân loại sức khỏe"
        ordering = ["name"]

    def __str__(self):
        return self.name


# --- Nhân viên ---
class Employee(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã nhân viên")
    full_name = models.CharField(max_length=200, verbose_name="Họ và tên")
    birth_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Năm sinh")
    GENDER_CHOICES = [("Nam", "Nam"), ("Nữ", "Nữ")]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Giới tính")
    job_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Chức danh nghề nghiệp")
    position = models.CharField(max_length=200, blank=True, null=True, verbose_name="Chức vụ")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Khoa/Phòng")

    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Danh sách nhân viên"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.code})"


# --- Hồ sơ sức khỏe từng năm ---
class HealthRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Nhân viên")
    year = models.PositiveIntegerField(verbose_name="Năm hồ sơ")
    exam_date = models.DateField(blank=True, null=True, verbose_name="Ngày khám")
    examination_type = models.ForeignKey(
        ExaminationType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loại khám"
    )
    clinic_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cơ sở khám")

    # --- Chỉ số đo ---
    height_cm = models.DecimalField("Chiều cao (cm)", max_digits=6, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField("Cân nặng (kg)", max_digits=6, decimal_places=2, blank=True, null=True)
    blood_pressure = models.CharField("Huyết áp (mmHg)", max_length=50, blank=True, null=True)

    # --- Vaccine ---
    vaccinated = models.BooleanField(default=False, verbose_name="Đã tiêm vắc-xin")
    vaccine_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên vắc-xin (nếu có)")
    vaccination_date = models.DateField(blank=True, null=True, verbose_name="Ngày tiêm (nếu có)")

    # --- Kết quả & phân loại ---
    health_classification = models.ForeignKey(
        HealthClassification, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phân loại sức khỏe"
    )
    conclusion_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kết luận (ghi tay, nếu có)")

    # --- File & thông tin thêm ---
    result_file = models.FileField(upload_to="health_results/", blank=True, null=True, verbose_name="File kết quả (PDF)")
    group = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nhóm")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    STATUS_CHOICES = [("done", "Đã khám"), ("pending", "Chưa khám")]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Trạng thái")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tạo lúc")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    class Meta:
        verbose_name = "Hồ sơ sức khỏe"
        verbose_name_plural = "Hồ sơ sức khỏe"
        ordering = ["-year", "employee__full_name"]
        unique_together = ("employee", "year")

    def __str__(self):
        return f"{self.employee.full_name} - {self.year}"

    @property
    def conclusion(self):
        """
        Nếu có nhập tay thì dùng, nếu không thì sinh tự động từ phân loại sức khỏe.
        """
        if self.conclusion_text:
            return self.conclusion_text
        if not self.health_classification:
            return ""
        name = self.health_classification.name.strip().upper()
        if name in ["I", "II", "III"]:
            return "Đủ sức khoẻ làm việc"
        elif name == "IV":
            return "Làm việc hợp lý"
        return ""
