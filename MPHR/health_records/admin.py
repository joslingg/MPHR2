from django.contrib import admin
from .models import HealthRecord

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('ho_ten_dem', 'ten', 'gioi_tinh', 'khoa_phong', 'chuc_danh', 'ket_luan')
    search_fields = ('ho_ten_dem', 'ten', 'khoa_phong', 'chuc_danh')
