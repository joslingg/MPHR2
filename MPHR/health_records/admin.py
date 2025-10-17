from django.contrib import admin
from .models import Department, ExamType, HealthClassification, HealthRecord


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(HealthClassification)
class HealthClassificationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = (
        "ma_nv", "full_name", "birth_year", "gender", "department",
        "year", "exam_type", "health_classification", "conclusion", "updated_at",
    )
    list_filter = (
        "year", "gender", "department", "exam_type", "health_classification",
    )
    search_fields = ("ma_nv", "full_name")
    readonly_fields = ("created_at", "updated_at", "conclusion_display")
    ordering = ("-year", "full_name")

    fieldsets = (
        ("Thông tin cá nhân", {
            "fields": ("ma_nv", "stt", "full_name", "birth_year", "gender")
        }),
        ("Công việc", {
            "fields": ("job_title", "position", "department")
        }),
        ("Tiêm chủng", {
            "fields": ("vaccinated_influvac", "vaccinated_vaxigrip", "vaccination_date")
        }),
        ("Khám sức khoẻ", {
            "fields": ("year", "exam_date", "exam_type", "clinic_name")
        }),
        ("Số đo", {
            "fields": ("height_cm", "weight_kg", "blood_pressure")
        }),
        ("Kết quả", {
            "fields": ("health_classification", "conclusion_display", "conclusion_text")
        }),
        ("Khác", {
            "fields": ("group", "note", "result_file", "created_at", "updated_at")
        }),
    )
    class Media:
        js = ("health_records/admin_auto_conclusion.js",)

    def conclusion_display(self, obj):
        """Hiển thị kết luận tự động trong admin (readonly)."""
        return obj.conclusion
    conclusion_display.short_description = "Kết luận tự động"

