from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên khoa/phòng")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Khoa/Phòng"
        verbose_name_plural = "Khoa/Phòng"


class ExamType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Loại khám")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Loại khám"
        verbose_name_plural = "Loại khám"


class HealthClassification(models.Model):
    """
    Ví dụ các bản ghi: "I", "II", "III", "IV"
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Phân loại")
    description = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Phân loại sức khoẻ"
        verbose_name_plural = "Phân loại sức khoẻ"


class HealthRecord(models.Model):
    # --- Nhận diện & thông tin cơ bản ---
    ma_nv = models.CharField(max_length=50, verbose_name="Mã NV", null=True, blank=True, help_text="Mã nhân viên, không bắt buộc phải unique để lưu nhiều năm")
    full_name = models.CharField(max_length=200, verbose_name="Họ và tên")
    # giữ cả ngày sinh (nếu có) và năm sinh nếu muốn import theo năm
    birth_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Năm sinh")
    GENDER_CHOICES = [('Nam', 'Nam'), ('Nữ', 'Nữ')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Giới tính")

    # --- Công việc ---
    job_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Chức danh nghề nghiệp")
    position = models.CharField(max_length=200, blank=True, null=True, verbose_name="Chức vụ")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Khoa/Phòng")

    # --- Tiêm chủng (2 loại checkbox + ngày tiêm) ---
    vaccinated_influvac = models.BooleanField(default=False, verbose_name="Influvac tetra 0.5ml/ Hà Lan")
    vaccinated_vaxigrip = models.BooleanField(default=False, verbose_name="Vaxigrip tetra 0.5ml/ Pháp")
    vaccination_date = models.DateField(blank=True, null=True, verbose_name="Ngày tiêm")

    # --- Thông tin khám ---
    year = models.PositiveIntegerField(verbose_name="Năm khám", help_text="Năm ghi nhận kết quả (ví dụ 2023)")
    exam_date = models.DateField(blank=True, null=True, verbose_name="Ngày khám")
    exam_type = models.ForeignKey(ExamType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loại khám")
    clinic_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cơ sở khám")

    # --- Số đo ---
    height_cm = models.DecimalField("Chiều cao (cm)", max_digits=6, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField("Cân nặng (kg)", max_digits=6, decimal_places=2, blank=True, null=True)
    blood_pressure = models.CharField("Huyết áp (mmHg)", max_length=50, blank=True, null=True)

    # --- Kết quả phân loại & kết luận ---
    health_classification = models.ForeignKey(HealthClassification, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phân loại sức khỏe")
    # kết luận không lưu trực tiếp (read-only) mà là property tự động
    # tuy nhiên vẫn giữ 1 trường text 'conclusion_text' nếu bạn muốn override/tự nhập tay
    conclusion_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kết luận (ghi tay, nếu có)")

    # --- File kết quả, nhóm, ghi chú ---
    result_file = models.FileField(upload_to="health_results/", blank=True, null=True, verbose_name="File kết quả (PDF)")
    group = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nhóm")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tạo lúc")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    class Meta:
        verbose_name = "Hồ sơ khám sức khoẻ"
        verbose_name_plural = "Hồ sơ khám sức khoẻ"
        ordering = ['-year', 'full_name']
        # nếu muốn ngăn duplicate hoàn toàn (ma_nv+năm), uncomment line dưới:
        # unique_together = ("ma_nv", "year")

    def __str__(self):
        return f"{self.full_name} ({self.ma_nv}) - {self.year}"

    @property
    def conclusion(self):
        """
        Ưu tiên trả conclusion_text nếu người dùng nhập thủ công.
        Nếu không có, tự động sinh theo phân loại:
          I, II, III -> "Đủ sức khoẻ làm việc"
          IV -> "Làm việc hợp lý"
        """
        if self.conclusion_text:
            return self.conclusion_text
        if not self.health_classification:
            return ""
        name = str(self.health_classification.name).strip().upper()
        if name in ["I", "II", "III"]:
            return "Đủ sức khoẻ làm việc"
        if name == "IV":
            return "Làm việc hợp lý"
        return ""
