from django.contrib import admin
from .models import (
    Department,
    ExaminationType,
    HealthClassification,
    Employee,
    HealthRecord,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ExaminationType)
class ExaminationTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(HealthClassification)
class HealthClassificationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("code", "full_name", "gender", "department", "job_title", "position")
    list_filter = ("department", "gender")
    search_fields = ("full_name", "code")
    ordering = ("full_name",)


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "year",
        "exam_date",
        "examination_type",
        "health_classification",
        "vaccinated",
        "vaccine_name",
        "status",
    )
    list_filter = (
        "year",
        "status",
        "examination_type",
        "health_classification",
        "employee__department",
    )
    search_fields = ("employee__full_name", "vaccine_name", "clinic_name")
    autocomplete_fields = ("employee",)
    date_hierarchy = "exam_date"
    ordering = ("-year", "employee__full_name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Thông tin cơ bản", {
            "fields": ("employee", "year", "exam_date", "examination_type", "clinic_name")
        }),
        ("Chỉ số đo", {
            "fields": ("height_cm", "weight_kg", "blood_pressure")
        }),
        ("Tiêm chủng", {
            "fields": ("vaccinated", "vaccine_name", "vaccination_date")
        }),
        ("Kết quả & phân loại", {
            "fields": ("health_classification", "conclusion_text", "status")
        }),
        ("Tệp & thông tin thêm", {
            "fields": ("result_file", "group", "note", "created_at", "updated_at")
        }),
    )
