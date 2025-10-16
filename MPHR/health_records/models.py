from django.db import models

class HealthRecord(models.Model):
    ho_ten_dem = models.CharField(max_length=100, blank=True, null=True)
    ten = models.CharField(max_length=50)
    nam_sinh = models.PositiveIntegerField()
    gioi_tinh = models.CharField(max_length=10, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')])
    khoa_phong = models.CharField(max_length=100, blank=True, null=True)
    chuc_danh = models.CharField(max_length=100, blank=True, null=True)
    ngay_tiem_cum = models.DateField(blank=True, null=True)
    chieu_cao = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    can_nang = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ket_qua_file = models.CharField(max_length=200, blank=True, null=True)
    nhom = models.CharField(max_length=20, blank=True, null=True)
    ket_luan = models.CharField(max_length=200, blank=True, null=True)
    ghi_chu = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['ten']

    def __str__(self):
        return f"{self.ho_ten_dem} {self.ten}".strip()

